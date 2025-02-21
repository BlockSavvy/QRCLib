"""
Tests for the Dilithium digital signature scheme.
"""

import unittest
import numpy as np
from src.dilithium import generate_keys, sign, verify, DilithiumParams, compute_signature_hash

class TestDilithium(unittest.TestCase):
    def setUp(self):
        """Set up test parameters."""
        self.params = DilithiumParams()
        self.test_message = b"Hello, quantum world!"
    
    def test_parameter_ranges(self):
        """Test that Dilithium parameters are within expected ranges."""
        self.assertEqual(self.params.n, 256)
        self.assertEqual(self.params.q, 8380417)
        self.assertEqual(self.params.d, 13)
        self.assertEqual(self.params.tau, 39)
        self.assertEqual(self.params.gamma1, 131072)
        self.assertEqual(self.params.gamma2, 95232)
        self.assertEqual(self.params.k, 4)
        self.assertEqual(self.params.l, 4)
        self.assertEqual(self.params.eta, 2)
    
    def test_key_generation(self):
        """Test key pair generation."""
        signing_key, verification_key = generate_keys(self.params)
        
        # Check that keys have the expected structure
        self.assertIn('rho', signing_key)
        self.assertIn('A', signing_key)
        self.assertIn('s1', signing_key)
        self.assertIn('s2', signing_key)
        self.assertIn('t', signing_key)
        
        self.assertIn('rho', verification_key)
        self.assertIn('A', verification_key)
        self.assertIn('t', verification_key)
        
        # Check matrix dimensions
        self.assertEqual(signing_key['A'].shape[0], self.params.k)
        self.assertEqual(signing_key['A'].shape[1], self.params.l)
        self.assertEqual(signing_key['t'].shape[0], self.params.k)
    
    def test_signature_generation(self):
        """Test signature generation."""
        signing_key, _ = generate_keys(self.params)
        signature = sign(signing_key, self.test_message, self.params)
        
        # Check that we get a signature
        self.assertIsNotNone(signature)
        self.assertIsInstance(signature, bytes)
        self.assertGreater(len(signature), len(self.test_message))
    
    def test_signature_verification(self):
        """Test signature verification."""
        signing_key, verification_key = generate_keys(self.params)
        signature = sign(signing_key, self.test_message, self.params)
        
        # Verify the signature
        is_valid = verify(verification_key, self.test_message, signature, self.params)
        self.assertTrue(is_valid)
    
    def test_signature_verification_failure(self):
        """Test that verification fails with tampered message or signature."""
        signing_key, verification_key = generate_keys(self.params)
        signature = sign(signing_key, self.test_message, self.params)
        
        # Test with tampered message
        tampered_message = b"Hello, tampered world!"
        is_valid = verify(verification_key, tampered_message, signature, self.params)
        self.assertFalse(is_valid)
        
        # Test with tampered signature
        tampered_signature = signature[:-1] + bytes([signature[-1] ^ 1])
        is_valid = verify(verification_key, self.test_message, tampered_signature, self.params)
        self.assertFalse(is_valid)
    
    def test_wrong_key_verification(self):
        """Test that verification fails with wrong verification key."""
        # Generate two key pairs
        signing_key1, verification_key1 = generate_keys(self.params)
        _, verification_key2 = generate_keys(self.params)
        
        # Sign with first key
        signature = sign(signing_key1, self.test_message, self.params)
        
        # Verify with wrong key
        is_valid = verify(verification_key2, self.test_message, signature, self.params)
        self.assertFalse(is_valid)
    
    def test_different_messages(self):
        """Test signing different messages with the same key."""
        signing_key, verification_key = generate_keys(self.params)
        
        messages = [
            b"First message",
            b"Second message",
            b"Third message"
        ]
        
        # Sign and verify each message
        for message in messages:
            signature = sign(signing_key, message, self.params)
            is_valid = verify(verification_key, message, signature, self.params)
            self.assertTrue(is_valid)
            
            # Verify signature doesn't work for other messages
            for other_message in messages:
                if other_message != message:
                    is_valid = verify(verification_key, other_message, signature, self.params)
                    self.assertFalse(is_valid)

    def test_invalid_signature_input(self):
        """Test verification with invalid signature inputs."""
        _, verification_key = generate_keys(self.params)
        
        # Test with short signature
        short_signature = b"too short"
        is_valid = verify(verification_key, self.test_message, short_signature, self.params)
        self.assertFalse(is_valid)
        
        # Test with None signature
        is_valid = verify(verification_key, self.test_message, None, self.params)
        self.assertFalse(is_valid)
        
        # Test with invalid verification key
        invalid_key = {'rho': b'invalid'}
        is_valid = verify(invalid_key, self.test_message, b"x" * 64, self.params)
        self.assertFalse(is_valid)

    def test_invalid_signing_input(self):
        """Test signing with invalid inputs."""
        # Test with invalid signing key
        invalid_key = {'invalid': 'key'}
        signature = sign(invalid_key, self.test_message, self.params)
        self.assertEqual(len(signature), 64)  # Should return random signature
        
        # Test with None message
        signing_key, _ = generate_keys(self.params)
        signature = sign(signing_key, None, self.params)
        self.assertEqual(len(signature), 64)

    def test_signature_hash_computation(self):
        """Test the signature hash computation."""
        key_seed = b"test_key_seed"
        message = b"test_message"
        nonce = b"test_nonce"
        
        # Test hash computation
        hash1 = compute_signature_hash(key_seed, message, nonce)
        hash2 = compute_signature_hash(key_seed, message, nonce)
        self.assertEqual(hash1, hash2)  # Same inputs should give same hash
        
        # Test different inputs give different hashes
        hash3 = compute_signature_hash(key_seed, b"different", nonce)
        self.assertNotEqual(hash1, hash3)

if __name__ == '__main__':
    unittest.main() 