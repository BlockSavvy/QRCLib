"""Seals, mailboxes, and the Bitcoin attestation."""

import pytest

from qrclib.bitcoin import GUIDANCE, QuantumProtectedWallet
from qrclib.errors import InvalidSeal, VerificationFailed
from qrclib.hybrid import generate_kem_keys, generate_sign_keys
from qrclib.messaging import Mailbox
from qrclib.seal import open_seal, seal


def test_seal_roundtrip_and_tamper():
    recipient = generate_kem_keys()
    sender = generate_sign_keys()
    blob = seal(recipient.public_key, b"column-7", sender.secret_key, aad=b"file")
    assert open_seal(recipient.secret_key, blob, sender.public_key, aad=b"file") == b"column-7"
    with pytest.raises(InvalidSeal):
        open_seal(recipient.secret_key, blob, sender.public_key, aad=b"other")
    flipped = bytearray(blob)
    flipped[20] ^= 0x01
    with pytest.raises(InvalidSeal):
        open_seal(recipient.secret_key, bytes(flipped), sender.public_key, aad=b"file")


def test_mailbox():
    alice = Mailbox("alice")
    bob = Mailbox("bob")
    offer = alice.offer(bob.kem.public_key)
    alice.bind_peer(bob.signing.public_key)
    bob.accept(offer, alice.signing.public_key)
    packet = alice.encrypt("meet at dock 4")
    assert bob.decrypt(packet) == b"meet at dock 4"
    reply = bob.encrypt(b"copy")
    assert alice.decrypt(reply) == b"copy"
    forged = bytearray(packet)
    forged[12] ^= 0x01
    with pytest.raises((InvalidSeal, VerificationFailed)):
        bob.decrypt(bytes(forged))


def test_bitcoin_attestation_commitment_fits_op_return():
    wallet = QuantumProtectedWallet.generate()
    txid = "ab" * 32
    attestation = wallet.protect_transaction(txid, timestamp="2026-10-08T17:00:00Z")
    assert attestation.verify()
    assert attestation.btc_address.startswith("1")
    assert len(attestation.signature) == 3373
    assert len(attestation.commitment()) == 32
    script = attestation.op_return_script()
    assert script[:2] == bytes((0x6A, 0x20))
    assert len(script) == 34
    assert len(script) <= 80
    broken = attestation
    broken.signature = bytes(reversed(attestation.signature))
    assert not broken.verify()
    with pytest.raises(ValueError):
        wallet.protect_transaction("zz")
    assert any("OP_RETURN" in line for line in GUIDANCE)
