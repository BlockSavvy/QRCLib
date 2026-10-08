"""X-Wing key establishment. Run: python examples/key_exchange_example.py"""

from qrclib.hybrid import XWING_CT_LEN, XWING_PK_LEN, decapsulate, encapsulate, generate_kem_keys


def main() -> None:
    public, secret = generate_kem_keys()
    ciphertext, shared = encapsulate(public)
    recovered = decapsulate(secret, ciphertext)
    assert recovered == shared
    print(f"X-Wing public key {XWING_PK_LEN} bytes")
    print(f"ciphertext {len(ciphertext)} bytes (spec {XWING_CT_LEN})")
    print(f"shared secret {shared.hex()}")


if __name__ == "__main__":
    main()
