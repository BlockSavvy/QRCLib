"""ML-DSA (FIPS 204) via pyca/cryptography.

Default parameter set is ML-DSA-65. Public keys and signatures are raw FIPS
encodings. Secret keys are a one-byte suite tag plus the 32-byte seed, because
every ML-DSA parameter set uses a 32-byte seed and the tag is the only way to
tell them apart.
"""

from __future__ import annotations

from enum import Enum
from typing import NamedTuple

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import mldsa


class Level(str, Enum):
    ML_DSA_44 = "ML-DSA-44"
    ML_DSA_65 = "ML-DSA-65"
    ML_DSA_87 = "ML-DSA-87"


class KeyPair(NamedTuple):
    public_key: bytes
    secret_key: bytes


_TAG = {Level.ML_DSA_44: 0x20, Level.ML_DSA_65: 0x21, Level.ML_DSA_87: 0x22}
_FROM_TAG = {tag: level for level, tag in _TAG.items()}

_PRIVATE = {
    Level.ML_DSA_44: mldsa.MLDSA44PrivateKey,
    Level.ML_DSA_65: mldsa.MLDSA65PrivateKey,
    Level.ML_DSA_87: mldsa.MLDSA87PrivateKey,
}
_PUBLIC = {
    Level.ML_DSA_44: mldsa.MLDSA44PublicKey,
    Level.ML_DSA_65: mldsa.MLDSA65PublicKey,
    Level.ML_DSA_87: mldsa.MLDSA87PublicKey,
}
_PK_LEN = {Level.ML_DSA_44: 1312, Level.ML_DSA_65: 1952, Level.ML_DSA_87: 2592}
_SIG_LEN = {Level.ML_DSA_44: 2420, Level.ML_DSA_65: 3309, Level.ML_DSA_87: 4627}
_SEED_LEN = 32

DEFAULT = Level.ML_DSA_65

_ALIASES = {
    "44": Level.ML_DSA_44,
    "ML-DSA-44": Level.ML_DSA_44,
    "MLDSA44": Level.ML_DSA_44,
    "DILITHIUM2": Level.ML_DSA_44,
    "65": Level.ML_DSA_65,
    "ML-DSA-65": Level.ML_DSA_65,
    "MLDSA65": Level.ML_DSA_65,
    "DILITHIUM3": Level.ML_DSA_65,
    "87": Level.ML_DSA_87,
    "ML-DSA-87": Level.ML_DSA_87,
    "MLDSA87": Level.ML_DSA_87,
    "DILITHIUM5": Level.ML_DSA_87,
}


def parse_level(level: Level | str | None) -> Level:
    if level is None:
        return DEFAULT
    if isinstance(level, Level):
        return level
    key = str(level).strip().upper().replace("_", "-")
    if key not in _ALIASES:
        raise ValueError(
            f"Unknown ML-DSA level {level!r}. Use ML-DSA-44, ML-DSA-65 (default), or ML-DSA-87."
        )
    return _ALIASES[key]


def _as_bytes(name: str, value: object) -> bytes:
    if isinstance(value, str) or not isinstance(value, (bytes, bytearray, memoryview)):
        raise TypeError(f"{name} must be bytes")
    return bytes(value)


def _check_context(context: bytes) -> bytes:
    raw = _as_bytes("context", context)
    if len(raw) > 255:
        raise ValueError("ML-DSA context must be at most 255 bytes")
    return raw


def generate_keys(level: Level | str = DEFAULT) -> KeyPair:
    """Return ``(public_key, secret_key)``. Both signature and KEM APIs use this order."""
    lv = parse_level(level)
    private = _PRIVATE[lv].generate()
    public = private.public_key().public_bytes_raw()
    secret = bytes([_TAG[lv]]) + private.private_bytes_raw()
    return KeyPair(public, secret)


def keys_from_seed(seed: bytes, level: Level | str = DEFAULT) -> KeyPair:
    lv = parse_level(level)
    raw = _as_bytes("seed", seed)
    if len(raw) != _SEED_LEN:
        raise ValueError(f"ML-DSA seed must be {_SEED_LEN} bytes, got {len(raw)}")
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
        "ML-DSA secret key must be a 32-byte seed or a tagged 33-byte QRCLib key"
    )


def _level_from_public(public_key: bytes) -> Level:
    for level, size in _PK_LEN.items():
        if len(public_key) == size:
            return level
    raise ValueError(
        "ML-DSA public key must be 1312, 1952, or 2592 bytes, "
        f"got {len(public_key)}"
    )


def sign(
    secret_key: bytes,
    message: bytes,
    context: bytes = b"",
    level: Level | str | None = None,
) -> bytes:
    lv, seed = split_secret(secret_key, level)
    msg = _as_bytes("message", message)
    ctx = _check_context(context)
    return _PRIVATE[lv].from_seed_bytes(seed).sign(msg, context=ctx or None)


def verify(
    public_key: bytes,
    message: bytes,
    signature: bytes,
    context: bytes = b"",
    level: Level | str | None = None,
) -> bool:
    """Return False on any failure. Does not raise for a bad signature."""
    try:
        pk = _as_bytes("public_key", public_key)
        msg = _as_bytes("message", message)
        sig = _as_bytes("signature", signature)
        ctx = _check_context(context)
        inferred = _level_from_public(pk)
        if level is not None and parse_level(level) is not inferred:
            return False
        if len(sig) != _SIG_LEN[inferred]:
            return False
        _PUBLIC[inferred].from_public_bytes(pk).verify(sig, msg, context=ctx or None)
    except (InvalidSignature, ValueError, TypeError):
        return False
    return True
