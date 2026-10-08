"""Round trips for ML-KEM, ML-DSA, X-Wing, and the hybrid signature."""

import pytest

from qrclib.dsa import generate_keys as dsa_keys
from qrclib.dsa import keys_from_seed as dsa_from_seed
from qrclib.dsa import sign as dsa_sign
from qrclib.dsa import verify as dsa_verify
from qrclib.hybrid import (
    HYBRID_SIGN_SIG_LEN,
    XWING_CT_LEN,
    XWING_LABEL,
    XWING_PK_LEN,
    XWING_SK_LEN,
    combiner,
    decapsulate,
    encapsulate,
    generate_kem_keys,
    generate_sign_keys,
    kem_keys_from_seed,
    sign,
    verify,
)
from qrclib.kem import decapsulate as kem_decaps
from qrclib.kem import encapsulate as kem_encaps
from qrclib.kem import generate_keys as kem_keys
from qrclib.kem import keys_from_seed as kem_from_seed
from qrclib.kyber import NOTE as KYBER_NOTE
from qrclib.kyber import generate_keys as kyber_keys


def test_mlkem_768_roundtrip():
    public, secret = kem_keys()
    assert len(public) == 1184
    assert len(secret) == 65
    ciphertext, shared = kem_encaps(public)
    assert len(ciphertext) == 1088
    assert len(shared) == 32
    assert kem_decaps(secret, ciphertext) == shared
    assert shared not in ciphertext


def test_mlkem_1024_and_seed_rebuild():
    public, secret = kem_keys("ML-KEM-1024")
    assert len(public) == 1568
    rebuilt = kem_from_seed(secret[1:], "1024")
    assert rebuilt.public_key == public
    ciphertext, shared = kem_encaps(public)
    assert kem_decaps(rebuilt.secret_key, ciphertext) == shared


def test_mlkem_rejects_level_mismatch_and_tamper():
    public, secret = kem_keys()
    ciphertext, shared = kem_encaps(public)
    flipped = bytearray(ciphertext)
    flipped[0] ^= 0x01
    assert kem_decaps(secret, bytes(flipped)) != shared
    with pytest.raises(ValueError):
        kem_decaps(secret, b"\x00" * 10)
    with pytest.raises(TypeError):
        kem_encaps({"t": b"nope"})


def test_two_encapsulations_differ():
    public, _secret = kem_keys()
    first, _ = kem_encaps(public)
    second, _ = kem_encaps(public)
    assert first != second


def test_mldsa_65_and_context():
    public, secret = dsa_keys()
    assert len(public) == 1952
    message = b"aidddmap settlement"
    signature = dsa_sign(secret, message, context=b"settlement-v1")
    assert len(signature) == 3309
    assert dsa_verify(public, message, signature, context=b"settlement-v1")
    assert not dsa_verify(public, message, signature, context=b"other")
    assert not dsa_verify(public, b"other", signature, context=b"settlement-v1")
    tampered = bytearray(signature)
    tampered[-1] ^= 0x01
    assert not dsa_verify(public, message, bytes(tampered), context=b"settlement-v1")


def test_mldsa_87_seed_and_44():
    public, secret = dsa_keys("ML-DSA-87")
    assert len(public) == 2592
    again = dsa_from_seed(secret[1:], "87")
    assert again.public_key == public
    signature = dsa_sign(secret, b"m")
    assert len(signature) == 4627
    assert dsa_verify(public, b"m", signature)
    public44, secret44 = dsa_keys("44")
    signature44 = dsa_sign(secret44, b"m")
    assert len(public44) == 1312
    assert len(signature44) == 2420
    assert not dsa_verify(public, b"m", signature44)


def test_kyber_alias_is_mlkem():
    assert "ML-KEM-768" in KYBER_NOTE
    public, secret = kyber_keys()
    ciphertext, shared = kem_encaps(public)
    assert kem_decaps(secret, ciphertext) == shared


def test_xwing_seed_matches_the_pinned_vector():
    public, secret = kem_keys_from_seed(bytes(range(32)))
    assert secret == bytes(range(32))
    assert public[:16].hex() == "6f54098a0a0e641146614b6960ba60d8"
    assert len(public) == XWING_PK_LEN
    ciphertext, shared = encapsulate(public)
    assert len(ciphertext) == XWING_CT_LEN
    assert decapsulate(secret, ciphertext) == shared
    fresh_public, fresh_secret = generate_kem_keys()
    other_ct, other_ss = encapsulate(fresh_public)
    assert decapsulate(fresh_secret, other_ct) == other_ss
    flipped = bytearray(other_ct)
    flipped[-1] ^= 0x01
    assert decapsulate(fresh_secret, bytes(flipped)) != other_ss


def test_combiner_label_vector():
    assert XWING_LABEL == bytes.fromhex("5c2e2f2f5e5c")
    digest = combiner(b"M" * 32, b"X" * 32, b"C" * 32, b"P" * 32)
    assert digest.hex() == "1e3a5d16eb8f2ecefa77a8cc32288ad5f15491d0b97c0d70d759ad308a8d50f3"


def test_hybrid_signature_needs_both_halves():
    public, secret = generate_sign_keys()
    message = b"both or nothing"
    signature = sign(secret, message, context=b"ctx")
    assert len(signature) == HYBRID_SIGN_SIG_LEN
    assert verify(public, message, signature, context=b"ctx")
    assert not verify(public, message, signature, context=b"nope")
    head = bytearray(signature)
    head[0] ^= 0x01
    tail = bytearray(signature)
    tail[-1] ^= 0x01
    assert not verify(public, message, bytes(head), context=b"ctx")
    assert not verify(public, message, bytes(tail), context=b"ctx")
    assert not verify(public, message, signature[:10], context=b"ctx")
