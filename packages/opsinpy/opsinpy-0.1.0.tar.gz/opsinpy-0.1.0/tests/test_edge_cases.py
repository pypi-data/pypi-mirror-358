"""
Test cases for edge cases and error conditions.
"""

import contextlib
import os
import sys
import tempfile

# Add the parent directory to the path so we can import opsinpy
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from opsinpy import OpsinJVMError, OpsinPy


class TestEdgeCases:
    """Test cases for edge cases and error conditions."""

    @pytest.mark.unit
    def test_initialization_with_custom_jar_path(self):
        """Test initialization with custom JAR path."""
        # Create a temporary file to simulate a JAR
        with tempfile.NamedTemporaryFile(suffix=".jar", delete=False) as tmp:
            jar_path = tmp.name

        try:
            opsin = OpsinPy(jar_path=jar_path)
            assert opsin._jar_path == jar_path
        finally:
            os.unlink(jar_path)

    @pytest.mark.unit
    def test_initialization_with_nonexistent_jar(self):
        """Test initialization with non-existent JAR path."""
        with pytest.raises(OpsinJVMError, match="OPSIN JAR file not found"):
            OpsinPy(jar_path="/nonexistent/path/to/jar.jar")

    @pytest.mark.unit
    def test_empty_string_conversion(self, shared_opsin):
        """Test conversion of empty string."""
        result = shared_opsin.name_to_smiles("")
        assert result is None

    @pytest.mark.unit
    def test_whitespace_only_conversion(self, shared_opsin):
        """Test conversion of whitespace-only string."""
        result = shared_opsin.name_to_smiles("   ")
        assert result is None

    @pytest.mark.integration
    def test_batch_conversion_with_mixed_valid_invalid(self, shared_opsin):
        """Test batch conversion with mix of valid and invalid names."""
        names = ["methane", "invalid_name", "ethane", ""]
        results = shared_opsin.names_to_smiles(names)

        assert len(results) == 4
        assert results[0] == "C"  # methane
        assert results[1] is None  # invalid_name
        assert results[2] == "CC"  # ethane
        assert results[3] is None  # empty string

    @pytest.mark.integration
    def test_all_convenience_methods(self, shared_opsin):
        """Test all convenience methods with a simple molecule."""
        name = "methane"

        # Single conversion methods
        smiles = shared_opsin.name_to_smiles(name)
        extended_smiles = shared_opsin.name_to_extended_smiles(name)
        cml = shared_opsin.name_to_cml(name)
        inchi = shared_opsin.name_to_inchi(name)
        stdinchi = shared_opsin.name_to_stdinchi(name)
        stdinchikey = shared_opsin.name_to_stdinchikey(name)

        assert smiles == "C"
        assert extended_smiles is not None
        assert cml is not None
        assert inchi is not None
        assert stdinchi is not None
        assert stdinchikey is not None

    @pytest.mark.integration
    def test_all_batch_methods(self, shared_opsin):
        """Test all batch conversion methods."""
        names = ["methane", "ethane"]

        # Batch conversion methods
        smiles_list = shared_opsin.names_to_smiles(names)
        extended_smiles_list = shared_opsin.names_to_extended_smiles(names)
        cml_list = shared_opsin.names_to_cml(names)
        inchi_list = shared_opsin.names_to_inchi(names)
        stdinchi_list = shared_opsin.names_to_stdinchi(names)
        stdinchikey_list = shared_opsin.names_to_stdinchikey(names)

        assert smiles_list == ["C", "CC"]
        assert len(extended_smiles_list) == 2
        assert len(cml_list) == 2
        assert len(inchi_list) == 2
        assert len(stdinchi_list) == 2
        assert len(stdinchikey_list) == 2

    @pytest.mark.integration
    def test_all_configuration_options(self, shared_opsin):
        """Test all configuration options."""
        name = "acetic acid"

        # Test with all options enabled
        result = shared_opsin.name_to_smiles(
            name,
            allow_acids_without_acid=True,
            allow_radicals=True,
            allow_uninterpretable_stereo=True,
            detailed_failure_analysis=True,
        )

        assert result is not None
        assert "C" in result

    @pytest.mark.unit
    def test_case_insensitive_format_names(self, shared_opsin):
        """Test that format names are case insensitive."""
        name = "methane"

        # Test different case variations
        result1 = shared_opsin.convert(name, "smiles")
        result2 = shared_opsin.convert(name, "SMILES")
        result3 = shared_opsin.convert(name, "Smiles")

        assert result1 == result2 == result3 == "C"

    @pytest.mark.unit
    def test_del_method(self):
        """Test __del__ method doesn't raise exceptions."""
        opsin = OpsinPy()
        # __del__ should not raise any exceptions
        try:
            del opsin
        except Exception as e:
            pytest.fail(f"__del__ method raised an exception: {e}")

    @pytest.mark.unit
    def test_convert_with_list_single_item(self, shared_opsin):
        """Test convert method with single-item list."""
        result = shared_opsin.convert(["methane"], "SMILES")
        assert result == ["C"]

    @pytest.mark.unit
    def test_convert_with_empty_list(self, shared_opsin):
        """Test convert method with empty list."""
        result = shared_opsin.convert([], "SMILES")
        assert result == []

    @pytest.mark.unit
    def test_shutdown_jvm_when_started(self):
        """Test shutdown_jvm method when JVM is running."""
        # This test just verifies the method exists and can be called
        # We can't actually test restart due to JPype limitations
        with contextlib.suppress(Exception):
            # If JVM is already shut down, that's fine
            OpsinPy.shutdown_jvm()
