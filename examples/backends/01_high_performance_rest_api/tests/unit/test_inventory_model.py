"""Unit tests for Inventory domain model."""

from datetime import datetime
from uuid import uuid4

import pytest

from examples.01_high_performance_rest_api.src.domain.models.inventory import (
    InventoryItem,
    InventoryStatus,
)


@pytest.mark.unit
class TestInventoryModel:
    """Test Inventory domain model."""

    def test_create_inventory(self):
        """Test creating inventory item."""
        product_id = uuid4()
        inventory = InventoryItem.create(
            product_id=product_id,
            quantity=100,
            reorder_point=20,
            reorder_quantity=50,
            warehouse_location="A-101",
        )

        assert inventory.id is not None
        assert inventory.product_id == product_id
        assert inventory.quantity == 100
        assert inventory.reserved == 0
        assert inventory.reorder_point == 20
        assert inventory.reorder_quantity == 50
        assert inventory.warehouse_location == "A-101"
        assert inventory.status == InventoryStatus.IN_STOCK
        assert isinstance(inventory.updated_at, datetime)

    def test_available_property(self):
        """Test available quantity calculation."""
        inventory = InventoryItem.create(
            product_id=uuid4(),
            quantity=100,
            reorder_point=20,
            reorder_quantity=50,
            warehouse_location="A-101",
        )

        assert inventory.available == 100

        # Reserve some stock
        inventory.reserved = 30
        assert inventory.available == 70

    def test_needs_reorder_property(self):
        """Test needs_reorder property."""
        inventory = InventoryItem.create(
            product_id=uuid4(),
            quantity=100,
            reorder_point=20,
            reorder_quantity=50,
            warehouse_location="A-101",
        )

        assert inventory.needs_reorder is False

        # Set quantity below reorder point
        inventory.quantity = 15
        assert inventory.needs_reorder is True

        # At reorder point should also trigger
        inventory.quantity = 20
        assert inventory.needs_reorder is True

    def test_reserve_stock_success(self):
        """Test successful stock reservation."""
        inventory = InventoryItem.create(
            product_id=uuid4(),
            quantity=100,
            reorder_point=20,
            reorder_quantity=50,
            warehouse_location="A-101",
        )

        success = inventory.reserve(30)
        assert success is True
        assert inventory.reserved == 30
        assert inventory.available == 70
        assert inventory.quantity == 100  # Total doesn't change

    def test_reserve_stock_insufficient(self):
        """Test stock reservation with insufficient stock."""
        inventory = InventoryItem.create(
            product_id=uuid4(),
            quantity=100,
            reorder_point=20,
            reorder_quantity=50,
            warehouse_location="A-101",
        )

        # Try to reserve more than available
        success = inventory.reserve(150)
        assert success is False
        assert inventory.reserved == 0  # Nothing reserved

    def test_reserve_stock_invalid_quantity(self):
        """Test stock reservation with invalid quantity."""
        inventory = InventoryItem.create(
            product_id=uuid4(),
            quantity=100,
            reorder_point=20,
            reorder_quantity=50,
            warehouse_location="A-101",
        )

        with pytest.raises(ValueError):
            inventory.reserve(0)

        with pytest.raises(ValueError):
            inventory.reserve(-10)

    def test_release_reservation_success(self):
        """Test successful reservation release."""
        inventory = InventoryItem.create(
            product_id=uuid4(),
            quantity=100,
            reorder_point=20,
            reorder_quantity=50,
            warehouse_location="A-101",
        )

        inventory.reserve(30)
        success = inventory.release(20)

        assert success is True
        assert inventory.reserved == 10
        assert inventory.available == 90

    def test_release_reservation_insufficient(self):
        """Test release with insufficient reserved amount."""
        inventory = InventoryItem.create(
            product_id=uuid4(),
            quantity=100,
            reorder_point=20,
            reorder_quantity=50,
            warehouse_location="A-101",
        )

        inventory.reserve(30)

        # Try to release more than reserved
        success = inventory.release(50)
        assert success is False
        assert inventory.reserved == 30  # Unchanged

    def test_fulfill_success(self):
        """Test successful order fulfillment."""
        inventory = InventoryItem.create(
            product_id=uuid4(),
            quantity=100,
            reorder_point=20,
            reorder_quantity=50,
            warehouse_location="A-101",
        )

        inventory.reserve(30)
        success = inventory.fulfill(30)

        assert success is True
        assert inventory.quantity == 70  # Decreased
        assert inventory.reserved == 0  # Released
        assert inventory.available == 70

    def test_fulfill_partial(self):
        """Test partial order fulfillment."""
        inventory = InventoryItem.create(
            product_id=uuid4(),
            quantity=100,
            reorder_point=20,
            reorder_quantity=50,
            warehouse_location="A-101",
        )

        inventory.reserve(50)
        success = inventory.fulfill(30)

        assert success is True
        assert inventory.quantity == 70
        assert inventory.reserved == 20  # Still 20 reserved
        assert inventory.available == 50

    def test_add_stock(self):
        """Test adding stock (restock)."""
        inventory = InventoryItem.create(
            product_id=uuid4(),
            quantity=100,
            reorder_point=20,
            reorder_quantity=50,
            warehouse_location="A-101",
        )

        inventory.add_stock(50)

        assert inventory.quantity == 150
        assert inventory.last_restock_date is not None

    def test_add_stock_invalid_quantity(self):
        """Test adding invalid stock quantity."""
        inventory = InventoryItem.create(
            product_id=uuid4(),
            quantity=100,
            reorder_point=20,
            reorder_quantity=50,
            warehouse_location="A-101",
        )

        with pytest.raises(ValueError):
            inventory.add_stock(0)

        with pytest.raises(ValueError):
            inventory.add_stock(-10)

    def test_remove_stock_success(self):
        """Test removing stock (shrinkage/damage)."""
        inventory = InventoryItem.create(
            product_id=uuid4(),
            quantity=100,
            reorder_point=20,
            reorder_quantity=50,
            warehouse_location="A-101",
        )

        success = inventory.remove_stock(20)

        assert success is True
        assert inventory.quantity == 80
        assert inventory.available == 80

    def test_remove_stock_with_reserved(self):
        """Test removing stock with reservations."""
        inventory = InventoryItem.create(
            product_id=uuid4(),
            quantity=100,
            reorder_point=20,
            reorder_quantity=50,
            warehouse_location="A-101",
        )

        inventory.reserve(30)

        # Can only remove from available (70)
        success = inventory.remove_stock(50)
        assert success is True
        assert inventory.quantity == 50
        assert inventory.reserved == 30  # Unchanged
        assert inventory.available == 20

        # Can't remove more than available
        success = inventory.remove_stock(30)
        assert success is False

    def test_status_updates(self):
        """Test automatic status updates."""
        inventory = InventoryItem.create(
            product_id=uuid4(),
            quantity=100,
            reorder_point=20,
            reorder_quantity=50,
            warehouse_location="A-101",
        )

        assert inventory.status == InventoryStatus.IN_STOCK

        # Reduce to low stock
        inventory.quantity = 15
        inventory._update_status()
        assert inventory.status == InventoryStatus.LOW_STOCK

        # Reduce to out of stock
        inventory.quantity = 0
        inventory._update_status()
        assert inventory.status == InventoryStatus.OUT_OF_STOCK

        # Restock
        inventory.add_stock(100)
        assert inventory.status == InventoryStatus.IN_STOCK

    def test_slots_optimization(self):
        """Test that __slots__ is properly defined for memory optimization."""
        inventory = InventoryItem.create(
            product_id=uuid4(),
            quantity=100,
            reorder_point=20,
            reorder_quantity=50,
            warehouse_location="A-101",
        )

        # __slots__ objects don't have __dict__
        assert not hasattr(inventory, "__dict__")

    def test_concurrent_reservations_simulation(self):
        """Test multiple reservations to simulate concurrent access."""
        inventory = InventoryItem.create(
            product_id=uuid4(),
            quantity=100,
            reorder_point=20,
            reorder_quantity=50,
            warehouse_location="A-101",
        )

        # Simulate multiple concurrent reservations
        # In real implementation, these would be atomic at DB level
        assert inventory.reserve(30) is True
        assert inventory.reserve(30) is True
        assert inventory.reserve(30) is True
        assert inventory.reserve(30) is False  # Should fail, only 10 available

        assert inventory.reserved == 90
        assert inventory.available == 10
