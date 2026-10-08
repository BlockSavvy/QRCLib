"""Hybrid signature. Run: python examples/signature_example.py"""

from qrclib.hybrid import HYBRID_SIGN_SIG_LEN, generate_sign_keys, sign, verify


def main() -> None:
    public, secret = generate_sign_keys()
    message = b"PQCL hybrid signature"
    signature = sign(secret, message)
    print(f"signature {len(signature)} bytes (spec {HYBRID_SIGN_SIG_LEN})")
    print("valid", verify(public, message, signature))
    print("tampered", verify(public, message + b"!", signature))


if __name__ == "__main__":
    main()
