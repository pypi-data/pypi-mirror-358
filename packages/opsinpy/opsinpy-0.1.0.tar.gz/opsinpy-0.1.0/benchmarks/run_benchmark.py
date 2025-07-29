#!/usr/bin/env python3
"""
Helper script to install dependencies and run the opsinpy vs py2opsin benchmark.

This script will:
1. Check if py2opsin is available
2. Offer to install it if missing
3. Run the benchmark comparison
"""

import importlib.util
import subprocess
import sys
from pathlib import Path


def check_py2opsin():
    """Check if py2opsin is installed."""
    return importlib.util.find_spec("py2opsin") is not None


def install_py2opsin():
    """Install py2opsin using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "py2opsin"])
        return True
    except subprocess.CalledProcessError:
        return False


def run_benchmark():
    """Run the benchmark comparison script."""
    benchmark_script = Path(__file__).parent / "benchmark_comparison.py"
    try:
        subprocess.check_call([sys.executable, str(benchmark_script)])
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    """Main function to orchestrate the benchmark setup and execution."""
    print("OPSINPY BENCHMARK SETUP")
    print("=" * 40)
    print()

    # Check py2opsin availability
    if check_py2opsin():
        print("✓ py2opsin is already installed")
    else:
        print("✗ py2opsin not found")
        print()
        response = input("Would you like to install py2opsin for comparison? (y/N): ")

        if response.lower() == "y":
            print("Installing py2opsin...")
            if install_py2opsin():
                print("✓ py2opsin installed successfully")
            else:
                print("✗ Failed to install py2opsin")
                print(
                    "Failed to install py2opsin. Running benchmark with opsinpy only."
                )
        else:
            print(
                "Skipping py2opsin installation. Running benchmark with opsinpy only."
            )

    print()
    print("Running benchmark...")
    print("=" * 40)

    if run_benchmark():
        print()
        print("✓ Benchmark completed successfully")
    else:
        print()
        print("✗ Benchmark failed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
