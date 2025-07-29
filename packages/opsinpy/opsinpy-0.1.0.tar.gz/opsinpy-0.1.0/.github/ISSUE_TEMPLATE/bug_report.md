---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: craabreu

---

## Bug Description

A clear and concise description of what the bug is.

## To Reproduce

Steps to reproduce the behavior:

1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior

A clear and concise description of what you expected to happen.

## Actual Behavior

A clear and concise description of what actually happened.

## Error Messages

```
Paste any error messages or stack traces here
```

## Environment

- **OS**: [e.g. Ubuntu 20.04, macOS 12.0, Windows 10]
- **Python version**: [e.g. 3.9.7]
- **Java version**: [e.g. OpenJDK 11.0.12]
- **opsinpy version**: [e.g. 0.1.0]
- **JPype1 version**: [e.g. 1.4.1]

## Minimal Example

```python
# Provide a minimal code example that reproduces the issue
from opsinpy import OpsinPy

opsin = OpsinPy()
result = opsin.name_to_smiles("problematic_name")
```

## Additional Context

Add any other context about the problem here, such as:
- Screenshots
- Related issues
- Workarounds you've tried
- Impact on your workflow 