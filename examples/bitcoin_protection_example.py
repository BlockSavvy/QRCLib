"""
Example demonstrating quantum-resistant Bitcoin transaction protection.

This example shows how to:
1. Create a hybrid wallet (Bitcoin + quantum-resistant)
2. Protect Bitcoin transactions with quantum-resistant signatures
3. Verify protected transactions
4. Handle multiple wallets and cross-verification
"""

from src.bitcoin_protection import QuantumProtectedWallet

def main():
    print("Creating Alice's hybrid wallet...")
    alice_wallet = QuantumProtectedWallet()
    alice_info = alice_wallet.get_public_info()
    print(f"Alice's Bitcoin address: {alice_info['btc_address']}")
    print(f"Alice's quantum public key: {alice_info['quantum_public_key'][:32]}...")
    
    print("\nCreating Bob's hybrid wallet...")
    bob_wallet = QuantumProtectedWallet()
    bob_info = bob_wallet.get_public_info()
    print(f"Bob's Bitcoin address: {bob_info['btc_address']}")
    print(f"Bob's quantum public key: {bob_info['quantum_public_key'][:32]}...")
    
    # Simulate a Bitcoin transaction from Alice to Bob
    print("\nSimulating a Bitcoin transaction from Alice to Bob...")
    mock_tx_hash = "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
    print(f"Transaction hash: {mock_tx_hash}")
    
    # Alice protects her transaction
    print("\nAlice adds quantum protection to her transaction...")
    protected_tx = alice_wallet.protect_transaction(mock_tx_hash)
    print("Transaction protected with quantum-resistant signature")
    
    # Bob verifies the protection
    print("\nBob verifies the quantum protection...")
    is_valid = bob_wallet.verify_protected_transaction(protected_tx)
    print(f"Protection verification: {'Valid' if is_valid else 'Invalid'}")
    
    # Demonstrate tampering detection
    print("\nDemonstrating tampering detection...")
    # Modify the transaction hash (simulating an attack)
    protected_tx.tx_hash = "0" * 64
    is_valid = bob_wallet.verify_protected_transaction(protected_tx)
    print(f"Verification of tampered transaction: {'Valid' if is_valid else 'Invalid'}")
    
    print("\nKey takeaways:")
    print("1. Each wallet now has both Bitcoin and quantum-resistant keys")
    print("2. Transactions are protected with quantum-resistant signatures")
    print("3. Anyone can verify the quantum protection using the public keys")
    print("4. Tampering is detected through signature verification")
    print("5. This provides protection against future quantum computer attacks")

if __name__ == "__main__":
    main() 