"""In-process sketch of a signature-checked API exchange.

No server is started. Run: python examples/web_api_example.py
"""

import json

from qrclib.hybrid import generate_sign_keys, sign, verify
from qrclib.seal import open_seal, seal
from qrclib.hybrid import generate_kem_keys


def main() -> None:
    user = generate_sign_keys()
    vault = generate_kem_keys()
    body = json.dumps({"route": "/v1/readings", "id": 18}).encode()
    signature = sign(user.secret_key, body)
    assert verify(user.public_key, body, signature)
    stored = seal(vault.public_key, body, user.secret_key, aad=b"/v1/readings")
    opened = open_seal(vault.secret_key, stored, user.public_key, aad=b"/v1/readings")
    print(json.dumps({"accepted": opened == body, "stored_bytes": len(stored)}))


if __name__ == "__main__":
    main()
