"""
Secure Messaging Example using QRCLib

This example demonstrates how to implement end-to-end encrypted messaging
using quantum-resistant cryptography. It features:

1. Secure session establishment using Kyber
2. Message signing with Dilithium
3. Forward secrecy through session key rotation
4. Message integrity verification

The example shows how to:
- Create secure messaging sessions
- Establish shared secrets
- Sign and verify messages
- Implement forward secrecy
"""

import json
import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from src.kyber import generate_keys as kyber_keygen, encapsulate, decapsulate
from src.dilithium import generate_keys as dilithium_keygen, sign, verify
from src.utils import secure_random_bytes

@dataclass
class SecureMessage:
    """
    Represents an encrypted message with metadata.
    
    Features:
    - Message encryption using session key
    - Dilithium signature for authenticity
    - Message chaining for forward secrecy
    - Timestamp for ordering
    """
    sender_id: str
    recipient_id: str
    ciphertext: bytes
    signature: bytes
    timestamp: str
    message_id: str
    previous_message_id: Optional[str] = None
    nonce: bytes = None

class SecureMessagingSession:
    """
    Implements end-to-end encrypted messaging with quantum resistance.
    
    Features:
    - Kyber for key exchange
    - Dilithium for message signing
    - Session key rotation
    - Forward secrecy
    """
    
    def __init__(self, user_id: str):
        """
        Initialize a secure messaging session.
        
        Args:
            user_id: Unique identifier for the user
        """
        self.user_id = user_id
        
        # Generate long-term identity keys
        self.enc_public_key, self.enc_private_key = kyber_keygen()
        self.sign_private_key, self.sign_public_key = dilithium_keygen()
        
        # Session state
        self.sessions: Dict[str, Dict] = {}
        self.message_chain: Dict[str, str] = {}
    
    def get_public_keys(self) -> Dict[str, bytes]:
        """Get the user's public keys."""
        return {
            'enc_public_key': self.enc_public_key,
            'sign_public_key': self.sign_public_key
        }
    
    def initiate_session(self, recipient_keys: Dict[str, bytes]) -> Dict:
        """
        Initiate a secure session with another user.
        
        Args:
            recipient_keys: Recipient's public keys
        
        Returns:
            Session initialization data
        """
        # Generate session key and encapsulate it
        session_key = secure_random_bytes(32)
        ciphertext, shared_secret = encapsulate(
            recipient_keys['enc_public_key'],
            session_key
        )
        
        # Create session data
        session_id = secure_random_bytes(16).hex()
        timestamp = datetime.utcnow().isoformat()
        
        # Sign session data
        signature = sign(
            self.sign_private_key,
            f"{session_id}:{timestamp}".encode()
        )
        
        # Store session with shared secret
        self.sessions[session_id] = {
            'key': shared_secret,  # Use shared secret as session key
            'recipient_keys': recipient_keys,
            'established': True
        }
        
        return {
            'session_id': session_id,
            'timestamp': timestamp,
            'ciphertext': ciphertext,
            'signature': signature
        }
    
    def accept_session(self, sender_keys: Dict[str, bytes],
                      session_data: Dict) -> None:
        """
        Accept a session initiated by another user.
        
        Args:
            sender_keys: Sender's public keys
            session_data: Session initialization data
        
        Raises:
            ValueError: If session data is invalid
        """
        # Verify session signature
        if not verify(
            sender_keys['sign_public_key'],
            f"{session_data['session_id']}:{session_data['timestamp']}".encode(),
            session_data['signature']
        ):
            raise ValueError("Invalid session signature")
        
        # Decrypt session key to get shared secret
        shared_secret = decapsulate(
            session_data['ciphertext'],
            self.enc_private_key
        )
        
        # Store session with shared secret
        self.sessions[session_data['session_id']] = {
            'key': shared_secret,  # Use shared secret as session key
            'sender_keys': sender_keys,
            'established': True
        }
        
        # Mark session as established for both parties
        if session_data['session_id'] not in self.sessions:
            self.sessions[session_data['session_id']] = {
                'key': shared_secret,
                'sender_keys': sender_keys,
                'established': True
            }
        else:
            self.sessions[session_data['session_id']]['established'] = True
    
    def encrypt_message(self, message: str, session_id: Optional[str] = None) -> SecureMessage:
        """
        Encrypt and sign a message.
        
        Args:
            message: Message to encrypt
            session_id: Optional session ID (uses latest if not specified)
        
        Returns:
            Encrypted and signed message
        
        Raises:
            ValueError: If no session exists
        """
        if not session_id:
            if not self.sessions:
                raise ValueError("No active session")
            session_id = list(self.sessions.keys())[-1]
        
        session = self.sessions[session_id]
        if not session['established']:
            raise ValueError("Session not established")
        
        # Generate message ID and get previous
        message_id = secure_random_bytes(16).hex()
        previous_id = self.message_chain.get(session_id)
        
        # Encrypt message
        message_bytes = message.encode()
        nonce = secure_random_bytes(12)
        
        # Use AESGCM for encryption
        cipher = AESGCM(session['key'])
        ciphertext = cipher.encrypt(nonce, message_bytes, None)
        
        # Create message object
        secure_message = SecureMessage(
            sender_id=self.user_id,
            recipient_id=session_id,
            ciphertext=ciphertext,
            signature=sign(
                self.sign_private_key,
                ciphertext
            ),
            timestamp=datetime.utcnow().isoformat(),
            message_id=message_id,
            previous_message_id=previous_id,
            nonce=nonce
        )
        
        # Update message chain
        self.message_chain[session_id] = message_id
        
        return secure_message
    
    def decrypt_message(self, message: SecureMessage) -> str:
        """
        Decrypt and verify a message.
        
        Args:
            message: Encrypted message to decrypt
        
        Returns:
            Decrypted message text
        
        Raises:
            ValueError: If message is invalid or session doesn't exist
        """
        session = self.sessions.get(message.recipient_id)
        if not session:
            raise ValueError("Session not found")
        
        # Verify message chain
        if message.previous_message_id != self.message_chain.get(message.recipient_id):
            raise ValueError("Invalid message chain")
        
        # Verify signature before decryption
        if not verify(
            session['sender_keys']['sign_public_key'],
            message.ciphertext,
            message.signature
        ):
            raise ValueError("Invalid message signature")
        
        # Decrypt message using AESGCM
        cipher = AESGCM(session['key'])
        try:
            plaintext = cipher.decrypt(message.nonce, message.ciphertext, None)
        except Exception:
            raise ValueError("Decryption failed")
        
        # Update message chain
        self.message_chain[message.recipient_id] = message.message_id
        
        # Rotate session key after successful decryption
        session['key'] = hashlib.sha256(session['key']).digest()
        
        return plaintext.decode()
    
    def is_session_established(self) -> bool:
        """Check if any session is established."""
        return any(s.get('established', False) for s in self.sessions.values())

def main():
    """
    Demonstrate the secure messaging implementation.
    
    This example shows:
    1. Creating secure messaging sessions
    2. Establishing shared secrets
    3. Sending encrypted messages
    4. Message verification
    5. Forward secrecy
    """
    print("Quantum-Resistant Secure Messaging Example")
    print("----------------------------------------")
    
    # Create users
    print("\n1. Creating users Alice and Bob...")
    alice = SecureMessagingSession("alice")
    bob = SecureMessagingSession("bob")
    print("   ✓ Users created successfully")
    
    # Establish session
    print("\n2. Establishing secure session...")
    init_data = alice.initiate_session(bob.get_public_keys())
    bob.accept_session(alice.get_public_keys(), init_data)
    print("   ✓ Session established successfully")
    
    # Send messages
    print("\n3. Exchanging encrypted messages...")
    
    # Alice sends message
    message1 = "Hello Bob! This is a secret message."
    encrypted1 = alice.encrypt_message(message1)
    decrypted1 = bob.decrypt_message(encrypted1)
    print("   Alice -> Bob:")
    print(f"   Original: {message1}")
    print(f"   Decrypted: {decrypted1}")
    
    # Bob replies
    message2 = "Hi Alice! Your secret is safe with me."
    encrypted2 = bob.encrypt_message(message2)
    decrypted2 = alice.decrypt_message(encrypted2)
    print("\n   Bob -> Alice:")
    print(f"   Original: {message2}")
    print(f"   Decrypted: {decrypted2}")
    
    print("\n✓ Example completed successfully")
    print("\nThis example demonstrated:")
    print("- Quantum-resistant session establishment")
    print("- End-to-end encryption")
    print("- Message integrity verification")
    print("- Forward secrecy through key rotation")

if __name__ == "__main__":
    main() 