"""Inventory query handlers for read operations.

Implements CQRS pattern - queries are optimized for reading.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from examples.01_high_performance_rest_api.src.domain.models.inventory import (
    InventoryItem,
    InventoryStatus,
)
from examples.01_high_performance_rest_api.src.domain.repositories.inventory_repository import (
    InventoryRepository,
)


# Query models


@dataclass
class GetInventoryByIdQuery:
    """Query to get inventory by ID."""

    inventory_id: UUID


@dataclass
class GetInventoryByProductIdQuery:
    """Query to get inventory by product ID."""

    product_id: UUID


@dataclass
class GetAllInventoryQuery:
    """Query to get all inventory with pagination."""

    skip: int = 0
    limit: int = 100
    status: Optional[InventoryStatus] = None


@dataclass
class GetInventoryByLocationQuery:
    """Query to get inventory by warehouse location."""

    warehouse_location: str
    skip: int = 0
    limit: int = 100


@dataclass
class GetLowStockItemsQuery:
    """Query to get low stock items."""

    skip: int = 0
    limit: int = 100


@dataclass
class GetOutOfStockItemsQuery:
    """Query to get out of stock items."""

    skip: int = 0
    limit: int = 100


@dataclass
class GetItemsNeedingRestockQuery:
    """Query to get items needing restock."""

    skip: int = 0
    limit: int = 100


@dataclass
class GetInventorySnapshotQuery:
    """Query to get inventory snapshot for reporting."""

    as_of_date: Optional[datetime] = None


# Query handler


class InventoryQueryHandler:
    """Handles inventory read operations.

    Optimized for read performance with caching and efficient queries.
    """

    __slots__ = ("_repository",)

    def __init__(self, repository: InventoryRepository):
        """Initialize query handler.

        Args:
            repository: Inventory repository implementation
        """
        self._repository = repository

    async def handle_get_by_id(
        self, query: GetInventoryByIdQuery
    ) -> Optional[InventoryItem]:
        """Handle get inventory by ID query.

        Args:
            query: Get by ID query

        Returns:
            Inventory item if found, None otherwise
        """
        return await self._repository.get_by_id(query.inventory_id)

    async def handle_get_by_product_id(
        self, query: GetInventoryByProductIdQuery
    ) -> Optional[InventoryItem]:
        """Handle get inventory by product ID query.

        Args:
            query: Get by product ID query

        Returns:
            Inventory item if found, None otherwise
        """
        return await self._repository.get_by_product_id(query.product_id)

    async def handle_get_all(self, query: GetAllInventoryQuery) -> List[InventoryItem]:
        """Handle get all inventory query.

        Args:
            query: Get all query

        Returns:
            List of inventory items
        """
        return await self._repository.get_all(
            skip=query.skip,
            limit=query.limit,
            status=query.status,
        )

    async def handle_get_by_location(
        self, query: GetInventoryByLocationQuery
    ) -> List[InventoryItem]:
        """Handle get inventory by location query.

        Args:
            query: Get by location query

        Returns:
            List of inventory items in location
        """
        return await self._repository.get_by_warehouse_location(
            warehouse_location=query.warehouse_location,
            skip=query.skip,
            limit=query.limit,
        )

    async def handle_get_low_stock(
        self, query: GetLowStockItemsQuery
    ) -> List[InventoryItem]:
        """Handle get low stock items query.

        Args:
            query: Get low stock query

        Returns:
            List of low stock items
        """
        return await self._repository.get_low_stock_items(
            skip=query.skip,
            limit=query.limit,
        )

    async def handle_get_out_of_stock(
        self, query: GetOutOfStockItemsQuery
    ) -> List[InventoryItem]:
        """Handle get out of stock items query.

        Args:
            query: Get out of stock query

        Returns:
            List of out of stock items
        """
        return await self._repository.get_out_of_stock_items(
            skip=query.skip,
            limit=query.limit,
        )

    async def handle_get_items_needing_restock(
        self, query: GetItemsNeedingRestockQuery
    ) -> List[InventoryItem]:
        """Handle get items needing restock query.

        Args:
            query: Get items needing restock query

        Returns:
            List of items needing restock
        """
        return await self._repository.get_items_needing_restock(
            skip=query.skip,
            limit=query.limit,
        )

    async def handle_get_by_status(
        self, status: InventoryStatus, skip: int = 0, limit: int = 100
    ) -> List[InventoryItem]:
        """Handle get inventory by status query.

        Args:
            status: Inventory status
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of inventory items with status
        """
        return await self._repository.get_by_status(
            status=status,
            skip=skip,
            limit=limit,
        )

    async def handle_get_snapshot(
        self, query: GetInventorySnapshotQuery
    ) -> List[dict]:
        """Handle get inventory snapshot query.

        Args:
            query: Get snapshot query

        Returns:
            List of inventory snapshots with product details
        """
        return await self._repository.get_inventory_snapshot(
            as_of_date=query.as_of_date
        )

    async def handle_count(self, status: Optional[InventoryStatus] = None) -> int:
        """Handle count inventory query.

        Args:
            status: Filter by status (optional)

        Returns:
            Number of inventory items
        """
        return await self._repository.count(status=status)

    async def handle_get_total_value(
        self, warehouse_location: Optional[str] = None
    ) -> float:
        """Handle get total inventory value query.

        Args:
            warehouse_location: Filter by location (optional)

        Returns:
            Total inventory value
        """
        return await self._repository.get_total_value(
            warehouse_location=warehouse_location
        )

    async def handle_exists(self, inventory_id: UUID) -> bool:
        """Handle inventory exists query.

        Args:
            inventory_id: Inventory ID

        Returns:
            True if exists, False otherwise
        """
        return await self._repository.exists(inventory_id)
