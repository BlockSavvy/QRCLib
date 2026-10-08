"""CKKS envelope. Needs `pip install 'qrclib[fhe]'`.

Run: python examples/lhe_example.py
"""

from qrclib.hybrid import generate_kem_keys, generate_sign_keys
from qrclib.lhe import evaluate, open_result, seal


def main() -> None:
    values = [10.0, 12.5, 11.0, 9.5]
    recipient = generate_kem_keys()
    sender = generate_sign_keys()
    envelope = seal(values, recipient.public_key, sender.secret_key)
    result = evaluate(envelope, "mean", sender.public_key)
    opened = open_result(envelope, result, recipient.secret_key, sender.public_key)
    exact = sum(values) / len(values)
    print(f"envelope {len(envelope)} bytes")
    print(f"mean exact {exact:.6f}  homomorphic {opened:.6f}  err {abs(opened - exact):.6f}")


if __name__ == "__main__":
    main()
