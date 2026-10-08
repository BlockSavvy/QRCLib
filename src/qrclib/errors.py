"""Errors raised by QRCLib."""


class QRCLError(Exception):
    """Base class for library errors."""


class InvalidSeal(QRCLError):
    """A sealed blob could not be authenticated or decrypted."""


class VerificationFailed(QRCLError):
    """A hybrid signature over a protocol message was rejected."""


class PolicyError(QRCLError):
    """The requested homomorphic operation is not in the signed policy."""


class FHEUnavailable(QRCLError):
    """TenSEAL is not installed, so the CKKS envelope cannot run."""
