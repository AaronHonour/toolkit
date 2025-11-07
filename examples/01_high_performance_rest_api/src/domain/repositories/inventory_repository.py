"""Inventory repository interface.

Defines the contract for inventory data access operations.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from examples.01_high_performance_rest_api.src.domain.models.inventory import (
    InventoryItem,
    InventoryStatus,
)


class InventoryRepository(ABC):
    """Abstract repository for InventoryItem entities.

    Defines the port for inventory data access in hexagonal architecture.
    Implementations (adapters) will be in the infrastructure layer.
    """

    @abstractmethod
    async def get_by_id(self, inventory_id: UUID) -> Optional[InventoryItem]:
        """Get inventory item by ID.

        Args:
            inventory_id: Inventory item unique identifier

        Returns:
            InventoryItem if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_product_id(self, product_id: UUID) -> Optional[InventoryItem]:
        """Get inventory item by product ID.

        Args:
            product_id: Product unique identifier

        Returns:
            InventoryItem if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[InventoryStatus] = None
    ) -> List[InventoryItem]:
        """Get all inventory items with pagination and filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by inventory status (optional)

        Returns:
            List of inventory items
        """
        pass

    @abstractmethod
    async def get_by_warehouse_location(
        self,
        warehouse_location: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryItem]:
        """Get inventory items by warehouse location.

        Args:
            warehouse_location: Warehouse location code
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of inventory items in location
        """
        pass

    @abstractmethod
    async def get_low_stock_items(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryItem]:
        """Get items with low stock (below reorder point).

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of low stock items
        """
        pass

    @abstractmethod
    async def get_out_of_stock_items(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryItem]:
        """Get items that are out of stock.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of out of stock items
        """
        pass

    @abstractmethod
    async def get_items_needing_restock(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryItem]:
        """Get items that need restocking (at or below reorder point).

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of items needing restock
        """
        pass

    @abstractmethod
    async def get_by_status(
        self,
        status: InventoryStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryItem]:
        """Get inventory items by status.

        Args:
            status: Inventory status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of inventory items with status
        """
        pass

    @abstractmethod
    async def reserve_stock(
        self,
        product_id: UUID,
        quantity: int
    ) -> Optional[InventoryItem]:
        """Reserve stock for a product.

        This is an atomic operation that checks availability and reserves
        stock in a single transaction to prevent race conditions.

        Args:
            product_id: Product unique identifier
            quantity: Quantity to reserve

        Returns:
            Updated inventory item if successful, None if insufficient stock

        Raises:
            ValueError: If quantity is invalid
        """
        pass

    @abstractmethod
    async def release_reservation(
        self,
        product_id: UUID,
        quantity: int
    ) -> Optional[InventoryItem]:
        """Release reserved stock.

        Args:
            product_id: Product unique identifier
            quantity: Quantity to release

        Returns:
            Updated inventory item if successful, None if not found

        Raises:
            ValueError: If quantity is invalid or exceeds reserved amount
        """
        pass

    @abstractmethod
    async def fulfill_reservation(
        self,
        product_id: UUID,
        quantity: int
    ) -> Optional[InventoryItem]:
        """Fulfill reservation (convert reservation to actual removal).

        This is an atomic operation that decreases both reserved and total
        quantity in a single transaction.

        Args:
            product_id: Product unique identifier
            quantity: Quantity to fulfill

        Returns:
            Updated inventory item if successful, None if not found

        Raises:
            ValueError: If quantity is invalid or exceeds reserved amount
        """
        pass

    @abstractmethod
    async def add_stock(
        self,
        product_id: UUID,
        quantity: int
    ) -> Optional[InventoryItem]:
        """Add stock to inventory (restock operation).

        Args:
            product_id: Product unique identifier
            quantity: Quantity to add

        Returns:
            Updated inventory item if successful, None if not found

        Raises:
            ValueError: If quantity is invalid
        """
        pass

    @abstractmethod
    async def remove_stock(
        self,
        product_id: UUID,
        quantity: int
    ) -> Optional[InventoryItem]:
        """Remove stock from inventory (shrinkage, damage, etc.).

        Args:
            product_id: Product unique identifier
            quantity: Quantity to remove

        Returns:
            Updated inventory item if successful, None if not found

        Raises:
            ValueError: If quantity is invalid or exceeds available stock
        """
        pass

    @abstractmethod
    async def transfer_stock(
        self,
        product_id: UUID,
        from_location: str,
        to_location: str,
        quantity: int
    ) -> bool:
        """Transfer stock between warehouse locations.

        Args:
            product_id: Product unique identifier
            from_location: Source warehouse location
            to_location: Destination warehouse location
            quantity: Quantity to transfer

        Returns:
            True if successful, False otherwise

        Raises:
            ValueError: If quantity is invalid or locations are the same
        """
        pass

    @abstractmethod
    async def create(self, inventory_item: InventoryItem) -> InventoryItem:
        """Create new inventory item.

        Args:
            inventory_item: Inventory item to create

        Returns:
            Created inventory item with generated ID and timestamps
        """
        pass

    @abstractmethod
    async def update(self, inventory_item: InventoryItem) -> InventoryItem:
        """Update existing inventory item.

        Args:
            inventory_item: Inventory item with updated data

        Returns:
            Updated inventory item

        Raises:
            ValueError: If inventory item not found
        """
        pass

    @abstractmethod
    async def delete(self, inventory_id: UUID) -> bool:
        """Delete inventory item by ID.

        Args:
            inventory_id: Inventory item unique identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def count(self, status: Optional[InventoryStatus] = None) -> int:
        """Count inventory items.

        Args:
            status: Filter by inventory status (optional)

        Returns:
            Number of inventory items
        """
        pass

    @abstractmethod
    async def exists(self, inventory_id: UUID) -> bool:
        """Check if inventory item exists.

        Args:
            inventory_id: Inventory item unique identifier

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def get_total_value(
        self,
        warehouse_location: Optional[str] = None
    ) -> float:
        """Calculate total inventory value.

        Requires joining with product data to get costs.

        Args:
            warehouse_location: Filter by location (optional)

        Returns:
            Total inventory value (quantity * product cost)
        """
        pass

    @abstractmethod
    async def bulk_update_reorder_points(
        self,
        updates: List[tuple[UUID, int]]
    ) -> int:
        """Bulk update reorder points for multiple items.

        Args:
            updates: List of (product_id, new_reorder_point) tuples

        Returns:
            Number of items updated
        """
        pass

    @abstractmethod
    async def get_inventory_snapshot(
        self,
        as_of_date: Optional[datetime] = None
    ) -> List[dict]:
        """Get inventory snapshot for reporting.

        Args:
            as_of_date: Date for snapshot (defaults to now)

        Returns:
            List of inventory snapshots with product details
        """
        pass
