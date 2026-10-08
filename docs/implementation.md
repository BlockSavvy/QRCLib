# Implementation

QRCLib does not implement lattice arithmetic. `cryptography` 48 and later
does, in Rust, and that is the only backend. ML-KEM-512 is not in that
wheel; 768 and 1024 are. ML-DSA-44, 65, and 87 are.

## X-Wing

`qrclib.hybrid` follows draft-connolly-cfrg-xwing-kem (dated 2026-09-23):

1. `SHAKE256(sk, 96)` splits into a 64-byte ML-KEM seed (`d || z`) and a
   32-byte X25519 scalar.
2. Encapsulation draws a fresh X25519 ephemeral, appends its public key to
   the ML-KEM-768 ciphertext, and combines with SHA3-256.
3. The label is the six bytes `5c2e2f2f5e5c`.

A frozen combiner vector lives in `tests/test_primitives.py`. Key generation
from a fixed seed is deterministic. Encapsulation is not.

## Hybrid signature

`QRCL-HYBRID-SIGN-v1` signs

```
domain || len(context) || context || message
```

with ML-DSA-65 (empty internal context) and Ed25519, and concatenates the
signatures (3309 + 64). The public key is the concatenation of the raw
public keys (1952 + 32). The secret is the two seeds (32 + 32).

## Envelope bytes

`QRS1` seals are X-Wing ciphertext, AES-256-GCM, and a hybrid signature over
the prefix plus associated data. The data key is `HKDF-SHA256` with salt
`qrclib-v1` and info `qrclib-seal-v1`.

`QRLHE1` adds a TenSEAL public context and one CKKS ciphertext per number.
The secret context is itself a `QRS1` seal with associated data `lhe-secret`.
Evaluation (`QRLHR1`) does not carry a signature. See `SECURITY.md` for the
semi-honest agent.

CKKS parameters: polynomial degree 8192, coefficient moduli `[50, 30, 50]`,
scale `2^30`. Addition and plaintext multiplication only, so no Galois keys
and no relinearization keys. That is why the public context stays under a
megabyte instead of tens of megabytes. It is also why the only filters on
offer are plaintext masks the agent already knows.
