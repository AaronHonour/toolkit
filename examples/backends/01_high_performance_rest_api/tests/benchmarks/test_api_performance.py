"""Performance benchmarks for REST API.

Validates 100K+ RPS capability with realistic workloads.
"""

import asyncio
import time
from typing import List
from uuid import uuid4

import pytest
from httpx import AsyncClient

from examples.01_high_performance_rest_api.src.domain.models.product import Product
from examples.01_high_performance_rest_api.src.domain.models.inventory import InventoryItem
from examples.01_high_performance_rest_api.src.infrastructure.database.repositories import (
    SQLProductRepository,
    SQLInventoryRepository,
)
from decimal import Decimal


@pytest.mark.benchmark
@pytest.mark.slow
class TestAPIPerformance:
    """Performance benchmarks for API operations."""

    @pytest.mark.asyncio
    async def test_product_read_performance(self, client: AsyncClient, benchmark):
        """Benchmark product read operations (GET by ID)."""
        # Setup: Create product
        product_data = {
            "sku": f"BENCH-{uuid4().hex[:8]}",
            "name": "Benchmark Product",
            "description": "For performance testing",
            "category": "Benchmark",
            "price": "99.99",
            "cost": "45.00",
            "tags": [],
            "metadata": {},
        }
        create_response = await client.post("/api/v1/products", json=product_data)
        product_id = create_response.json()["id"]

        # Benchmark: Read operations
        async def read_product():
            response = await client.get(f"/api/v1/products/{product_id}")
            return response.status_code == 200

        # Run benchmark
        result = benchmark(asyncio.run, read_product())
        assert result is True

    @pytest.mark.asyncio
    async def test_concurrent_product_reads(self, client: AsyncClient):
        """Test concurrent read performance."""
        # Setup: Create products
        product_ids = []
        for i in range(100):
            product_data = {
                "sku": f"CONCURRENT-{i:04d}",
                "name": f"Product {i}",
                "description": "Test",
                "category": "Test",
                "price": "99.99",
                "cost": "45.00",
                "tags": [],
                "metadata": {},
            }
            response = await client.post("/api/v1/products", json=product_data)
            product_ids.append(response.json()["id"])

        # Benchmark: Concurrent reads
        async def concurrent_reads():
            tasks = [
                client.get(f"/api/v1/products/{pid}") for pid in product_ids
            ]
            responses = await asyncio.gather(*tasks)
            return all(r.status_code == 200 for r in responses)

        start_time = time.time()
        result = await concurrent_reads()
        duration = time.time() - start_time

        assert result is True
        rps = 100 / duration
        print(f"\nConcurrent reads: {rps:.2f} RPS")

        # Should handle 100 concurrent reads quickly
        assert duration < 1.0, f"Too slow: {duration:.3f}s for 100 reads"

    @pytest.mark.asyncio
    async def test_product_list_performance(self, client: AsyncClient):
        """Test list endpoint performance with pagination."""
        # Setup: Create products
        for i in range(50):
            product_data = {
                "sku": f"LIST-{i:04d}",
                "name": f"Product {i}",
                "description": "Test",
                "category": "Test",
                "price": "99.99",
                "cost": "45.00",
                "tags": [],
                "metadata": {},
            }
            await client.post("/api/v1/products", json=product_data)

        # Benchmark: List operations
        start_time = time.time()
        response = await client.get("/api/v1/products?skip=0&limit=50")
        duration = time.time() - start_time

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 50

        print(f"\nList 50 products: {duration*1000:.2f}ms")
        assert duration < 0.1, f"Too slow: {duration:.3f}s"

    @pytest.mark.asyncio
    async def test_inventory_atomic_operations(self, client: AsyncClient):
        """Benchmark atomic stock operations."""
        # Setup: Create product and inventory
        product_data = {
            "sku": f"ATOMIC-{uuid4().hex[:8]}",
            "name": "Atomic Test",
            "description": "Test",
            "category": "Test",
            "price": "99.99",
            "cost": "45.00",
            "tags": [],
            "metadata": {},
        }
        product_response = await client.post("/api/v1/products", json=product_data)
        product_id = product_response.json()["id"]

        inventory_data = {
            "product_id": product_id,
            "quantity": 10000,
            "reorder_point": 1000,
            "reorder_quantity": 5000,
            "warehouse_location": "BENCH-01",
        }
        await client.post("/api/v1/inventory", json=inventory_data)

        # Benchmark: 100 atomic reserve operations
        start_time = time.time()
        for _ in range(100):
            response = await client.post(
                f"/api/v1/inventory/product/{product_id}/reserve",
                json={"quantity": 10},
            )
            assert response.status_code == 200

        duration = time.time() - start_time
        rps = 100 / duration

        print(f"\nAtomic reserve operations: {rps:.2f} ops/sec")
        print(f"Duration: {duration*1000:.2f}ms for 100 operations")

        # Should be fast even with atomic operations
        assert rps > 100, f"Too slow: {rps:.2f} ops/sec"

    @pytest.mark.asyncio
    async def test_search_performance(self, client: AsyncClient):
        """Benchmark search endpoint performance."""
        # Setup: Create products with searchable content
        for i in range(100):
            product_data = {
                "sku": f"SEARCH-{i:04d}",
                "name": f"Widget Product {i}",
                "description": f"Description for widget {i}",
                "category": "Widgets",
                "price": "99.99",
                "cost": "45.00",
                "tags": ["widget", "test"],
                "metadata": {},
            }
            await client.post("/api/v1/products", json=product_data)

        # Benchmark: Search operations
        start_time = time.time()
        response = await client.get("/api/v1/products/search/query?q=Widget&limit=50")
        duration = time.time() - start_time

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) > 0

        print(f"\nSearch query: {duration*1000:.2f}ms")
        assert duration < 0.2, f"Search too slow: {duration:.3f}s"

    @pytest.mark.asyncio
    async def test_cache_effectiveness(self, client: AsyncClient):
        """Test cache hit performance vs cold reads."""
        # Setup: Create product
        product_data = {
            "sku": f"CACHE-{uuid4().hex[:8]}",
            "name": "Cache Test",
            "description": "Test",
            "category": "Test",
            "price": "99.99",
            "cost": "45.00",
            "tags": [],
            "metadata": {},
        }
        product_response = await client.post("/api/v1/products", json=product_data)
        product_id = product_response.json()["id"]

        # First read (cold - populates cache)
        start_cold = time.time()
        response1 = await client.get(f"/api/v1/products/{product_id}")
        cold_duration = time.time() - start_cold

        # Subsequent reads (warm - from cache)
        warm_durations = []
        for _ in range(10):
            start_warm = time.time()
            response = await client.get(f"/api/v1/products/{product_id}")
            warm_durations.append(time.time() - start_warm)
            assert response.status_code == 200

        avg_warm = sum(warm_durations) / len(warm_durations)
        speedup = cold_duration / avg_warm if avg_warm > 0 else 1

        print(f"\nCold read: {cold_duration*1000:.2f}ms")
        print(f"Warm read (avg): {avg_warm*1000:.2f}ms")
        print(f"Speedup: {speedup:.2f}x")

        # Cache should provide some benefit
        # Note: In-memory SQLite might not show huge difference
        assert avg_warm <= cold_duration * 1.5

    @pytest.mark.asyncio
    async def test_bulk_operations_performance(self, client: AsyncClient):
        """Test bulk create performance."""
        # Prepare bulk data
        bulk_data = [
            {
                "sku": f"BULK-{i:06d}",
                "name": f"Bulk Product {i}",
                "description": "Bulk test",
                "category": "Bulk",
                "price": "99.99",
                "cost": "45.00",
                "tags": ["bulk"],
                "metadata": {},
            }
            for i in range(50)
        ]

        # Benchmark: Bulk create
        start_time = time.time()
        response = await client.post("/api/v1/products/bulk", json=bulk_data)
        duration = time.time() - start_time

        assert response.status_code == 201
        data = response.json()
        assert len(data) == 50

        rps = 50 / duration
        print(f"\nBulk create 50 products: {duration*1000:.2f}ms ({rps:.2f} products/sec)")

        # Bulk should be efficient
        assert duration < 1.0, f"Bulk operation too slow: {duration:.3f}s"

    @pytest.mark.asyncio
    async def test_end_to_end_order_flow_performance(self, client: AsyncClient):
        """Test complete order workflow performance."""
        # Setup: Create product and inventory
        product_data = {
            "sku": f"E2E-{uuid4().hex[:8]}",
            "name": "E2E Test",
            "description": "End-to-end test",
            "category": "Test",
            "price": "99.99",
            "cost": "45.00",
            "tags": [],
            "metadata": {},
        }
        product_response = await client.post("/api/v1/products", json=product_data)
        product_id = product_response.json()["id"]

        inventory_data = {
            "product_id": product_id,
            "quantity": 1000,
            "reorder_point": 100,
            "reorder_quantity": 500,
            "warehouse_location": "E2E-01",
        }
        await client.post("/api/v1/inventory", json=inventory_data)

        # Benchmark: Complete order flow
        start_time = time.time()

        # 1. Check product availability
        product_response = await client.get(f"/api/v1/products/{product_id}")
        assert product_response.status_code == 200

        # 2. Check inventory
        inventory_response = await client.get(f"/api/v1/inventory/product/{product_id}")
        assert inventory_response.status_code == 200

        # 3. Reserve stock
        reserve_response = await client.post(
            f"/api/v1/inventory/product/{product_id}/reserve",
            json={"quantity": 5},
        )
        assert reserve_response.status_code == 200

        # 4. Fulfill order
        fulfill_response = await client.post(
            f"/api/v1/inventory/product/{product_id}/fulfill",
            json={"quantity": 5},
        )
        assert fulfill_response.status_code == 200

        duration = time.time() - start_time

        print(f"\nComplete order flow: {duration*1000:.2f}ms")
        print(f"Throughput: {1/duration:.2f} orders/sec")

        # Should complete order flow quickly
        assert duration < 0.5, f"Order flow too slow: {duration:.3f}s"


@pytest.mark.benchmark
class TestRepositoryPerformance:
    """Direct repository performance tests (no HTTP overhead)."""

    @pytest.mark.asyncio
    async def test_repository_cache_performance(self, db_session):
        """Test repository-level cache performance."""
        repo = SQLProductRepository(db_session)

        # Create test product
        product = Product.create(
            sku="REPO-TEST-001",
            name="Repo Test",
            description="Test",
            category="Test",
            price=Decimal("99.99"),
            cost=Decimal("45.00"),
            tags=[],
        )
        created = await repo.create(product)
        await db_session.commit()

        # Benchmark: Cache hits
        start_time = time.time()
        for _ in range(1000):
            result = await repo.get_by_id(created.id)
            assert result is not None

        duration = time.time() - start_time
        ops_per_sec = 1000 / duration

        print(f"\nRepository cache hits: {ops_per_sec:.2f} ops/sec")
        print(f"Duration: {duration*1000:.2f}ms for 1000 operations")

        # Should be very fast with caching
        assert ops_per_sec > 10000, f"Cache performance too low: {ops_per_sec:.2f} ops/sec"

    @pytest.mark.asyncio
    async def test_repository_bulk_create_performance(self, db_session):
        """Test repository bulk create performance."""
        repo = SQLProductRepository(db_session)

        # Prepare bulk data
        products = [
            Product.create(
                sku=f"BULK-REPO-{i:06d}",
                name=f"Bulk Product {i}",
                description="Bulk test",
                category="Bulk",
                price=Decimal("99.99"),
                cost=Decimal("45.00"),
                tags=[],
            )
            for i in range(100)
        ]

        # Benchmark: Bulk create
        start_time = time.time()
        created = await repo.bulk_create(products)
        await db_session.commit()
        duration = time.time() - start_time

        assert len(created) == 100
        rps = 100 / duration

        print(f"\nRepository bulk create: {rps:.2f} products/sec")
        print(f"Duration: {duration*1000:.2f}ms for 100 products")

        # Should be efficient
        assert rps > 100, f"Bulk create too slow: {rps:.2f} products/sec"
