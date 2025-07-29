#!/usr/bin/env python3
"""
Basic usage examples for opsinpy package.

This script demonstrates the basic functionality of the opsinpy package
for converting chemical names to various formats.
"""

import os
import sys
import traceback

# Add the parent directory to the path so we can import opsinpy
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from opsinpy import OpsinPy


def main():
    """Demonstrate basic usage of OpsinPy."""
    print("OPSIN Python Bindings - Basic Usage Examples")
    print("=" * 50)

    try:
        # Initialize the converter
        print("Initializing OPSIN...")
        opsin = OpsinPy()
        print("✓ OPSIN initialized successfully")
        print()

        # Single name conversions
        print("Single Name Conversions:")
        print("-" * 25)

        test_names = [
            "ethane",
            "acetamide",
            "benzene",
            "2-methylpropane",
            "cyclohexane",
        ]

        for name in test_names:
            smiles = opsin.name_to_smiles(name)
            print(f"{name:20} → {smiles}")

        print()

        # Different output formats
        print("Different Output Formats:")
        print("-" * 26)

        test_name = "acetamide"
        print(f"Chemical name: {test_name}")

        smiles = opsin.name_to_smiles(test_name)
        cml = opsin.name_to_cml(test_name)
        inchi = opsin.name_to_inchi(test_name)
        stdinchi = opsin.name_to_stdinchi(test_name)
        stdinchikey = opsin.name_to_stdinchikey(test_name)

        print(f"SMILES:       {smiles}")
        print(f"InChI:        {inchi}")
        print(f"StdInChI:     {stdinchi}")
        print(f"StdInChIKey:  {stdinchikey}")
        if cml:
            print(
                f"CML:          {cml[:100]}..."
                if len(cml) > 100
                else f"CML:          {cml}"
            )

        print()

        # Batch conversion
        print("Batch Conversion:")
        print("-" * 17)

        batch_names = ["methane", "ethane", "propane", "butane"]
        batch_smiles = opsin.names_to_smiles(batch_names)

        print("Alkane series:")
        for name, smiles in zip(batch_names, batch_smiles):
            print(f"  {name:10} → {smiles}")

        print()

        # Options demonstration
        print("Using Options:")
        print("-" * 14)

        # Try with radicals
        radical_name = "ethyl"
        without_radicals = opsin.name_to_smiles(radical_name)
        with_radicals = opsin.name_to_smiles(radical_name, allow_radicals=True)

        print(f"'{radical_name}' without allow_radicals: {without_radicals}")
        print(f"'{radical_name}' with allow_radicals:    {with_radicals}")

        print()
        print("✓ All examples completed successfully!")

    except Exception as e:
        print(f"✗ Error: {e}")
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
