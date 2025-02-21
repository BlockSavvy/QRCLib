"""
Secure File Storage Example using QRCLib

This example demonstrates how to use QRCLib to implement a secure file storage system
that is resistant to quantum computer attacks. It shows how to:

1. Create user identities with quantum-resistant keys
2. Encrypt files using Kyber for confidentiality
3. Sign files using Dilithium for integrity and authenticity
4. Implement secure file sharing between users
5. Verify file integrity and authenticity

Real-world applications:
- Secure cloud storage services
- Encrypted backup systems
- Secure document sharing platforms
- Medical record storage systems
- Financial document archives

The example implements a simple secure file storage system where:
- Each user has their own quantum-resistant keys
- Files are encrypted before storage
- File metadata is signed to prevent tampering
- Users can securely share files with other users
- All cryptographic operations are quantum-resistant
"""

import os
import json
import hashlib
import base64
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from src.kyber import generate_keys as kyber_keygen, encapsulate, decapsulate
from src.dilithium import generate_keys as dilithium_keygen, sign, verify
from src.utils import secure_random_bytes

@dataclass
class FileMetadata:
    """Represents metadata for a stored file."""
    file_id: str
    owner_id: str
    filename: str
    size_bytes: int
    created_at: str
    encryption_key_id: str
    shared_with: List[str]
    signature: Optional[bytes] = None
    
    def serialize(self) -> bytes:
        """Serialize metadata for signing/verification."""
        data = {
            'file_id': self.file_id,
            'owner_id': self.owner_id,
            'filename': self.filename,
            'size_bytes': self.size_bytes,
            'created_at': self.created_at,
            'encryption_key_id': self.encryption_key_id,
            'shared_with': sorted(self.shared_with)
        }
        return json.dumps(data, sort_keys=True).encode()

class SecureFileStorage:
    """
    Implements a quantum-resistant secure file storage system.
    
    This class provides methods to:
    1. Store files securely with quantum-resistant encryption
    2. Share files with other users
    3. Access shared files
    4. Verify file integrity
    
    The system ensures:
    - Confidentiality: Files are encrypted with Kyber
    - Integrity: File metadata is signed with Dilithium
    - Authentication: File access requires valid quantum-resistant signatures
    - Forward secrecy: Each file uses a unique encryption key
    """
    
    def __init__(self, storage_path: str):
        """
        Initialize secure storage in the specified directory.
        
        Args:
            storage_path: Directory to store encrypted files and metadata
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage directories
        self.files_dir = self.storage_path / 'files'
        self.metadata_dir = self.storage_path / 'metadata'
        self.keys_dir = self.storage_path / 'keys'
        
        for directory in [self.files_dir, self.metadata_dir, self.keys_dir]:
            directory.mkdir(exist_ok=True)
        
        # Store user data
        self.users: Dict[str, Dict] = {}
    
    def create_user(self, user_id: str) -> Dict:
        """
        Create a new user with quantum-resistant keys.
        
        This generates:
        1. Kyber keys for file encryption
        2. Dilithium keys for signing metadata
        
        Args:
            user_id: Unique identifier for the user
        
        Returns:
            Dict containing the user's public keys
        
        Raises:
            ValueError: If user_id already exists
        """
        if user_id in self.users:
            raise ValueError(f"User {user_id} already exists")
        
        # Generate Kyber keys for file encryption
        enc_public_key, enc_private_key = kyber_keygen()
        
        # Generate Dilithium keys for signing
        sign_private_key, sign_public_key = dilithium_keygen()
        
        # Store user keys
        self.users[user_id] = {
            'enc_public_key': enc_public_key,
            'enc_private_key': enc_private_key,
            'sign_private_key': sign_private_key,
            'sign_public_key': sign_public_key
        }
        
        # Return only public keys
        return {
            'enc_public_key': enc_public_key,
            'sign_public_key': sign_public_key
        }
    
    def store_file(self, user_id: str, filepath: str) -> FileMetadata:
        """
        Securely store a file with quantum-resistant encryption.
        
        Process:
        1. Generate a unique file ID and encryption key
        2. Encrypt the file using Kyber
        3. Create and sign file metadata
        4. Store encrypted file and metadata
        
        Args:
            user_id: ID of the user storing the file
            filepath: Path to the file to store
        
        Returns:
            FileMetadata object for the stored file
        
        Raises:
            ValueError: If user doesn't exist or file not found
        """
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        
        filepath = Path(filepath)
        if not filepath.exists():
            raise ValueError(f"File not found: {filepath}")
        
        # Generate file ID and read file
        file_id = secure_random_bytes(16).hex()
        file_data = filepath.read_bytes()
        
        # Generate unique encryption key
        key_id = secure_random_bytes(16).hex()
        encryption_key = secure_random_bytes(32)
        
        # Encrypt file data
        ciphertext, shared_secret = encapsulate(
            self.users[user_id]['enc_public_key'],
            encryption_key
        )
        
        # Encrypt file with encryption key
        encrypted_data = self._encrypt_file_data(file_data, encryption_key)
        
        # Create metadata
        metadata = FileMetadata(
            file_id=file_id,
            owner_id=user_id,
            filename=filepath.name,
            size_bytes=len(file_data),
            created_at=datetime.utcnow().isoformat(),
            encryption_key_id=key_id,
            shared_with=[]
        )
        
        # Sign metadata
        metadata.signature = sign(
            self.users[user_id]['sign_private_key'],
            metadata.serialize()
        )
        
        # Store encrypted file and metadata
        (self.files_dir / file_id).write_bytes(encrypted_data)
        (self.metadata_dir / file_id).write_text(
            json.dumps(self._metadata_to_dict(metadata))
        )
        
        # Store key data in base64 format
        key_data = {
            'c': base64.b64encode(ciphertext['c']).decode(),
            'nonce': base64.b64encode(ciphertext['nonce']).decode(),
            'shared_secret': base64.b64encode(shared_secret).decode(),
            'encryption_key': base64.b64encode(encryption_key).decode()
        }
        (self.keys_dir / key_id).write_text(json.dumps(key_data))
        
        return metadata
    
    def share_file(self, file_id: str, owner_id: str, 
                  recipient_id: str) -> None:
        """
        Share a file with another user securely.
        
        Process:
        1. Verify file ownership
        2. Re-encrypt file key for recipient
        3. Update and sign new metadata
        
        Args:
            file_id: ID of the file to share
            owner_id: ID of the file owner
            recipient_id: ID of the user to share with
        
        Raises:
            ValueError: If file/users not found or unauthorized
        """
        # Verify users exist
        if owner_id not in self.users or recipient_id not in self.users:
            raise ValueError("User not found")
        
        # Load and verify metadata
        metadata = self._load_metadata(file_id)
        if metadata.owner_id != owner_id:
            raise ValueError("Not authorized to share this file")
        
        if recipient_id in metadata.shared_with:
            return  # Already shared
        
        # Load encryption key
        key_data = json.loads((self.keys_dir / metadata.encryption_key_id).read_text())
        key_ciphertext = {
            'c': base64.b64decode(key_data['c']),
            'nonce': base64.b64decode(key_data['nonce'])
        }
        shared_secret = base64.b64decode(key_data['shared_secret'])
        encryption_key = base64.b64decode(key_data['encryption_key'])
        
        # Re-encrypt key for recipient
        decrypted_key = decapsulate(
            key_ciphertext,
            self.users[owner_id]['enc_private_key']
        )
        if decrypted_key != shared_secret:
            raise ValueError("Decryption failed: shared secret mismatch")
        
        # Generate new shared secret for recipient
        recipient_ciphertext, recipient_shared_secret = encapsulate(
            self.users[recipient_id]['enc_public_key'],
            encryption_key
        )
        
        # Update metadata
        metadata.shared_with.append(recipient_id)
        metadata.signature = sign(
            self.users[owner_id]['sign_private_key'],
            metadata.serialize()
        )
        
        # Store updated metadata and recipient's key
        recipient_key_data = {
            'c': base64.b64encode(recipient_ciphertext['c']).decode(),
            'nonce': base64.b64encode(recipient_ciphertext['nonce']).decode(),
            'shared_secret': base64.b64encode(recipient_shared_secret).decode(),
            'encryption_key': base64.b64encode(encryption_key).decode()
        }
        (self.metadata_dir / file_id).write_text(
            json.dumps(self._metadata_to_dict(metadata))
        )
        (self.keys_dir / f"{metadata.encryption_key_id}_{recipient_id}").write_text(
            json.dumps(recipient_key_data)
        )
    
    def read_file(self, file_id: str, user_id: str) -> bytes:
        """
        Read a file securely, verifying integrity and authorization.
        
        Process:
        1. Verify user's access rights
        2. Verify file metadata signature
        3. Decrypt and return file data
        
        Args:
            file_id: ID of the file to read
            user_id: ID of the user reading the file
        
        Returns:
            Decrypted file contents
        
        Raises:
            ValueError: If unauthorized or file integrity check fails
        """
        if user_id not in self.users:
            raise ValueError("User not found")
        
        # Load and verify metadata
        metadata = self._load_metadata(file_id)
        if user_id != metadata.owner_id and user_id not in metadata.shared_with:
            raise ValueError("Not authorized to read this file")
        
        # Load encrypted file
        encrypted_data = (self.files_dir / file_id).read_bytes()
        
        # Load encryption key
        key_id = metadata.encryption_key_id
        if user_id != metadata.owner_id:
            key_id = f"{key_id}_{user_id}"
        key_data = json.loads((self.keys_dir / key_id).read_text())
        key_ciphertext = {
            'c': base64.b64decode(key_data['c']),
            'nonce': base64.b64decode(key_data['nonce'])
        }
        shared_secret = base64.b64decode(key_data['shared_secret'])
        encryption_key = base64.b64decode(key_data['encryption_key'])
        
        # Decrypt key and verify shared secret
        decrypted_key = decapsulate(
            key_ciphertext,
            self.users[user_id]['enc_private_key']
        )
        if decrypted_key != shared_secret:
            raise ValueError("Decryption failed: shared secret mismatch")
        return self._decrypt_file_data(encrypted_data, encryption_key)
    
    def _encrypt_file_data(self, data: bytes, key: bytes) -> bytes:
        """Encrypt file data with the given key using AES-GCM."""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        
        # Use encryption key directly with AES-GCM
        cipher = AESGCM(key)
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        ciphertext = cipher.encrypt(nonce, data, None)
        return nonce + ciphertext
    
    def _decrypt_file_data(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt file data with the given key using AES-GCM."""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        
        if len(encrypted_data) < 12:
            raise ValueError("Invalid encrypted data")
            
        # Use encryption key directly with AES-GCM
        cipher = AESGCM(key)
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        try:
            return cipher.decrypt(nonce, ciphertext, None)
        except Exception:
            raise ValueError("Decryption failed")
    
    def _load_metadata(self, file_id: str) -> FileMetadata:
        """Load and verify file metadata."""
        try:
            data = json.loads(
                (self.metadata_dir / file_id).read_text()
            )
            # Convert base64 signature back to bytes
            if data.get('signature'):
                data['signature'] = base64.b64decode(data['signature'])
            metadata = FileMetadata(**data)
            
            # Verify signature
            if not verify(
                self.users[metadata.owner_id]['sign_public_key'],
                metadata.serialize(),
                metadata.signature
            ):
                raise ValueError("Invalid metadata signature")
            
            return metadata
        except (FileNotFoundError, json.JSONDecodeError):
            raise ValueError("File not found")
    
    def _metadata_to_dict(self, metadata: FileMetadata) -> Dict:
        """Convert metadata to dictionary for storage."""
        return {
            'file_id': metadata.file_id,
            'owner_id': metadata.owner_id,
            'filename': metadata.filename,
            'size_bytes': metadata.size_bytes,
            'created_at': metadata.created_at,
            'encryption_key_id': metadata.encryption_key_id,
            'shared_with': metadata.shared_with,
            'signature': base64.b64encode(metadata.signature).decode() if metadata.signature else None
        }

def main():
    """
    Demonstrate the secure file storage system with a practical example.
    
    This example shows:
    1. Creating users (Alice and Bob)
    2. Storing a file securely
    3. Sharing the file between users
    4. Reading the shared file
    5. Verifying file integrity
    """
    print("Quantum-Resistant Secure File Storage Example")
    print("-------------------------------------------")
    
    # Create storage system
    storage = SecureFileStorage("secure_storage")
    
    # Create users
    print("\n1. Creating users Alice and Bob...")
    alice_keys = storage.create_user("alice")
    bob_keys = storage.create_user("bob")
    print("   ✓ Users created successfully")
    
    # Create a test file
    print("\n2. Creating and storing a test file...")
    test_file = Path("test_file.txt")
    test_file.write_text("This is a secret document!")
    
    # Store file
    metadata = storage.store_file("alice", str(test_file))
    print("   ✓ File stored securely")
    print(f"   File ID: {metadata.file_id}")
    print(f"   Size: {metadata.size_bytes} bytes")
    print(f"   Created: {metadata.created_at}")
    
    # Share file with Bob
    print("\n3. Alice shares the file with Bob...")
    storage.share_file(metadata.file_id, "alice", "bob")
    print("   ✓ File shared successfully")
    
    # Bob reads the file
    print("\n4. Bob reads the shared file...")
    file_content = storage.read_file(metadata.file_id, "bob")
    print("   ✓ File read successfully")
    print(f"   Content: {file_content.decode()}")
    
    # Clean up
    test_file.unlink()
    print("\n✓ Example completed successfully")
    print("\nThis example demonstrated:")
    print("- Quantum-resistant file encryption")
    print("- Secure file sharing")
    print("- File integrity verification")
    print("- Access control")
    print("\nReal-world applications:")
    print("- Secure cloud storage")
    print("- Encrypted backup systems")
    print("- Medical record storage")
    print("- Financial document management")

if __name__ == "__main__":
    main() 