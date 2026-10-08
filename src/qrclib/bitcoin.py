"""Off-chain hybrid attestation for a Bitcoin transaction.

Bitcoin consensus still verifies ECDSA or Schnorr on secp256k1. An ML-DSA-65
signature is 3,309 bytes and does not fit in an 80-byte OP_RETURN, so this
module does not pretend to make a transaction unspendable by a quantum
adversary.

What it does:

* Hold a real secp256k1 key and a QRCL hybrid signing key side by side.
* Sign a canonical statement of ``(txid, compressed pubkey, hybrid pubkey, time)``.
* Publish the 32-byte SHA-256 commitment. The script ``OP_RETURN PUSH32``
  is 34 bytes, which does fit. The full attestation stays off-chain
  (heir packet, exchange record, cosigner policy).

What it does not do:

* It does not change what miners accept.
* A quantum adversary who recovers the secp256k1 secret from a revealed
  public key can still produce a consensus-valid signature.
* Do not reuse addresses. Prefer a spend path that hides the public key
  until the moment of spend, and plan to move coins when a post-quantum
  output type is actually consensus.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from qrclib.hybrid import HYBRID_SIGN_SIG_LEN, SignKeyPair, generate_sign_keys, sign, verify

_TX_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_ALPHABET = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

GUIDANCE = (
    "This attestation is off-chain. Miners will not see the ML-DSA signature.",
    "OP_RETURN can carry the 32-byte commitment (script is 34 bytes), not the 3,373-byte hybrid signature.",
    "A quantum break of secp256k1 still produces a consensus-valid spend once the public key is revealed.",
    "Do not reuse addresses. Move coins when a post-quantum output type activates.",
)


def _b58encode(data: bytes) -> str:
    number = int.from_bytes(data, "big")
    chars = bytearray()
    while number:
        number, rem = divmod(number, 58)
        chars.append(_ALPHABET[rem])
    pad = 0
    for byte in data:
        if byte == 0:
            pad += 1
        else:
            break
    return (_ALPHABET[:1] * pad + bytes(reversed(chars))).decode("ascii")


def p2pkh_address(compressed_pubkey: bytes) -> str:
    if len(compressed_pubkey) != 33:
        raise ValueError("expected a 33-byte compressed secp256k1 public key")
    hashed = hashlib.new("ripemd160", hashlib.sha256(compressed_pubkey).digest()).digest()
    payload = b"\x00" + hashed
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    return _b58encode(payload + checksum)


@dataclass
class Attestation:
    tx_hash: str
    btc_public_key: bytes
    btc_address: str
    hybrid_public_key: bytes
    signature: bytes
    timestamp: str

    def signing_bytes(self) -> bytes:
        if not _TX_RE.match(self.tx_hash):
            raise ValueError("txid must be 64 hex characters")
        stamp = self.timestamp.encode("ascii")
        if len(stamp) > 80:
            raise ValueError("timestamp is too long")
        return (
            b"QRCL-BTC-ATTEST-v1\n"
            + bytes.fromhex(self.tx_hash)
            + self.btc_public_key
            + self.hybrid_public_key
            + bytes([len(stamp)])
            + stamp
        )

    def verify(self) -> bool:
        try:
            return verify(self.hybrid_public_key, self.signing_bytes(), self.signature)
        except (ValueError, TypeError):
            return False

    def commitment(self) -> bytes:
        """32 bytes. Bind this, not the signature, into a chain that has no room."""
        return hashlib.sha256(self.signing_bytes() + self.signature).digest()

    def op_return_script(self) -> bytes:
        commitment = self.commitment()
        return bytes((0x6A, 0x20)) + commitment


class QuantumProtectedWallet:
    """secp256k1 key plus an ML-DSA-65/Ed25519 hybrid signing key."""

    def __init__(self, btc_secret: bytes, signing: SignKeyPair):
        if len(btc_secret) != 32:
            raise ValueError("secp256k1 secret must be 32 bytes")
        self._btc_secret = bytes(btc_secret)
        self.signing = signing
        private = ec.derive_private_key(int.from_bytes(self._btc_secret, "big"), ec.SECP256K1())
        self.btc_public_key = private.public_key().public_bytes(
            serialization.Encoding.X962,
            serialization.PublicFormat.CompressedPoint,
        )
        self.btc_address = p2pkh_address(self.btc_public_key)

    @classmethod
    def generate(cls) -> QuantumProtectedWallet:
        private = ec.generate_private_key(ec.SECP256K1())
        secret = private.private_numbers().private_value.to_bytes(32, "big")
        return cls(secret, generate_sign_keys())

    def protect_transaction(self, tx_hash: str, timestamp: str | None = None) -> Attestation:
        if not _TX_RE.match(tx_hash):
            raise ValueError("txid must be 64 hex characters")
        stamp = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        draft = Attestation(
            tx_hash=tx_hash.lower(),
            btc_public_key=self.btc_public_key,
            btc_address=self.btc_address,
            hybrid_public_key=self.signing.public_key,
            signature=b"",
            timestamp=stamp,
        )
        signature = sign(self.signing.secret_key, draft.signing_bytes())
        if len(signature) != HYBRID_SIGN_SIG_LEN:
            raise RuntimeError("unexpected hybrid signature length")
        draft.signature = signature
        return draft

    def public_info(self) -> dict[str, str]:
        return {
            "btc_address": self.btc_address,
            "btc_public_key": self.btc_public_key.hex(),
            "hybrid_public_key": self.signing.public_key.hex(),
        }
