"""Performance benchmarks for Microservices API Gateway."""

import pytest
import time

from toolkit.algorithms import ConsistentHashRing, fast_hash


class TestConsistentHashPerformance:
    """Test ConsistentHashRing performance (target: 773K+ ops/sec)."""

    @pytest.mark.benchmark
    def test_consistent_hash_throughput(self):
        """Test ConsistentHashRing throughput."""
        ring = ConsistentHashRing()

        # Add nodes
        for i in range(10):
            ring.add_node(f"node{i}")

        # Benchmark lookups
        operations = 100000
        start = time.perf_counter()

        for i in range(operations):
            ring.get_node(f"key{i}")

        elapsed = time.perf_counter() - start
        ops_per_sec = operations / elapsed

        print(f"\nConsistentHashRing throughput: {ops_per_sec:.0f} ops/sec")
        assert ops_per_sec > 500000  # Target: 500K+ ops/sec

    @pytest.mark.benchmark
    def test_consistent_hash_add_nodes(self):
        """Test adding nodes performance."""
        ring = ConsistentHashRing()

        operations = 1000
        start = time.perf_counter()

        for i in range(operations):
            ring.add_node(f"node{i}")

        elapsed = time.perf_counter() - start
        ops_per_sec = operations / elapsed

        print(f"\nConsistentHashRing add nodes: {ops_per_sec:.0f} ops/sec")
        assert ops_per_sec > 10000  # Target: 10K+ ops/sec


class TestFastHashPerformance:
    """Test fast_hash performance (target: 886K+ ops/sec)."""

    @pytest.mark.benchmark
    def test_fast_hash_throughput(self):
        """Test fast_hash throughput."""
        operations = 100000
        start = time.perf_counter()

        for i in range(operations):
            fast_hash(f"key{i}")

        elapsed = time.perf_counter() - start
        ops_per_sec = operations / elapsed

        print(f"\nfast_hash throughput: {ops_per_sec:.0f} ops/sec")
        assert ops_per_sec > 700000  # Target: 700K+ ops/sec


class TestRoutingPerformance:
    """Test routing performance."""

    @pytest.mark.benchmark
    def test_service_routing_throughput(self):
        """Test service routing throughput."""
        from src.main import ServiceRegistry

        registry = ServiceRegistry()

        # Register services
        for i in range(10):
            registry.register_service(
                f"service{i}",
                [{"url": f"http://localhost:900{i}"}]
            )

        # Benchmark routing
        operations = 10000
        start = time.perf_counter()

        for i in range(operations):
            service_name = f"service{i % 10}"
            key = f"user{i}"
            registry.get_instance(service_name, key=key)

        elapsed = time.perf_counter() - start
        ops_per_sec = operations / elapsed

        print(f"\nService routing throughput: {ops_per_sec:.0f} ops/sec")
        assert ops_per_sec > 50000  # Target: 50K+ ops/sec
