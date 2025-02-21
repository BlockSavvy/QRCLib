# Implementation Details

## Overview

QRCLib implements two post-quantum cryptographic algorithms: Kyber for key encapsulation and Dilithium for digital signatures. This document provides detailed information about the implementation choices and mathematical background.

## Mathematical Background

### Polynomial Ring

Both Kyber and Dilithium operate in the polynomial ring \(R_q = \mathbb{Z}_q[X]/(X^n + 1)\) where:

- \(n\) is a power of 2 (256 for both algorithms)
- \(q\) is a prime modulus (3329 for Kyber, 8380417 for Dilithium)

### Number Theoretic Transform (NTT)

The library implements an efficient Number Theoretic Transform (NTT) for polynomial multiplication:

1. **Forward NTT**:
   - Input: Polynomial \(a(X) = \sum_{i=0}^{n-1} a_i X^i\)
   - Output: NTT coefficients \(A = \text{NTT}(a)\)
   - Uses Cooley-Tukey butterfly operations
   - Time complexity: \(O(n \log n)\)

2. **Inverse NTT**:
   - Input: NTT coefficients \(A\)
   - Output: Polynomial coefficients \(a = \text{NTT}^{-1}(A)\)
   - Includes scaling by \(n^{-1} \bmod q\)
   - Same complexity as forward NTT

3. **Polynomial Multiplication**:
   - Compute \(c = a \cdot b \bmod (X^n + 1)\) as:
   - \(C = \text{NTT}(a) \odot \text{NTT}(b)\)
   - \(c = \text{NTT}^{-1}(C)\)
   - Where \(\odot\) is pointwise multiplication

## Kyber Implementation

### Key Generation

1. **Parameters**:
   - \(k\): Security parameter (2, 3, or 4)
   - Matrix dimension: \(k \times k\)
   - Polynomial degree: \(n = 256\)
   - Modulus: \(q = 3329\)

2. **Process**:

   ```python
   def generate_keys(params):
       # Generate random matrix A
       A = generate_matrix(params.k, params.k, params.q)
       
       # Generate secret vector s
       s = generate_small_polynomials(params.k)
       
       # Compute public key t = As + e
       t = matrix_vector_multiply(A, s) + generate_error()
       
       return {'A': A, 't': t}, {'s': s}
   ```

### Encapsulation

1. **Input**: Public key \((A, t)\)
2. **Output**: Ciphertext and shared secret
3. **Process**:
   - Sample random vector \(r\)
   - Compute \(u = A^T r + e_1\)
   - Compute \(v = t^T r + e_2 + \text{encode}(m)\)
   - Derive shared secret using KDF

### Decapsulation

1. **Input**: Ciphertext \((u, v)\) and private key \(s\)
2. **Process**:
   - Compute \(m' = \text{decode}(v - s^T u)\)
   - Verify ciphertext
   - Derive shared secret

## Dilithium Implementation

### Key Generation

1. **Parameters**:
   - Matrix dimension: \(k \times l\)
   - Polynomial degree: \(n = 256\)
   - Modulus: \(q = 8380417\)

2. **Process**:

   ```python
   def generate_keys(params):
       # Generate seed and expand to matrix A
       rho = secure_random_bytes(32)
       A = expand_matrix(rho)
       
       # Generate secret vectors s1, s2
       s1 = sample_in_ball(params.l)
       s2 = sample_in_ball(params.k)
       
       # Compute t = As1 + s2
       t = matrix_vector_multiply(A, s1) + s2
       
       return {
           'rho': rho,
           'A': A,
           's1': s1,
           's2': s2,
           't': t
       }, {
           'rho': rho,
           'A': A,
           't': t
       }
   ```

### Signature Generation

1. **Process**:
   - Sample \(y\) from appropriate distribution
   - Compute \(w = Ay\)
   - Generate challenge \(c\) using message and \(w\)
   - Compute \(z = y + cs_1\)
   - If \(z\) is too large, restart
   - Compute hint \(h\) for verification

2. **Implementation**:

   ```python
   def sign(signing_key, message):
       while True:
           # Sample y uniformly at random
           y = sample_uniform()
           
           # Compute w = Ay
           w = matrix_vector_multiply(A, y)
           
           # Generate challenge c
           c = generate_challenge(message, w)
           
           # Compute z = y + cs1
           z = y + multiply(c, signing_key['s1'])
           
           # Check if z is within bounds
           if not is_small_enough(z):
               continue
               
           # Compute hint h
           h = compute_hint(c, signing_key['s2'])
           
           return pack_signature(z, h)
   ```

### Signature Verification

1. **Process**:
   - Unpack signature into \(z\) and \(h\)
   - Check norm bounds
   - Compute \(w' = Az - ct\)
   - Verify challenge computation

2. **Implementation**:

   ```python
   def verify(verification_key, message, signature):
       # Unpack signature
       z, h = unpack_signature(signature)
       
       # Check bounds
       if not is_small_enough(z):
           return False
           
       # Compute w' = Az - ct
       w_prime = compute_w_prime(z, verification_key)
       
       # Verify challenge
       c = generate_challenge(message, w_prime)
       return verify_challenge(c, h)
   ```

## Core Utility Functions

### Constant-Time Operations

1. **Comparison**:

   ```python
   def constant_time_compare(a: bytes, b: bytes) -> bool:
       if len(a) != len(b):
           return False
       result = 0
       for x, y in zip(a, b):
           result |= x ^ y
       return result == 0
   ```

2. **Modular Reduction**:

   ```python
   def mod_q(x: int, q: int) -> int:
       return ((x % q) + q) % q
   ```

### Random Number Generation

1. **Secure Bytes**:

   ```python
   def secure_random_bytes(n: int) -> bytes:
       return secrets.token_bytes(n)
   ```

2. **Uniform Sampling**:

   ```python
   def sample_uniform(min_val: int, max_val: int) -> int:
       return secrets.randbelow(max_val - min_val + 1) + min_val
   ```

## Performance Considerations

1. **NTT Optimization**:
   - Pre-compute twiddle factors
   - Use bit-reversal permutation
   - Implement butterfly operations efficiently

2. **Memory Management**:
   - Reuse arrays where possible
   - Clear sensitive data after use
   - Use appropriate data types

3. **Vectorization**:
   - Leverage NumPy for matrix operations
   - Use vectorized operations where possible
   - Avoid Python loops in critical paths

## Future Improvements

1. **Optimization**:
   - Implement AVX2 optimizations via C extensions
   - Add parallel processing for large matrices
   - Optimize memory usage

2. **Features**:
   - Add support for additional parameter sets
   - Implement hybrid schemes
   - Add serialization formats

3. **Security**:
   - Add more side-channel protections
   - Implement constant-time polynomial arithmetic
   - Add formal verification
