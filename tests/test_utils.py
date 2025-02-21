"""
Tests for cryptographic utility functions.
"""

import unittest
import numpy as np
from src.utils import (
    secure_random_bytes,
    secure_random_int,
    bytes_to_bits,
    bits_to_bytes,
    constant_time_compare,
    generate_matrix,
    polynomial_multiply,
    ntt_transform,
    inverse_ntt_transform
)

class TestUtils(unittest.TestCase):
    def test_secure_random_bytes(self):
        """Test secure random byte generation."""
        # Test different lengths
        lengths = [16, 24, 32, 64]
        for length in lengths:
            random_bytes = secure_random_bytes(length)
            self.assertEqual(len(random_bytes), length)
            
        # Test uniqueness
        samples = [secure_random_bytes(32) for _ in range(100)]
        unique_samples = set(samples)
        self.assertEqual(len(samples), len(unique_samples))
    
    def test_secure_random_int(self):
        """Test secure random integer generation."""
        # Test range boundaries
        for _ in range(1000):
            num = secure_random_int(0, 10)
            self.assertGreaterEqual(num, 0)
            self.assertLessEqual(num, 10)
        
        # Test distribution (roughly)
        samples = [secure_random_int(0, 1) for _ in range(10000)]
        zeros = samples.count(0)
        ones = samples.count(1)
        # Check if the distribution is roughly uniform (within 10%)
        self.assertLess(abs(zeros - ones), 1000)
    
    def test_bytes_bits_conversion(self):
        """Test conversion between bytes and bits."""
        test_cases = [
            b"Hello",
            b"Test123",
            bytes([0xFF, 0x00, 0xAA, 0x55])
        ]
        
        for data in test_cases:
            bits = bytes_to_bits(data)
            recovered = bits_to_bytes(bits)
            self.assertEqual(data, recovered[:len(data)])
    
    def test_constant_time_compare(self):
        """Test constant-time comparison."""
        # Test equal strings
        a = b"test string"
        b = b"test string"
        self.assertTrue(constant_time_compare(a, b))
        
        # Test unequal strings
        c = b"test string!"
        self.assertFalse(constant_time_compare(a, c))
        
        # Test different lengths
        d = b"test"
        self.assertFalse(constant_time_compare(a, d))
    
    def test_generate_matrix(self):
        """Test matrix generation."""
        rows, cols = 4, 4
        q = 3329  # Kyber's q
        
        matrix = generate_matrix(rows, cols, q)
        
        # Check dimensions
        self.assertEqual(matrix.shape, (rows, cols))
        
        # Check value ranges
        self.assertTrue(np.all(matrix >= 0))
        self.assertTrue(np.all(matrix < q))
        
        # Check that we get different matrices
        matrix2 = generate_matrix(rows, cols, q)
        self.assertFalse(np.array_equal(matrix, matrix2))
    
    def test_polynomial_multiply(self):
        """Test polynomial multiplication."""
        # Test simple polynomials
        a = np.array([1, 2, 3])
        b = np.array([2, 1])
        modulus = 7
        
        result = polynomial_multiply(a, b, modulus)
        
        # Check that result is within the modulus
        self.assertTrue(np.all(result >= 0))
        self.assertTrue(np.all(result < modulus))
        
        # Test with zero polynomial
        zero = np.zeros_like(a)
        result_zero = polynomial_multiply(a, zero, modulus)
        self.assertTrue(np.all(result_zero == 0))
    
    def test_ntt_transforms(self):
        """Test NTT and inverse NTT transforms."""
        # Test with a simple polynomial
        poly = np.array([1, 2, 3, 4])
        modulus = 17
        
        # Transform and inverse transform should give back the original
        transformed = ntt_transform(poly, modulus)
        recovered = inverse_ntt_transform(transformed, modulus)
        
        # Note: This is a simplified test as we're using placeholder NTT functions
        self.assertTrue(np.array_equal(poly, recovered))

if __name__ == '__main__':
    unittest.main() 