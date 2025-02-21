# Virtual Environment Management for PQCL

## Overview

This document explains how to manage the Python virtual environment for the Quantum-Resistant Cryptography Library (PQCL) project.

## Why Virtual Environments?

Virtual environments are isolated Python environments that:

- Prevent package conflicts between different projects
- Ensure consistent dependencies across development machines
- Make it easier to track and manage project dependencies
- Allow different projects to use different versions of the same package

## Project Virtual Environment Setup

### Initial Setup

1. Create a new virtual environment:

   ```bash
   # In the project root directory
   python -m venv venv
   ```

1. Activate the virtual environment:

   ```bash
   # On Unix/macOS
   source venv/bin/activate

   # On Windows
   .\venv\Scripts\activate
   ```

1. Install project dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Daily Development

1. **Starting Work**:
   - Open your terminal
   - Navigate to the project directory
   - Activate the virtual environment:

     ```bash
     source venv/bin/activate  # Unix/macOS
     # or
     .\venv\Scripts\activate   # Windows
     ```

   - Verify activation by checking for `(venv)` prefix in your terminal

2. **During Development**:
   - Any `pip install` commands will install packages into the virtual environment
   - Python will use packages from the virtual environment
   - Run tests and examples using the virtual environment's Python

3. **Ending Work**:
   - Deactivate the virtual environment when done:

     ```bash
     deactivate
     ```

### Managing Dependencies

1. **Adding New Dependencies**:

   ```bash
   pip install new_package
   pip freeze > requirements.txt
   ```

2. **Updating Dependencies**:

   ```bash
   pip install --upgrade package_name
   pip freeze > requirements.txt
   ```

3. **Viewing Installed Packages**:

   ```bash
   pip list
   ```

### IDE Integration

#### VS Code

1. Select Python Interpreter:
   - Press `Cmd/Ctrl + Shift + P`
   - Type "Python: Select Interpreter"
   - Choose the interpreter from your virtual environment (`venv/bin/python`)

#### PyCharm

1. Set Project Interpreter:
   - Go to Preferences/Settings → Project → Python Interpreter
   - Click the gear icon → Add
   - Select "Existing Environment" → Choose `venv/bin/python`

## Troubleshooting

### Common Issues

1. **"Command not found: pip"**
   - Ensure virtual environment is activated
   - Try upgrading pip:

     ```bash
     python -m pip install --upgrade pip
     ```

2. **Package Import Errors**
   - Verify virtual environment is activated
   - Check if package is installed:

     ```bash
     pip list | grep package_name
     ```

   - Reinstall dependencies:

     ```bash
     pip install -r requirements.txt
     ```

3. **Virtual Environment Not Activating**
   - Check if `venv` directory exists
   - Try recreating the virtual environment:

     ```bash
     rm -rf venv
     python -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt
     ```

### Best Practices

1. **Always** activate the virtual environment before working on the project
2. Keep `requirements.txt` up to date
3. Don't commit the `venv` directory to version control
4. Use `pip freeze > requirements.txt` to update dependencies
5. Regularly upgrade pip and dependencies

## Project-Specific Dependencies

Current project dependencies (from requirements.txt):

```python
numpy>=1.24.0
pytest>=7.3.1
cryptography>=41.0.0
coverage>=7.3.2
pytest-cov>=4.1.0
pytest-xdist>=3.3.1
```

## Security Considerations

1. Keep pip and setuptools updated
2. Review package security advisories
3. Use specific version numbers in requirements.txt
4. Regularly audit dependencies for vulnerabilities

## Continuous Integration

When setting up CI (e.g., GitHub Actions):

1. Create virtual environment in CI pipeline
2. Install dependencies from requirements.txt
3. Run tests using the virtual environment

## Additional Resources

- [Python venv documentation](https://docs.python.org/3/library/venv.html)
- [pip documentation](https://pip.pypa.io/en/stable/)
- [Python Packaging User Guide](https://packaging.python.org/)
