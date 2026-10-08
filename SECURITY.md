# Security

## The old pure-Python code was not a cryptosystem

Versions before 1.0 shipped `src/kyber.py` and `src/dilithium.py` that looked
like Kyber and Dilithium and were not. Encapsulation stored the message next
to a hash of a seed. Signatures were `SHA-256(seed || message || nonce)`.
Several failure paths returned fresh random bytes and still claimed success.
Nothing in that tree was constant-time, correct, or safe to ship.

Those implementations have been deleted. 1.0 is a thin wrapper:

| Primitive | Implementation |
| --- | --- |
| ML-KEM-768 / ML-KEM-1024 (FIPS 203) | `cryptography` ≥ 48 (Rust / AWS-LC backend) |
| ML-DSA-44 / 65 / 87 (FIPS 204) | same |
| X25519, Ed25519, AES-256-GCM, HKDF, SHA3, SHAKE | same |
| X-Wing | this repo, on top of those primitives, following draft-connolly-cfrg-xwing-kem (2026-09-23) |
| CKKS envelope | TenSEAL / Microsoft SEAL, optional |

Do not vendor a second pure-Python lattice implementation "for platforms
without wheels." If the wheel is missing, fail closed.

## What "hybrid" means here

* **X-Wing** remains confidential if either ML-KEM-768 or X25519 does, in the
  sense of the X-Wing proof. The combiner is SHA3-256 over both secrets, the
  X25519 ciphertext, the X25519 public key, and the six-byte label. Do not
  replace it with XOR or concatenation.
* **QRCL-HYBRID-SIGN-v1** requires both the ML-DSA-65 signature and the
  Ed25519 signature. Forging it means forging both. Verifiers must check both
  halves. A deployment that checks only one has thrown the construction away.

Kyber and Dilithium names in `qrclib.kyber` and `qrclib.dilithium` are aliases
onto ML-KEM-768 and ML-DSA-65. They are not Round-3 wire formats.

## Bitcoin

`qrclib.bitcoin` does not make a coin quantum-safe. Consensus still checks
secp256k1. The hybrid signature does not fit in an OP_RETURN. The 32-byte
commitment does. A quantum adversary who sees a secp256k1 public key can still
produce a signature miners will accept. The attestation is a policy tool for
heirs, exchanges, and cosigners, not a consensus rule. See the module docstring.

## Lattice envelope

The CKKS path is approximate and optional. The computation agent is assumed
semi-honest: it can substitute a result ciphertext, and the recipient cannot
tell from the cryptography alone. The envelope signature stops an outsider
from changing the signed policy. It does not stop the agent. Parameters are
fixed (`n = 8192`, moduli `[50, 30, 50]`, scale `2^30`) and are not a general
FHE product. Do not put more than 16 values in, and do not feed it secrets you
cannot tolerate being approximate.

The long-term X-Wing mailbox is not forward secret.

## Reporting

Report vulnerabilities privately to the maintainers of
https://github.com/BlockSavvy/QRCLib before opening a public issue.
This library is MIT-licensed and is not warranted fit for any particular
custody or protocol deployment.
