# QRCLib

Post-quantum primitives for Python, wrapped rather than reimplemented.

ML-KEM (FIPS 203) and ML-DSA (FIPS 204) come from
[pyca/cryptography](https://cryptography.io) 48 or newer. The recommended
calls are hybrid: X-Wing (ML-KEM-768 + X25519) for key establishment, and
ML-DSA-65 + Ed25519 for signatures. An optional CKKS envelope
([TenSEAL](https://github.com/OpenMined/TenSEAL)) lets a computation agent
sum or average numbers it cannot read.

The pure-Python Kyber and Dilithium files in earlier revisions were teaching
stubs. They hashed stand-ins and returned them as ciphertexts. They have been
removed. Read [SECURITY.md](SECURITY.md) before using this for anything real.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"          # tests
pip install -e ".[fhe]"          # CKKS envelope, optional
```

Python 3.10+. No system C library to compile: `cryptography` ships wheels.

## Use

```python
from qrclib.hybrid import (
    generate_kem_keys, encapsulate, decapsulate,
    generate_sign_keys, sign, verify,
)

public, secret = generate_kem_keys()
ciphertext, shared = encapsulate(public)
assert decapsulate(secret, ciphertext) == shared

verify_key, sign_key = generate_sign_keys()
signature = sign(sign_key, b"hello")
assert verify(verify_key, b"hello", signature)
```

Pure ML-KEM-768 / ML-KEM-1024 and ML-DSA-44 / 65 / 87 are in `qrclib.kem` and
`qrclib.dsa`. `qrclib.kyber` and `qrclib.dilithium` are names only: the bytes
are FIPS 203 and 204, not Round-3 Kyber or Dilithium.

| Call | Sizes |
| --- | --- |
| X-Wing public / secret / ciphertext | 1216 / 32 / 1120 |
| Hybrid signature public / secret / signature | 1984 / 64 / 3373 |
| ML-KEM-768 public / ciphertext | 1184 / 1088 |
| ML-DSA-65 public / signature | 1952 / 3309 |

`encapsulate` returns `(ciphertext, shared_secret)`.

## Examples

From the repository root, after `pip install -e .`:

```bash
python examples/key_exchange_example.py
python examples/signature_example.py
python examples/secure_messaging.py
python examples/secure_file_storage.py
python examples/blockchain_example.py
python examples/bitcoin_protection_example.py
python examples/web_api_example.py
python examples/lhe_example.py          # needs the fhe extra
pytest -q
```

The Bitcoin example signs an off-chain attestation and prints a 34-byte
`OP_RETURN` commitment. It does not change Bitcoin consensus. The messaging
example is not forward secret. The lattice example is approximate and assumes
a semi-honest agent. All three limits are spelled out in
[SECURITY.md](SECURITY.md) and [docs/api.md](docs/api.md).

## Demo

The Next.js app in [`web/`](web/) is what [pqcl.aiya.sh](https://pqcl.aiya.sh) deploys.
The browser runs the same X-Wing and hybrid signature constructions as `qrclib.hybrid` (`@noble/post-quantum`).
`/hash` runs SLH-DSA-SHA2-128f in the browser only. `cryptography` 50 does not ship FIPS 205, and this
library does not vendor a second copy. The mailbox is not forward secret. The Bitcoin page commits 32 bytes;
it does not change consensus. CKKS stays in `examples/lhe_example.py` and is a short-horizon lattice computation.

## Layout

```
src/qrclib/kem.py        ML-KEM
src/qrclib/dsa.py        ML-DSA
src/qrclib/hybrid.py     X-Wing and the hybrid signature
src/qrclib/seal.py       AES-GCM under X-Wing, signed
src/qrclib/messaging.py  two-party mailbox
src/qrclib/bitcoin.py    off-chain attestation
src/qrclib/lhe.py        CKKS envelope (optional)
```

Screenshots in `screenshots/` are from the earlier demo and show the old UI.

## License

MIT. Copyright (c) 2024 BlockSavvy. See [LICENSE](LICENSE).
