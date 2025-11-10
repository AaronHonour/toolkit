#!/usr/bin/env python3
"""
Comprehensive benchmark runner for all Composable Toolkit patterns.

Runs performance benchmarks and generates HTML reports with historical tracking.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import platform


class BenchmarkRunner:
    """Runs comprehensive benchmarks and generates reports."""

    def __init__(self, output_dir: Path = None):
        """Initialize benchmark runner.

        Args:
            output_dir: Directory for output files (default: benchmarks/results)
        """
        self.root_dir = Path(__file__).parent.parent
        self.output_dir = output_dir or self.root_dir / "benchmarks" / "results"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.timestamp = datetime.now().isoformat()
        self.results: Dict[str, Any] = {
            "timestamp": self.timestamp,
            "environment": self._get_environment(),
            "benchmarks": {}
        }

    def _get_environment(self) -> Dict[str, str]:
        """Get environment information."""
        return {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "machine": platform.machine(),
        }

    def run_pytest_benchmarks(self, pattern: str = None) -> bool:
        """Run pytest benchmarks.

        Args:
            pattern: Optional pattern to filter tests

        Returns:
            True if successful
        """
        print(f"\n{'='*70}")
        print("Running pytest benchmarks...")
        print(f"{'='*70}")

        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "tests/benchmarks/",
            "tests/performance/",
            "-v",
            "--benchmark-only",
            "--benchmark-json=" + str(self.output_dir / "pytest-benchmark.json"),
            "--benchmark-columns=min,max,mean,median,ops,rounds",
            "--benchmark-sort=name",
            "--no-cov"  # Disable coverage for benchmarks
        ]

        if pattern:
            cmd.append(f"-k {pattern}")

        result = subprocess.run(cmd, cwd=self.root_dir)
        return result.returncode == 0

    def run_algorithm_benchmarks(self) -> Dict[str, Any]:
        """Run algorithm performance benchmarks."""
        print(f"\n{'='*70}")
        print("Running algorithm benchmarks...")
        print(f"{'='*70}")

        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "tests/benchmarks/test_algorithms_benchmarks.py",
            "-v",
            "-s",  # Show print statements
            "--tb=short",
            "--no-cov"  # Disable coverage for benchmarks
        ]

        result = subprocess.run(cmd, cwd=self.root_dir, capture_output=True, text=True)

        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr if result.returncode != 0 else None
        }

    def run_cache_benchmarks(self) -> Dict[str, Any]:
        """Run cache performance benchmarks."""
        print(f"\n{'='*70}")
        print("Running cache benchmarks...")
        print(f"{'='*70}")

        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "tests/performance/test_cache_performance.py",
            "-v",
            "-s",
            "--tb=short",
            "--no-cov"  # Disable coverage for benchmarks
        ]

        result = subprocess.run(cmd, cwd=self.root_dir, capture_output=True, text=True)

        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr if result.returncode != 0 else None
        }

    def run_rate_limit_benchmarks(self) -> Dict[str, Any]:
        """Run rate limiter performance benchmarks."""
        print(f"\n{'='*70}")
        print("Running rate limiter benchmarks...")
        print(f"{'='*70}")

        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "tests/performance/test_ratelimit_performance.py",
            "-v",
            "-s",
            "--tb=short",
            "--no-cov"  # Disable coverage for benchmarks
        ]

        result = subprocess.run(cmd, cwd=self.root_dir, capture_output=True, text=True)

        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr if result.returncode != 0 else None
        }

    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate summary of all benchmark results."""
        summary = {
            "timestamp": self.timestamp,
            "environment": self.results["environment"],
            "total_benchmarks": len(self.results["benchmarks"]),
            "passed": sum(1 for b in self.results["benchmarks"].values() if b.get("success")),
            "failed": sum(1 for b in self.results["benchmarks"].values() if not b.get("success")),
        }

        return summary

    def save_results(self):
        """Save results to JSON file."""
        output_file = self.output_dir / f"results-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n✓ Results saved to: {output_file}")

        # Also save as latest.json for easy access
        latest_file = self.output_dir / "latest.json"
        with open(latest_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"✓ Latest results: {latest_file}")

        return output_file

    def generate_html_report(self) -> Path:
        """Generate HTML report from results."""
        html_file = self.output_dir / f"report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"

        summary = self.generate_summary_report()

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Composable Toolkit - Benchmark Results</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 40px;
        }}

        h1 {{
            color: #2563eb;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}

        .subtitle {{
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}

        .metric {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 8px;
            color: white;
        }}

        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 5px;
        }}

        .metric-value {{
            font-size: 2em;
            font-weight: bold;
        }}

        .section {{
            margin: 40px 0;
        }}

        .section h2 {{
            color: #1e40af;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e5e7eb;
        }}

        .benchmark-card {{
            background: #f9fafb;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 15px;
            border-left: 4px solid #10b981;
        }}

        .benchmark-card.failed {{
            border-left-color: #ef4444;
        }}

        .benchmark-title {{
            font-weight: 600;
            font-size: 1.1em;
            margin-bottom: 10px;
        }}

        .benchmark-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}

        .stat {{
            background: white;
            padding: 12px;
            border-radius: 4px;
        }}

        .stat-label {{
            font-size: 0.85em;
            color: #6b7280;
            margin-bottom: 4px;
        }}

        .stat-value {{
            font-size: 1.3em;
            font-weight: 600;
            color: #1f2937;
        }}

        .environment {{
            background: #fef3c7;
            padding: 20px;
            border-radius: 6px;
            margin-top: 20px;
        }}

        .environment h3 {{
            color: #92400e;
            margin-bottom: 10px;
        }}

        .environment dl {{
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 10px 20px;
        }}

        .environment dt {{
            font-weight: 600;
            color: #78350f;
        }}

        .environment dd {{
            color: #92400e;
        }}

        .footer {{
            margin-top: 60px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            color: #6b7280;
            font-size: 0.9em;
        }}

        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
            margin-left: 10px;
        }}

        .status-badge.success {{
            background: #d1fae5;
            color: #065f46;
        }}

        .status-badge.failed {{
            background: #fee2e2;
            color: #991b1b;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Composable Toolkit</h1>
        <div class="subtitle">Performance Benchmark Results</div>

        <div class="summary">
            <div class="metric">
                <div class="metric-label">Total Benchmarks</div>
                <div class="metric-value">{summary['total_benchmarks']}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Passed</div>
                <div class="metric-value">{summary['passed']}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Failed</div>
                <div class="metric-value">{summary['failed']}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Success Rate</div>
                <div class="metric-value">{(summary['passed']/summary['total_benchmarks']*100) if summary['total_benchmarks'] > 0 else 0:.1f}%</div>
            </div>
        </div>

        <div class="section">
            <h2>Benchmark Results</h2>
"""

        for name, result in self.results["benchmarks"].items():
            status = "success" if result.get("success") else "failed"
            badge_class = "success" if result.get("success") else "failed"
            badge_text = "✓ Passed" if result.get("success") else "✗ Failed"

            html += f"""
            <div class="benchmark-card {status}">
                <div class="benchmark-title">
                    {name.replace('_', ' ').title()}
                    <span class="status-badge {badge_class}">{badge_text}</span>
                </div>
"""

            if not result.get("success") and result.get("errors"):
                html += f"""
                <div style="color: #991b1b; margin-top: 10px; padding: 10px; background: #fee2e2; border-radius: 4px;">
                    <strong>Error:</strong> {result['errors'][:200]}...
                </div>
"""

            html += """
            </div>
"""

        html += f"""
        </div>

        <div class="environment">
            <h3>Test Environment</h3>
            <dl>
                <dt>Timestamp:</dt>
                <dd>{summary['timestamp']}</dd>
                <dt>Python Version:</dt>
                <dd>{summary['environment']['python_version']}</dd>
                <dt>Platform:</dt>
                <dd>{summary['environment']['platform']}</dd>
                <dt>Processor:</dt>
                <dd>{summary['environment']['processor']}</dd>
                <dt>Machine:</dt>
                <dd>{summary['environment']['machine']}</dd>
            </dl>
        </div>

        <div class="footer">
            <p>Generated by Composable Toolkit Benchmark Runner</p>
            <p>Report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""

        with open(html_file, 'w') as f:
            f.write(html)

        print(f"✓ HTML report: {html_file}")

        # Also save as latest.html
        latest_html = self.output_dir / "latest.html"
        with open(latest_html, 'w') as f:
            f.write(html)

        print(f"✓ Latest report: {latest_html}")

        return html_file

    def run_all(self, quick: bool = False):
        """Run all benchmarks.

        Args:
            quick: If True, run quick benchmarks only
        """
        print(f"\n{'='*70}")
        print("COMPOSABLE TOOLKIT - COMPREHENSIVE BENCHMARK SUITE")
        print(f"{'='*70}")
        print(f"Timestamp: {self.timestamp}")
        print(f"Python: {self.results['environment']['python_version']}")
        print(f"Platform: {self.results['environment']['platform']}")
        print(f"{'='*70}\n")

        # Run individual benchmark suites
        self.results["benchmarks"]["algorithms"] = self.run_algorithm_benchmarks()
        self.results["benchmarks"]["cache"] = self.run_cache_benchmarks()
        self.results["benchmarks"]["rate_limit"] = self.run_rate_limit_benchmarks()

        if not quick:
            # Run full pytest benchmarks
            self.run_pytest_benchmarks()

        # Generate reports
        self.save_results()
        self.generate_html_report()

        # Print summary
        summary = self.generate_summary_report()
        print(f"\n{'='*70}")
        print("BENCHMARK SUMMARY")
        print(f"{'='*70}")
        print(f"Total Benchmarks: {summary['total_benchmarks']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success Rate: {(summary['passed']/summary['total_benchmarks']*100) if summary['total_benchmarks'] > 0 else 0:.1f}%")
        print(f"{'='*70}\n")

        return summary['failed'] == 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run Composable Toolkit benchmarks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick benchmarks only (skip full pytest suite)"
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for results (default: benchmarks/results)"
    )

    args = parser.parse_args()

    runner = BenchmarkRunner(output_dir=args.output_dir)
    success = runner.run_all(quick=args.quick)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
