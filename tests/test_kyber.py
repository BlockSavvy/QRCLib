"""
Tests for the Kyber key encapsulation mechanism.
"""

import unittest
import numpy as np
from src.kyber import generate_keys, encapsulate, decapsulate, KyberParams, derive_shared_secret

class TestKyber(unittest.TestCase):
    def setUp(self):
        """Set up test parameters."""
        self.params = KyberParams()
    
    def test_parameter_ranges(self):
        """Test that Kyber parameters are within expected ranges."""
        self.assertEqual(self.params.n, 256)
        self.assertEqual(self.params.q, 3329)
        self.assertEqual(self.params.eta, 2)
        self.assertIn(self.params.k, [2, 3, 4])  # Valid security levels
    
    def test_key_generation(self):
        """Test key pair generation."""
        public_key, private_key = generate_keys(self.params)
        
        # Check that keys have the expected structure
        self.assertIn('A', public_key)
        self.assertIn('t', public_key)
        self.assertIn('s', private_key)
        
        # Check matrix dimensions
        self.assertEqual(public_key['A'].shape[0], self.params.k)
        self.assertEqual(public_key['t'].shape[0], self.params.k)
        self.assertEqual(private_key['s'].shape[0], self.params.k)
    
    def test_encapsulation(self):
        """Test secret encapsulation."""
        public_key, _ = generate_keys(self.params)
        ciphertext, shared_secret = encapsulate(public_key, self.params)
        
        # Check that we get a ciphertext and shared secret
        self.assertIsNotNone(ciphertext)
        self.assertIsNotNone(shared_secret)
        self.assertIsInstance(shared_secret, bytes)
        self.assertEqual(len(shared_secret), 32)  # Expected shared secret length
    
    def test_decapsulation(self):
        """Test secret decapsulation."""
        public_key, private_key = generate_keys(self.params)
        ciphertext, shared_secret_a = encapsulate(public_key, self.params)
        shared_secret_b = decapsulate(ciphertext, private_key, self.params)
        
        # Check that both parties derive the same shared secret
        self.assertEqual(shared_secret_a, shared_secret_b)
    
    def test_failed_decapsulation(self):
        """Test that decapsulation fails with wrong private key."""
        # Generate two key pairs
        public_key1, private_key1 = generate_keys(self.params)
        _, private_key2 = generate_keys(self.params)
        
        # Encapsulate with first public key
        ciphertext, shared_secret_a = encapsulate(public_key1, self.params)
        
        # Try to decapsulate with wrong private key
        shared_secret_b = decapsulate(ciphertext, private_key2, self.params)
        
        # Check that the shared secrets are different
        self.assertNotEqual(shared_secret_a, shared_secret_b)
    
    def test_key_reuse(self):
        """Test that the same public key can be used multiple times."""
        public_key, private_key = generate_keys(self.params)
        
        # Perform two encapsulations with the same public key
        ciphertext1, shared_secret1 = encapsulate(public_key, self.params)
        ciphertext2, shared_secret2 = encapsulate(public_key, self.params)
        
        # Check that we get different shared secrets
        self.assertNotEqual(shared_secret1, shared_secret2)
        
        # Check that both can be correctly decapsulated
        decap_secret1 = decapsulate(ciphertext1, private_key, self.params)
        decap_secret2 = decapsulate(ciphertext2, private_key, self.params)
        
        self.assertEqual(shared_secret1, decap_secret1)
        self.assertEqual(shared_secret2, decap_secret2)

    def test_invalid_decapsulation_input(self):
        """Test decapsulation with invalid inputs."""
        # Test with invalid ciphertext
        _, private_key = generate_keys(self.params)
        invalid_ciphertext = {'invalid': 'ciphertext'}
        shared_secret = decapsulate(invalid_ciphertext, private_key, self.params)
        self.assertEqual(len(shared_secret), 32)  # Should return random secret
        
        # Test with missing nonce
        ciphertext_no_nonce = {'c': b'message'}
        shared_secret = decapsulate(ciphertext_no_nonce, private_key, self.params)
        self.assertEqual(len(shared_secret), 32)
        
        # Test with invalid private key
        public_key, _ = generate_keys(self.params)
        ciphertext, _ = encapsulate(public_key, self.params)
        invalid_private_key = {'invalid': 'key'}
        shared_secret = decapsulate(ciphertext, invalid_private_key, self.params)
        self.assertEqual(len(shared_secret), 32)

    def test_invalid_encapsulation_input(self):
        """Test encapsulation with invalid inputs."""
        # Test with invalid public key
        invalid_public_key = {'invalid': 'key'}
        ciphertext, shared_secret = encapsulate(invalid_public_key, self.params)
        self.assertIsNotNone(ciphertext)
        self.assertEqual(len(shared_secret), 32)

    def test_shared_secret_derivation(self):
        """Test the shared secret derivation function."""
        seed = b"test_seed"
        message = b"test_message"
        nonce = b"test_nonce"
        
        # Test deterministic derivation
        secret1 = derive_shared_secret(seed, message, nonce)
        secret2 = derive_shared_secret(seed, message, nonce)
        self.assertEqual(secret1, secret2)  # Same inputs should give same secret
        
        # Test different inputs give different secrets
        secret3 = derive_shared_secret(seed, b"different", nonce)
        self.assertNotEqual(secret1, secret3)
        
        # Test output length
        self.assertEqual(len(secret1), 32)  # SHA-256 output is 32 bytes

    def test_different_security_levels(self):
        """Test Kyber with different security levels."""
        for k in [2, 3, 4]:  # Test all valid k values
            params = KyberParams(k=k)
            public_key, private_key = generate_keys(params)
            
            # Check matrix dimensions match security level
            self.assertEqual(public_key['A'].shape[0], k)
            self.assertEqual(private_key['s'].shape[0], k)
            
            # Test encapsulation/decapsulation
            ciphertext, shared_secret_a = encapsulate(public_key, params)
            shared_secret_b = decapsulate(ciphertext, private_key, params)
            self.assertEqual(shared_secret_a, shared_secret_b)

if __name__ == '__main__':
    unittest.main() 