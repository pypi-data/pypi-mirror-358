# Contributing to opsinpy

Thank you for your interest in contributing to opsinpy! This document provides guidelines for contributing to the project.

## Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/opsinpy.git
   cd opsinpy
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Verify the installation:**
   ```bash
   python -m pytest tests/
   ```

## Development Workflow

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines below

3. **Run tests:**
   ```bash
   python -m pytest tests/ -v
   ```

4. **Run linting and formatting:**
   ```bash
   ruff check . --fix
   ruff format .
   ```

5. **Check type hints:**
   ```bash
   mypy opsinpy/
   ```

### Code Style

This project uses:
- **Ruff** for linting and import sorting
- **Black** for code formatting (via ruff format)
- **MyPy** for type checking
- **Line length**: 88 characters

### Testing

- Write tests for new functionality
- Maintain test coverage above 85%
- Use descriptive test names
- Include both unit and integration tests

Test categories:
- `@pytest.mark.unit` - Fast, isolated tests
- `@pytest.mark.integration` - Tests involving Java/OPSIN
- `@pytest.mark.slow` - Long-running tests

Run specific test categories:
```bash
pytest -m unit          # Fast tests only
pytest -m integration   # Integration tests
pytest -m "not slow"    # Exclude slow tests
```

### Commit Messages

Use clear, descriptive commit messages:
```
Add support for new OPSIN configuration option

- Implement allow_uninterpretable_stereo parameter
- Add tests for stereochemistry handling
- Update documentation
```

## Pull Request Process

1. **Ensure all tests pass** and coverage is maintained
2. **Update documentation** if needed
3. **Add changelog entry** in CHANGELOG.md
4. **Create pull request** with:
   - Clear description of changes
   - Reference to any related issues
   - Screenshots if UI changes

### Pull Request Template

```markdown
## Description
Brief description of changes

## Changes Made
- [ ] New feature/fix implemented
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Changelog updated

## Testing
- [ ] All tests pass
- [ ] Coverage maintained/improved
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Breaking changes documented
```

## Issue Reporting

When reporting issues, please include:
- Python version
- Java version
- Operating system
- opsinpy version
- Minimal reproduction example
- Error messages/stack traces

## Types of Contributions

### Bug Fixes
- Fix incorrect behavior
- Improve error handling
- Performance improvements

### Features
- New OPSIN configuration options
- Additional output formats
- Utility functions

### Documentation
- API documentation improvements
- Examples and tutorials
- Installation guides

### Testing
- Additional test cases
- Performance benchmarks
- Edge case coverage

## Development Guidelines

### Code Organization
- Keep functions small and focused
- Use type hints for all public APIs
- Handle errors gracefully with informative messages
- Follow existing naming conventions

### Performance Considerations
- Minimize JVM startup overhead
- Support batch processing where possible
- Cache expensive operations when appropriate

### Compatibility
- Maintain Python 3.8+ compatibility
- Test with multiple Python versions
- Consider Java version compatibility

## Getting Help

- Check existing issues and documentation
- Ask questions in GitHub Discussions
- Review examples in the `examples/` directory
- Check the OPSIN documentation for underlying functionality

## Recognition

Contributors will be acknowledged in:
- AUTHORS file
- Release notes
- Project documentation

Thank you for contributing to opsinpy! 