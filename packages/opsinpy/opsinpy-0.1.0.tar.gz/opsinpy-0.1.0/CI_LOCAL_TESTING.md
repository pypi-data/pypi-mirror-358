# Local CI Testing Guide

This document explains how to test CI workflows locally before pushing to GitHub.

## Issues We Fixed

### 1. **MyPy Type Annotation Issues**
- **Problem**: Missing type annotations, incompatible return types, Java import issues
- **Solution**: 
  - Added comprehensive type annotations to all methods
  - Updated `pyproject.toml` to use Python 3.8+ for MyPy
  - Added MyPy overrides for Java imports and runtime-only issues
  - Fixed return type mismatches in convenience methods

### 2. **License Configuration Warnings**
- **Problem**: Deprecated license format causing setuptools warnings
- **Solution**: Updated `pyproject.toml` to use modern SPDX license format

### 3. **Code Formatting Issues**
- **Problem**: Code not properly formatted according to project standards
- **Solution**: Applied ruff formatting to all files

### 4. **Python Version Compatibility Issues**
- **Problem**: Python 3.7 reached end-of-life and is no longer supported on Ubuntu 24.04
- **Solution**: Updated minimum Python version to 3.8 and removed 3.7 from CI matrix

## How to Test CI Locally

### Prerequisites
```bash
# Install the package with dev dependencies
pip install -e ".[dev]"
```

### 1. **Linter Workflow Tests**
```bash
# Ruff linting check
ruff check opsinpy/ tests/ examples/ benchmarks/

# Ruff formatting check
ruff format --check opsinpy/ tests/ examples/ benchmarks/

# MyPy type checking
mypy opsinpy/

# Build validation
python -m build

# Package validation with twine
python -m twine check dist/*
```

### 2. **Test Workflow Tests**
```bash
# Run tests with coverage
pytest tests/ -v --cov=opsinpy --cov-report=xml --cov-report=term-missing

# Check coverage threshold (should be ≥85%)
pytest tests/ --cov=opsinpy --cov-fail-under=85
```

### 3. **Security Workflow Tests**
```bash
# Install security tools (if not already installed)
pip install safety bandit

# Run safety check
safety check

# Run bandit security scan
bandit -r opsinpy/
```

### 4. **Benchmark Workflow Tests**
```bash
# Run benchmarks
cd benchmarks/
python run_benchmark.py
```

### 5. **Comprehensive Test Script**
```bash
# Run all CI checks at once
echo "=== LINTER CHECKS ===" && \
ruff check opsinpy/ tests/ examples/ benchmarks/ && \
ruff format --check opsinpy/ tests/ examples/ benchmarks/ && \
mypy opsinpy/ && \
python -m build >/dev/null 2>&1 && \
python -m twine check dist/* >/dev/null 2>&1 && \
echo "=== TEST CHECKS ===" && \
pytest tests/ -q --cov=opsinpy --cov-fail-under=85 && \
echo "=== ALL CI CHECKS PASSED! ==="
```

## Common Issues and Solutions

### MyPy Errors
- **Java imports**: Use `# type: ignore[import-not-found]` or configure in `pyproject.toml`
- **Runtime-only attributes**: Use `# type: ignore[attr-defined]`
- **Any returns**: Use `# type: ignore[no-any-return]`

### Ruff Formatting
- **Auto-fix**: `ruff format opsinpy/ tests/ examples/ benchmarks/`
- **Check only**: `ruff format --check opsinpy/ tests/ examples/ benchmarks/`

### Build Issues
- **License warnings**: Use SPDX license format in `pyproject.toml`
- **Missing files**: Check `MANIFEST.in` includes all necessary files

### Test Coverage
- **Low coverage**: Add more tests or exclude non-testable lines
- **Missing coverage**: Use `pytest --cov-report=html` to see detailed report

### Python Version Compatibility
- **Minimum Python version**: 3.8+ (3.7 is end-of-life)
- **CI testing**: Tests run on Python 3.8, 3.9, 3.10, 3.11, 3.12
- **Ubuntu compatibility**: Use ubuntu-latest (24.04) which supports Python 3.8+

## GitHub Actions Workflow Files

Our CI consists of these workflows:
- **Linter.yaml**: Code quality checks (ruff, mypy, build)
- **Linux.yaml**: Tests on Linux with Python 3.8-3.12
- **MacOS.yaml**: Tests on macOS with Python 3.8, 3.11, 3.12
- **Windows.yaml**: Tests on Windows with Python 3.8, 3.11, 3.12
- **PyPI.yaml**: Package publication on releases
- **benchmark.yaml**: Performance monitoring
- **security.yaml**: Security vulnerability scanning

## Tips for Success

1. **Always test locally first** before pushing to GitHub
2. **Use the comprehensive test script** to catch all issues at once
3. **Fix formatting issues immediately** with `ruff format`
4. **Check MyPy incrementally** as you add type annotations
5. **Monitor test coverage** and aim to keep it above 85%
6. **Run security scans periodically** to catch vulnerabilities early

## Environment Setup

For consistent results, ensure your local environment matches CI:
- Python version: 3.8+ (required minimum)
- Java version: 8+ (for OPSIN JAR execution)
- All dev dependencies installed: `pip install -e ".[dev]"` 