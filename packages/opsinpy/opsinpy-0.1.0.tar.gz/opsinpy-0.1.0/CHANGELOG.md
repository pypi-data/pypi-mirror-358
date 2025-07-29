# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **BREAKING**: Minimum Python version updated from 3.7 to 3.8
  - Python 3.7 reached end-of-life in June 2023
  - Ubuntu 24.04 no longer supports Python 3.7
  - CI now tests on Python 3.8, 3.9, 3.10, 3.11, 3.12

### Fixed
- Updated deprecated GitHub Actions to latest versions
- Fixed Python 3.7 compatibility issues in test suite
- Resolved CI workflow failures on Ubuntu 24.04

## [0.1.0] - 2024-06-26

### Added
- Initial release of opsinpy (renamed from opsin-py)
- Python bindings for OPSIN using JPype
- Support for all OPSIN output formats (SMILES, CML, InChI, StdInChI, StdInChIKey)
- Batch processing capabilities
- Comprehensive test suite with 58 tests
- Performance benchmarks showing 10-1000x speedup over subprocess-based alternatives
- Type hints and error handling
- Configuration options for chemical name parsing
- Documentation and examples

### Changed
- Package name changed from `opsin-py` to `opsinpy`
- Updated all imports, documentation, and references
- Modernized packaging using pyproject.toml
- Improved code quality with ruff and black formatting

### Technical Details
- Python 3.8+ support (3.7 end-of-life)
- JPype1 integration for direct Java access
- OPSIN 2.8.0 JAR included
- 91% test coverage
- MIT License 