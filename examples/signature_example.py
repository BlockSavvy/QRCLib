"""
Example of digital signatures using Dilithium.
"""

from src.dilithium import generate_keys, sign, verify

def main():
    print("Quantum-Resistant Digital Signature Example using Dilithium")
    print("-------------------------------------------------------")
    
    # Generate keys for Alice (signer)
    print("\n1. Alice generates her key pair...")
    signing_key, verification_key = generate_keys()
    print("   ✓ Keys generated successfully")
    
    # Create a message to sign
    message = b"Hello, quantum-resistant world!"
    print(f"\n2. Alice wants to sign the message: {message.decode()}")
    
    # Alice signs the message
    print("\n3. Alice signs the message...")
    signature = sign(signing_key, message)
    print("   ✓ Message signed successfully")
    print(f"   Signature length: {len(signature)} bytes")
    print(f"   First 16 bytes: {signature[:16].hex()}")
    
    # Bob verifies the signature
    print("\n4. Bob verifies the signature using Alice's verification key...")
    is_valid = verify(verification_key, message, signature)
    
    if is_valid:
        print("   ✓ Signature verified successfully!")
        print("   Bob can trust that this message came from Alice")
    else:
        print("   ✗ Signature verification failed!")
        print("   The message may have been tampered with")
    
    # Demonstrate signature verification failure
    print("\n5. Let's try to verify with a tampered message...")
    tampered_message = b"Hello, tampered world!"
    is_valid = verify(verification_key, tampered_message, signature)
    
    if not is_valid:
        print("   ✓ Tampering detected! Signature verification failed as expected")
    else:
        print("   ✗ Error: Signature verified despite message tampering")

if __name__ == "__main__":
    main() 