"""
Example of key exchange using Kyber KEM.
"""

from src.kyber import generate_keys, encapsulate, decapsulate

def main():
    print("Quantum-Resistant Key Exchange Example using Kyber")
    print("------------------------------------------------")
    
    # Generate keys for Bob (recipient)
    print("\n1. Bob generates his key pair...")
    public_key, private_key = generate_keys()
    print("   ✓ Keys generated successfully")
    
    # Alice (sender) encapsulates a shared secret
    print("\n2. Alice encapsulates a shared secret using Bob's public key...")
    ciphertext, shared_secret_alice = encapsulate(public_key)
    print("   ✓ Secret encapsulated successfully")
    print(f"   Alice's shared secret (first 8 bytes): {shared_secret_alice[:8].hex()}")
    
    # Bob decapsulates to get the same shared secret
    print("\n3. Bob decapsulates the shared secret using his private key...")
    shared_secret_bob = decapsulate(ciphertext, private_key)
    print("   ✓ Secret decapsulated successfully")
    print(f"   Bob's shared secret (first 8 bytes): {shared_secret_bob[:8].hex()}")
    
    # Verify that both parties have the same shared secret
    if shared_secret_alice == shared_secret_bob:
        print("\n✓ Success! Both parties have derived the same shared secret")
    else:
        print("\n✗ Error: The shared secrets do not match")

if __name__ == "__main__":
    main() 