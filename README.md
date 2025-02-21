# QRCLib: Quantum-Resistant Cryptography Library

QRCLib is a Python library implementing post-quantum cryptographic algorithms, designed to protect against both classical and quantum computer attacks. The library currently implements NIST's selected post-quantum cryptographic standards: Kyber for key encapsulation and Dilithium for digital signatures.

## Features

- **Kyber Key Encapsulation Mechanism (KEM)**
  - Key generation
  - Encapsulation
  - Decapsulation
  - Multiple security levels (Kyber-512, Kyber-768, Kyber-1024)

- **Dilithium Digital Signatures**
  - Key generation
  - Signature generation
  - Signature verification
  - NIST security level 2 implementation

- **Optimized Implementation**
  - Number Theoretic Transform (NTT) for efficient polynomial operations
  - Constant-time operations to prevent timing attacks
  - Secure random number generation
  - Comprehensive test suite

## Installation

```bash
# Clone the repository
git clone https://github.com/BlockSavvy/QRCLib.git

# Change to the project directory
cd QRCLib

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Key Encapsulation with Kyber

```python
from src.kyber import generate_keys, encapsulate, decapsulate

# Generate key pair
public_key, private_key = generate_keys()

# Encapsulate a shared secret
ciphertext, shared_secret_a = encapsulate(public_key)

# Decapsulate to recover the shared secret
shared_secret_b = decapsulate(ciphertext, private_key)

# Verify both parties have the same shared secret
assert shared_secret_a == shared_secret_b
```

### Digital Signatures with Dilithium

```python
from src.dilithium import generate_keys, sign, verify

# Generate key pair
signing_key, verification_key = generate_keys()

# Sign a message
message = b"Hello, quantum world!"
signature = sign(signing_key, message)

# Verify the signature
is_valid = verify(verification_key, message, signature)
assert is_valid == True
```

## Security Considerations

- The library implements constant-time operations where possible to prevent timing attacks
- Uses Python's `secrets` module for cryptographically secure random number generation
- Follows NIST's post-quantum cryptography standards
- Regular security audits and updates are recommended for production use

## Testing

The library includes a comprehensive test suite covering both normal operation and edge cases:

```bash
# Run all tests with coverage report
./run_tests.py
```

## Documentation

- [API Documentation](docs/api.md)
- [Security Guidelines](docs/security.md)
- [Implementation Details](docs/implementation.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- NIST Post-Quantum Cryptography Standardization
- The Kyber and Dilithium teams for their specifications
- Contributors and reviewers

## Citation

If you use QRCLib in your research, please cite:

```bibtex
@software{qrclib2024,
  title = {QRCLib: A Quantum-Resistant Cryptography Library},
  author = {BlockSavvy},
  year = {2024},
  url = {https://github.com/BlockSavvy/QRCLib}
}
```

## Contact

- GitHub Issues: [https://github.com/BlockSavvy/QRCLib/issues](https://github.com/BlockSavvy/QRCLib/issues)
- Email: [your-email@example.com]
