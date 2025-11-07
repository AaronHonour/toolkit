"""Integration tests for Product API endpoints."""

import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.integration
@pytest.mark.asyncio
class TestProductAPI:
    """Test Product API endpoints."""

    async def test_create_product(self, client: AsyncClient, sample_product_data: dict):
        """Test creating a product via API."""
        response = await client.post("/api/v1/products", json=sample_product_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["sku"] == sample_product_data["sku"]
        assert data["name"] == sample_product_data["name"]
        assert data["status"] == "active"
        assert "id" in data
        assert "margin" in data

    async def test_create_product_duplicate_sku(
        self, client: AsyncClient, sample_product_data: dict
    ):
        """Test creating product with duplicate SKU fails."""
        # Create first product
        await client.post("/api/v1/products", json=sample_product_data)

        # Try to create duplicate
        response = await client.post("/api/v1/products", json=sample_product_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_get_product_by_id(self, client: AsyncClient, sample_product_data: dict):
        """Test getting product by ID."""
        # Create product
        create_response = await client.post(
            "/api/v1/products", json=sample_product_data
        )
        product_id = create_response.json()["id"]

        # Get product
        response = await client.get(f"/api/v1/products/{product_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == product_id
        assert data["sku"] == sample_product_data["sku"]

    async def test_get_product_not_found(self, client: AsyncClient):
        """Test getting non-existent product returns 404."""
        from uuid import uuid4

        fake_id = str(uuid4())
        response = await client.get(f"/api/v1/products/{fake_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_product_by_sku(
        self, client: AsyncClient, sample_product_data: dict
    ):
        """Test getting product by SKU."""
        # Create product
        await client.post("/api/v1/products", json=sample_product_data)

        # Get by SKU
        response = await client.get(
            f"/api/v1/products/sku/{sample_product_data['sku']}"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["sku"] == sample_product_data["sku"]

    async def test_list_products(self, client: AsyncClient, sample_product_data: dict):
        """Test listing products with pagination."""
        # Create multiple products
        for i in range(5):
            data = sample_product_data.copy()
            data["sku"] = f"TEST-{i:04d}"
            data["name"] = f"Product {i}"
            await client.post("/api/v1/products", json=data)

        # List products
        response = await client.get("/api/v1/products?skip=0&limit=10")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) == 5
        assert data["total"] >= 5

    async def test_list_products_with_status_filter(
        self, client: AsyncClient, sample_product_data: dict
    ):
        """Test filtering products by status."""
        # Create active product
        await client.post("/api/v1/products", json=sample_product_data)

        # List only active products
        response = await client.get("/api/v1/products?status=active")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for item in data["items"]:
            assert item["status"] == "active"

    async def test_search_products(
        self, client: AsyncClient, sample_product_data: dict
    ):
        """Test product search."""
        # Create product
        sample_product_data["name"] = "Unique Widget Name"
        await client.post("/api/v1/products", json=sample_product_data)

        # Search for it
        response = await client.get("/api/v1/products/search/query?q=Unique+Widget")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) >= 1
        assert "Unique Widget" in data["items"][0]["name"]

    async def test_filter_by_category(
        self, client: AsyncClient, sample_product_data: dict
    ):
        """Test filtering by category."""
        # Create products in same category
        sample_product_data["category"] = "Electronics"
        await client.post("/api/v1/products", json=sample_product_data)

        # Filter by category
        response = await client.get("/api/v1/products/category/Electronics")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for item in data["items"]:
            assert item["category"] == "Electronics"

    async def test_update_product(self, client: AsyncClient, sample_product_data: dict):
        """Test updating product."""
        # Create product
        create_response = await client.post(
            "/api/v1/products", json=sample_product_data
        )
        product_id = create_response.json()["id"]

        # Update product
        update_data = {
            "name": "Updated Product Name",
            "price": "109.99",
        }
        response = await client.put(
            f"/api/v1/products/{product_id}", json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Product Name"
        assert data["price"] == "109.99"

    async def test_delete_product(self, client: AsyncClient, sample_product_data: dict):
        """Test deleting product."""
        # Create product
        create_response = await client.post(
            "/api/v1/products", json=sample_product_data
        )
        product_id = create_response.json()["id"]

        # Delete product
        response = await client.delete(f"/api/v1/products/{product_id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deleted
        get_response = await client.get(f"/api/v1/products/{product_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_product_not_found(self, client: AsyncClient):
        """Test deleting non-existent product."""
        from uuid import uuid4

        fake_id = str(uuid4())
        response = await client.delete(f"/api/v1/products/{fake_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_filter_by_price_range(
        self, client: AsyncClient, sample_product_data: dict
    ):
        """Test filtering by price range."""
        # Create products with different prices
        for i, price in enumerate(["50.00", "100.00", "150.00"]):
            data = sample_product_data.copy()
            data["sku"] = f"PRICE-{i:04d}"
            data["price"] = price
            await client.post("/api/v1/products", json=data)

        # Filter by price range
        response = await client.get(
            "/api/v1/products/filter/price-range?min_price=75&max_price=125"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for item in data["items"]:
            price = float(item["price"])
            assert 75.0 <= price <= 125.0

    async def test_get_low_margin_products(
        self, client: AsyncClient, sample_product_data: dict
    ):
        """Test getting low margin products."""
        # Create product with low margin
        sample_product_data["price"] = "100.00"
        sample_product_data["cost"] = "90.00"  # 10% margin
        await client.post("/api/v1/products", json=sample_product_data)

        # Get low margin products (threshold 20%)
        response = await client.get(
            "/api/v1/products/filter/low-margin?threshold=0.20"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should include our 10% margin product
        margins = [float(item["margin"]) for item in data["items"]]
        assert any(m < 0.20 for m in margins)

    async def test_request_validation(self, client: AsyncClient):
        """Test request validation."""
        # Missing required fields
        invalid_data = {"name": "Test"}
        response = await client.post("/api/v1/products", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_process_time_header(
        self, client: AsyncClient, sample_product_data: dict
    ):
        """Test that X-Process-Time header is present."""
        response = await client.post("/api/v1/products", json=sample_product_data)

        assert "x-process-time" in response.headers
        process_time = float(response.headers["x-process-time"])
        assert process_time > 0
