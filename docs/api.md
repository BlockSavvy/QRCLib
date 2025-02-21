# QRCLib API Documentation

## Table of Contents

- [Kyber Module](#kyber-module)
- [Dilithium Module](#dilithium-module)
- [Utilities Module](#utilities-module)

## Kyber Module

The Kyber module implements the Kyber key encapsulation mechanism (KEM).

### Classes

#### `KyberParams`

Parameters for the Kyber algorithm.

```python
class KyberParams:
    def __init__(self, k: int = 3):
        """
        Initialize Kyber parameters.
        
        Args:
            k (int): Security parameter (2, 3, or 4 for Kyber-512, -768, -1024)
        """
```

### Functions

#### `generate_keys`

```python
def generate_keys(params: KyberParams = KyberParams()) -> Tuple[Dict, Dict]:
    """
    Generate a Kyber key pair.
    
    Args:
        params: Kyber parameters (optional)
    
    Returns:
        Tuple[Dict, Dict]: (public_key, private_key)
            public_key: {'A': ndarray, 't': ndarray}
            private_key: {'s': ndarray}
    """
```

#### `encapsulate`

```python
def encapsulate(public_key: Dict, params: KyberParams = KyberParams()) -> Tuple[Dict, bytes]:
    """
    Encapsulate a shared secret using a public key.
    
    Args:
        public_key: Recipient's public key
        params: Kyber parameters (optional)
    
    Returns:
        Tuple[Dict, bytes]: (ciphertext, shared_secret)
    """
```

#### `decapsulate`

```python
def decapsulate(ciphertext: Dict, private_key: Dict, params: KyberParams = KyberParams()) -> bytes:
    """
    Decapsulate a shared secret using a private key.
    
    Args:
        ciphertext: The encapsulated secret
        private_key: Recipient's private key
        params: Kyber parameters (optional)
    
    Returns:
        bytes: The shared secret
    """
```

## Dilithium Module

The Dilithium module implements the Dilithium digital signature scheme.

### Classes

#### `DilithiumParams`

Parameters for the Dilithium algorithm.

```python
class DilithiumParams:
    def __init__(self):
        """Initialize Dilithium parameters (security level 2)."""
```

### Functions

#### `generate_keys`

```python
def generate_keys(params: DilithiumParams = DilithiumParams()) -> Tuple[Dict, Dict]:
    """
    Generate a Dilithium key pair.
    
    Args:
        params: Dilithium parameters (optional)
    
    Returns:
        Tuple[Dict, Dict]: (signing_key, verification_key)
            signing_key: {'rho': bytes, 'key_seed': bytes, 'A': ndarray, 
                         's1': ndarray, 's2': ndarray, 't': ndarray}
            verification_key: {'rho': bytes, 'key_seed': bytes, 'A': ndarray, 't': ndarray}
    """
```

#### `sign`

```python
def sign(signing_key: Dict, message: bytes, params: DilithiumParams = DilithiumParams()) -> bytes:
    """
    Sign a message using the Dilithium signature scheme.
    
    Args:
        signing_key: The signer's private key
        message: The message to sign
        params: Dilithium parameters (optional)
    
    Returns:
        bytes: The signature
    
    Raises:
        ValueError: If message is None or not bytes
    """
```

#### `verify`

```python
def verify(verification_key: Dict, message: bytes, signature: bytes,
          params: DilithiumParams = DilithiumParams()) -> bool:
    """
    Verify a Dilithium signature.
    
    Args:
        verification_key: The signer's public key
        message: The message that was signed
        signature: The signature to verify
        params: Dilithium parameters (optional)
    
    Returns:
        bool: True if the signature is valid, False otherwise
    """
```

## Utilities Module

The utilities module provides common cryptographic operations used by both Kyber and Dilithium.

### Functions

#### `secure_random_bytes`

```python
def secure_random_bytes(n: int) -> bytes:
    """
    Generate cryptographically secure random bytes.
    
    Args:
        n: Number of bytes to generate
    
    Returns:
        bytes: Random bytes
    """
```

#### `secure_random_int`

```python
def secure_random_int(min_val: int, max_val: int) -> int:
    """
    Generate a cryptographically secure random integer.
    
    Args:
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)
    
    Returns:
        int: Random integer in [min_val, max_val]
    """
```

#### `ntt_transform`

```python
def ntt_transform(polynomial: np.ndarray, modulus: int, inverse: bool = False) -> np.ndarray:
    """
    Perform Number Theoretic Transform (NTT) on a polynomial.
    
    Args:
        polynomial: Coefficient array of the polynomial
        modulus: The modulus for the finite field
        inverse: Whether to perform inverse NTT
    
    Returns:
        np.ndarray: Transformed polynomial coefficients
    
    Raises:
        ValueError: If polynomial length is not a power of 2
    """
```

#### `polynomial_multiply`

```python
def polynomial_multiply(a: np.ndarray, b: np.ndarray, modulus: int, n: int = 256) -> np.ndarray:
    """
    Multiply two polynomials in R_q = Z_q[X]/(X^n + 1) using NTT.
    
    Args:
        a: First polynomial coefficients
        b: Second polynomial coefficients
        modulus: Modulus for coefficient reduction
        n: Degree of X^n + 1 (default: 256)
    
    Returns:
        np.ndarray: Resulting polynomial coefficients modulo q
    """
```

#### `constant_time_compare`

```python
def constant_time_compare(a: bytes, b: bytes) -> bool:
    """
    Compare two byte strings in constant time to prevent timing attacks.
    
    Args:
        a: First byte string
        b: Second byte string
    
    Returns:
        bool: True if the strings are equal, False otherwise
    """
```
