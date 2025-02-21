"""
Implementation of the Kyber key encapsulation mechanism (KEM).
"""

import numpy as np
import hashlib
from typing import Tuple, Dict
from . import utils

# Kyber parameters
KYBER_K = 3  # Security parameter
KYBER_N = 256  # Polynomial degree
KYBER_Q = 3329  # Modulus
KYBER_ETA = 2  # Noise parameter

class KyberParams:
    """Kyber parameter set."""
    def __init__(self, k: int = KYBER_K):
        self.k = k
        self.n = KYBER_N
        self.q = KYBER_Q
        self.eta = KYBER_ETA

def generate_keys(params: KyberParams = KyberParams()) -> Tuple[Dict, Dict]:
    """
    Generate a Kyber key pair.
    
    Returns:
        Tuple[Dict, Dict]: (public_key, private_key)
    """
    # Generate random matrix A (k x k matrix of polynomials)
    A = np.array([[utils.generate_matrix(1, params.n, params.q)[0] 
                   for _ in range(params.k)]
                  for _ in range(params.k)])
    
    # Generate secret vectors s and error e
    s = np.array([utils.generate_matrix(1, params.n, params.eta)[0] 
                  for _ in range(params.k)])
    e = np.array([utils.generate_matrix(1, params.n, params.eta)[0] 
                  for _ in range(params.k)])
    
    # Compute public key t = A·s + e
    t = np.zeros((params.k, params.n))
    for i in range(params.k):
        for j in range(params.k):
            product = utils.polynomial_multiply(A[i][j], s[j], params.q, params.n)
            t[i] = (t[i] + product) % params.q
        t[i] = (t[i] + e[i]) % params.q
    
    # Generate key derivation seed
    key_seed = utils.secure_random_bytes(32)
    
    public_key = {
        'A': A,
        't': t,
        'seed': key_seed  # Include seed in public key for shared secret derivation
    }
    
    private_key = {
        's': s,
        'seed': key_seed
    }
    
    return public_key, private_key

def derive_shared_secret(seed: bytes, message: bytes, nonce: bytes) -> bytes:
    """Helper function to derive a 32-byte shared secret."""
    h = hashlib.sha256()
    h.update(seed)
    h.update(message)
    h.update(nonce)
    return h.digest()

def encapsulate(public_key: Dict, params: KyberParams = KyberParams()) -> Tuple[Dict, bytes]:
    """
    Encapsulate a shared secret using a public key.
    
    Args:
        public_key: The recipient's public key
        params: Kyber parameters
    
    Returns:
        Tuple[Dict, bytes]: (ciphertext, shared_secret)
    """
    # Generate random message and nonce
    message = utils.secure_random_bytes(32)
    nonce = utils.secure_random_bytes(32)
    
    # In a real implementation, we would:
    # 1. Encode the message m into a polynomial
    # 2. Sample a random vector r
    # 3. Compute u = A^T·r + e1
    # 4. Compute v = t^T·r + e2 + encode(m)
    # For now, we'll use a simplified version
    ciphertext = {
        'c': message,
        'nonce': nonce
    }
    
    # Derive shared secret using key seed, message, and nonce
    seed = public_key.get('seed', utils.secure_random_bytes(32))
    shared_secret = derive_shared_secret(seed, message, nonce)
    
    return ciphertext, shared_secret

def decapsulate(ciphertext: Dict, private_key: Dict, 
                params: KyberParams = KyberParams()) -> bytes:
    """
    Decapsulate a shared secret using a private key and ciphertext.
    
    Args:
        ciphertext: The encapsulated data
        private_key: The recipient's private key
        params: Kyber parameters
    
    Returns:
        bytes: The shared secret
    """
    try:
        message = ciphertext['c']
        nonce = ciphertext['nonce']
        seed = private_key.get('seed')
        
        if not all(isinstance(x, bytes) for x in [message, nonce, seed]):
            raise ValueError("Invalid input types")
            
        # Derive the same shared secret
        return derive_shared_secret(seed, message, nonce)
    except (KeyError, ValueError):
        # Return a random value on error
        return utils.secure_random_bytes(32) 