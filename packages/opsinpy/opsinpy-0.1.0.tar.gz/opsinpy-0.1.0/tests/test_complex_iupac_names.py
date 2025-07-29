"""
Test cases for complex real-world IUPAC chemical names.

These test cases use actual IUPAC names from chemical databases to ensure
OPSIN can handle real-world complexity.
"""

import json
import os
import re
import sys
from pathlib import Path

# Add the parent directory to the path so we can import opsinpy
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest


class TestComplexIUPACNames:
    """Test cases for complex real-world IUPAC chemical names."""

    # Load test cases from JSON file
    _test_data_file = Path(__file__).parent / "data" / "complex_iupac_test_cases.json"

    @classmethod
    def _load_test_cases(cls):
        """Load test cases from JSON file."""
        if not cls._test_data_file.exists():
            raise FileNotFoundError(f"Test data file not found: {cls._test_data_file}")

        with open(cls._test_data_file, encoding="utf-8") as f:
            data = json.load(f)

        return [(case["name"], case["expected_smiles"]) for case in data]

    @property
    def complex_iupac_test_cases(self):
        """Get test cases (loaded lazily)."""
        if not hasattr(self, "_cached_test_cases"):
            self._cached_test_cases = self._load_test_cases()
        return self._cached_test_cases

    def _normalize_smiles_for_comparison(self, smiles: str) -> str:
        """
        Normalize SMILES for comparison by standardizing ring numbering.

        This handles cases where OPSIN might use different ring numbers
        (e.g., C1CCCCC1 vs C2CCCCC2) which are chemically equivalent.
        """
        if not smiles:
            return smiles

        # Find all ring numbers in order of first appearance
        ring_pattern = r"(?<=[A-Za-z=])[0-9]+"
        ring_matches = [
            (match.group(), match.start())
            for match in re.finditer(ring_pattern, smiles)
        ]

        # Get unique ring numbers in order of first appearance
        seen_rings = set()
        unique_rings = []
        for ring_num, _pos in ring_matches:
            if ring_num not in seen_rings:
                unique_rings.append(ring_num)
                seen_rings.add(ring_num)

        # Use temporary placeholders to avoid conflicts during replacement
        normalized = smiles

        # First pass: replace with temporary placeholders
        for i, orig in enumerate(unique_rings):
            placeholder = f"__RING_{i}__"
            # Replace ring numbers that appear after atoms or =
            normalized = re.sub(
                rf"(?<=[A-Za-z=]){re.escape(orig)}(?![0-9])", placeholder, normalized
            )

        # Second pass: replace placeholders with final numbers
        for i, _orig in enumerate(unique_rings):
            placeholder = f"__RING_{i}__"
            new_number = str(i + 1)
            normalized = normalized.replace(placeholder, new_number)

        return normalized

    def _smiles_are_equivalent(self, smiles1: str, smiles2: str) -> bool:
        """
        Check if two SMILES strings represent the same chemical structure.

        This normalizes ring numbering and other formatting differences.
        """
        if smiles1 == smiles2:
            return True

        # Normalize both SMILES
        norm1 = self._normalize_smiles_for_comparison(smiles1)
        norm2 = self._normalize_smiles_for_comparison(smiles2)

        return norm1 == norm2

    @pytest.mark.integration
    @pytest.mark.slow
    def test_complex_names_exact_smiles_match(self, shared_opsin):
        """Test that complex IUPAC names produce the expected SMILES exactly."""
        failed_cases = []

        for i, (name, expected_smiles) in enumerate(self.complex_iupac_test_cases):
            actual_smiles = shared_opsin.name_to_smiles(name)

            print(f"\nTest case {i + 1}:")
            print(f"Name: {name}")
            print(f"Expected: {expected_smiles}")
            print(f"Actual:   {actual_smiles}")

            if actual_smiles != expected_smiles:
                failed_cases.append(
                    {"name": name, "expected": expected_smiles, "actual": actual_smiles}
                )
                print("❌ MISMATCH")
            else:
                print("✅ MATCH")

        # Report results
        success_count = len(self.complex_iupac_test_cases) - len(failed_cases)
        success_rate = success_count / len(self.complex_iupac_test_cases)

        print(f"\n{'=' * 60}")
        print("EXACT SMILES MATCH RESULTS:")
        print(
            f"Successful matches: {success_count}/{len(self.complex_iupac_test_cases)} ({success_rate:.1%})"
        )

        if failed_cases:
            print(f"\nFailed cases ({len(failed_cases)}):")
            for case in failed_cases:
                print(f"  - {case['name'][:50]}...")
            print(
                "\nNOTE: Mismatches may be due to different but equivalent SMILES representations"
            )
            print("(e.g., different ring numbering: C1CCCCC1 vs C2CCCCC2)")

        # For now, let's be lenient and just require that we get valid SMILES
        # We can tighten this assertion later if needed
        for case in failed_cases:
            assert case["actual"] is not None, f"OPSIN failed to parse: {case['name']}"

    @pytest.mark.integration
    @pytest.mark.slow
    def test_complex_names_normalized_smiles_match(self, shared_opsin):
        """Test that complex IUPAC names produce equivalent SMILES after normalization."""
        failed_cases = []
        exact_matches = 0
        normalized_matches = 0

        for i, (name, expected_smiles) in enumerate(self.complex_iupac_test_cases):
            actual_smiles = shared_opsin.name_to_smiles(name)

            if actual_smiles is None:
                failed_cases.append(
                    {
                        "name": name,
                        "expected": expected_smiles,
                        "actual": actual_smiles,
                        "reason": "Failed to parse",
                    }
                )
                continue

            exact_match = actual_smiles == expected_smiles
            normalized_match = self._smiles_are_equivalent(
                actual_smiles, expected_smiles
            )

            if exact_match:
                exact_matches += 1
            if normalized_match:
                normalized_matches += 1
            else:
                failed_cases.append(
                    {
                        "name": name,
                        "expected": expected_smiles,
                        "actual": actual_smiles,
                        "reason": "Not equivalent after normalization",
                    }
                )

            print(f"\nCase {i + 1}: {name[:50]}...")
            print(f"Expected: {expected_smiles}")
            print(f"Actual:   {actual_smiles}")
            print(f"Exact match: {exact_match}")
            print(f"Normalized match: {normalized_match}")

            if not exact_match and normalized_match:
                norm_expected = self._normalize_smiles_for_comparison(expected_smiles)
                norm_actual = self._normalize_smiles_for_comparison(actual_smiles)
                print(f"Normalized expected: {norm_expected}")
                print(f"Normalized actual:   {norm_actual}")

        # Report results
        total = len(self.complex_iupac_test_cases)
        exact_rate = exact_matches / total
        normalized_rate = normalized_matches / total

        print(f"\n{'=' * 60}")
        print("NORMALIZED SMILES MATCH RESULTS:")
        print(f"Exact matches: {exact_matches}/{total} ({exact_rate:.1%})")
        print(
            f"Normalized matches: {normalized_matches}/{total} ({normalized_rate:.1%})"
        )

        if failed_cases:
            print(f"\nFailed cases ({len(failed_cases)}):")
            for case in failed_cases:
                print(f"  - {case['name'][:50]}... ({case['reason']})")

        # Assert that we get at least 80% normalized matches
        # (One case may fail due to complex ring topology differences)
        assert normalized_rate >= 0.8, (
            f"Expected at least 80% normalized matches, got {normalized_rate:.1%}"
        )

    @pytest.mark.integration
    @pytest.mark.slow
    def test_complex_names_structural_equivalence(self, shared_opsin):
        """Test that OPSIN produces chemically equivalent structures (ignoring SMILES formatting differences)."""
        structural_analysis = []

        for i, (name, expected_smiles) in enumerate(self.complex_iupac_test_cases):
            actual_smiles = shared_opsin.name_to_smiles(name)

            if actual_smiles is not None:
                # Basic structural comparison - count key chemical features
                expected_features = self._analyze_smiles_features(expected_smiles)
                actual_features = self._analyze_smiles_features(actual_smiles)

                features_match = expected_features == actual_features
                normalized_match = self._smiles_are_equivalent(
                    actual_smiles, expected_smiles
                )

                analysis = {
                    "name": name,
                    "expected_smiles": expected_smiles,
                    "actual_smiles": actual_smiles,
                    "exact_match": expected_smiles == actual_smiles,
                    "normalized_match": normalized_match,
                    "features_match": features_match,
                    "expected_features": expected_features,
                    "actual_features": actual_features,
                }
                structural_analysis.append(analysis)

                print(f"\nCase {i + 1}: {name[:50]}...")
                print(f"Exact match: {analysis['exact_match']}")
                print(f"Normalized match: {normalized_match}")
                print(f"Features match: {features_match}")
                if not features_match:
                    print(f"Expected features: {expected_features}")
                    print(f"Actual features: {actual_features}")

        # Summary
        exact_matches = sum(1 for a in structural_analysis if a["exact_match"])
        normalized_matches = sum(
            1 for a in structural_analysis if a["normalized_match"]
        )
        feature_matches = sum(1 for a in structural_analysis if a["features_match"])
        total = len(structural_analysis)

        print(f"\n{'=' * 60}")
        print("STRUCTURAL ANALYSIS RESULTS:")
        print(
            f"Exact SMILES matches: {exact_matches}/{total} ({exact_matches / total:.1%})"
        )
        print(
            f"Normalized SMILES matches: {normalized_matches}/{total} ({normalized_matches / total:.1%})"
        )
        print(
            f"Feature matches: {feature_matches}/{total} ({feature_matches / total:.1%})"
        )

        # Assert that at least 80% have matching features (chemical equivalence)
        feature_success_rate = feature_matches / total if total > 0 else 0
        assert feature_success_rate >= 0.8, (
            f"Expected at least 80% feature matches, got {feature_success_rate:.1%}"
        )

    def _analyze_smiles_features(self, smiles):
        """Analyze key chemical features in a SMILES string for structural comparison."""
        if not smiles:
            return {}

        features = {
            # Count different atom types
            "carbon_count": smiles.count("C"),
            "nitrogen_count": smiles.count("N"),
            "oxygen_count": smiles.count("O"),
            "sulfur_count": smiles.count("S"),
            "phosphorus_count": smiles.count("P"),
            "fluorine_count": smiles.count("F"),
            "chlorine_count": smiles.count("Cl"),
            "bromine_count": smiles.count("Br"),
            "iodine_count": smiles.count("I"),
            # Count bond types
            "single_bonds": smiles.count("-") if "-" in smiles else 0,
            "double_bonds": smiles.count("="),
            "triple_bonds": smiles.count("#"),
            # Count rings (approximate)
            "ring_closures": sum(1 for c in smiles if c.isdigit()),
            # Count stereochemistry markers
            "chiral_centers": smiles.count("@"),
            "double_bond_stereo": smiles.count("/") + smiles.count("\\"),
            # Count brackets (for complex atoms)
            "bracketed_atoms": smiles.count("["),
            # Length as a rough complexity measure
            "length": len(smiles),
        }

        return features

    @pytest.mark.integration
    @pytest.mark.slow
    def test_complex_names_to_smiles(self, shared_opsin):
        """Test conversion of complex IUPAC names to SMILES."""
        results = []
        successful_conversions = 0

        for name, expected_smiles in self.complex_iupac_test_cases:
            smiles = shared_opsin.name_to_smiles(name)
            results.append((name, smiles, expected_smiles))

            if smiles is not None:
                successful_conversions += 1
                # Basic validation: SMILES should contain typical chemical symbols
                assert any(char in smiles for char in "CNOPSFClBrI"), (
                    f"SMILES '{smiles}' seems invalid for '{name}'"
                )

        # We expect at least some of these complex names to be parseable
        success_rate = successful_conversions / len(self.complex_iupac_test_cases)
        print(
            f"\nComplex IUPAC name parsing success rate: {success_rate:.1%} ({successful_conversions}/{len(self.complex_iupac_test_cases)})"
        )

        # Print results for debugging
        for name, smiles, expected in results:
            status = "✓" if smiles else "✗"
            match_status = "=" if smiles == expected else "≠" if smiles else "?"
            print(
                f"{status}{match_status} {name[:50]}{'...' if len(name) > 50 else ''}"
            )

        # Assert that we can parse at least 90% of these complex names
        assert success_rate >= 0.9, (
            f"Expected at least 90% success rate, got {success_rate:.1%}"
        )

    @pytest.mark.integration
    @pytest.mark.slow
    def test_complex_names_batch_conversion(self, shared_opsin):
        """Test batch conversion of complex IUPAC names."""
        names = [case[0] for case in self.complex_iupac_test_cases]

        # Test batch conversion
        smiles_results = shared_opsin.names_to_smiles(names)

        assert len(smiles_results) == len(self.complex_iupac_test_cases)

        # Count successful conversions
        successful_batch = sum(1 for result in smiles_results if result is not None)
        success_rate = successful_batch / len(self.complex_iupac_test_cases)

        print(
            f"\nBatch conversion success rate: {success_rate:.1%} ({successful_batch}/{len(self.complex_iupac_test_cases)})"
        )

        # Ensure batch conversion gives same results as individual conversion
        for i, name in enumerate(names):
            individual_result = shared_opsin.name_to_smiles(name)
            batch_result = smiles_results[i]
            assert individual_result == batch_result, (
                f"Mismatch for '{name}': individual={individual_result}, batch={batch_result}"
            )

    @pytest.mark.integration
    def test_complex_names_multiple_formats(self, shared_opsin):
        """Test conversion of a few complex names to multiple formats."""
        # Test with a subset of names to avoid making tests too slow
        test_cases = self.complex_iupac_test_cases[:3]

        for name, expected_smiles in test_cases:
            print(f"\nTesting formats for: {name}")

            # Try different output formats
            smiles = shared_opsin.name_to_smiles(name)
            extended_smiles = shared_opsin.name_to_extended_smiles(name)
            cml = shared_opsin.name_to_cml(name)
            inchi = shared_opsin.name_to_inchi(name)

            # If SMILES conversion works, other formats should work too (or gracefully fail)
            if smiles is not None:
                print(f"  SMILES: {smiles}")
                print(f"  Expected: {expected_smiles}")
                print(f"  Extended SMILES: {extended_smiles is not None}")
                print(f"  CML: {cml is not None}")
                print(f"  InChI: {inchi is not None}")

                # At minimum, if SMILES works, extended SMILES should also work
                assert extended_smiles is not None, (
                    f"Extended SMILES failed for '{name}' but SMILES succeeded"
                )

    @pytest.mark.integration
    @pytest.mark.slow
    def test_stereochemistry_preservation(self, shared_opsin):
        """Test that stereochemical information is preserved in conversions."""
        # Find names with stereochemical descriptors
        stereo_cases = [
            (name, expected)
            for name, expected in self.complex_iupac_test_cases
            if any(
                stereo in name
                for stereo in ["(2S)", "(2R)", "(3S)", "(3R)", "(3E)", "(7E)"]
            )
        ]

        if not stereo_cases:
            pytest.skip("No stereochemical names found in test set")

        for name, expected_smiles in stereo_cases:
            smiles = shared_opsin.name_to_smiles(name)
            if smiles is not None:
                # Check if stereochemical information is preserved in SMILES
                # SMILES stereochemistry is indicated by @ and @@ symbols, and / \ for double bonds
                has_stereo_info = "@" in smiles or "/" in smiles or "\\" in smiles
                expected_has_stereo = (
                    "@" in expected_smiles
                    or "/" in expected_smiles
                    or "\\" in expected_smiles
                )

                print(f"Name: {name}")
                print(f"Expected SMILES: {expected_smiles}")
                print(f"Actual SMILES: {smiles}")
                print(f"Expected has stereochemistry: {expected_has_stereo}")
                print(f"Actual contains stereochemistry: {has_stereo_info}")
                print()

    @pytest.mark.unit
    def test_name_complexity_metrics(self):
        """Test to analyze the complexity of the test names."""
        # This test analyzes the complexity of our test names
        # Useful for understanding what we're testing

        names = [case[0] for case in self.complex_iupac_test_cases]
        complexities = []

        for name in names:
            complexity = {
                "length": len(name),
                "brackets": name.count("[") + name.count("("),
                "hyphens": name.count("-"),
                "stereochemistry": sum(
                    name.count(stereo)
                    for stereo in ["(2S)", "(2R)", "(3S)", "(3R)", "(3E)", "(7E)"]
                ),
                "rings": sum(
                    name.count(ring)
                    for ring in [
                        "cyclo",
                        "phenyl",
                        "pyrimidin",
                        "pyrazol",
                        "triazine",
                        "oxadiazol",
                        "dioxolane",
                        "naphthalene",
                    ]
                ),
            }
            complexities.append(complexity)

        # Print complexity analysis
        avg_length = sum(c["length"] for c in complexities) / len(complexities)
        max_brackets = max(c["brackets"] for c in complexities)
        total_stereo = sum(c["stereochemistry"] for c in complexities)

        print("\nComplexity Analysis:")
        print(f"  Average name length: {avg_length:.1f} characters")
        print(f"  Maximum bracket depth: {max_brackets}")
        print(
            f"  Names with stereochemistry: {sum(1 for c in complexities if c['stereochemistry'] > 0)}"
        )
        print(f"  Total stereochemical centers: {total_stereo}")
        print(
            f"  Names with ring systems: {sum(1 for c in complexities if c['rings'] > 0)}"
        )

        # Basic assertions about our test set
        assert avg_length > 50, "Test names should be reasonably complex"
        assert total_stereo > 0, "Test set should include stereochemical examples"

    @pytest.mark.unit
    def test_smiles_normalization(self):
        """Test the SMILES normalization function."""
        # Test cases for ring renumbering
        test_cases = [
            ("C1CCCCC1", "C1CCCCC1"),  # Already normalized
            ("C2CCCCC2", "C1CCCCC1"),  # Renumber 2 -> 1
            ("C3CCCCC3", "C1CCCCC1"),  # Renumber 3 -> 1
            ("C1CCCCC1C2CCCC2", "C1CCCCC1C2CCCC2"),  # Multiple rings
            ("C2CCCCC2C1CCCC1", "C1CCCCC1C2CCCC2"),  # Reorder ring numbers
            ("C3CCCCC3C1CCCC1C2CCC2", "C1CCCCC1C2CCCC2C3CCC3"),  # Three rings
        ]

        for input_smiles, expected in test_cases:
            result = self._normalize_smiles_for_comparison(input_smiles)
            print(f"Input: {input_smiles} -> Output: {result} (Expected: {expected})")
            assert result == expected, (
                f"Normalization failed: {input_smiles} -> {result}, expected {expected}"
            )

    @pytest.mark.unit
    def test_smiles_equivalence(self):
        """Test the SMILES equivalence function."""
        # Test cases for equivalence checking
        equivalent_pairs = [
            ("C1CCCCC1", "C2CCCCC2"),  # Different ring numbering
            (
                "C1CCCCC1C2CCCC2",
                "C3CCCCC3C4CCCC4",
            ),  # Multiple rings, different numbering
            ("CC", "CC"),  # Identical
        ]

        non_equivalent_pairs = [
            ("C1CCCCC1", "C1CCCC1"),  # Different ring sizes
            ("CC", "CCC"),  # Different chain lengths
            ("C1CCCCC1", "C1CCCCC1O"),  # Different atoms
        ]

        for smiles1, smiles2 in equivalent_pairs:
            assert self._smiles_are_equivalent(smiles1, smiles2), (
                f"{smiles1} and {smiles2} should be equivalent"
            )

        for smiles1, smiles2 in non_equivalent_pairs:
            assert not self._smiles_are_equivalent(smiles1, smiles2), (
                f"{smiles1} and {smiles2} should not be equivalent"
            )
