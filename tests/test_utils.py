"""Tests for utility functions."""

import unittest
import numpy as np
from typing import List

from src.utils import (
    secure_random_bytes,
    secure_random_int,
    constant_time_compare,
    bits_to_bytes,
    bytes_to_bits,
    generate_matrix,
    find_primitive_root,
    ntt_transform,
    intt_transform,
    polynomial_multiply
)

class TestUtils(unittest.TestCase):
    """Test suite for utility functions."""
    
    def test_secure_random_bytes(self):
        """Test secure random byte generation."""
        # Test different lengths
        for length in [1, 16, 32, 64]:
            result = secure_random_bytes(length)
            self.assertEqual(len(result), length)
            self.assertIsInstance(result, bytes)
    
    def test_secure_random_int(self):
        """Test secure random integer generation."""
        # Test range boundaries
        for _ in range(100):
            result = secure_random_int(0, 10)
            self.assertGreaterEqual(result, 0)
            self.assertLessEqual(result, 10)
        
        # Test negative range
        for _ in range(100):
            result = secure_random_int(-5, 5)
            self.assertGreaterEqual(result, -5)
            self.assertLessEqual(result, 5)
    
    def test_constant_time_compare(self):
        """Test constant-time comparison."""
        # Test equal strings
        a = b"test string"
        b = b"test string"
        self.assertTrue(constant_time_compare(a, b))
        
        # Test different strings
        c = b"test string2"
        self.assertFalse(constant_time_compare(a, c))
        
        # Test different lengths
        d = b"test"
        self.assertFalse(constant_time_compare(a, d))
    
    def test_bytes_bits_conversion(self):
        """Test conversion between bytes and bits."""
        # Test single byte
        data = bytes([0b10101010])
        bits = bytes_to_bits(data)
        self.assertEqual(bits, [1, 0, 1, 0, 1, 0, 1, 0])
        self.assertEqual(bits_to_bytes(bits), data)
        
        # Test multiple bytes
        data = bytes([0xFF, 0x00, 0xAA])
        bits = bytes_to_bits(data)
        expected = [1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0, 1,0,1,0,1,0,1,0]
        self.assertEqual(bits, expected)
        self.assertEqual(bits_to_bytes(bits), data)
    
    def test_generate_matrix(self):
        """Test random matrix generation."""
        rows, cols = 3, 4
        modulus = 7
        
        matrix = generate_matrix(rows, cols, modulus)
        
        # Check dimensions
        self.assertEqual(matrix.shape, (rows, cols))
        
        # Check elements are in range [0, modulus)
        self.assertTrue(np.all(matrix >= 0))
        self.assertTrue(np.all(matrix < modulus))
    
    def test_find_primitive_root(self):
        """Test finding primitive roots."""
        # Test Kyber prime
        root = find_primitive_root(3329)
        self.assertEqual(root, 17)
        
        # Test Dilithium prime
        root = find_primitive_root(8380417)
        self.assertEqual(root, 1753)
    
    def test_ntt_transforms(self):
        """Test NTT and inverse NTT transforms."""
        # Test with small prime and polynomial
        modulus = 17
        poly = np.array([1, 2, 3, 4, 0, 0, 0, 0], dtype=int)
        
        # Transform and inverse transform
        transformed = ntt_transform(poly, modulus)
        recovered = intt_transform(transformed, modulus)
        
        # Check recovery (element-wise comparison)
        self.assertTrue(np.all(poly == recovered % modulus))
        
        # Test with different polynomial
        poly2 = np.array([5, 6, 7, 8, 1, 2, 3, 4], dtype=int)
        transformed2 = ntt_transform(poly2, modulus)
        recovered2 = intt_transform(transformed2, modulus)
        self.assertTrue(np.all(poly2 == recovered2 % modulus))
    
    def test_polynomial_multiply(self):
        """Test polynomial multiplication."""
        modulus = 17
        a = np.array([1, 2, 3, 4, 0, 0, 0, 0])
        b = np.array([2, 1, 0, 3, 0, 0, 0, 0])
        
        # Multiply polynomials
        result = polynomial_multiply(a, b, modulus)
        
        # Check result is correct length
        self.assertEqual(len(result), len(a))
        
        # Check elements are in range [0, modulus)
        self.assertTrue(np.all(result >= 0))
        self.assertTrue(np.all(result < modulus))

if __name__ == '__main__':
    unittest.main() 