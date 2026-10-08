"""Two-party messages over a long-term X-Wing key.

This is not forward secret. A later compromise of the recipient's X-Wing
secret decrypts recorded offers. Rotate the key pair to bound that window.
"""

from __future__ import annotations

import secrets

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from qrclib.errors import InvalidSeal, VerificationFailed
from qrclib.hybrid import (
    HYBRID_SIGN_SIG_LEN,
    XWING_CT_LEN,
    KemKeyPair,
    SignKeyPair,
    decapsulate,
    encapsulate,
    generate_kem_keys,
    generate_sign_keys,
    sign,
    verify,
)
from qrclib.kdf import hkdf_sha256

_INFO = b"qrclib-session-v1"
_AAD = b"qrclib-msg-v1"


class Mailbox:
    def __init__(self, name: str, kem: KemKeyPair | None = None, signing: SignKeyPair | None = None):
        if not isinstance(name, str) or not name:
            raise ValueError("name must be a non-empty string")
        self.name = name
        self.kem = kem or generate_kem_keys()
        self.signing = signing or generate_sign_keys()
        self._key: bytes | None = None
        self._peer_sign: bytes | None = None

    def offer(self, peer_kem_public: bytes) -> bytes:
        """Encapsulate to a peer and sign the ciphertext. Sets the local session key."""
        ciphertext, shared = encapsulate(peer_kem_public)
        self._key = hkdf_sha256(shared, _INFO)
        return ciphertext + sign(self.signing.secret_key, ciphertext)

    def accept(self, offer_blob: bytes, peer_sign_public: bytes) -> None:
        """Verify an offer, decapsulate, and remember the peer's signing key."""
        raw = bytes(offer_blob)
        if len(raw) != XWING_CT_LEN + HYBRID_SIGN_SIG_LEN:
            raise VerificationFailed("offer has the wrong length")
        ciphertext, signature = raw[:XWING_CT_LEN], raw[XWING_CT_LEN:]
        if not verify(peer_sign_public, ciphertext, signature):
            raise VerificationFailed("offer signature rejected")
        shared = decapsulate(self.kem.secret_key, ciphertext)
        self._key = hkdf_sha256(shared, _INFO)
        self._peer_sign = bytes(peer_sign_public)

    def bind_peer(self, peer_sign_public: bytes) -> None:
        """Caller of ``offer`` must bind the peer signing key before reading replies."""
        self._peer_sign = bytes(peer_sign_public)

    def encrypt(self, plaintext: bytes) -> bytes:
        key = self._require_key()
        if isinstance(plaintext, str):
            plaintext = plaintext.encode("utf-8")
        nonce = secrets.token_bytes(12)
        body = AESGCM(key).encrypt(nonce, plaintext, _AAD)
        packet = nonce + body
        return packet + sign(self.signing.secret_key, packet)

    def decrypt(self, packet: bytes) -> bytes:
        key = self._require_key()
        if self._peer_sign is None:
            raise VerificationFailed("peer signing key is not bound")
        raw = bytes(packet)
        if len(raw) < 12 + 16 + HYBRID_SIGN_SIG_LEN:
            raise InvalidSeal("truncated message")
        signature = raw[-HYBRID_SIGN_SIG_LEN:]
        body = raw[:-HYBRID_SIGN_SIG_LEN]
        if not verify(self._peer_sign, body, signature):
            raise VerificationFailed("message signature rejected")
        try:
            return AESGCM(key).decrypt(body[:12], body[12:], _AAD)
        except InvalidTag as exc:
            raise InvalidSeal("message decryption failed") from exc

    def _require_key(self) -> bytes:
        if self._key is None:
            raise VerificationFailed("no session yet")
        return self._key
