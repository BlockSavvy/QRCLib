"""Tests for the Bitcoin protection module."""

import unittest
from datetime import datetime

from src.bitcoin_protection import QuantumProtectedWallet, ProtectedTransaction

class TestBitcoinProtection(unittest.TestCase):
    """Test cases for quantum-resistant Bitcoin protection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wallet = QuantumProtectedWallet()
        self.valid_tx_hash = 'a' * 64  # Mock valid transaction hash
        
    def test_wallet_creation(self):
        """Test hybrid wallet creation."""
        # Check Bitcoin credentials
        self.assertTrue(self.wallet.btc_address.startswith('1'))
        self.assertEqual(len(self.wallet.btc_public_key), 64)
        
        # Check quantum credentials
        self.assertIsNotNone(self.wallet.quantum_private_key)
        self.assertIsNotNone(self.wallet.quantum_public_key)
        
        # Check public info format
        info = self.wallet.get_public_info()
        self.assertIn('btc_address', info)
        self.assertIn('btc_public_key', info)
        self.assertIn('quantum_public_key', info)
    
    def test_transaction_protection(self):
        """Test protecting a Bitcoin transaction."""
        # Protect a valid transaction
        protected_tx = self.wallet.protect_transaction(self.valid_tx_hash)
        
        # Check protected transaction attributes
        self.assertEqual(protected_tx.tx_hash, self.valid_tx_hash)
        self.assertEqual(protected_tx.btc_pubkey, self.wallet.btc_public_key)
        self.assertIsNotNone(protected_tx.quantum_signature)
        
        # Verify the protection
        self.assertTrue(
            self.wallet.verify_protected_transaction(protected_tx)
        )
    
    def test_invalid_transaction_hash(self):
        """Test handling of invalid transaction hashes."""
        invalid_hashes = [
            '',  # Empty
            'abc',  # Too short
            'x' * 64,  # Invalid characters
            '0' * 63,  # Wrong length
            123,  # Wrong type
            None  # None value
        ]
        
        for invalid_hash in invalid_hashes:
            with self.assertRaises(ValueError):
                self.wallet.protect_transaction(invalid_hash)
    
    def test_tampered_protection(self):
        """Test detection of tampered protection data."""
        # Create valid protection
        protected_tx = self.wallet.protect_transaction(self.valid_tx_hash)
        
        # Tamper with different fields
        tampered_tx = ProtectedTransaction(
            tx_hash='b' * 64,  # Changed transaction hash
            btc_pubkey=protected_tx.btc_pubkey,
            quantum_pubkey=protected_tx.quantum_pubkey,
            quantum_signature=protected_tx.quantum_signature
        )
        self.assertFalse(
            self.wallet.verify_protected_transaction(tampered_tx)
        )
        
        # Tamper with signature
        tampered_tx = ProtectedTransaction(
            tx_hash=protected_tx.tx_hash,
            btc_pubkey=protected_tx.btc_pubkey,
            quantum_pubkey=protected_tx.quantum_pubkey,
            quantum_signature=b'tampered'
        )
        self.assertFalse(
            self.wallet.verify_protected_transaction(tampered_tx)
        )
    
    def test_cross_wallet_verification(self):
        """Test verification between different wallets."""
        # Create two wallets
        wallet1 = QuantumProtectedWallet()
        wallet2 = QuantumProtectedWallet()
        
        # Protect transaction with wallet1
        protected_tx = wallet1.protect_transaction(self.valid_tx_hash)
        
        # Verify with wallet2 (should work as it uses the quantum pubkey from tx)
        self.assertTrue(
            wallet2.verify_protected_transaction(protected_tx)
        )
    
    def test_serialization(self):
        """Test transaction serialization for signing."""
        protected_tx = self.wallet.protect_transaction(self.valid_tx_hash)
        
        # Create a new transaction with same data
        same_tx = ProtectedTransaction(
            tx_hash=protected_tx.tx_hash,
            btc_pubkey=protected_tx.btc_pubkey,
            quantum_pubkey=protected_tx.quantum_pubkey,
            quantum_signature=protected_tx.quantum_signature,
            timestamp=protected_tx.timestamp
        )
        
        # Serialization should be identical
        self.assertEqual(
            protected_tx.serialize(),
            same_tx.serialize()
        )

if __name__ == '__main__':
    unittest.main() 