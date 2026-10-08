"""Old Dilithium name, new bytes.

CRYSTALS-Dilithium is not wire-compatible with ML-DSA (FIPS 204).
These callables are ML-DSA-65.
"""

from qrclib.dsa import DEFAULT, KeyPair, generate_keys, sign, verify

__all__ = ["DEFAULT", "KeyPair", "generate_keys", "sign", "verify"]

NOTE = (
    "dilithium.generate_keys is ML-DSA-65. "
    "It returns (public_key, secret_key), not the old (private, public) dicts."
)
