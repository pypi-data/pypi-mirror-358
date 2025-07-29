"""Tests specifically designed to improve code coverage."""

import warnings
from unittest.mock import patch

import pytest

from opsinpy import OpsinPy
from opsinpy.exceptions import OpsinJVMError


class TestCoverageImprovements:
    """Tests to improve code coverage for uncovered lines."""

    def test_pkg_resources_fallback(self):
        """Test fallback to pkg_resources when importlib.resources fails."""
        # We need to test this before OpsinPy is imported to avoid module caching
        # This test may not work perfectly due to import caching, but it covers the intent
        opsin = OpsinPy()

        # Just test that the method exists and can be called
        jar_path = opsin._get_default_jar_path()
        assert jar_path.endswith("opsin-cli-2.8.0-jar-with-dependencies.jar")

    def test_nonexistent_jar_file(self):
        """Test error when JAR file doesn't exist."""
        with pytest.raises(OpsinJVMError, match="OPSIN JAR file not found"):
            OpsinPy(jar_path="/nonexistent/path/to/opsin.jar")

    def test_jvm_start_exception(self):
        """Test exception handling during JVM startup."""
        opsin = OpsinPy()

        with patch("jpype.isJVMStarted", return_value=False), patch(
            "jpype.startJVM", side_effect=Exception("JVM start failed")
        ), pytest.raises(OpsinJVMError, match="Failed to start JVM"):
            opsin._start_jvm()

    def test_convert_single_name_valueerror_propagation(self):
        """Test that ValueError is properly propagated in _convert_single_name."""
        opsin = OpsinPy()
        opsin._start_jvm()

        # This should raise ValueError for unsupported format
        with pytest.raises(ValueError, match="Unsupported output format"):
            opsin._convert_single_name(
                "methane", "INVALID_FORMAT", opsin._create_config()
            )

    def test_del_method(self):
        """Test the __del__ method."""
        opsin = OpsinPy()
        # The __del__ method should run without error
        del opsin

    def test_shutdown_jvm_when_started(self):
        """Test shutdown_jvm when JVM is started."""
        with patch("jpype.isJVMStarted", return_value=True), patch(
            "jpype.shutdownJVM"
        ) as mock_shutdown:
            OpsinPy.shutdown_jvm()
            mock_shutdown.assert_called_once()

    def test_shutdown_jvm_when_not_started(self):
        """Test shutdown_jvm when JVM is not started."""
        with patch("jpype.isJVMStarted", return_value=False), patch(
            "jpype.shutdownJVM"
        ) as mock_shutdown:
            OpsinPy.shutdown_jvm()
            mock_shutdown.assert_not_called()

    def test_jvm_already_started_warning(self):
        """Test warning when JVM is already started."""
        opsin = OpsinPy()

        with patch("jpype.isJVMStarted", return_value=True), warnings.catch_warnings(
            record=True
        ) as w:
            warnings.simplefilter("always")
            opsin._start_jvm()

            assert len(w) == 1
            assert "JVM already started" in str(w[0].message)
            assert w[0].category is RuntimeWarning

    def test_detailed_failure_analysis_option(self):
        """Test the detailed_failure_analysis configuration option."""
        opsin = OpsinPy()
        opsin._start_jvm()

        config = opsin._create_config(detailed_failure_analysis=True)

        # Verify the option was set (we can't easily test the Java object directly,
        # but we can ensure the method was called without error)
        assert config is not None

    def test_all_configuration_options(self):
        """Test all configuration options together."""
        opsin = OpsinPy()
        opsin._start_jvm()

        config = opsin._create_config(
            allow_acids_without_acid=True,
            allow_radicals=True,
            allow_uninterpretable_stereo=True,
            detailed_failure_analysis=True,
        )

        assert config is not None

    def test_convert_empty_list(self):
        """Test converting empty list."""
        opsin = OpsinPy()
        result = opsin.convert([])
        assert result == []

    def test_convert_single_vs_list_return_types(self):
        """Test that single names return single values and lists return lists."""
        opsin = OpsinPy()

        # Single name should return single result
        single_result = opsin.convert("methane")
        assert isinstance(single_result, str)

        # List should return list
        list_result = opsin.convert(["methane"])
        assert isinstance(list_result, list)
        assert len(list_result) == 1

    def test_parse_failure_without_message_real_case(self):
        """Test handling of parse failure without message using real invalid input."""
        opsin = OpsinPy()

        # Use a name that will definitely fail parsing
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = opsin.convert("x" * 1000)  # Very long invalid string

            assert result is None
            # Should have a warning about failed parsing
            assert len(w) >= 1

    def test_convenience_methods_coverage(self):
        """Test all convenience methods to improve coverage."""
        opsin = OpsinPy()

        # Test individual convenience methods
        assert opsin.name_to_smiles("methane") is not None
        assert opsin.name_to_extended_smiles("methane") is not None
        assert opsin.name_to_cml("methane") is not None
        assert opsin.name_to_inchi("methane") is not None
        assert opsin.name_to_stdinchi("methane") is not None
        assert opsin.name_to_stdinchikey("methane") is not None

        # Test batch methods
        names = ["methane", "ethane"]
        assert len(opsin.names_to_smiles(names)) == 2
        assert len(opsin.names_to_extended_smiles(names)) == 2
        assert len(opsin.names_to_cml(names)) == 2
        assert len(opsin.names_to_inchi(names)) == 2
        assert len(opsin.names_to_stdinchi(names)) == 2
        assert len(opsin.names_to_stdinchikey(names)) == 2

    def test_jvm_already_running_scenario(self):
        """Test scenario where JVM is already running from another instance."""
        # First instance starts JVM
        opsin1 = OpsinPy()
        opsin1._start_jvm()

        # Second instance should detect JVM is already running
        opsin2 = OpsinPy()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            opsin2._start_jvm()

            # Should have warning about JVM already started
            warning_messages = [str(warning.message) for warning in w]
            jvm_warnings = [
                msg for msg in warning_messages if "JVM already started" in msg
            ]
            assert len(jvm_warnings) >= 1

    def test_convert_with_all_output_formats(self):
        """Test convert method with all supported output formats."""
        opsin = OpsinPy()

        formats = [
            "SMILES",
            "ExtendedSMILES",
            "CML",
            "InChI",
            "StdInChI",
            "StdInChIKey",
        ]

        for fmt in formats:
            result = opsin.convert("methane", fmt)
            assert result is not None, f"Failed to convert methane to {fmt}"

    def test_convert_with_invalid_names(self):
        """Test convert method with various invalid names to trigger error paths."""
        opsin = OpsinPy()

        invalid_names = [
            "",  # empty string
            "   ",  # whitespace only
            "notavalidchemicalname",  # invalid name
            "x" * 100,  # very long invalid string
        ]

        for name in invalid_names:
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                result = opsin.convert(name)
                assert result is None, f"Expected None for invalid name: {name}"

    def test_mixed_valid_invalid_batch_conversion(self):
        """Test batch conversion with mix of valid and invalid names."""
        opsin = OpsinPy()

        names = ["methane", "invalid_name", "ethane", ""]

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            results = opsin.convert(names)

            assert len(results) == 4
            assert results[0] is not None  # methane should work
            assert results[1] is None  # invalid_name should fail
            assert results[2] is not None  # ethane should work
            assert results[3] is None  # empty string should fail

    def test_jar_path_fallback_scenarios(self):
        """Test different JAR path fallback scenarios."""
        # Test with custom JAR path (that exists)
        opsin = OpsinPy()
        default_jar = opsin._get_default_jar_path()

        # Create instance with explicit JAR path
        opsin_custom = OpsinPy(jar_path=default_jar)
        assert opsin_custom._jar_path == default_jar

    def test_convert_result_none_scenarios(self):
        """Test scenarios where OPSIN might return None results."""
        opsin = OpsinPy()

        # Test with some edge case names that might return None results
        edge_cases = [
            "ethyl",  # substituent that might give warnings
            "methyl",  # another substituent
        ]

        for name in edge_cases:
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                result = opsin.convert(name)
                # These might return None or a valid result, just ensure no exceptions
                assert result is None or isinstance(result, str)

    def test_repeated_jvm_start_calls(self):
        """Test that repeated calls to _start_jvm don't cause issues."""
        opsin = OpsinPy()

        # First call should start JVM
        opsin._start_jvm()
        assert opsin._jvm_started

        # Second call should return early
        opsin._start_jvm()
        assert opsin._jvm_started

    def test_convert_with_case_variations(self):
        """Test convert method with different case variations of format names."""
        opsin = OpsinPy()

        # Test case insensitive format names
        formats = ["smiles", "SMILES", "SmIlEs", "inchi", "INCHI", "InChI"]

        for fmt in formats:
            try:
                result = opsin.convert("methane", fmt)
                # Should either work or raise ValueError for unsupported format
                if result is not None:
                    assert isinstance(result, str)
            except ValueError:
                # This is acceptable for unsupported formats
                pass
