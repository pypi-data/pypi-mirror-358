"""
Test cases for custom exceptions.
"""

import os
import sys

# Add the parent directory to the path so we can import opsinpy
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from opsinpy import OpsinError, OpsinJVMError, OpsinParsingError


class TestExceptions:
    """Test cases for custom exceptions."""

    @pytest.mark.unit
    def test_opsin_error_base(self):
        """Test OpsinError base exception."""
        error = OpsinError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    @pytest.mark.unit
    def test_opsin_jvm_error(self):
        """Test OpsinJVMError exception."""
        error = OpsinJVMError("JVM initialization failed")
        assert str(error) == "JVM initialization failed"
        assert isinstance(error, OpsinError)
        assert isinstance(error, Exception)

    @pytest.mark.unit
    def test_opsin_parsing_error_without_name(self):
        """Test OpsinParsingError without chemical name."""
        error = OpsinParsingError("Parsing failed")
        assert str(error) == "Parsing failed"
        assert error.chemical_name is None
        assert isinstance(error, OpsinError)

    @pytest.mark.unit
    def test_opsin_parsing_error_with_name(self):
        """Test OpsinParsingError with chemical name."""
        error = OpsinParsingError("Invalid structure", "invalid_name")
        expected_str = "Failed to parse 'invalid_name': Invalid structure"
        assert str(error) == expected_str
        assert error.chemical_name == "invalid_name"
        assert isinstance(error, OpsinError)

    @pytest.mark.unit
    def test_exception_inheritance(self):
        """Test exception inheritance hierarchy."""
        # Test that all custom exceptions inherit from OpsinError
        assert issubclass(OpsinJVMError, OpsinError)
        assert issubclass(OpsinParsingError, OpsinError)

        # Test that OpsinError inherits from Exception
        assert issubclass(OpsinError, Exception)

        # Test that all custom exceptions inherit from Exception
        assert issubclass(OpsinJVMError, Exception)
        assert issubclass(OpsinParsingError, Exception)
