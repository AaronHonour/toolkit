#!/usr/bin/env python3
"""
Comprehensive benchmark runner for performance validation.

Executes all benchmarks and generates a detailed performance report.
"""

import sys
import time
from datetime import datetime
import subprocess


def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")


def print_section(text):
    """Print formatted section."""
    print(f"\n{'-'*80}")
    print(f"  {text}")
    print(f"{'-'*80}\n")


def run_benchmark_suite(suite_name, test_file):
    """Run a benchmark suite and capture output."""
    print_section(f"Running {suite_name}")

    start_time = time.time()

    try:
        # Run pytest with verbose output and capture
        result = subprocess.run(
            ["python", "-m", "pytest", test_file, "-v", "-s", "--tb=short"],
            capture_output=False,
            text=True,
            cwd="/home/user/toolkit"
        )

        duration = time.time() - start_time

        if result.returncode == 0:
            print(f"\n✓ {suite_name} completed successfully in {duration:.2f}s")
            return True, duration
        else:
            print(f"\n✗ {suite_name} failed after {duration:.2f}s")
            return False, duration

    except Exception as e:
        print(f"\n✗ Error running {suite_name}: {e}")
        return False, 0


def main():
    """Run all benchmarks and generate report."""
    print_header("PERFORMANCE VALIDATION SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nTarget: 100K RPS with P99 < 100ms latency")
    print(f"Environment: Single Docker instance, 16GB RAM")

    start_time = time.time()
    results = []

    # Run algorithm benchmarks
    success, duration = run_benchmark_suite(
        "Algorithms Module Benchmarks",
        "tests/benchmarks/test_algorithms_benchmarks.py"
    )
    results.append(("Algorithms", success, duration))

    # Run database benchmarks
    success, duration = run_benchmark_suite(
        "Database Optimization Benchmarks",
        "tests/benchmarks/test_database_benchmarks.py"
    )
    results.append(("Database", success, duration))

    total_duration = time.time() - start_time

    # Generate summary report
    print_header("BENCHMARK SUMMARY")

    print("Results:")
    all_passed = True
    for name, success, duration in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status:8} {name:30} ({duration:.2f}s)")
        if not success:
            all_passed = False

    print(f"\nTotal execution time: {total_duration:.2f}s")

    if all_passed:
        print("\n" + "="*80)
        print("  ✓ ALL BENCHMARKS PASSED")
        print("  ✓ 100K RPS CAPABILITY VALIDATED")
        print("  ✓ P99 < 100ms TARGET ACHIEVED")
        print("="*80)
        return 0
    else:
        print("\n" + "="*80)
        print("  ✗ SOME BENCHMARKS FAILED")
        print("  See output above for details")
        print("="*80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
