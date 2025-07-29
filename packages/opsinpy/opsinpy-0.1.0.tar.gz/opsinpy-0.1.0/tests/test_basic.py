"""
Test cases for OpsinPy class.
"""

import os
import sys

# Add the parent directory to the path so we can import opsinpy
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from opsinpy import OpsinPy


class TestOpsinPy:
    """Test cases for OpsinPy class."""

    @pytest.fixture(scope="class")
    def opsin(self):
        """Create an OpsinPy instance for testing."""
        return OpsinPy()

    @pytest.mark.unit
    def test_initialization(self, opsin):
        """Test that OpsinPy can be initialized."""
        assert opsin is not None
        assert hasattr(opsin, "_jar_path")
        assert os.path.exists(opsin._jar_path)

    @pytest.mark.unit
    def test_simple_conversion(self, opsin):
        """Test basic chemical name conversion."""
        result = opsin.name_to_smiles("ethane")
        assert result == "CC"

    @pytest.mark.integration
    def test_multiple_formats(self, opsin):
        """Test conversion to different output formats."""
        name = "acetamide"

        smiles = opsin.name_to_smiles(name)
        cml = opsin.name_to_cml(name)
        inchi = opsin.name_to_inchi(name)
        stdinchi = opsin.name_to_stdinchi(name)
        stdinchikey = opsin.name_to_stdinchikey(name)

        assert smiles is not None
        assert cml is not None
        assert inchi is not None
        assert stdinchi is not None
        assert stdinchikey is not None

        # Basic format checks
        assert smiles.count("C") > 0  # Should contain carbon
        assert cml.startswith("<?xml") or cml.startswith("<cml")  # Should be XML or CML
        assert inchi.startswith("InChI=")  # Should start with InChI=
        assert stdinchi.startswith("InChI=")  # Should start with InChI=
        assert len(stdinchikey) == 27  # Standard InChI key length

    @pytest.mark.integration
    def test_batch_conversion(self, opsin):
        """Test batch conversion of multiple names."""
        names = ["methane", "ethane", "propane"]
        results = opsin.names_to_smiles(names)

        assert len(results) == len(names)
        assert results[0] == "C"
        assert results[1] == "CC"
        assert results[2] == "CCC"

    @pytest.mark.integration
    def test_options(self, opsin):
        """Test conversion with different options."""
        # Test radical handling
        name = "ethyl"

        without_radicals = opsin.name_to_smiles(name)
        with_radicals = opsin.name_to_smiles(name, allow_radicals=True)

        # Without radicals should fail (return None)
        # With radicals should succeed
        assert without_radicals is None
        assert with_radicals is not None
        assert "C" in with_radicals

    @pytest.mark.unit
    def test_invalid_name(self, opsin):
        """Test handling of invalid chemical names."""
        result = opsin.name_to_smiles("thisisnotavalidchemicalname")
        assert result is None

    @pytest.mark.unit
    def test_convert_method(self, opsin):
        """Test the generic convert method."""
        # Single name
        result = opsin.convert("ethane", "SMILES")
        assert result == "CC"

        # Multiple names
        results = opsin.convert(["methane", "ethane"], "SMILES")
        assert results == ["C", "CC"]

    @pytest.mark.unit
    def test_invalid_format(self, opsin):
        """Test handling of invalid output format."""
        with pytest.raises(ValueError):
            opsin.convert("ethane", "INVALID_FORMAT")


if __name__ == "__main__":
    pytest.main([__file__])
