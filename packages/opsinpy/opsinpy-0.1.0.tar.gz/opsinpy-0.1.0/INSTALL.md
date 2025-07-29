# Installation Guide for opsinpy

## Prerequisites

Before installing opsinpy, ensure you have:

1. **Python 3.8 or higher**
2. **Java 8 or higher** (required by OPSIN)

### Checking Java Installation

```bash
java -version
```

If Java is not installed, install it using your system's package manager:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install openjdk-11-jdk
```

**macOS:**
```bash
brew install openjdk@11
```

**Windows:**
Download and install from [Oracle](https://www.oracle.com/java/technologies/downloads/) or [OpenJDK](https://openjdk.org/).

## Installation

### From PyPI (Recommended)

```bash
pip install opsinpy
```

### From Source (Development)

1. **Clone the repository:**
```bash
git clone https://github.com/craabreu/opsinpy.git
cd opsinpy
```

2. **Install in development mode:**
```bash
pip install -e .
```

3. **Install development dependencies (optional):**
```bash
pip install -e ".[dev]"
```

### Building a Wheel

```bash
python -m build
pip install dist/opsinpy-*.whl
```

## Verification

Test the installation:

```python
from opsinpy import OpsinPy

opsin = OpsinPy()
result = opsin.name_to_smiles("ethane")
print(result)  # Should output: CC
```

Or run the example script:

```bash
python examples/basic_usage.py
```

## Running Tests

```bash
python -m pytest tests/
```

## Troubleshooting

### Common Issues

1. **"Java may not be installed/accessible"**
   - Ensure Java is installed and accessible via `java -version`
   - Check your PATH environment variable

2. **"OPSIN JAR file not found"**
   - The JAR file should be bundled with the package
   - If missing, reinstall the package

3. **JPype import errors**
   - Install JPype1: `pip install JPype1>=1.4.0`
   - Ensure you have a compatible Java version

4. **JVM startup errors**
   - Only one JVM can run per Python process
   - Restart Python if you encounter JVM conflicts

### Getting Help

- Check the [GitHub repository](https://github.com/craabreu/opsinpy) for issues and documentation
- Review the examples in the `examples/` directory
- Check the [OPSIN documentation](https://opsin.ch.cam.ac.uk/) for underlying functionality 