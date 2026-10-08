"""Mailbox over X-Wing. Not forward secret. Run: python examples/secure_messaging.py"""

from qrclib.messaging import Mailbox


def main() -> None:
    alice, bob = Mailbox("alice"), Mailbox("bob")
    offer = alice.offer(bob.kem.public_key)
    alice.bind_peer(bob.signing.public_key)
    bob.accept(offer, alice.signing.public_key)
    packet = alice.encrypt("The truss pack is on the truck.")
    print("wire bytes", len(packet))
    print("bob reads", bob.decrypt(packet).decode())


if __name__ == "__main__":
    main()
