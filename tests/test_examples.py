"""
Tests for the example implementations.

This test suite verifies:
1. Blockchain example functionality
2. Secure messaging example
3. Web API example
4. Secure file storage example
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import json
import base64

from examples.blockchain_example import QuantumResistantWallet, QuantumResistantTransaction
from examples.secure_messaging import SecureMessagingSession
from examples.web_api_example import create_app, generate_user_keys, users, messages
from examples.secure_file_storage import SecureFileStorage, FileMetadata

class TestBlockchainExample(unittest.TestCase):
    """Test suite for the blockchain example."""
    
    def setUp(self):
        """Set up test environment."""
        self.alice = QuantumResistantWallet()
        self.bob = QuantumResistantWallet()
    
    def test_transaction_creation(self):
        """Test creating and signing transactions."""
        # Create transaction
        tx = QuantumResistantTransaction(
            sender=self.alice.address,
            recipient=self.bob.address,
            amount=100
        )
        
        # Sign transaction
        signed_tx = self.alice.sign_transaction(tx)
        
        # Verify transaction
        self.assertTrue(
            QuantumResistantTransaction.verify_transaction(signed_tx)
        )
    
    def test_invalid_transaction(self):
        """Test transaction verification with wrong signature."""
        # Create transaction with Bob as sender
        tx = QuantumResistantTransaction(
            sender=self.bob.address,
            recipient=self.alice.address,
            amount=100
        )
        
        # Try to sign with Alice's key (should fail)
        with self.assertRaises(ValueError):
            signed_tx = self.alice.sign_transaction(tx)
    
    def test_encrypted_messaging(self):
        """Test encrypted messaging between wallets."""
        # Send encrypted message
        message = "Hello Bob!"
        encrypted = self.alice.encrypt_message(
            self.bob.get_public_key(),
            message
        )
        
        # Decrypt message
        decrypted = self.bob.decrypt_message(
            self.alice.get_public_key(),
            encrypted
        )
        
        self.assertEqual(message, decrypted)

class TestSecureMessaging(unittest.TestCase):
    """Test suite for the secure messaging example."""
    
    def setUp(self):
        """Set up test environment."""
        self.alice = SecureMessagingSession("alice")
        self.bob = SecureMessagingSession("bob")
    
    def test_session_establishment(self):
        """Test establishing a secure session."""
        # Initialize session
        init_data = self.alice.initiate_session(
            self.bob.get_public_keys()
        )
        
        # Accept session
        self.bob.accept_session(
            self.alice.get_public_keys(),
            init_data
        )
        
        self.assertTrue(self.alice.is_session_established())
        self.assertTrue(self.bob.is_session_established())
    
    def test_message_exchange(self):
        """Test sending and receiving messages."""
        # Establish session
        init_data = self.alice.initiate_session(
            self.bob.get_public_keys()
        )
        self.bob.accept_session(
            self.alice.get_public_keys(),
            init_data
        )
        
        # Send message
        message = "Hello Bob!"
        encrypted = self.alice.encrypt_message(message)
        decrypted = self.bob.decrypt_message(encrypted)
        
        self.assertEqual(message, decrypted)

class TestWebAPI(unittest.TestCase):
    """Test suite for the web API example."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up test environment."""
        self.app_context.pop()
    
    def test_user_creation(self):
        """Test creating a new user."""
        # Clear existing users
        users.clear()
        messages.clear()
        
        response = self.client.post('/api/users', json={
            'user_id': 'alice'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['user_id'], 'alice')
        self.assertIn('enc_public_key', data)
        self.assertIn('sign_public_key', data)
    
    def test_duplicate_user(self):
        """Test creating a duplicate user."""
        # Create first user
        self.client.post('/api/users', json={
            'user_id': 'alice'
        })
        
        # Try to create duplicate
        response = self.client.post('/api/users', json={
            'user_id': 'alice'
        })
        
        self.assertEqual(response.status_code, 409)
    
    def test_get_public_keys(self):
        """Test retrieving public keys."""
        # Create user
        self.client.post('/api/users', json={
            'user_id': 'alice'
        })
        
        # Get keys
        response = self.client.get('/api/users/alice/keys')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('enc_public_key', data)
        self.assertIn('sign_public_key', data)
    
    def test_send_message(self):
        """Test sending an encrypted message."""
        # Create users
        self.client.post('/api/users', json={'user_id': 'alice'})
        self.client.post('/api/users', json={'user_id': 'bob'})
        
        # Create authentication
        timestamp = datetime.utcnow().isoformat()
        message = f"alice:{timestamp}".encode()
        signature = base64.b64encode(
            bytes.fromhex('deadbeef')  # Mock signature
        ).decode()
        auth = f"QR alice:{timestamp}:{signature}"
        
        # Send message
        response = self.client.post(
            '/api/messages',
            json={
                'recipient_id': 'bob',
                'message': 'Hello Bob!'
            },
            headers={'Authorization': auth}
        )
        
        self.assertEqual(response.status_code, 401)  # Should fail with mock signature

class TestSecureFileStorage(unittest.TestCase):
    """Test suite for the secure file storage example."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = SecureFileStorage(self.temp_dir)
        
        # Create test users
        self.alice_keys = self.storage.create_user("alice")
        self.bob_keys = self.storage.create_user("bob")
        
        # Create test file
        self.test_file = Path(self.temp_dir) / "test.txt"
        self.test_content = "This is a test file."
        self.test_file.write_text(self.test_content)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_file_storage(self):
        """Test storing and retrieving files."""
        # Store file
        metadata = self.storage.store_file("alice", str(self.test_file))
        
        # Read file
        content = self.storage.read_file(metadata.file_id, "alice")
        self.assertEqual(content.decode(), self.test_content)
    
    def test_file_sharing(self):
        """Test sharing files between users."""
        # Store and share file
        metadata = self.storage.store_file("alice", str(self.test_file))
        self.storage.share_file(metadata.file_id, "alice", "bob")
        
        # Bob reads file
        content = self.storage.read_file(metadata.file_id, "bob")
        self.assertEqual(content.decode(), self.test_content)
    
    def test_access_control(self):
        """Test access control enforcement."""
        # Store file
        metadata = self.storage.store_file("alice", str(self.test_file))
        
        # Bob shouldn't be able to read
        with self.assertRaises(ValueError):
            self.storage.read_file(metadata.file_id, "bob")

if __name__ == '__main__':
    unittest.main() 