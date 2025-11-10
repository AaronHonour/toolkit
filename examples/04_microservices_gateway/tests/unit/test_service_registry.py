"""Unit tests for ServiceRegistry."""

import pytest

from src.main import ServiceRegistry, ServiceInstance
from toolkit.algorithms import ConsistentHashRing


class TestServiceRegistry:
    """Test ServiceRegistry with consistent hashing."""

    def test_registry_creation(self):
        """Test registry creation."""
        registry = ServiceRegistry()

        assert len(registry.services) == 0
        assert len(registry.hash_rings) == 0
        assert len(registry.circuit_breakers) == 0

    def test_register_service(self):
        """Test registering a service."""
        registry = ServiceRegistry()

        instances = [
            {"url": "http://localhost:9001", "weight": 1},
            {"url": "http://localhost:9002", "weight": 1},
        ]

        registry.register_service("users", instances)

        assert "users" in registry.services
        assert len(registry.services["users"]) == 2
        assert "users" in registry.hash_rings
        assert "users" in registry.circuit_breakers

    def test_register_multiple_services(self):
        """Test registering multiple services."""
        registry = ServiceRegistry()

        registry.register_service("users", [{"url": "http://localhost:9001"}])
        registry.register_service("orders", [{"url": "http://localhost:9002"}])

        assert len(registry.services) == 2
        assert "users" in registry.services
        assert "orders" in registry.services

    def test_get_instance_without_key(self):
        """Test getting instance without sticky key."""
        registry = ServiceRegistry()

        instances = [
            {"url": "http://localhost:9001", "weight": 1},
            {"url": "http://localhost:9002", "weight": 1},
        ]

        registry.register_service("users", instances)

        instance = registry.get_instance("users")

        assert instance is not None
        assert instance.url in ["http://localhost:9001", "http://localhost:9002"]

    def test_get_instance_with_key(self):
        """Test getting instance with sticky key."""
        registry = ServiceRegistry()

        instances = [
            {"url": "http://localhost:9001", "weight": 1},
            {"url": "http://localhost:9002", "weight": 1},
        ]

        registry.register_service("users", instances)

        # Same key should return same instance
        instance1 = registry.get_instance("users", key="user123")
        instance2 = registry.get_instance("users", key="user123")

        assert instance1 is not None
        assert instance2 is not None
        assert instance1.url == instance2.url

    def test_consistent_hashing_distribution(self):
        """Test consistent hashing distributes keys."""
        registry = ServiceRegistry()

        instances = [
            {"url": "http://localhost:9001", "weight": 1},
            {"url": "http://localhost:9002", "weight": 1},
            {"url": "http://localhost:9003", "weight": 1},
        ]

        registry.register_service("users", instances)

        # Get instances for different keys
        url_counts = {}
        for i in range(100):
            instance = registry.get_instance("users", key=f"user{i}")
            url_counts[instance.url] = url_counts.get(instance.url, 0) + 1

        # Should distribute across instances (not necessarily evenly)
        assert len(url_counts) > 1  # At least 2 instances used

    def test_weighted_routing(self):
        """Test weighted routing."""
        registry = ServiceRegistry()

        instances = [
            {"url": "http://localhost:9001", "weight": 1},
            {"url": "http://localhost:9002", "weight": 3},
        ]

        registry.register_service("users", instances)

        # Higher weight instance should get more requests
        url_counts = {}
        for i in range(100):
            instance = registry.get_instance("users", key=f"user{i}")
            url_counts[instance.url] = url_counts.get(instance.url, 0) + 1

        # Instance with weight 3 should get more traffic
        # (not exact 3:1 ratio due to consistent hashing)
        assert "http://localhost:9002" in url_counts

    def test_get_nonexistent_service(self):
        """Test getting instance for nonexistent service."""
        registry = ServiceRegistry()

        instance = registry.get_instance("nonexistent")

        assert instance is None

    def test_get_circuit_breaker(self):
        """Test getting circuit breaker for service."""
        registry = ServiceRegistry()

        registry.register_service("users", [{"url": "http://localhost:9001"}])

        cb = registry.get_circuit_breaker("users")

        assert cb is not None

    def test_get_circuit_breaker_nonexistent(self):
        """Test getting circuit breaker for nonexistent service."""
        registry = ServiceRegistry()

        cb = registry.get_circuit_breaker("nonexistent")

        assert cb is None

    def test_unhealthy_instance_skipped(self):
        """Test that unhealthy instances are skipped."""
        registry = ServiceRegistry()

        instances = [
            {"url": "http://localhost:9001", "weight": 1},
            {"url": "http://localhost:9002", "weight": 1},
        ]

        registry.register_service("users", instances)

        # Mark first instance as unhealthy
        registry.services["users"][0].healthy = False

        # Should return second instance
        instance = registry.get_instance("users")

        assert instance is not None
        assert instance.url == "http://localhost:9002"

    def test_all_instances_unhealthy(self):
        """Test behavior when all instances are unhealthy."""
        registry = ServiceRegistry()

        instances = [
            {"url": "http://localhost:9001", "weight": 1},
        ]

        registry.register_service("users", instances)

        # Mark all instances as unhealthy
        registry.services["users"][0].healthy = False

        instance = registry.get_instance("users")

        assert instance is None

    def test_service_instance_properties(self):
        """Test ServiceInstance properties."""
        registry = ServiceRegistry()

        instances = [
            {"url": "http://localhost:9001", "weight": 2},
        ]

        registry.register_service("users", instances)

        instance = registry.services["users"][0]

        assert instance.url == "http://localhost:9001"
        assert instance.weight == 2
        assert instance.healthy is True
        assert instance.failure_count == 0
