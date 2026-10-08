"""Hybrid primitives. These are the ones new code should call.

X-Wing (draft-connolly-cfrg-xwing-kem, 2026-09-23)
    ML-KEM-768 + X25519. The 32-byte shared secret is

        SHA3-256(ss_M || ss_X || ct_X || pk_X || label)

    with label ``\\./`` || ``/^\\`` (hex ``5c2e2f2f5e5c``). The secret key is the
    32-byte X-Wing decapsulation key. Public key is 1216 bytes, ciphertext 1120.

QRCL-HYBRID-SIGN-v1
    ML-DSA-65 concatenated with Ed25519. Both halves sign the same
    domain-separated payload and both must verify. An attacker has to forge
    both schemes.
"""

from __future__ import annotations

import secrets
from typing import NamedTuple

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, mldsa, mlkem
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)

# 0x5c 0x2e 0x2f 0x2f 0x5e 0x5c  ==  \.//^\
XWING_LABEL = bytes((0x5C, 0x2E, 0x2F, 0x2F, 0x5E, 0x5C))

XWING_PK_LEN = 1216
XWING_SK_LEN = 32
XWING_CT_LEN = 1120
XWING_SS_LEN = 32
_MLKEM_PK = 1184
_MLKEM_CT = 1088

MLDSA65_PK_LEN = 1952
MLDSA65_SIG_LEN = 3309
ED25519_PK_LEN = 32
ED25519_SIG_LEN = 64

HYBRID_SIGN_PK_LEN = MLDSA65_PK_LEN + ED25519_PK_LEN  # 1984
HYBRID_SIGN_SK_LEN = 64  # ML-DSA seed || Ed25519 seed
HYBRID_SIGN_SIG_LEN = MLDSA65_SIG_LEN + ED25519_SIG_LEN  # 3373

SIGN_DOMAIN = b"QRCL-HYBRID-SIGN-v1"


class KemKeyPair(NamedTuple):
    public_key: bytes
    secret_key: bytes


class SignKeyPair(NamedTuple):
    public_key: bytes
    secret_key: bytes


def _as_bytes(name: str, value: object, length: int | None = None) -> bytes:
    if isinstance(value, str) or not isinstance(value, (bytes, bytearray, memoryview)):
        raise TypeError(f"{name} must be bytes")
    raw = bytes(value)
    if length is not None and len(raw) != length:
        raise ValueError(f"{name} must be {length} bytes, got {len(raw)}")
    return raw


def _shake256(data: bytes, size: int) -> bytes:
    digest = hashes.Hash(hashes.SHAKE256(size))
    digest.update(data)
    return digest.finalize()


def _sha3_256(data: bytes) -> bytes:
    digest = hashes.Hash(hashes.SHA3_256())
    digest.update(data)
    return digest.finalize()


def combiner(ss_m: bytes, ss_x: bytes, ct_x: bytes, pk_x: bytes) -> bytes:
    """X-Wing shared-secret combiner. Exposed so tests can pin the label."""
    parts = (ss_m, ss_x, ct_x, pk_x)
    if any(len(part) != 32 for part in parts):
        raise ValueError("X-Wing combiner inputs must each be 32 bytes")
    return _sha3_256(b"".join(parts) + XWING_LABEL)


def _x25519_public(scalar: bytes) -> bytes:
    private = X25519PrivateKey.from_private_bytes(scalar)
    return private.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )


def _x25519(scalar: bytes, point: bytes) -> bytes:
    private = X25519PrivateKey.from_private_bytes(scalar)
    return private.exchange(X25519PublicKey.from_public_bytes(point))


def _expand(secret: bytes):
    secret = _as_bytes("secret_key", secret, XWING_SK_LEN)
    expanded = _shake256(secret, 96)
    seed_m = expanded[:64]
    scalar_x = expanded[64:]
    kem_secret = mlkem.MLKEM768PrivateKey.from_seed_bytes(seed_m)
    kem_public = kem_secret.public_key().public_bytes_raw()
    x_public = _x25519_public(scalar_x)
    return kem_secret, scalar_x, kem_public, x_public


def kem_keys_from_seed(seed: bytes) -> KemKeyPair:
    """Deterministic X-Wing ``GenerateKeyPairDerand``."""
    _, _, kem_public, x_public = _expand(seed)
    return KemKeyPair(kem_public + x_public, bytes(seed))


def generate_kem_keys() -> KemKeyPair:
    """X-Wing key pair. This is the default key-establishment API."""
    return kem_keys_from_seed(secrets.token_bytes(XWING_SK_LEN))


def encapsulate(public_key: bytes) -> tuple[bytes, bytes]:
    """Returns ``(ciphertext, shared_secret)``."""
    public = _as_bytes("public_key", public_key, XWING_PK_LEN)
    kem_public = public[:_MLKEM_PK]
    x_public = public[_MLKEM_PK:]
    ephemeral = secrets.token_bytes(32)
    ct_x = _x25519_public(ephemeral)
    ss_x = _x25519(ephemeral, x_public)
    ss_m, ct_m = mlkem.MLKEM768PublicKey.from_public_bytes(kem_public).encapsulate()
    return ct_m + ct_x, combiner(ss_m, ss_x, ct_x, x_public)


def decapsulate(secret_key: bytes, ciphertext: bytes) -> bytes:
    ciphertext = _as_bytes("ciphertext", ciphertext, XWING_CT_LEN)
    kem_secret, scalar_x, _, x_public = _expand(secret_key)
    ct_m = ciphertext[:_MLKEM_CT]
    ct_x = ciphertext[_MLKEM_CT:]
    ss_m = kem_secret.decapsulate(ct_m)
    ss_x = _x25519(scalar_x, ct_x)
    return combiner(ss_m, ss_x, ct_x, x_public)


def _payload(message: bytes, context: bytes) -> bytes:
    message = _as_bytes("message", message)
    context = _as_bytes("context", context)
    if len(context) > 255:
        raise ValueError("context must be at most 255 bytes")
    return SIGN_DOMAIN + bytes([len(context)]) + context + message


def sign_keys_from_seed(seed: bytes) -> SignKeyPair:
    seed = _as_bytes("seed", seed, HYBRID_SIGN_SK_LEN)
    mldsa_secret = mldsa.MLDSA65PrivateKey.from_seed_bytes(seed[:32])
    ed_secret = ed25519.Ed25519PrivateKey.from_private_bytes(seed[32:])
    public = mldsa_secret.public_key().public_bytes_raw() + ed_secret.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    return SignKeyPair(public, seed)


def generate_sign_keys() -> SignKeyPair:
    """ML-DSA-65 + Ed25519. This is the default signature API."""
    return sign_keys_from_seed(secrets.token_bytes(HYBRID_SIGN_SK_LEN))


def sign(secret_key: bytes, message: bytes, context: bytes = b"") -> bytes:
    seed = _as_bytes("secret_key", secret_key, HYBRID_SIGN_SK_LEN)
    payload = _payload(message, context)
    mldsa_sig = mldsa.MLDSA65PrivateKey.from_seed_bytes(seed[:32]).sign(payload)
    ed_sig = ed25519.Ed25519PrivateKey.from_private_bytes(seed[32:]).sign(payload)
    return mldsa_sig + ed_sig


def verify(
    public_key: bytes,
    message: bytes,
    signature: bytes,
    context: bytes = b"",
) -> bool:
    """Check both halves. A failure of either half rejects the signature."""
    try:
        public = _as_bytes("public_key", public_key, HYBRID_SIGN_PK_LEN)
        signature = _as_bytes("signature", signature, HYBRID_SIGN_SIG_LEN)
        payload = _payload(message, context)
    except (TypeError, ValueError):
        return False
    mldsa_sig = signature[:MLDSA65_SIG_LEN]
    ed_sig = signature[MLDSA65_SIG_LEN:]
    try:
        mldsa_public = mldsa.MLDSA65PublicKey.from_public_bytes(public[:MLDSA65_PK_LEN])
        ed_public = ed25519.Ed25519PublicKey.from_public_bytes(public[MLDSA65_PK_LEN:])
    except ValueError:
        return False
    return _accepts(lambda: mldsa_public.verify(mldsa_sig, payload)) and _accepts(
        lambda: ed_public.verify(ed_sig, payload)
    )


def _accepts(check) -> bool:
    try:
        check()
    except InvalidSignature:
        return False
    return True
