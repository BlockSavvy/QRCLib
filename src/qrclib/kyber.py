"""Old Kyber name, new bytes.

Round-3 CRYSTALS-Kyber is not wire-compatible with ML-KEM (FIPS 203).
These callables are ML-KEM-768. They exist so a migration can keep the
names without pretending the historical Kyber encoding still applies.
"""

from qrclib.kem import (
    DEFAULT,
    KeyPair,
    decapsulate,
    encapsulate,
    generate_keys,
)

__all__ = ["DEFAULT", "KeyPair", "decapsulate", "encapsulate", "generate_keys"]

NOTE = (
    "kyber.generate_keys is ML-KEM-768. It does not emit Round-3 Kyber keys."
)
