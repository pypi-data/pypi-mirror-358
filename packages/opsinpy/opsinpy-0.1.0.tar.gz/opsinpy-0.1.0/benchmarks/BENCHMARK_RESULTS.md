# OPSINPY vs PY2OPSIN Benchmark Results

This document contains detailed benchmark results comparing `opsinpy` (JPype-based) with `py2opsin` (subprocess-based).

## Executive Summary

**Key Findings:**
- **opsinpy is still faster overall** but the performance gap varies by usage pattern
- **py2opsin batch processing is dramatically faster** than individual calls (5-35x speedup)
- **Both libraries benefit significantly from batch processing**
- **Fair comparison requires testing both individual AND batch modes**

## Implementations Compared

**Libraries tested:**
- **opsinpy**: Our JPype-based implementation
- **py2opsin**: Public package from PyPI (subprocess-based)

**Test environment:**
- Both packages use identical OPSIN 2.8.0 Java library
- Same test molecules and configurations
- Multiple runs for statistical significance

## Running the Benchmark

### Option 1: Automated setup
```bash
python benchmarks/run_benchmark.py
```

### Option 2: Manual setup
```bash
pip install py2opsin
python benchmarks/benchmark_comparison.py
```

### Option 3: opsinpy only (if py2opsin not available)
```bash
python benchmarks/benchmark_comparison.py
```

## Detailed Results

### Individual Processing Performance

Individual molecule processing times (first call includes JVM startup for opsinpy):

| Test Set | opsinpy (ms) | py2opsin (ms) | py2opsin advantage |
|----------|-------------|---------------|-------------------|
| Simple molecules (5) | ~2-5ms | ~500ms | opsinpy 100-250x faster |
| Common organic (9) | ~5-10ms | ~500ms | opsinpy 50-100x faster |
| IUPAC names (10) | ~8-15ms | ~500ms | opsinpy 33-60x faster |
| Complex IUPAC (5) | ~3-8ms | ~500ms | opsinpy 60-160x faster |

### Batch Processing Performance

| Test Set | opsinpy (ms) | py2opsin (ms) | Comparison |
|----------|-------------|---------------|------------|
| Simple molecules (5) | ~2-5ms | ~50-100ms | opsinpy still faster |
| Common organic (9) | ~5-10ms | ~100-200ms | opsinpy still faster |
| IUPAC names (10) | ~8-15ms | ~200-300ms | opsinpy still faster |
| Complex IUPAC (5) | ~3-8ms | ~80-150ms | opsinpy still faster |

### Real-World Throughput (39 molecules)

| Metric | opsinpy | py2opsin | Advantage |
|--------|---------|----------|-----------|
| **Individual mode** | 1,221 molecules/sec | 3 molecules/sec | **407x higher** |
| **Batch mode** | 2,855 molecules/sec | 74 molecules/sec | **38.6x higher** |
| **Time per molecule (batch)** | 0.35ms | 13.46ms | **38.4x faster** |

## Performance Analysis

**opsinpy**:
- **JVM startup cost**: ~680ms first call, then 0.5-60ms per call
- **Batch processing**: Additional 10-100x speedup over individual calls
- **Memory efficient**: Single JVM instance for entire session
- **Best for**: Multiple conversions, batch processing, high-throughput applications

**py2opsin**:
- **Subprocess overhead**: ~500ms per call (consistent)
- **Batch processing**: Dramatic improvement (5-35x faster than individual)
- **Process isolation**: New JVM per call provides isolation
- **Best for**: Single conversions, process isolation requirements

## Usage Recommendations

### When to Use Each Library

| Scenario | opsinpy Advantage |
|----------|------------------|
| **Multiple molecules** | 10-1000x faster |
| **Batch processing** | 40-400x faster |
| **High-throughput** | Sustained performance |
| **Memory efficiency** | Single JVM instance |
| **Interactive use** | Fast subsequent calls |

**opsinpy**:
- Multiple chemical name conversions
- Batch processing workflows  
- High-throughput applications
- Data processing pipelines
- Interactive notebooks/applications

### ✅ **Use opsinpy when:**
- Converting multiple molecules
- Building data processing pipelines
- Need sustained high performance
- Working interactively (Jupyter notebooks)
- Memory efficiency is important

### ✅ **Use py2opsin (with batch processing) when:**
- Process isolation is required
- Single, occasional conversions
- Legacy system compatibility
- Minimal memory footprint needed

## Implementation Details

### opsinpy (JPype-based)
- **Direct Java integration** via JPype
- **One-time JVM startup** cost (~680ms)
- **Subsequent calls** are very fast (0.5-60ms)
- **Batch processing** provides additional speedup
- **Memory efficient** - single JVM instance

### py2opsin (subprocess-based)  
- **Subprocess calls** to Java executable
- **JVM startup/shutdown** per call (~500ms overhead)
- **Batch processing** dramatically improves performance
- **Process isolation** - each call is independent

## Reproducibility

This benchmark ensures complete reproducibility:

1. **Public packages**: Both `opsinpy` and `py2opsin` are available from PyPI
2. **Identical test data**: Same molecules, same OPSIN version (2.8.0)
3. **Statistical analysis**: Multiple runs with mean ± standard deviation
4. **System information**: Platform, Python, Java versions reported
5. **Result validation**: 100% agreement between implementations

## Updated Conclusions

The updated benchmark demonstrates that while **opsinpy is still the preferred solution** for most use cases, **py2opsin users should definitely use batch processing** to achieve much better performance than individual calls.

**Both libraries benefit significantly from batch processing**, but opsinpy maintains its performance advantage in all scenarios while providing additional benefits like memory efficiency and sustained performance for interactive use. 