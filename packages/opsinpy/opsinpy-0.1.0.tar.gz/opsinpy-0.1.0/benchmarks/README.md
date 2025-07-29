# OPSINPY Benchmarks

This directory contains benchmark scripts and results comparing `opsinpy` with `py2opsin`.

## Files

- **`benchmark_comparison.py`** - Main benchmark script that compares performance
- **`run_benchmark.py`** - Helper script for automated setup and execution
- **`BENCHMARK_RESULTS.md`** - Detailed benchmark results and analysis

## Quick Start

### Option 1: Automated Setup

```bash
python run_benchmark.py
```

This script will:
1. Check if `py2opsin` is installed
2. Offer to install it if missing
3. Run the complete benchmark suite

### Option 2: Manual Setup

```bash
# Install py2opsin for comparison
pip install py2opsin

# Run the benchmark
python benchmark_comparison.py
```

### Option 3: opsinpy Only

If you don't want to install `py2opsin`, you can run the benchmark with `opsinpy` only:

```bash
python benchmark_comparison.py
```

The script will detect that `py2opsin` is not available and run benchmarks for `opsinpy` only.

## What the Benchmark Tests

### Test Sets
1. **Simple molecules** (5 compounds)
2. **Common organic compounds** (9 compounds)  
3. **IUPAC names from py2opsin test suite** (10 compounds)
4. **Complex IUPAC names** (15 compounds including stereochemistry)
5. **Comprehensive batch test** (all 39 compounds combined)

### Performance Metrics
- **Execution time** (multiple runs with statistics)
- **Result accuracy** (comparison between implementations)
- **Individual vs batch processing** comparison for both libraries
- **Throughput analysis** (molecules per second)
- **Real-world performance** with substantial datasets

### Key Findings

- **Both libraries benefit significantly from batch processing**
- **py2opsin batch processing is MUCH faster than individual calls** (as documented)
- **opsinpy is faster in both individual and batch modes**
- **100% result accuracy** - identical outputs
- **Fair comparison requires testing both processing modes**

## Reproducibility

The benchmark is designed for complete reproducibility:

- Uses **publicly available packages** from PyPI
- Reports **system information** for context
- Includes **statistical analysis** (mean ± std dev)
- **Validates results** between implementations
- **Multiple runs** to account for variance

## System Requirements

- Python 3.8+
- Java 8+ (required by OPSIN)
- opsinpy (this package)
- py2opsin (optional, for comparison)

## Understanding the Results

### Performance Numbers

- **opsinpy**: Direct Java integration via JPype
  - First call: ~680ms (JVM startup)
  - Subsequent calls: 0.5-60ms
  
- **py2opsin**: Subprocess-based approach
  - Every call: ~500ms (subprocess + JVM startup/shutdown)

### When opsinpy Excels

- Multiple chemical name conversions
- Batch processing workflows
- High-throughput applications
- Data processing pipelines

### When py2opsin Might Be Preferred

- Single, occasional conversions
- Minimal memory footprint requirements
- Process isolation needs
- Legacy system compatibility

## Contributing

If you find issues with the benchmarks or have suggestions for additional test cases, please open an issue or submit a pull request. 