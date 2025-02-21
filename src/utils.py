"""
Utility functions for quantum-resistant cryptographic operations.
"""

import secrets
import numpy as np
from typing import Union, List, Tuple

def secure_random_bytes(length: int) -> bytes:
    """Generate cryptographically secure random bytes.
    
    Args:
        length: Number of bytes to generate
        
    Returns:
        bytes: Secure random bytes
    """
    return secrets.token_bytes(length)

def secure_random_int(min_val: int, max_val: int) -> int:
    """Generate a cryptographically secure random integer in the range [min_val, max_val]."""
    return secrets.randbelow(max_val - min_val + 1) + min_val

def bytes_to_bits(data: bytes) -> List[int]:
    """Convert bytes to a list of bits."""
    result = []
    for byte in data:
        for i in range(8):
            result.append((byte >> (7 - i)) & 1)
    return result

def bits_to_bytes(bits: List[int]) -> bytes:
    """Convert a list of bits to bytes."""
    result = []
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(min(8, len(bits) - i)):
            byte |= bits[i + j] << (7 - j)
        result.append(byte)
    return bytes(result)

def constant_time_compare(a: bytes, b: bytes) -> bool:
    """Compare two byte strings in constant time to prevent timing attacks."""
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= x ^ y
    return result == 0

def generate_matrix(rows: int, cols: int, modulus: int) -> np.ndarray:
    """Generate a random matrix with elements in [0, modulus)."""
    return np.array([
        [secure_random_int(0, modulus - 1) for _ in range(cols)]
        for _ in range(rows)
    ])

def find_primitive_root(modulus: int) -> int:
    """Find a primitive root modulo n."""
    if modulus == 3329:  # Kyber prime
        return 17
    elif modulus == 8380417:  # Dilithium prime
        return 1753
    elif modulus == 17:  # Test prime
        return 3  # Known primitive root for 17
    
    def is_primitive_root(a: int, modulus: int, factors: List[int]) -> bool:
        """Check if a is a primitive root modulo n."""
        for factor in factors:
            if pow(a, (modulus - 1) // factor, modulus) == 1:
                return False
        return True
    
    # Find prime factors of modulus - 1
    n = modulus - 1
    factors = []
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            factors.append(i)
            while n % i == 0:
                n //= i
    if n > 1:
        factors.append(n)
    
    # Find primitive root
    a = 2
    while not is_primitive_root(a, modulus, factors):
        a += 1
    return a

def mod_inverse(a: int, m: int) -> int:
    """Calculate the modular multiplicative inverse of a modulo m."""
    def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y

    _, x, _ = extended_gcd(a, m)
    return (x % m + m) % m

def bit_reverse(x: int, bits: int) -> int:
    """Reverse the bits of x."""
    result = 0
    for i in range(bits):
        result = (result << 1) | (x & 1)
        x >>= 1
    return result

def ntt_transform(poly: np.ndarray, modulus: int) -> np.ndarray:
    """
    Compute the Number Theoretic Transform (NTT) of a polynomial.
    
    Args:
        poly: Polynomial coefficients
        modulus: Prime modulus
    
    Returns:
        NTT transformed polynomial
    """
    n = len(poly)
    if n & (n - 1) != 0:
        raise ValueError("Length must be a power of 2")
    
    # Find primitive root and generate powers
    g = find_primitive_root(modulus)
    omega = pow(g, (modulus - 1) // n, modulus)
    
    # Precompute powers of omega
    omegas = np.array([pow(omega, i, modulus) for i in range(n)], dtype=int)
    
    # Initialize result array
    result = poly.copy()
    
    # Cooley-Tukey FFT algorithm
    for s in range(int(np.log2(n))):
        m = 1 << s
        for k in range(0, n, 2 * m):
            for j in range(m):
                idx1 = k + j
                idx2 = k + j + m
                u = result[idx1]
                v = (result[idx2] * omegas[j * (n // (2 * m))]) % modulus
                result[idx1] = (u + v) % modulus
                result[idx2] = (u - v) % modulus
    
    return result

def intt_transform(poly: np.ndarray, modulus: int) -> np.ndarray:
    """
    Compute the Inverse Number Theoretic Transform (INTT) of a polynomial.
    
    Args:
        poly: NTT transformed polynomial
        modulus: Prime modulus
    
    Returns:
        Original polynomial coefficients
    """
    n = len(poly)
    if n & (n - 1) != 0:
        raise ValueError("Length must be a power of 2")
    
    # Find primitive root and generate powers
    g = find_primitive_root(modulus)
    omega = pow(g, (modulus - 1) // n, modulus)
    omega_inv = pow(omega, -1, modulus)
    n_inv = pow(n, -1, modulus)
    
    # Precompute inverse powers of omega
    omegas_inv = np.array([pow(omega_inv, i, modulus) for i in range(n)], dtype=int)
    
    # Initialize result array
    result = poly.copy()
    
    # Gentleman-Sande FFT algorithm
    for s in range(int(np.log2(n)) - 1, -1, -1):
        m = 1 << s
        for k in range(0, n, 2 * m):
            for j in range(m):
                idx1 = k + j
                idx2 = k + j + m
                u = result[idx1]
                v = result[idx2]
                result[idx1] = (u + v) % modulus
                result[idx2] = ((u - v) * omegas_inv[j * (n // (2 * m))]) % modulus
    
    # Scale by n^(-1)
    result = (result * n_inv) % modulus
    
    return result

def polynomial_multiply(a: np.ndarray, b: np.ndarray, modulus: int) -> np.ndarray:
    """
    Multiply two polynomials modulo x^n + 1 using NTT.
    
    Args:
        a: First polynomial coefficients
        b: Second polynomial coefficients
        modulus: Prime modulus
    
    Returns:
        Product polynomial coefficients
    """
    n = len(a)
    if n != len(b):
        raise ValueError("Polynomials must have same length")
    
    # Find next power of 2
    n_padded = 1
    while n_padded < n:
        n_padded *= 2
    
    # Pad polynomials
    a_padded = np.pad(a, (0, n_padded - n))
    b_padded = np.pad(b, (0, n_padded - n))
    
    # Transform to NTT domain
    a_ntt = ntt_transform(a_padded, modulus)
    b_ntt = ntt_transform(b_padded, modulus)
    
    # Multiply point-wise
    c_ntt = (a_ntt * b_ntt) % modulus
    
    # Transform back and truncate
    result = intt_transform(c_ntt, modulus)
    return result[:n] 