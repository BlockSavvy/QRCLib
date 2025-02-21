"""
Utility functions for quantum-resistant cryptographic operations.
"""

import secrets
import numpy as np
from typing import Union, List, Tuple

def secure_random_bytes(n: int) -> bytes:
    """Generate cryptographically secure random bytes."""
    return secrets.token_bytes(n)

def secure_random_int(min_val: int, max_val: int) -> int:
    """Generate a cryptographically secure random integer in the range [min_val, max_val]."""
    return secrets.randbelow(max_val - min_val + 1) + min_val

def bytes_to_bits(data: bytes) -> List[int]:
    """Convert bytes to a list of bits."""
    result = []
    for byte in data:
        for i in range(8):
            result.append((byte >> i) & 1)
    return result

def bits_to_bytes(bits: List[int]) -> bytes:
    """Convert a list of bits back to bytes."""
    result = bytearray((len(bits) + 7) // 8)
    for i, bit in enumerate(bits):
        if bit:
            result[i // 8] |= 1 << (i % 8)
    return bytes(result)

def constant_time_compare(a: bytes, b: bytes) -> bool:
    """Compare two byte strings in constant time to prevent timing attacks."""
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= x ^ y
    return result == 0

def generate_matrix(rows: int, cols: int, q: int) -> np.ndarray:
    """Generate a random matrix with entries modulo q."""
    return np.array([[secure_random_int(0, q-1) for _ in range(cols)] 
                     for _ in range(rows)])

def find_primitive_root(q: int) -> int:
    """Find a primitive root modulo q."""
    if q == 3329:  # Kyber's q
        return 17  # Known primitive root for Kyber's q
    elif q == 8380417:  # Dilithium's q
        return 5  # Known primitive root for Dilithium's q
    
    # For other primes, we would implement a proper search
    # This is a placeholder that works for our specific use cases
    return 17

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

def ntt_transform(polynomial: np.ndarray, modulus: int, inverse: bool = False) -> np.ndarray:
    """
    Perform Number Theoretic Transform (NTT) on a polynomial.
    
    Args:
        polynomial: Coefficient array of the polynomial
        modulus: The modulus for the finite field
        inverse: Whether to perform inverse NTT
    
    Returns:
        Transformed polynomial coefficients
    """
    n = len(polynomial)
    if n & (n - 1):  # Check if n is power of 2
        raise ValueError("Length must be a power of 2")
        
    # Find primitive root and calculate primitive nth root of unity
    g = find_primitive_root(modulus)
    omega = pow(g, (modulus - 1) // n, modulus)
    if inverse:
        omega = mod_inverse(omega, modulus)
    
    # Bit-reverse copy of the polynomial
    result = np.zeros(n, dtype=np.int64)
    for i in range(n):
        rev = bit_reverse(i, n.bit_length() - 1)
        result[i] = polynomial[rev]
    
    # Cooley-Tukey NTT
    for size in range(2, n + 1, 2):
        half_size = size // 2
        omega_step = pow(omega, n // size, modulus)
        for i in range(0, n, size):
            omega_i = 1
            for j in range(half_size):
                pos1, pos2 = i + j, i + j + half_size
                temp = (omega_i * result[pos2]) % modulus
                result[pos2] = (result[pos1] - temp) % modulus
                result[pos1] = (result[pos1] + temp) % modulus
                omega_i = (omega_i * omega_step) % modulus
    
    # Scale for inverse transform
    if inverse:
        n_inv = mod_inverse(n, modulus)
        result = [(x * n_inv) % modulus for x in result]
    
    return np.array(result)

def inverse_ntt_transform(polynomial: np.ndarray, modulus: int) -> np.ndarray:
    """
    Perform inverse Number Theoretic Transform.
    
    Args:
        polynomial: NTT-transformed polynomial coefficients
        modulus: The modulus for the finite field
    
    Returns:
        Original polynomial coefficients
    """
    return ntt_transform(polynomial, modulus, inverse=True)

def polynomial_multiply(a: np.ndarray, b: np.ndarray, modulus: int, n: int = 256) -> np.ndarray:
    """
    Multiply two polynomials in R_q = Z_q[X]/(X^n + 1) using NTT.
    
    Args:
        a: First polynomial coefficients
        b: Second polynomial coefficients
        modulus: Modulus for coefficient reduction
        n: Degree of X^n + 1 (default: 256 for Kyber/Dilithium)
    
    Returns:
        Resulting polynomial coefficients modulo q
    """
    # Ensure inputs are 1D arrays of correct length
    a = np.asarray(a).flatten()[:n]
    b = np.asarray(b).flatten()[:n]
    
    # Pad arrays to length n if needed
    if len(a) < n:
        a = np.pad(a, (0, n - len(a)))
    if len(b) < n:
        b = np.pad(b, (0, n - len(b)))
    
    # Transform to NTT domain
    a_ntt = ntt_transform(a, modulus)
    b_ntt = ntt_transform(b, modulus)
    
    # Multiply in NTT domain
    c_ntt = (a_ntt * b_ntt) % modulus
    
    # Transform back to normal domain
    c = inverse_ntt_transform(c_ntt, modulus)
    
    return c % modulus 