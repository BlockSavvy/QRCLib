"""QRCLib — ML-KEM, ML-DSA, and hybrid constructions on pyca/cryptography.

The pure-Python Kyber and Dilithium modules that used to live here were
educational stubs. They are gone. Use ``qrclib.hybrid`` unless you have a
reason to call a single primitive.
"""

from qrclib import bitcoin, dilithium, dsa, hybrid, kem, kyber, lhe, messaging, seal

__version__ = "1.0.0"

__all__ = [
    "__version__",
    "bitcoin",
    "dilithium",
    "dsa",
    "hybrid",
    "kem",
    "kyber",
    "lhe",
    "messaging",
    "seal",
]
