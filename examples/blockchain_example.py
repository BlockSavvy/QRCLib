"""A two-transaction chain signed with the hybrid signature.

This is an application sketch, not a consensus protocol.
Run: python examples/blockchain_example.py
"""

import hashlib
import json

from qrclib.hybrid import generate_sign_keys, sign, verify


def _digest(body: dict) -> bytes:
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).digest()


def main() -> None:
    alice = generate_sign_keys()
    bob = generate_sign_keys()
    genesis = hashlib.sha256(b"qrclib-genesis").digest()
    first = {
        "prev": genesis.hex(),
        "from": alice.public_key.hex(),
        "to": bob.public_key.hex(),
        "amount": 100,
    }
    first_sig = sign(alice.secret_key, _digest(first))
    assert verify(alice.public_key, _digest(first), first_sig)
    link = hashlib.sha256(_digest(first) + first_sig).digest()
    second = {
        "prev": link.hex(),
        "from": bob.public_key.hex(),
        "to": alice.public_key.hex(),
        "amount": 40,
    }
    second_sig = sign(bob.secret_key, _digest(second))
    assert verify(bob.public_key, _digest(second), second_sig)
    print("tx1", link.hex())
    print("tx2 valid", True)


if __name__ == "__main__":
    main()
