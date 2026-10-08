"""Authenticated hybrid encryption.

X-Wing establishes a data key. AES-256-GCM encrypts the payload.
QRCL-HYBRID-SIGN-v1 signs the ciphertext and the associated data.
"""

from __future__ import annotations

import secrets

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from qrclib.errors import InvalidSeal
from qrclib.hybrid import (
    HYBRID_SIGN_SIG_LEN,
    XWING_CT_LEN,
    decapsulate,
    encapsulate,
    sign,
    verify,
)
from qrclib.kdf import hkdf_sha256

MAGIC = b"QRS1"
_INFO = b"qrclib-seal-v1"
_HEADER = len(MAGIC) + XWING_CT_LEN + 12 + 4


def seal(
    recipient_public: bytes,
    plaintext: bytes,
    sender_secret: bytes,
    aad: bytes = b"",
) -> bytes:
    """Seal ``plaintext`` for ``recipient_public``, signed by ``sender_secret``."""
    if isinstance(plaintext, str) or not isinstance(plaintext, (bytes, bytearray, memoryview)):
        raise TypeError("plaintext must be bytes")
    if isinstance(aad, str) or not isinstance(aad, (bytes, bytearray, memoryview)):
        raise TypeError("aad must be bytes")
    kem_ct, shared = encapsulate(recipient_public)
    key = hkdf_sha256(shared, _INFO)
    nonce = secrets.token_bytes(12)
    body = AESGCM(key).encrypt(nonce, bytes(plaintext), bytes(aad))
    prefix = MAGIC + kem_ct + nonce + len(body).to_bytes(4, "big") + body
    return prefix + sign(sender_secret, prefix + bytes(aad))


def open_seal(
    recipient_secret: bytes,
    blob: bytes,
    sender_public: bytes,
    aad: bytes = b"",
) -> bytes:
    """Verify, decapsulate, and decrypt. Raises ``InvalidSeal`` on failure."""
    try:
        raw = bytes(blob)
        extra = bytes(aad)
    except TypeError as exc:
        raise InvalidSeal("blob and aad must be bytes") from exc
    if len(raw) < _HEADER + HYBRID_SIGN_SIG_LEN:
        raise InvalidSeal("truncated")
    if raw[: len(MAGIC)] != MAGIC:
        raise InvalidSeal("bad magic")
    offset = len(MAGIC)
    kem_ct = raw[offset : offset + XWING_CT_LEN]
    offset += XWING_CT_LEN
    nonce = raw[offset : offset + 12]
    offset += 12
    body_len = int.from_bytes(raw[offset : offset + 4], "big")
    offset += 4
    end = offset + body_len
    if end + HYBRID_SIGN_SIG_LEN != len(raw):
        raise InvalidSeal("length mismatch")
    body = raw[offset:end]
    signature = raw[end:]
    prefix = raw[:end]
    if not verify(sender_public, prefix + extra, signature):
        raise InvalidSeal("signature rejected")
    try:
        shared = decapsulate(recipient_secret, kem_ct)
        key = hkdf_sha256(shared, _INFO)
        return AESGCM(key).decrypt(nonce, body, extra)
    except (InvalidTag, ValueError) as exc:
        raise InvalidSeal("decryption failed") from exc
