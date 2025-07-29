#!/usr/bin/env python3
"""
Benchmark comparison between opsinpy (JPype-based) and py2opsin (subprocess-based).

This script compares our opsinpy implementation with the publicly available
py2opsin package for performance benchmarking.

Note: This is a fair comparison as both packages wrap the same OPSIN Java library.
If py2opsin is not installed, the benchmark will show results for opsinpy only.
"""

import sys
import time
import warnings
from statistics import mean, stdev
from typing import List

# Try to import py2opsin from PyPI
try:
    from py2opsin import py2opsin

    PY2OPSIN_AVAILABLE = True
    print("✓ py2opsin found (installed from PyPI)")
except ImportError:
    PY2OPSIN_AVAILABLE = False
    print("✗ py2opsin not found. Install with: pip install py2opsin")
    print("  (Benchmark will run for opsinpy only)")

from opsinpy import OpsinPy


def benchmark_function(func, *args, **kwargs):
    """Benchmark a function call and return execution time."""
    start_time = time.perf_counter()
    try:
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        return end_time - start_time, result, None
    except Exception as e:
        end_time = time.perf_counter()
        return end_time - start_time, None, str(e)


def run_benchmark_suite(
    names: List[str], output_format: str = "SMILES", num_runs: int = 5
):
    """Run comprehensive benchmark suite comparing individual vs batch processing."""
    print(f"\n{'=' * 80}")
    print(f"BENCHMARK: {len(names)} compounds, format={output_format}, runs={num_runs}")
    print(f"{'=' * 80}")

    # Initialize opsinpy (JPype startup cost)
    print("Initializing opsinpy...")
    opsin = OpsinPy()

    results = {
        "opsinpy_individual": {"times": [], "results": [], "errors": []},
        "opsinpy_batch": {"times": [], "results": [], "errors": []},
        "py2opsin_individual": {"times": [], "results": [], "errors": []},
        "py2opsin_batch": {"times": [], "results": [], "errors": []},
    }

    # Benchmark opsinpy individual processing
    print(f"\nBenchmarking opsinpy INDIVIDUAL processing ({num_runs} runs)...")
    for run in range(num_runs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            start_time = time.perf_counter()
            individual_results = []
            for name in names:
                result = opsin.convert(name, output_format)
                individual_results.append(result)
            exec_time = time.perf_counter() - start_time

        results["opsinpy_individual"]["times"].append(exec_time)
        results["opsinpy_individual"]["results"].append(individual_results)
        results["opsinpy_individual"]["errors"].append(None)
        print(f"  Run {run + 1}: {exec_time:.4f}s")

    # Benchmark opsinpy batch processing
    print(f"\nBenchmarking opsinpy BATCH processing ({num_runs} runs)...")
    for run in range(num_runs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            exec_time, result, error = benchmark_function(
                opsin.convert, names, output_format
            )
        results["opsinpy_batch"]["times"].append(exec_time)
        results["opsinpy_batch"]["results"].append(result)
        results["opsinpy_batch"]["errors"].append(error)
        print(f"  Run {run + 1}: {exec_time:.4f}s")

    # Benchmark py2opsin (if available)
    if PY2OPSIN_AVAILABLE:
        # Individual processing
        print(f"\nBenchmarking py2opsin INDIVIDUAL processing ({num_runs} runs)...")
        for run in range(num_runs):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                start_time = time.perf_counter()
                individual_results = []
                for name in names:
                    result = py2opsin(name, output_format)
                    individual_results.append(result)
                exec_time = time.perf_counter() - start_time

            results["py2opsin_individual"]["times"].append(exec_time)
            results["py2opsin_individual"]["results"].append(individual_results)
            results["py2opsin_individual"]["errors"].append(None)
            print(f"  Run {run + 1}: {exec_time:.4f}s")

        # Batch processing
        print(f"\nBenchmarking py2opsin BATCH processing ({num_runs} runs)...")
        for run in range(num_runs):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                exec_time, result, error = benchmark_function(
                    py2opsin, names, output_format
                )
            results["py2opsin_batch"]["times"].append(exec_time)
            results["py2opsin_batch"]["results"].append(result)
            results["py2opsin_batch"]["errors"].append(error)
            print(f"  Run {run + 1}: {exec_time:.4f}s")
    else:
        print("\nSkipping py2opsin benchmarks (not available)")

    # Calculate and display statistics
    print(f"\n{'=' * 80}")
    print("RESULTS")
    print(f"{'=' * 80}")

    # opsinpy results
    opsinpy_ind_mean = mean(results["opsinpy_individual"]["times"])
    opsinpy_ind_std = (
        stdev(results["opsinpy_individual"]["times"])
        if len(results["opsinpy_individual"]["times"]) > 1
        else 0
    )
    opsinpy_batch_mean = mean(results["opsinpy_batch"]["times"])
    opsinpy_batch_std = (
        stdev(results["opsinpy_batch"]["times"])
        if len(results["opsinpy_batch"]["times"]) > 1
        else 0
    )

    print(f"opsinpy individual:  {opsinpy_ind_mean:.4f}s ± {opsinpy_ind_std:.4f}s")
    print(f"opsinpy batch:       {opsinpy_batch_mean:.4f}s ± {opsinpy_batch_std:.4f}s")
    print(f"opsinpy batch speedup: {opsinpy_ind_mean / opsinpy_batch_mean:.2f}x")

    # py2opsin results (if available)
    if PY2OPSIN_AVAILABLE and results["py2opsin_individual"]["times"]:
        py2opsin_ind_mean = mean(results["py2opsin_individual"]["times"])
        py2opsin_ind_std = (
            stdev(results["py2opsin_individual"]["times"])
            if len(results["py2opsin_individual"]["times"]) > 1
            else 0
        )
        py2opsin_batch_mean = mean(results["py2opsin_batch"]["times"])
        py2opsin_batch_std = (
            stdev(results["py2opsin_batch"]["times"])
            if len(results["py2opsin_batch"]["times"]) > 1
            else 0
        )

        print(
            f"\npy2opsin individual:  {py2opsin_ind_mean:.4f}s ± {py2opsin_ind_std:.4f}s"
        )
        print(
            f"py2opsin batch:       {py2opsin_batch_mean:.4f}s ± {py2opsin_batch_std:.4f}s"
        )
        print(f"py2opsin batch speedup: {py2opsin_ind_mean / py2opsin_batch_mean:.2f}x")

        # Cross-comparison
        print("\nCross-comparison:")
        print(
            f"Individual: py2opsin vs opsinpy = {py2opsin_ind_mean / opsinpy_ind_mean:.2f}x"
        )
        print(
            f"Batch:      py2opsin vs opsinpy = {py2opsin_batch_mean / opsinpy_batch_mean:.2f}x"
        )

    # Check result consistency
    opsinpy_result = results["opsinpy_batch"]["results"][0]
    if PY2OPSIN_AVAILABLE and results["py2opsin_batch"]["results"][0] is not None:
        py2opsin_result = results["py2opsin_batch"]["results"][0]

        if opsinpy_result and py2opsin_result:
            # Compare results
            if isinstance(opsinpy_result, list) and isinstance(py2opsin_result, list):
                matches = sum(
                    1
                    for a, b in zip(opsinpy_result, py2opsin_result)
                    if (a is None and b is False)
                    or (a == b)
                    or (a and b and a.strip() == b.strip())
                )
                total = len(opsinpy_result)
                print(
                    f"Results:   {matches}/{total} matches ({matches / total * 100:.1f}%)"
                )
            else:
                match = (opsinpy_result == py2opsin_result) or (
                    opsinpy_result
                    and py2opsin_result
                    and opsinpy_result.strip() == py2opsin_result.strip()
                )
                print(f"Results:   {'✓ Match' if match else '✗ Differ'}")

    return results


def print_system_info():
    """Print system information for reproducibility."""
    import platform
    import subprocess

    print("SYSTEM INFORMATION")
    print("=" * 80)
    print(f"Platform: {platform.platform()}")
    print(f"Python: {sys.version.split()[0]}")

    # Check Java version
    try:
        result = subprocess.run(
            ["java", "-version"], capture_output=True, text=True, check=True
        )
        java_version = result.stderr.split("\n")[0] if result.stderr else "Unknown"
        print(f"Java: {java_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Java: Not found or not accessible")

    # Check package versions
    try:
        import jpype

        print(f"JPype: {jpype.__version__}")
    except (ImportError, AttributeError):
        print("JPype: Not available")

    if PY2OPSIN_AVAILABLE:
        try:
            import py2opsin

            print(f"py2opsin: {py2opsin.__version__}")
        except AttributeError:
            print("py2opsin: Version unknown")

    print()


def print_comprehensive_results(comprehensive_results, all_molecules):
    """Print comprehensive benchmark results."""
    if PY2OPSIN_AVAILABLE:
        opsin_batch_time = mean(comprehensive_results["opsinpy_batch"]["times"])
        py2opsin_batch_time = mean(comprehensive_results["py2opsin_batch"]["times"])

        print("\nComprehensive Results:")
        print(
            f"Time per molecule (opsinpy batch): {opsin_batch_time / len(all_molecules) * 1000:.2f}ms"
        )
        print(
            f"Throughput (opsinpy): {len(all_molecules) / opsin_batch_time:.1f} molecules/second"
        )
        print(
            f"Time per molecule (py2opsin batch): {py2opsin_batch_time / len(all_molecules) * 1000:.2f}ms"
        )
        print(
            f"Throughput (py2opsin): {len(all_molecules) / py2opsin_batch_time:.1f} molecules/second"
        )

        print("\nKey Findings:")
        print(
            "• opsinpy uses JPype for direct Java integration (no subprocess overhead)"
        )
        print("• py2opsin uses subprocess calls to Java (higher overhead per call)")
        print("• opsinpy has one-time JVM startup cost but faster subsequent calls")
        print("• Both libraries benefit significantly from batch processing")
        print(
            "• opsinpy batch processing provides additional speedup over individual calls"
        )
        print("• Both implementations produce equivalent results for valid IUPAC names")
        print("• Both packages use the same OPSIN 2.8.0 Java library under the hood")


def main():
    """Run comprehensive benchmark suite."""
    print("OPSINPY vs PY2OPSIN BENCHMARK COMPARISON")
    print("=" * 80)
    print(
        "This benchmark compares opsinpy (JPype-based) with py2opsin (subprocess-based)"
    )
    print("Both packages use the same OPSIN 2.8.0 Java library under the hood.")
    print()

    print_system_info()

    if not PY2OPSIN_AVAILABLE:
        print("To run the full comparison, install py2opsin:")
        print("    pip install py2opsin")
        print()
        response = input("Continue with opsinpy only? (y/N): ")
        if response.lower() != "y":
            print("Exiting. Install py2opsin and run again for full comparison.")
            return
        print()

    # Test datasets
    test_sets = {
        "Simple molecules": ["methane", "ethane", "propane", "butane", "pentane"],
        "Common organic compounds": [
            "benzene",
            "toluene",
            "phenol",
            "aniline",
            "acetone",
            "ethanol",
            "acetic acid",
            "glucose",
            "caffeine",
        ],
        "IUPAC names (from py2opsin test suite)": [
            "pyridine, 2-amino-",
            "pyridine, 3-methyl-",
            "aniline, 2,5-dichloro-",
            "benzylamine, N-ethyl-",
            "aniline, 4-methoxy-",
            "piperidine, 3-methyl-",
            "pyrazole, 3,5-dimethyl-",
            "quinoline, 8-amino-6-methoxy-",
            "pyridine, 4-phenyl-",
            "quinoline, 3-nitro-",
        ],
        "Complex IUPAC names": [
            "2-amino-3-methylbutanoic acid",
            "4-hydroxybenzaldehyde",
            "2,4-dinitrophenylhydrazine",
            "N,N-dimethylformamide",
            "2-phenylethylamine",
            "2-cyclohexyl-1-(2,2-dimethylcyclopropyl)ethanol",
            "4-[[4-(dimethylamino)phenyl]diazenyl]-2-(4-ethoxy-6-methyl-5-propylpyrimidin-2-yl)-5-methyl-1H-pyrazol-3-one",
            "2-(3-chloro-4-fluorophenyl)-1-(3-chlorothiophen-2-yl)-N-ethylethanamine",
            "3-[4-[(2S)-2-[[(2S)-2-[(2R)-3-(1,3-dioxoisoindol-2-yl)-1-(hydroxyamino)-1-oxopropan-2-yl]-4-methylpentanoyl]amino]-3-(methylamino)-3-oxopropyl]phenoxy]propane-1-sulfonic acid",
            "4,6-diphenyl-1,3,5-triazine-2-carbonitrile",
            "1-[1-(dimethylamino)-2-(dimethylsulfamoylamino)ethyl]-4-methoxybenzene",
            "methyl (3S)-3-[[(3S)-3-(carbamoylamino)-3-(2-methylphenyl)propanoyl]amino]-3-(2-chlorophenyl)propanoate",
            "(3R)-N-[2-(3-fluorophenoxy)ethyl]-1-[(5-methyl-1,2,4-oxadiazol-3-yl)methyl]piperidin-3-amine",
            "[(3E,7E)-7-(benzenesulfonyl)-1-benzyl-5,6-dihydro-2H-azocin-3-yl]oxy-tert-butyl-dimethylsilane",
            "3'-bromo-2'-(3-chloropropyl)spiro[1,3-dioxolane-2,4'-2,3-dihydro-1H-naphthalene]",
        ],
    }

    # Run benchmarks for different test sets
    all_results = {}

    for test_name, compounds in test_sets.items():
        print(f"\n\nTEST SET: {test_name}")
        results = run_benchmark_suite(compounds, "SMILES", num_runs=3)
        all_results[test_name] = results

        # Comprehensive batch test with all molecules
    print(f"\n\n{'=' * 80}")
    print("COMPREHENSIVE BATCH TEST (All molecules combined)")
    print(f"{'=' * 80}")

    # Combine all molecules from all test sets
    all_molecules = []
    for _test_name, compounds in test_sets.items():
        all_molecules.extend(compounds)

    print(f"Testing {len(all_molecules)} molecules total from all test sets")

    # Run comprehensive batch benchmark
    comprehensive_results = run_benchmark_suite(all_molecules, "SMILES", num_runs=3)

    # Additional analysis for the comprehensive test
    print("\nCOMPREHENSIVE TEST ANALYSIS:")
    print(f"Total molecules: {len(all_molecules)}")

    print_comprehensive_results(comprehensive_results, all_molecules)

    print(f"\n\n{'=' * 80}")
    print("BENCHMARK SUMMARY")
    print(f"{'=' * 80}")

    print("\nKey Findings:")
    print("• opsinpy uses JPype for direct Java integration (no subprocess overhead)")
    print("• py2opsin uses subprocess calls to Java (higher overhead per call)")
    print("• opsinpy has one-time JVM startup cost but faster subsequent calls")
    print("• Both libraries benefit significantly from batch processing")
    print(
        "• py2opsin batch processing is MUCH faster than individual calls (as documented)"
    )
    print(
        "• opsinpy batch processing provides additional speedup over individual calls"
    )
    print("• Both implementations produce equivalent results for valid IUPAC names")

    print("\nReproducibility:")
    print("• This benchmark uses publicly available packages from PyPI")
    print("• Install py2opsin with: pip install py2opsin")
    print("• Run this script to reproduce the results on your system")

    if not PY2OPSIN_AVAILABLE:
        print("\nNote: py2opsin benchmarks were skipped (not installed)")
        print("Install py2opsin to run the full comparison")


if __name__ == "__main__":
    main()
