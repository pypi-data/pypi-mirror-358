"""
Pytest configuration and shared fixtures.
"""

import warnings

import pytest

from opsinpy import OpsinPy


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


@pytest.fixture(autouse=True)
def suppress_jvm_warnings():
    """Suppress JVM-related warnings during tests."""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="JVM already started")
        yield


@pytest.fixture(scope="session")
def shared_opsin():
    """Create a shared OpsinPy instance for the entire test session."""
    return OpsinPy()
