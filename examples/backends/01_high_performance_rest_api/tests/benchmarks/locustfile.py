"""Locust load testing configuration for 100K+ RPS validation.

Usage:
    # Start API server first
    python src/main.py

    # Run load test
    locust -f tests/benchmarks/locustfile.py --host=http://localhost:8000

    # Or headless with specific parameters
    locust -f tests/benchmarks/locustfile.py \
        --host=http://localhost:8000 \
        --users=1000 \
        --spawn-rate=100 \
        --run-time=60s \
        --headless
"""

import random
from uuid import uuid4
from locust import HttpUser, task, between, events


# Global storage for created resources
created_products = []
created_inventory = []


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Setup: Create initial test data."""
    print("Setting up test data...")

    # Create products via API
    for i in range(100):
        product_data = {
            "sku": f"LOAD-{i:06d}",
            "name": f"Load Test Product {i}",
            "description": f"Product for load testing {i}",
            "category": f"Category-{i % 10}",
            "price": "99.99",
            "cost": "45.00",
            "tags": ["loadtest"],
            "metadata": {},
        }

        response = environment.runner.user_classes[0].client_class().post(
            "/api/v1/products",
            json=product_data,
            catch_response=True,
        )

        if response.status_code == 201:
            product_id = response.json()["id"]
            created_products.append(product_id)

            # Create inventory for product
            inventory_data = {
                "product_id": product_id,
                "quantity": 10000,
                "reorder_point": 1000,
                "reorder_quantity": 5000,
                "warehouse_location": f"W-{i % 5:02d}",
            }

            inv_response = environment.runner.user_classes[0].client_class().post(
                "/api/v1/inventory",
                json=inventory_data,
                catch_response=True,
            )

            if inv_response.status_code == 201:
                created_inventory.append(product_id)

    print(f"Created {len(created_products)} products for testing")


class InventoryAPIUser(HttpUser):
    """Simulated user performing various API operations."""

    wait_time = between(0.1, 0.5)  # Wait 0.1-0.5s between tasks
    host = "http://localhost:8000"

    @task(10)  # Weight: 10 (most common operation)
    def get_product_by_id(self):
        """Read product by ID (cacheable)."""
        if not created_products:
            return

        product_id = random.choice(created_products)
        with self.client.get(
            f"/api/v1/products/{product_id}",
            catch_response=True,
            name="/api/v1/products/[id]",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got {response.status_code}")

    @task(5)
    def list_products(self):
        """List products with pagination."""
        skip = random.randint(0, 50)
        with self.client.get(
            f"/api/v1/products?skip={skip}&limit=20",
            catch_response=True,
            name="/api/v1/products",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got {response.status_code}")

    @task(8)
    def get_inventory(self):
        """Get inventory for product."""
        if not created_inventory:
            return

        product_id = random.choice(created_inventory)
        with self.client.get(
            f"/api/v1/inventory/product/{product_id}",
            catch_response=True,
            name="/api/v1/inventory/product/[id]",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got {response.status_code}")

    @task(3)
    def search_products(self):
        """Search products."""
        queries = ["Load", "Product", "Test", "Category"]
        query = random.choice(queries)
        with self.client.get(
            f"/api/v1/products/search/query?q={query}",
            catch_response=True,
            name="/api/v1/products/search/query",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got {response.status_code}")

    @task(2)
    def reserve_stock(self):
        """Reserve stock (atomic operation)."""
        if not created_inventory:
            return

        product_id = random.choice(created_inventory)
        with self.client.post(
            f"/api/v1/inventory/product/{product_id}/reserve",
            json={"quantity": random.randint(1, 10)},
            catch_response=True,
            name="/api/v1/inventory/product/[id]/reserve",
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 400:
                # Insufficient stock is acceptable in load test
                response.success()
            else:
                response.failure(f"Got {response.status_code}")

    @task(1)
    def get_low_stock_alerts(self):
        """Get low stock alerts."""
        with self.client.get(
            "/api/v1/inventory/alerts/low-stock",
            catch_response=True,
            name="/api/v1/inventory/alerts/low-stock",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got {response.status_code}")

    @task(1)
    def filter_by_category(self):
        """Filter products by category."""
        category = f"Category-{random.randint(0, 9)}"
        with self.client.get(
            f"/api/v1/products/category/{category}",
            catch_response=True,
            name="/api/v1/products/category/[name]",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got {response.status_code}")

    @task(1)
    def health_check(self):
        """Check API health."""
        with self.client.get(
            "/health",
            catch_response=True,
            name="/health",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got {response.status_code}")


class ReadHeavyUser(HttpUser):
    """User that only performs read operations (no writes)."""

    wait_time = between(0.05, 0.2)
    host = "http://localhost:8000"

    @task(20)
    def get_product(self):
        """Read product (heavily cached)."""
        if not created_products:
            return

        product_id = random.choice(created_products)
        self.client.get(f"/api/v1/products/{product_id}", name="/api/v1/products/[id]")

    @task(10)
    def get_inventory(self):
        """Read inventory (cached)."""
        if not created_inventory:
            return

        product_id = random.choice(created_inventory)
        self.client.get(
            f"/api/v1/inventory/product/{product_id}",
            name="/api/v1/inventory/product/[id]",
        )

    @task(5)
    def list_products(self):
        """List products."""
        skip = random.randint(0, 50)
        self.client.get(f"/api/v1/products?skip={skip}&limit=20", name="/api/v1/products")


# Performance targets for validation
TARGET_RPS = 100000  # 100K RPS target
TARGET_P99_MS = 100  # P99 < 100ms target
