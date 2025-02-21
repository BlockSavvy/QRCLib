"""
Tests for the secure file storage example.

This test suite verifies:
1. User management (creation, key generation)
2. File operations (storing, sharing, reading)
3. Security features (encryption, signatures, access control)
4. Error handling and edge cases
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

from examples.secure_file_storage import SecureFileStorage, FileMetadata

class TestSecureFileStorage(unittest.TestCase):
    """Test suite for the SecureFileStorage class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create temporary directory for storage
        self.temp_dir = tempfile.mkdtemp()
        self.storage = SecureFileStorage(self.temp_dir)
        
        # Create test users
        self.alice_keys = self.storage.create_user("alice")
        self.bob_keys = self.storage.create_user("bob")
        self.charlie_keys = self.storage.create_user("charlie")
        
        # Create test file
        self.test_file = Path(self.temp_dir) / "test.txt"
        self.test_content = "This is a test file."
        self.test_file.write_text(self.test_content)
    
    def tearDown(self):
        """Clean up after each test."""
        shutil.rmtree(self.temp_dir)
    
    def test_user_creation(self):
        """Test user creation and key generation."""
        # Test duplicate user
        with self.assertRaises(ValueError):
            self.storage.create_user("alice")
        
        # Verify key structure
        self.assertIn("enc_public_key", self.alice_keys)
        self.assertIn("sign_public_key", self.alice_keys)
        
        # Verify private keys are stored but not returned
        self.assertIn("enc_private_key", self.storage.users["alice"])
        self.assertIn("sign_private_key", self.storage.users["alice"])
    
    def test_file_storage(self):
        """Test storing files securely."""
        # Store file
        metadata = self.storage.store_file("alice", str(self.test_file))
        
        # Verify metadata
        self.assertEqual(metadata.owner_id, "alice")
        self.assertEqual(metadata.filename, "test.txt")
        self.assertEqual(metadata.size_bytes, len(self.test_content))
        self.assertEqual(metadata.shared_with, [])
        
        # Verify files are created
        self.assertTrue((Path(self.temp_dir) / "files" / metadata.file_id).exists())
        self.assertTrue((Path(self.temp_dir) / "metadata" / metadata.file_id).exists())
        self.assertTrue((Path(self.temp_dir) / "keys" / metadata.encryption_key_id).exists())
    
    def test_file_sharing(self):
        """Test secure file sharing between users."""
        # Store file as Alice
        metadata = self.storage.store_file("alice", str(self.test_file))
        
        # Share with Bob
        self.storage.share_file(metadata.file_id, "alice", "bob")
        
        # Verify Bob can read
        content = self.storage.read_file(metadata.file_id, "bob")
        self.assertEqual(content.decode(), self.test_content)
        
        # Verify Charlie cannot read
        with self.assertRaises(ValueError):
            self.storage.read_file(metadata.file_id, "charlie")
    
    def test_file_integrity(self):
        """Test file integrity verification."""
        # Store file
        metadata = self.storage.store_file("alice", str(self.test_file))
        
        # Tamper with metadata file
        metadata_path = Path(self.temp_dir) / "metadata" / metadata.file_id
        metadata_dict = self.storage._metadata_to_dict(metadata)
        metadata_dict["filename"] = "tampered.txt"
        metadata_path.write_text("tampered data")
        
        # Verify reading fails
        with self.assertRaises(ValueError):
            self.storage.read_file(metadata.file_id, "alice")
    
    def test_access_control(self):
        """Test access control enforcement."""
        # Store file as Alice
        metadata = self.storage.store_file("alice", str(self.test_file))
        
        # Verify only Alice can share
        with self.assertRaises(ValueError):
            self.storage.share_file(metadata.file_id, "bob", "charlie")
        
        # Share with Bob
        self.storage.share_file(metadata.file_id, "alice", "bob")
        
        # Verify Bob cannot share
        with self.assertRaises(ValueError):
            self.storage.share_file(metadata.file_id, "bob", "charlie")
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Test invalid user
        with self.assertRaises(ValueError):
            self.storage.store_file("invalid_user", str(self.test_file))
        
        # Test invalid file
        with self.assertRaises(ValueError):
            self.storage.store_file("alice", "nonexistent.txt")
        
        # Test invalid file ID
        with self.assertRaises(ValueError):
            self.storage.read_file("invalid_id", "alice")
        
        # Test sharing with invalid user
        metadata = self.storage.store_file("alice", str(self.test_file))
        with self.assertRaises(ValueError):
            self.storage.share_file(metadata.file_id, "alice", "invalid_user")
    
    def test_file_metadata(self):
        """Test file metadata handling."""
        # Create file with metadata
        metadata = self.storage.store_file("alice", str(self.test_file))
        
        # Test metadata serialization
        serialized = metadata.serialize()
        self.assertIsInstance(serialized, bytes)
        
        # Test metadata verification
        loaded_metadata = self.storage._load_metadata(metadata.file_id)
        self.assertEqual(loaded_metadata.file_id, metadata.file_id)
        self.assertEqual(loaded_metadata.owner_id, metadata.owner_id)
        self.assertEqual(loaded_metadata.filename, metadata.filename)
    
    def test_multiple_shares(self):
        """Test sharing file with multiple users."""
        # Store file
        metadata = self.storage.store_file("alice", str(self.test_file))
        
        # Share with multiple users
        self.storage.share_file(metadata.file_id, "alice", "bob")
        self.storage.share_file(metadata.file_id, "alice", "charlie")
        
        # Verify both can read
        bob_content = self.storage.read_file(metadata.file_id, "bob")
        charlie_content = self.storage.read_file(metadata.file_id, "charlie")
        
        self.assertEqual(bob_content.decode(), self.test_content)
        self.assertEqual(charlie_content.decode(), self.test_content)
    
    def test_duplicate_share(self):
        """Test sharing file multiple times with same user."""
        # Store and share file
        metadata = self.storage.store_file("alice", str(self.test_file))
        self.storage.share_file(metadata.file_id, "alice", "bob")
        
        # Share again (should not raise error)
        self.storage.share_file(metadata.file_id, "alice", "bob")
        
        # Verify Bob can still read
        content = self.storage.read_file(metadata.file_id, "bob")
        self.assertEqual(content.decode(), self.test_content)
    
    def test_large_file(self):
        """Test handling of larger files."""
        # Create large test file (1MB)
        large_content = b"x" * (1024 * 1024)
        large_file = Path(self.temp_dir) / "large.bin"
        large_file.write_bytes(large_content)
        
        # Store and verify
        metadata = self.storage.store_file("alice", str(large_file))
        content = self.storage.read_file(metadata.file_id, "alice")
        
        self.assertEqual(len(content), len(large_content))
        self.assertEqual(content, large_content)

if __name__ == "__main__":
    unittest.main() 