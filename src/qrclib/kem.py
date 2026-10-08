"""ML-KEM (FIPS 203) via pyca/cryptography.

Public keys and ciphertexts are raw FIPS encodings. Secret keys are a one-byte
suite tag plus the 64-byte seed (``d || z``) so a 768 seed cannot be silently
used as a 1024 key.

``encapsulate`` returns ``(ciphertext, shared_secret)``, matching the historical
QRCLib call shape. ``cryptography`` itself returns the pair in the other order.
"""

from __future__ import annotations

import secrets
from enum import Enum
from typing import NamedTuple

from cryptography.hazmat.primitives.asymmetric import mlkem


class Level(str, Enum):
    ML_KEM_768 = "ML-KEM-768"
    ML_KEM_1024 = "ML-KEM-1024"


class KeyPair(NamedTuple):
    public_key: bytes
    secret_key: bytes


# Suite tags are local to QRCLib secret keys. They are not part of FIPS 203.
_TAG = {Level.ML_KEM_768: 0x10, Level.ML_KEM_1024: 0x11}
_FROM_TAG = {tag: level for level, tag in _TAG.items()}

_PRIVATE = {
    Level.ML_KEM_768: mlkem.MLKEM768PrivateKey,
    Level.ML_KEM_1024: mlkem.MLKEM1024PrivateKey,
}
_PUBLIC = {
    Level.ML_KEM_768: mlkem.MLKEM768PublicKey,
    Level.ML_KEM_1024: mlkem.MLKEM1024PublicKey,
}
_PK_LEN = {Level.ML_KEM_768: 1184, Level.ML_KEM_1024: 1568}
_CT_LEN = {Level.ML_KEM_768: 1088, Level.ML_KEM_1024: 1568}
_SEED_LEN = 64

DEFAULT = Level.ML_KEM_768

_ALIASES = {
    "768": Level.ML_KEM_768,
    "ML-KEM-768": Level.ML_KEM_768,
    "MLKEM768": Level.ML_KEM_768,
    "KYBER768": Level.ML_KEM_768,
    "KYBER-768": Level.ML_KEM_768,
    "1024": Level.ML_KEM_1024,
    "ML-KEM-1024": Level.ML_KEM_1024,
    "MLKEM1024": Level.ML_KEM_1024,
    "KYBER1024": Level.ML_KEM_1024,
    "KYBER-1024": Level.ML_KEM_1024,
}


def parse_level(level: Level | str | None) -> Level:
    if level is None:
        return DEFAULT
    if isinstance(level, Level):
        return level
    key = str(level).strip().upper().replace("_", "-")
    if key not in _ALIASES:
        raise ValueError(
            f"Unknown ML-KEM level {level!r}. "
            "Use ML-KEM-768 (default) or ML-KEM-1024. "
            "cryptography does not ship ML-KEM-512."
        )
    return _ALIASES[key]


def _as_bytes(name: str, value: object) -> bytes:
    if isinstance(value, str) or not isinstance(value, (bytes, bytearray, memoryview)):
        raise TypeError(
            f"{name} must be bytes. QRCLib 1.0 dropped the dict keys from the "
            "educational stubs."
        )
    return bytes(value)


def generate_keys(level: Level | str = DEFAULT) -> KeyPair:
    """Return ``(public_key, secret_key)`` for ML-KEM-768 unless told otherwise."""
    lv = parse_level(level)
    private = _PRIVATE[lv].generate()
    public = private.public_key().public_bytes_raw()
    secret = bytes([_TAG[lv]]) + private.private_bytes_raw()
    return KeyPair(public, secret)


def keys_from_seed(seed: bytes, level: Level | str = DEFAULT) -> KeyPair:
    """Rebuild a key pair from a raw 64-byte FIPS seed (no suite tag)."""
    lv = parse_level(level)
    raw = _as_bytes("seed", seed)
    if len(raw) != _SEED_LEN:
        raise ValueError(f"ML-KEM seed must be {_SEED_LEN} bytes, got {len(raw)}")
    private = _PRIVATE[lv].from_seed_bytes(raw)
    public = private.public_key().public_bytes_raw()
    return KeyPair(public, bytes([_TAG[lv]]) + raw)


def split_secret(secret_key: bytes, level: Level | str | None = None) -> tuple[Level, bytes]:
    raw = _as_bytes("secret_key", secret_key)
    if len(raw) == _SEED_LEN + 1 and raw[0] in _FROM_TAG:
        tagged = _FROM_TAG[raw[0]]
        if level is not None and parse_level(level) is not tagged:
            raise ValueError("level does not match the secret-key suite tag")
        return tagged, raw[1:]
    if len(raw) == _SEED_LEN:
        return parse_level(level), raw
    raise ValueError(
        "ML-KEM secret key must be a 64-byte seed or a tagged 65-byte QRCLib key"
    )


def _level_from_public(public_key: bytes) -> Level:
    for level, size in _PK_LEN.items():
        if len(public_key) == size:
            return level
    raise ValueError(
        "ML-KEM public key must be 1184 bytes (768) or 1568 bytes (1024), "
        f"got {len(public_key)}"
    )


def _level_from_ciphertext(ciphertext: bytes) -> Level:
    for level, size in _CT_LEN.items():
        if len(ciphertext) == size:
            return level
    raise ValueError(
        "ML-KEM ciphertext must be 1088 bytes (768) or 1568 bytes (1024), "
        f"got {len(ciphertext)}"
    )


def encapsulate(
    public_key: bytes, level: Level | str | None = None
) -> tuple[bytes, bytes]:
    """Encapsulate. Returns ``(ciphertext, shared_secret)``."""
    pk = _as_bytes("public_key", public_key)
    inferred = _level_from_public(pk)
    if level is not None and parse_level(level) is not inferred:
        raise ValueError("level does not match the public-key length")
    shared, ciphertext = _PUBLIC[inferred].from_public_bytes(pk).encapsulate()
    return ciphertext, shared


def decapsulate(
    secret_key: bytes,
    ciphertext: bytes,
    level: Level | str | None = None,
) -> bytes:
    """Decapsulate. A wrong ciphertext of the right length yields a different secret."""
    ct = _as_bytes("ciphertext", ciphertext)
    from_ct = _level_from_ciphertext(ct)
    from_sk, seed = split_secret(secret_key, level)
    if from_sk is not from_ct:
        raise ValueError(
            f"secret key is {from_sk.value} but ciphertext is {from_ct.value}"
        )
    return _PRIVATE[from_sk].from_seed_bytes(seed).decapsulate(ct)


def random_seed() -> bytes:
    return secrets.token_bytes(_SEED_LEN)
