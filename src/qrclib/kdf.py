"""Domain-separated key derivation for seals and sessions."""

from __future__ import annotations

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def hkdf_sha256(ikm: bytes, info: bytes, length: int = 32) -> bytes:
    """Derive ``length`` bytes. Salt is fixed so the info string is the domain."""
    return HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=b"qrclib-v1",
        info=info,
    ).derive(ikm)
