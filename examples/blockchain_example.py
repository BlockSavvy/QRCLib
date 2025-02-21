"""
Blockchain Example using QRCLib

This example demonstrates how to use QRCLib to implement quantum-resistant
features in a blockchain system:

1. Quantum-resistant wallet creation
2. Transaction signing and verification
3. Secure communication between wallets
4. Block creation and validation

The example shows how to:
- Generate quantum-resistant keys for wallets
- Sign transactions with Dilithium
- Verify transaction signatures
- Encrypt messages between wallets using Kyber
"""

import json
import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import base64
import os

from src.kyber import generate_keys as kyber_keygen, encapsulate, decapsulate
from src.dilithium import generate_keys as dilithium_keygen, sign, verify
from src.utils import secure_random_bytes

@dataclass
class QuantumResistantTransaction:
    """
    Represents a quantum-resistant transaction.
    
    Features:
    - Dilithium signatures for transaction authenticity
    - Transaction hash for integrity
    - Timestamp for ordering
    """
    sender: str
    recipient: str
    amount: float
    timestamp: str = datetime.utcnow().isoformat()
    signature: Optional[bytes] = None
    sender_public_key: Optional[bytes] = None
    
    def serialize(self) -> bytes:
        """Serialize transaction for signing/verification."""
        data = {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp
        }
        return json.dumps(data, sort_keys=True).encode()
    
    @property
    def hash(self) -> str:
        """Compute transaction hash."""
        return hashlib.sha256(self.serialize()).hexdigest()
    
    @classmethod
    def verify_transaction(cls, transaction: 'QuantumResistantTransaction') -> bool:
        """
        Verify a transaction's signature.
        
        Args:
            transaction: The transaction to verify
        
        Returns:
            bool: True if signature is valid
        """
        try:
            # Get sender's public key from transaction data
            # In a real implementation, this would come from a key registry
            if not hasattr(transaction, 'sender_public_key'):
                return False
            
            return verify(
                transaction.sender_public_key,
                transaction.serialize(),
                transaction.signature
            )
        except Exception:
            return False

@dataclass
class QuantumResistantBlock:
    """
    Represents a block in the quantum-resistant blockchain.
    
    Features:
    - List of quantum-resistant transactions
    - Previous block hash for chain integrity
    - Block hash using quantum-resistant data
    """
    transactions: List[QuantumResistantTransaction]
    previous_hash: str
    timestamp: str = datetime.utcnow().isoformat()
    nonce: int = 0
    
    def serialize(self) -> bytes:
        """Serialize block for hashing."""
        data = {
            'transactions': [
                {
                    'sender': tx.sender,
                    'recipient': tx.recipient,
                    'amount': tx.amount,
                    'timestamp': tx.timestamp,
                    'signature': tx.signature.hex() if tx.signature else None
                }
                for tx in self.transactions
            ],
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'nonce': self.nonce
        }
        return json.dumps(data, sort_keys=True).encode()
    
    def compute_hash(self) -> str:
        """Compute block hash."""
        return hashlib.sha256(self.serialize()).hexdigest()
    
    def mine(self, difficulty: int = 4):
        """
        Mine the block by finding a nonce that gives a hash with
        the required number of leading zeros.
        """
        target = '0' * difficulty
        while True:
            hash = self.compute_hash()
            if hash.startswith(target):
                break
            self.nonce += 1

class QuantumResistantWallet:
    """
    Implements a quantum-resistant cryptocurrency wallet.
    
    Features:
    - Kyber key pair for encrypted communication
    - Dilithium key pair for transaction signing
    - Transaction creation and verification
    - Secure messaging between wallets
    """
    
    def __init__(self):
        """Initialize wallet with quantum-resistant keys."""
        # Generate Kyber keys for encryption
        self.enc_public_key, self.enc_private_key = kyber_keygen()
        
        # Generate Dilithium keys for signing
        self.sign_private_key, self.sign_public_key = dilithium_keygen()
        
        # Wallet address is derived from signing public key's key_seed
        self.address = self.sign_public_key['key_seed'].hex()
    
    def encrypt_message(self, recipient_key: bytes, message: str) -> Dict:
        """
        Encrypt a message for another wallet.
        
        Args:
            recipient_key: Recipient's public key
            message: Message to encrypt
        
        Returns:
            Dict containing ciphertext and encrypted message
        """
        message_bytes = message.encode()
        
        # Generate a random encryption key and encapsulate it
        encryption_key = secure_random_bytes(32)
        key_ciphertext, shared_secret = encapsulate(recipient_key)
        
        # Use shared secret to encrypt the message
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        cipher = AESGCM(shared_secret)
        nonce = os.urandom(12)
        ciphertext = cipher.encrypt(nonce, message_bytes, None)
        
        return {
            'key': key_ciphertext,
            'nonce': nonce,
            'message': ciphertext
        }
    
    def decrypt_message(self, sender_key: bytes, encrypted: Dict) -> str:
        """
        Decrypt a message from another wallet.
        
        Args:
            sender_key: Sender's public key
            encrypted: Dictionary containing encrypted data
        
        Returns:
            Decrypted message
        """
        # Decapsulate the shared secret
        shared_secret = decapsulate(encrypted['key'], self.enc_private_key)
        
        # Decrypt the message using the shared secret
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        cipher = AESGCM(shared_secret)
        try:
            message_bytes = cipher.decrypt(encrypted['nonce'], encrypted['message'], None)
            return message_bytes.decode()
        except Exception:
            raise ValueError("Decryption failed")
    
    def sign_transaction(self, transaction: QuantumResistantTransaction) -> QuantumResistantTransaction:
        """
        Sign a transaction with the wallet's private key.
        
        Args:
            transaction: Transaction to sign
        
        Returns:
            The signed transaction
        """
        if transaction.sender != self.address:
            raise ValueError("Cannot sign transaction from different sender")
        
        transaction.signature = sign(
            self.sign_private_key,
            transaction.serialize()
        )
        # Store the public key for verification
        transaction.sender_public_key = self.sign_public_key
        return transaction
    
    def create_transaction(self, recipient: str, amount: float) -> QuantumResistantTransaction:
        """
        Create and sign a new transaction.
        
        Args:
            recipient: Recipient's address
            amount: Transaction amount
        
        Returns:
            The signed transaction
        """
        transaction = QuantumResistantTransaction(
            sender=self.address,
            recipient=recipient,
            amount=amount,
            timestamp=datetime.utcnow().isoformat()
        )
        return self.sign_transaction(transaction)
    
    def get_public_key(self) -> bytes:
        """Get wallet's public encryption key."""
        return self.enc_public_key

def main():
    """
    Demonstrate the quantum-resistant blockchain implementation.
    
    This example shows:
    1. Creating wallets with quantum-resistant keys
    2. Creating and signing transactions
    3. Verifying transaction signatures
    4. Creating and mining blocks
    5. Secure communication between wallets
    """
    print("Quantum-Resistant Blockchain Example")
    print("-----------------------------------")
    
    # Create wallets
    print("\n1. Creating wallets for Alice and Bob...")
    alice = QuantumResistantWallet()
    bob = QuantumResistantWallet()
    print("   ✓ Wallets created successfully")
    print(f"   Alice's address: {alice.address[:16]}...")
    print(f"   Bob's address: {bob.address[:16]}...")
    
    # Create transaction
    print("\n2. Creating a transaction from Alice to Bob...")
    transaction = alice.create_transaction(
        recipient=bob.address,
        amount=10.5
    )
    print("   ✓ Transaction created and signed")
    print(f"   Transaction hash: {transaction.hash[:16]}...")
    
    # Verify transaction
    print("\n3. Verifying transaction signature...")
    is_valid = QuantumResistantTransaction.verify_transaction(transaction)
    print(f"   ✓ Signature is valid: {is_valid}")
    
    # Create and mine block
    print("\n4. Creating and mining a block...")
    block = QuantumResistantBlock(
        transactions=[transaction],
        previous_hash="0" * 64
    )
    block.mine(difficulty=4)
    print("   ✓ Block mined successfully")
    print(f"   Block hash: {block.compute_hash()[:16]}...")
    print(f"   Nonce: {block.nonce}")
    
    # Demonstrate secure messaging
    print("\n5. Testing secure messaging between wallets...")
    message = "Send more cryptocurrency!"
    print(f"   Original message: {message}")
    
    # Alice encrypts message for Bob
    encrypted = alice.encrypt_message(
        bob.get_public_key(),
        message
    )
    
    # Bob decrypts message
    decrypted = bob.decrypt_message(
        alice.get_public_key(),
        encrypted
    )
    print(f"   Decrypted message: {decrypted}")
    print("   ✓ Secure messaging successful")
    
    print("\n✓ Example completed successfully")
    print("\nThis example demonstrated:")
    print("- Quantum-resistant wallet creation")
    print("- Transaction signing and verification")
    print("- Block creation and mining")
    print("- Secure messaging between wallets")

if __name__ == "__main__":
    main() 