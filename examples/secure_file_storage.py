"""Seal a file to a recipient. Run: python examples/secure_file_storage.py"""

from pathlib import Path

from qrclib.hybrid import generate_kem_keys, generate_sign_keys
from qrclib.seal import open_seal, seal


def main() -> None:
    recipient = generate_kem_keys()
    sender = generate_sign_keys()
    payload = b"panel schedule, bay 4"
    blob = seal(recipient.public_key, payload, sender.secret_key, aad=b"bay-4")
    path = Path("sealed-bay-4.qrs")
    path.write_bytes(blob)
    opened = open_seal(recipient.secret_key, path.read_bytes(), sender.public_key, aad=b"bay-4")
    path.unlink()
    assert opened == payload
    print(f"wrote and read {len(blob)} sealed bytes")


if __name__ == "__main__":
    main()
