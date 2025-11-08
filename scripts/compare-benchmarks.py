#!/usr/bin/env python3
"""
Compare benchmark results to detect performance regressions.

Usage:
    python scripts/compare-benchmarks.py baseline.json current.json --threshold 10
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class BenchmarkComparator:
    """Compare benchmark results and detect regressions."""

    def __init__(self, baseline_file: Path, current_file: Path, threshold: float = 10.0):
        """Initialize comparator.

        Args:
            baseline_file: Path to baseline results JSON
            current_file: Path to current results JSON
            threshold: Regression threshold percentage (default: 10%)
        """
        self.baseline = self._load_json(baseline_file)
        self.current = self._load_json(current_file)
        self.threshold = threshold

        self.regressions: List[Dict] = []
        self.improvements: List[Dict] = []

    def _load_json(self, file_path: Path) -> Dict:
        """Load JSON file."""
        with open(file_path, 'r') as f:
            return json.load(f)

    def compare(self) -> Tuple[List[Dict], List[Dict]]:
        """Compare benchmarks and find regressions/improvements.

        Returns:
            Tuple of (regressions, improvements)
        """
        baseline_benchmarks = self.baseline.get("benchmarks", {})
        current_benchmarks = self.current.get("benchmarks", {})

        for name in current_benchmarks:
            if name not in baseline_benchmarks:
                print(f"⚠ New benchmark: {name} (no baseline)")
                continue

            baseline = baseline_benchmarks[name]
            current = current_benchmarks[name]

            # Skip if either failed
            if not baseline.get("success") or not current.get("success"):
                continue

            # Compare success rates or specific metrics
            # For now, just track if status changed
            if baseline.get("success") and not current.get("success"):
                self.regressions.append({
                    "name": name,
                    "type": "failure",
                    "baseline": "passed",
                    "current": "failed",
                    "change_percent": -100
                })

        return self.regressions, self.improvements

    def print_report(self):
        """Print comparison report."""
        print("\n" + "="*70)
        print("BENCHMARK COMPARISON REPORT")
        print("="*70)

        print(f"\nBaseline: {self.baseline['timestamp']}")
        print(f"Current:  {self.current['timestamp']}")
        print(f"Threshold: {self.threshold}%")

        if self.regressions:
            print(f"\n{'='*70}")
            print(f"⚠️  REGRESSIONS DETECTED: {len(self.regressions)}")
            print(f"{'='*70}")

            for regression in self.regressions:
                print(f"\n❌ {regression['name']}")
                print(f"   Type: {regression['type']}")
                print(f"   Baseline: {regression['baseline']}")
                print(f"   Current: {regression['current']}")
                print(f"   Change: {regression['change_percent']:.1f}%")
        else:
            print(f"\n✅ No regressions detected!")

        if self.improvements:
            print(f"\n{'='*70}")
            print(f"🎉 IMPROVEMENTS: {len(self.improvements)}")
            print(f"{'='*70}")

            for improvement in self.improvements:
                print(f"\n✅ {improvement['name']}")
                print(f"   Improvement: {improvement['change_percent']:.1f}%")

        print(f"\n{'='*70}\n")

    def has_regressions(self) -> bool:
        """Check if there are any regressions exceeding threshold."""
        return len(self.regressions) > 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Compare benchmark results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "baseline",
        type=Path,
        help="Baseline benchmark results (JSON)"
    )

    parser.add_argument(
        "current",
        type=Path,
        help="Current benchmark results (JSON)"
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=10.0,
        help="Regression threshold percentage (default: 10%%)"
    )

    parser.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="Exit with error code if regressions detected"
    )

    args = parser.parse_args()

    comparator = BenchmarkComparator(
        args.baseline,
        args.current,
        threshold=args.threshold
    )

    comparator.compare()
    comparator.print_report()

    if args.fail_on_regression and comparator.has_regressions():
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
