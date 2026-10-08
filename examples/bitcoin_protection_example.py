"""Off-chain hybrid attestation for a Bitcoin txid.

Run: python examples/bitcoin_protection_example.py
"""

from qrclib.bitcoin import GUIDANCE, QuantumProtectedWallet


def main() -> None:
    wallet = QuantumProtectedWallet.generate()
    info = wallet.public_info()
    attestation = wallet.protect_transaction("11" * 32, timestamp="2026-10-08T17:00:00Z")
    print("address", info["btc_address"])
    print("hybrid signature bytes", len(attestation.signature))
    print("verifies", attestation.verify())
    print("op_return script", attestation.op_return_script().hex())
    for line in GUIDANCE:
        print("-", line)


if __name__ == "__main__":
    main()
