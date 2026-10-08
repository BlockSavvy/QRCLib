# API

Install: `pip install -e .` from a checkout, or `pip install cryptography` plus
this package. CKKS: `pip install -e '.[fhe]'`.

Defaults are ML-KEM-768, ML-DSA-65, X-Wing, and the hybrid signature.
New code should call `qrclib.hybrid`.

## Key establishment

```python
from qrclib.hybrid import generate_kem_keys, encapsulate, decapsulate

public, secret = generate_kem_keys()          # 1216-byte pk, 32-byte sk
ciphertext, shared = encapsulate(public)      # 1120-byte ct, 32-byte secret
assert decapsulate(secret, ciphertext) == shared
```

Pure ML-KEM, when a protocol already has its own combiner:

```python
from qrclib.kem import generate_keys, encapsulate, decapsulate

public, secret = generate_keys()              # ML-KEM-768
public, secret = generate_keys("ML-KEM-1024")
ciphertext, shared = encapsulate(public)
assert decapsulate(secret, ciphertext) == shared
```

Secret keys carry a one-byte suite tag. Public keys and ciphertexts are raw
FIPS bytes. `encapsulate` returns `(ciphertext, shared_secret)`.

## Signatures

```python
from qrclib.hybrid import generate_sign_keys, sign, verify

public, secret = generate_sign_keys()         # ML-DSA-65 || Ed25519
signature = sign(secret, b"msg", context=b"app-v1")
assert verify(public, b"msg", signature, context=b"app-v1")
```

Pure ML-DSA:

```python
from qrclib.dsa import generate_keys, sign, verify

public, secret = generate_keys()              # ML-DSA-65
public, secret = generate_keys("ML-DSA-44")   # or "ML-DSA-87"
assert verify(public, b"msg", sign(secret, b"msg"))
```

`verify` returns `False` on failure. It does not raise.

## Seal and mailbox

```python
from qrclib.seal import seal, open_seal
blob = seal(recipient_public, b"payload", sender_secret, aad=b"file-id")
open_seal(recipient_secret, blob, sender_public, aad=b"file-id")
```

```python
from qrclib.messaging import Mailbox
alice, bob = Mailbox("alice"), Mailbox("bob")
offer = alice.offer(bob.kem.public_key)
alice.bind_peer(bob.signing.public_key)
bob.accept(offer, alice.signing.public_key)
assert bob.decrypt(alice.encrypt(b"hi")) == b"hi"
```

## CKKS envelope

```python
from qrclib.hybrid import generate_kem_keys, generate_sign_keys
from qrclib.lhe import seal, evaluate, open_result

recipient, sender = generate_kem_keys(), generate_sign_keys()
env = seal([1.5, 2.5, 3.0], recipient.public_key, sender.secret_key)
result = evaluate(env, "mean", sender.public_key)   # no recipient secret
value = open_result(env, result, recipient.secret_key, sender.public_key)
```

Allowed ops: `sum`, `mean`, `shift`, `scale`, `mask`. Results are approximate.
The agent holding only `(env, sender_public)` cannot open the values.

## Bitcoin attestation

```python
from qrclib.bitcoin import QuantumProtectedWallet
wallet = QuantumProtectedWallet.generate()
att = wallet.protect_transaction("ab" * 32)
assert att.verify()
script = att.op_return_script()   # 34 bytes: OP_RETURN PUSH32 commitment
```

See `SECURITY.md`. This is not a consensus change.

## Names that moved

| 0.1 | 1.0 |
| --- | --- |
| `src.kyber.generate_keys()` dicts | `qrclib.kem.generate_keys()` raw bytes, or `qrclib.kyber` as an alias |
| `src.dilithium` private-then-public dicts | `qrclib.dsa`, public key first |
| NTT helpers in `utils` | removed |
| Fake forward secrecy | not claimed |
