"""Integration tests for Inventory API endpoints."""

import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.integration
@pytest.mark.asyncio
class TestInventoryAPI:
    """Test Inventory API endpoints."""

    async def _create_product(self, client: AsyncClient) -> str:
        """Helper to create a product and return its ID."""
        from uuid import uuid4

        product_data = {
            "sku": f"TEST-{uuid4().hex[:8].upper()}",
            "name": "Test Product",
            "description": "Test",
            "category": "Test",
            "price": "99.99",
            "cost": "45.00",
            "tags": [],
            "metadata": {},
        }
        response = await client.post("/api/v1/products", json=product_data)
        return response.json()["id"]

    async def test_create_inventory(self, client: AsyncClient):
        """Test creating inventory for a product."""
        product_id = await self._create_product(client)

        inventory_data = {
            "product_id": product_id,
            "quantity": 100,
            "reorder_point": 20,
            "reorder_quantity": 50,
            "warehouse_location": "A-101",
        }

        response = await client.post("/api/v1/inventory", json=inventory_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["product_id"] == product_id
        assert data["quantity"] == 100
        assert data["reserved"] == 0
        assert data["available"] == 100
        assert data["status"] == "in_stock"

    async def test_create_inventory_duplicate(self, client: AsyncClient):
        """Test creating duplicate inventory fails."""
        product_id = await self._create_product(client)

        inventory_data = {
            "product_id": product_id,
            "quantity": 100,
            "reorder_point": 20,
            "reorder_quantity": 50,
            "warehouse_location": "A-101",
        }

        # Create first inventory
        await client.post("/api/v1/inventory", json=inventory_data)

        # Try to create duplicate
        response = await client.post("/api/v1/inventory", json=inventory_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_get_inventory_by_product_id(self, client: AsyncClient):
        """Test getting inventory by product ID."""
        product_id = await self._create_product(client)

        # Create inventory
        inventory_data = {
            "product_id": product_id,
            "quantity": 100,
            "reorder_point": 20,
            "reorder_quantity": 50,
            "warehouse_location": "A-101",
        }
        await client.post("/api/v1/inventory", json=inventory_data)

        # Get inventory
        response = await client.get(f"/api/v1/inventory/product/{product_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["product_id"] == product_id

    async def test_list_inventory(self, client: AsyncClient):
        """Test listing inventory."""
        # Create multiple inventory items
        for _ in range(3):
            product_id = await self._create_product(client)
            inventory_data = {
                "product_id": product_id,
                "quantity": 100,
                "reorder_point": 20,
                "reorder_quantity": 50,
                "warehouse_location": "A-101",
            }
            await client.post("/api/v1/inventory", json=inventory_data)

        # List inventory
        response = await client.get("/api/v1/inventory?skip=0&limit=10")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 3

    async def test_update_inventory(self, client: AsyncClient):
        """Test updating inventory settings."""
        product_id = await self._create_product(client)

        # Create inventory
        inventory_data = {
            "product_id": product_id,
            "quantity": 100,
            "reorder_point": 20,
            "reorder_quantity": 50,
            "warehouse_location": "A-101",
        }
        create_response = await client.post("/api/v1/inventory", json=inventory_data)
        inventory_id = create_response.json()["id"]

        # Update inventory
        update_data = {
            "reorder_point": 30,
            "reorder_quantity": 60,
        }
        response = await client.put(
            f"/api/v1/inventory/{inventory_id}", json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["reorder_point"] == 30
        assert data["reorder_quantity"] == 60

    async def test_reserve_stock(self, client: AsyncClient):
        """Test reserving stock."""
        product_id = await self._create_product(client)

        # Create inventory with stock
        inventory_data = {
            "product_id": product_id,
            "quantity": 100,
            "reorder_point": 20,
            "reorder_quantity": 50,
            "warehouse_location": "A-101",
        }
        await client.post("/api/v1/inventory", json=inventory_data)

        # Reserve stock
        response = await client.post(
            f"/api/v1/inventory/product/{product_id}/reserve",
            json={"quantity": 30},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["reserved"] == 30
        assert data["available"] == 70
        assert data["quantity"] == 100

    async def test_reserve_stock_insufficient(self, client: AsyncClient):
        """Test reserving more stock than available."""
        product_id = await self._create_product(client)

        # Create inventory with limited stock
        inventory_data = {
            "product_id": product_id,
            "quantity": 10,
            "reorder_point": 5,
            "reorder_quantity": 50,
            "warehouse_location": "A-101",
        }
        await client.post("/api/v1/inventory", json=inventory_data)

        # Try to reserve more than available
        response = await client.post(
            f"/api/v1/inventory/product/{product_id}/reserve",
            json={"quantity": 20},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_release_reservation(self, client: AsyncClient):
        """Test releasing reserved stock."""
        product_id = await self._create_product(client)

        # Create inventory and reserve stock
        inventory_data = {
            "product_id": product_id,
            "quantity": 100,
            "reorder_point": 20,
            "reorder_quantity": 50,
            "warehouse_location": "A-101",
        }
        await client.post("/api/v1/inventory", json=inventory_data)
        await client.post(
            f"/api/v1/inventory/product/{product_id}/reserve",
            json={"quantity": 30},
        )

        # Release reservation
        response = await client.post(
            f"/api/v1/inventory/product/{product_id}/release",
            json={"quantity": 20},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["reserved"] == 10
        assert data["available"] == 90

    async def test_fulfill_reservation(self, client: AsyncClient):
        """Test fulfilling reservation (shipping order)."""
        product_id = await self._create_product(client)

        # Create inventory and reserve stock
        inventory_data = {
            "product_id": product_id,
            "quantity": 100,
            "reorder_point": 20,
            "reorder_quantity": 50,
            "warehouse_location": "A-101",
        }
        await client.post("/api/v1/inventory", json=inventory_data)
        await client.post(
            f"/api/v1/inventory/product/{product_id}/reserve",
            json={"quantity": 30},
        )

        # Fulfill order
        response = await client.post(
            f"/api/v1/inventory/product/{product_id}/fulfill",
            json={"quantity": 30},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["quantity"] == 70  # Decreased
        assert data["reserved"] == 0  # Released
        assert data["available"] == 70

    async def test_add_stock(self, client: AsyncClient):
        """Test adding stock (restock operation)."""
        product_id = await self._create_product(client)

        # Create inventory
        inventory_data = {
            "product_id": product_id,
            "quantity": 10,
            "reorder_point": 20,
            "reorder_quantity": 50,
            "warehouse_location": "A-101",
        }
        await client.post("/api/v1/inventory", json=inventory_data)

        # Add stock
        response = await client.post(
            f"/api/v1/inventory/product/{product_id}/add",
            json={"quantity": 50},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["quantity"] == 60
        assert data["last_restock_date"] is not None

    async def test_remove_stock(self, client: AsyncClient):
        """Test removing stock (shrinkage/damage)."""
        product_id = await self._create_product(client)

        # Create inventory
        inventory_data = {
            "product_id": product_id,
            "quantity": 100,
            "reorder_point": 20,
            "reorder_quantity": 50,
            "warehouse_location": "A-101",
        }
        await client.post("/api/v1/inventory", json=inventory_data)

        # Remove stock
        response = await client.post(
            f"/api/v1/inventory/product/{product_id}/remove",
            json={"quantity": 20},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["quantity"] == 80

    async def test_get_low_stock_items(self, client: AsyncClient):
        """Test getting low stock alerts."""
        product_id = await self._create_product(client)

        # Create inventory with low stock
        inventory_data = {
            "product_id": product_id,
            "quantity": 15,  # Below reorder point of 20
            "reorder_point": 20,
            "reorder_quantity": 50,
            "warehouse_location": "A-101",
        }
        await client.post("/api/v1/inventory", json=inventory_data)

        # Get low stock items
        response = await client.get("/api/v1/inventory/alerts/low-stock")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should include our low stock item
        product_ids = [item["product_id"] for item in data["items"]]
        assert product_id in product_ids

    async def test_get_out_of_stock_items(self, client: AsyncClient):
        """Test getting out of stock items."""
        product_id = await self._create_product(client)

        # Create inventory with no stock
        inventory_data = {
            "product_id": product_id,
            "quantity": 0,
            "reorder_point": 20,
            "reorder_quantity": 50,
            "warehouse_location": "A-101",
        }
        await client.post("/api/v1/inventory", json=inventory_data)

        # Get out of stock items
        response = await client.get("/api/v1/inventory/alerts/out-of-stock")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        product_ids = [item["product_id"] for item in data["items"]]
        assert product_id in product_ids

    async def test_get_inventory_snapshot(self, client: AsyncClient):
        """Test getting inventory snapshot for reporting."""
        # Create inventory items
        for _ in range(3):
            product_id = await self._create_product(client)
            inventory_data = {
                "product_id": product_id,
                "quantity": 100,
                "reorder_point": 20,
                "reorder_quantity": 50,
                "warehouse_location": "A-101",
            }
            await client.post("/api/v1/inventory", json=inventory_data)

        # Get snapshot
        response = await client.get("/api/v1/inventory/reports/snapshot")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    async def test_get_total_inventory_value(self, client: AsyncClient):
        """Test getting total inventory value."""
        # Create product and inventory
        product_id = await self._create_product(client)
        inventory_data = {
            "product_id": product_id,
            "quantity": 100,
            "reorder_point": 20,
            "reorder_quantity": 50,
            "warehouse_location": "A-101",
        }
        await client.post("/api/v1/inventory", json=inventory_data)

        # Get total value
        response = await client.get("/api/v1/inventory/reports/total-value")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_value" in data
        assert data["total_value"] >= 0

    async def test_complete_order_workflow(self, client: AsyncClient):
        """Test complete order workflow: reserve -> fulfill."""
        product_id = await self._create_product(client)

        # 1. Create inventory
        inventory_data = {
            "product_id": product_id,
            "quantity": 100,
            "reorder_point": 20,
            "reorder_quantity": 50,
            "warehouse_location": "A-101",
        }
        await client.post("/api/v1/inventory", json=inventory_data)

        # 2. Reserve stock for order
        reserve_response = await client.post(
            f"/api/v1/inventory/product/{product_id}/reserve",
            json={"quantity": 25},
        )
        assert reserve_response.status_code == status.HTTP_200_OK

        # 3. Fulfill order (ship)
        fulfill_response = await client.post(
            f"/api/v1/inventory/product/{product_id}/fulfill",
            json={"quantity": 25},
        )
        assert fulfill_response.status_code == status.HTTP_200_OK
        data = fulfill_response.json()
        assert data["quantity"] == 75
        assert data["reserved"] == 0
        assert data["available"] == 75
