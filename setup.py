from setuptools import setup, find_packages

setup(
    name="qrclib",
    version="0.1.0",
    description="A Python library implementing quantum-resistant cryptographic algorithms",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="BlockSavvy",
    author_email="m@aiya.sh",
    url="https://github.com/BlockSavvy/QRCLib",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "cryptography>=3.4.7",
        "flask>=2.0.1",
        "pytest>=6.2.5",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.8",
) 