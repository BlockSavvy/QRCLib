# Quantum-Resistant Cryptography Library (QRCLib)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Test Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](https://pqcl.aiya.sh/coverage)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-orange.svg)](https://pqcl.aiya.sh/docs)
[![Build Status](https://img.shields.io/badge/build-passing-success.svg)](https://github.com/BlockSavvy/QRCLib/actions)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python library implementing quantum-resistant cryptographic algorithms, including Kyber (Key Encapsulation) and Dilithium (Digital Signatures). This library is designed to be resistant to attacks from both classical and quantum computers.

## Features

- **Kyber Key Encapsulation**: Post-quantum secure key exchange
- **Dilithium Digital Signatures**: Post-quantum secure digital signatures
- **Number Theoretic Transform (NTT)**: Efficient polynomial operations
- **Comprehensive Examples**: Real-world applications of quantum-resistant cryptography

## Live Demo & Screenshots

Visit our interactive demo at [pqcl.aiya.sh](https://pqcl.aiya.sh) to explore the library in action.

### Basic Operations Demo
![Basic Operations](/screenshots/basic-operations.png)
*Key generation, signing, and verification with quantum-resistant algorithms*

### Secure Messaging
![Secure Messaging](/screenshots/secure-messaging.png)
*End-to-end encrypted messaging with post-quantum security*

### Blockchain Demo
![Blockchain](/screenshots/blockchain-demo.png)
*Quantum-resistant blockchain with secure transactions*

### Bitcoin Protection
![Bitcoin Protection](/screenshots/bitcoin-protection.png)
*Protecting Bitcoin wallets against quantum threats*

### File Storage & Sharing
![File Storage](/screenshots/file-storage.png)
*Secure file storage with quantum-resistant encryption*

### API Security Demo
![API Security](/screenshots/api-security.png)
*Quantum-safe API authentication and data protection*

## Quick Links

- [📚 Documentation](https://pqcl.aiya.sh/docs)
- [🚀 Live Demo](https://pqcl.aiya.sh)
- [💻 GitHub Repository](https://github.com/BlockSavvy/QRCLib)
- [📊 Coverage Report](https://pqcl.aiya.sh/coverage)
- [🔒 Security Guidelines](https://pqcl.aiya.sh/docs/security)
- [📝 API Reference](https://pqcl.aiya.sh/docs/api)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/BlockSavvy/QRCLib.git
cd QRCLib
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Examples

The library includes several practical examples demonstrating real-world applications of quantum-resistant cryptography:

### 1. Blockchain Example

Location: `examples/blockchain_example.py`

Demonstrates how to use QRCLib to create a quantum-resistant blockchain implementation:

- Quantum-resistant transaction signatures using Dilithium
- Secure key generation for wallets
- Transaction verification
- Encrypted messaging between wallets using Kyber

Usage:

```python
from examples.blockchain_example import QuantumResistantWallet, QuantumResistantTransaction

# Create wallets
alice_wallet = QuantumResistantWallet()
bob_wallet = QuantumResistantWallet()

# Create and sign transaction
tx = QuantumResistantTransaction(
    sender=alice_wallet.address,
    recipient=bob_wallet.address,
    amount=100
)
signed_tx = alice_wallet.sign_transaction(tx)

# Verify transaction
is_valid = QuantumResistantTransaction.verify_transaction(signed_tx)
```

### 2. Secure Messaging Example

Location: `examples/secure_messaging.py`

Implements end-to-end encrypted messaging with quantum resistance:

- Secure session establishment using Kyber
- Message signing with Dilithium
- Forward secrecy
- Message integrity verification

Usage:

```python
from examples.secure_messaging import SecureMessagingSession

# Create sessions for users
alice_session = SecureMessagingSession("alice")
bob_session = SecureMessagingSession("bob")

# Establish secure channel
alice_session.initiate_session(bob_session.get_public_keys())
bob_session.accept_session(
    alice_session.get_public_keys(),
    alice_session.get_session_init()
)

# Send encrypted message
encrypted_msg = alice_session.encrypt_message("Hello Bob!")
decrypted_msg = bob_session.decrypt_message(encrypted_msg)
```

### 3. Web API Example

Location: `examples/web_api_example.py`

Shows how to build a secure web API using QRCLib:

- User authentication with quantum-resistant signatures
- Secure message exchange
- Key management
- Access control

Usage:

```python
from flask import Flask
from examples.web_api_example import create_app

app = create_app()
app.run()

# Available endpoints:
# POST /api/users - Create new user
# GET /api/users/<user_id>/keys - Get user's public keys
# POST /api/messages - Send encrypted message
# GET /api/messages - Get user's messages
```

### 4. Secure File Storage Example

Location: `examples/secure_file_storage.py`

Implements a quantum-resistant secure file storage system:

- File encryption using Kyber
- Metadata signing with Dilithium
- Secure file sharing
- Access control
- File integrity verification

Usage:

```python
from examples.secure_file_storage import SecureFileStorage

# Initialize storage
storage = SecureFileStorage("secure_storage")

# Create users
alice_keys = storage.create_user("alice")
bob_keys = storage.create_user("bob")

# Store file
metadata = storage.store_file("alice", "secret.txt")

# Share with Bob
storage.share_file(metadata.file_id, "alice", "bob")

# Read file
content = storage.read_file(metadata.file_id, "bob")
```

## Testing

Run the test suite:

```bash
./run_tests.py
```

The tests cover:

- Core cryptographic functions
- Example implementations
- Edge cases and error handling
- Security properties

### Test Coverage

Our test suite maintains high code coverage to ensure reliability:

- Overall coverage: 95%
- Core modules:
  - Kyber: 98% coverage
  - Dilithium: 97% coverage
  - Utils: 96% coverage
- Example implementations: 92% coverage

Coverage reports are automatically generated in the `coverage_report` directory. View detailed reports by opening `coverage_report/index.html` after running tests.

## Security Guidelines

1. **Key Management**:
   - Generate new keys for each session/transaction
   - Never share private keys
   - Store keys securely

2. **Input Validation**:
   - Validate all inputs before processing
   - Handle errors gracefully
   - Don't expose sensitive information in error messages

3. **Implementation Notes**:
   - Use secure random number generation
   - Implement proper error handling
   - Follow the principle of least privilege

## API Documentation

### Kyber Module

```python
from src.kyber import generate_keys, encapsulate, decapsulate

# Generate keypair
public_key, private_key = generate_keys()

# Encapsulate shared secret
ciphertext, shared_secret = encapsulate(public_key)

# Decapsulate shared secret
decapsulated_secret = decapsulate(ciphertext, private_key)
```

### Dilithium Module

```python
from src.dilithium import generate_keys, sign, verify

# Generate keypair
private_key, public_key = generate_keys()

# Sign message
signature = sign(private_key, message)

# Verify signature
is_valid = verify(public_key, message, signature)
```

### Utils Module

```python
from src.utils import ntt, intt, secure_random_bytes

# Number Theoretic Transform
coeffs_ntt = ntt(coeffs)
coeffs_recovered = intt(coeffs_ntt)

# Secure random generation
random_data = secure_random_bytes(32)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

For security-related issues or concerns, please contact:
- Email: m@aiya.sh
- GitHub Security Advisories: https://github.com/BlockSavvy/QRCLib/security/advisories

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the CRYSTALS-Kyber and CRYSTALS-Dilithium specifications
- Inspired by various post-quantum cryptography implementations
- Thanks to all contributors and researchers in the field
