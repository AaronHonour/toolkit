#!/usr/bin/env python3
"""
Build Docker services in batches to avoid overwhelming Docker Desktop.
Cross-platform script that works on Windows, macOS, and Linux.
"""

import subprocess
import sys
import time

# Define service batches
BATCHES = [
    {
        "name": "Infrastructure",
        "services": ["postgres", "redis", "zookeeper", "kafka", "loki", "prometheus", "jaeger", "timescale"]
    },
    {
        "name": "Apps 01-05",
        "services": ["app01", "app02", "app03", "app04", "app05"]
    },
    {
        "name": "Apps 06-10",
        "services": ["app06", "app07", "app08", "app09", "app10"]
    },
    {
        "name": "Apps 11-15",
        "services": ["app11", "app12", "app13", "app14", "app15"]
    },
    {
        "name": "Apps 16-19 + Frontend",
        "services": ["app16", "app17", "app18", "app19", "frontend"]
    }
]

def run_command(cmd):
    """Run a shell command and return exit code."""
    print(f"\nRunning: {' '.join(cmd)}")
    result = subprocess.run(cmd, shell=False)
    return result.returncode

def build_batch(batch_num, batch_name, services):
    """Build a batch of services."""
    total_batches = len(BATCHES)
    print(f"\n{'='*60}")
    print(f"[Batch {batch_num}/{total_batches}] Building {batch_name}...")
    print(f"{'='*60}")

    cmd = ["docker", "compose", "build"] + services
    exit_code = run_command(cmd)

    if exit_code != 0:
        print(f"\nERROR: Failed to build {batch_name}")
        return False

    print(f"\n✓ {batch_name} built successfully")
    return True

def main():
    print("Building Unistax services in batches...")
    print("This helps avoid overwhelming Docker Desktop")
    print("")

    start_time = time.time()

    for i, batch in enumerate(BATCHES, 1):
        if not build_batch(i, batch["name"], batch["services"]):
            print("\nBuild failed. Exiting...")
            sys.exit(1)

        # Small pause between batches to let Docker catch up
        if i < len(BATCHES):
            print("\nPausing 5 seconds before next batch...")
            time.sleep(5)

    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    print(f"\n{'='*60}")
    print(f"All services built successfully!")
    print(f"Total time: {minutes}m {seconds}s")
    print(f"{'='*60}")
    print("\nNext steps:")
    print("  Start services:  docker compose up -d")
    print("  Run tests:       docker compose exec app01 pytest -v")
    print("  Check status:    docker compose ps")
    print("")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBuild interrupted by user")
        sys.exit(1)
