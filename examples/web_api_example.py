"""
Web API Example using QRCLib

This example demonstrates how to build a secure web API using quantum-resistant
cryptography. It implements:

1. User registration with quantum-resistant keys
2. Message encryption and signing
3. Secure message exchange between users
4. Authentication using quantum-resistant signatures

The API provides endpoints for:
- Creating new users
- Retrieving public keys
- Sending encrypted messages
- Reading messages
"""

from flask import Flask, request, jsonify
from functools import wraps
import json
from datetime import datetime
from typing import Dict, List, Optional
import base64

from src.kyber import generate_keys as kyber_keygen, encapsulate, decapsulate
from src.dilithium import generate_keys as dilithium_keygen, sign, verify
from src.utils import secure_random_bytes

# In-memory storage (replace with database in production)
users: Dict[str, Dict] = {}
messages: Dict[str, List[Dict]] = {}
sessions: Dict[str, Dict] = {}

def generate_user_keys() -> Dict:
    """Generate quantum-resistant keys for a new user."""
    enc_public_key, enc_private_key = kyber_keygen()
    sign_private_key, sign_public_key = dilithium_keygen()
    
    # Convert keys to bytes for storage
    return {
        'enc_public_key': enc_public_key['seed'],
        'enc_private_key': enc_private_key['seed'],
        'sign_public_key': sign_public_key['key_seed'],
        'sign_private_key': sign_private_key['key_seed']
    }

def require_auth(f):
    """Decorator to enforce quantum-resistant authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or not auth.startswith('QR '):
            return jsonify({'error': 'Missing authentication'}), 401
        
        try:
            # Auth format: QR user_id:timestamp:signature
            auth_parts = auth[3:].split(':')
            if len(auth_parts) != 3:
                raise ValueError("Invalid auth format")
            
            user_id, timestamp, signature = auth_parts
            signature = bytes.fromhex(signature)
            
            if user_id not in users:
                return jsonify({'error': 'User not found'}), 404
            
            # Verify timestamp is recent (within 5 minutes)
            timestamp_dt = datetime.fromisoformat(timestamp)
            if abs((datetime.utcnow() - timestamp_dt).total_seconds()) > 300:
                return jsonify({'error': 'Authentication expired'}), 401
            
            # Verify signature
            message = f"{user_id}:{timestamp}".encode()
            if not verify(users[user_id]['sign_public_key'], message, signature):
                return jsonify({'error': 'Invalid signature'}), 401
            
            return f(user_id, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    return decorated

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    @app.route('/api/users', methods=['POST'])
    def create_user():
        """Create a new user with quantum-resistant keys."""
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        if user_id in users:
            return jsonify({'error': 'User already exists'}), 409
        
        # Generate keys
        keys = generate_user_keys()
        users[user_id] = keys
        messages[user_id] = []
        
        # Return public keys in base64 format
        return jsonify({
            'user_id': user_id,
            'enc_public_key': base64.b64encode(keys['enc_public_key']).decode(),
            'sign_public_key': base64.b64encode(keys['sign_public_key']).decode()
        }), 200
    
    @app.route('/api/users/<user_id>/keys', methods=['GET'])
    def get_public_keys(user_id):
        """Get a user's public keys."""
        if user_id not in users:
            return jsonify({'error': 'User not found'}), 404
        
        # Convert keys to base64 for JSON serialization
        return jsonify({
            'user_id': user_id,
            'enc_public_key': base64.b64encode(users[user_id]['enc_public_key']).decode(),
            'sign_public_key': base64.b64encode(users[user_id]['sign_public_key']).decode()
        }), 200
    
    @app.route('/api/messages', methods=['POST'])
    @require_auth
    def send_message(sender_id):
        """Send an encrypted and signed message to another user."""
        data = request.get_json()
        recipient_id = data.get('recipient_id')
        message_text = data.get('message')
        
        if not recipient_id or not message_text:
            return jsonify({'error': 'Missing recipient_id or message'}), 400
        
        if recipient_id not in users:
            return jsonify({'error': 'Recipient not found'}), 404
        
        try:
            # Generate message ID and encryption key
            message_id = secure_random_bytes(16).hex()
            encryption_key = secure_random_bytes(32)
            
            # Encrypt message key for recipient
            key_ciphertext, _ = encapsulate(
                users[recipient_id]['enc_public_key'],
                encryption_key
            )
            
            # Encrypt message
            message_bytes = message_text.encode()
            ciphertext = bytes([a ^ b for a, b in zip(
                message_bytes,
                encryption_key[:len(message_bytes)]
            )])
            
            # Sign message
            signature = sign(
                users[sender_id]['sign_private_key'],
                message_bytes
            )
            
            # Store message
            message_data = {
                'id': message_id,
                'sender_id': sender_id,
                'timestamp': datetime.utcnow().isoformat(),
                'key_ciphertext': key_ciphertext.hex(),
                'ciphertext': base64.b64encode(ciphertext).decode(),
                'signature': signature.hex()
            }
            messages[recipient_id].append(message_data)
            
            return jsonify({'message_id': message_id})
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/messages', methods=['GET'])
    @require_auth
    def get_messages(user_id):
        """Get all messages for the authenticated user."""
        try:
            user_messages = messages.get(user_id, [])
            decrypted_messages = []
            
            for msg in user_messages:
                # Decrypt message key
                key_ciphertext = bytes.fromhex(msg['key_ciphertext'])
                encryption_key = decapsulate(
                    key_ciphertext,
                    users[user_id]['enc_private_key']
                )
                
                # Decrypt message
                ciphertext = base64.b64decode(msg['ciphertext'])
                message_bytes = bytes([a ^ b for a, b in zip(
                    ciphertext,
                    encryption_key[:len(ciphertext)]
                )])
                
                # Verify signature
                signature = bytes.fromhex(msg['signature'])
                if not verify(
                    users[msg['sender_id']]['sign_public_key'],
                    message_bytes,
                    signature
                ):
                    continue  # Skip messages with invalid signatures
                
                decrypted_messages.append({
                    'id': msg['id'],
                    'sender_id': msg['sender_id'],
                    'timestamp': msg['timestamp'],
                    'message': message_bytes.decode()
                })
            
            return jsonify({'messages': decrypted_messages})
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app

def main():
    """
    Run the example API server.
    
    This demonstrates:
    1. Creating users with quantum-resistant keys
    2. Sending encrypted messages
    3. Reading and verifying messages
    4. Authentication with quantum-resistant signatures
    """
    app = create_app()
    app.run(debug=True)

if __name__ == "__main__":
    main() 