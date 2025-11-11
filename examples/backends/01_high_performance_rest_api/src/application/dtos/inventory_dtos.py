"""Inventory Data Transfer Objects for API layer.

DTOs are optimized for JSON serialization and API responses.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.domain.models.inventory import (
    InventoryItem,
    StockStatus,
)


@dataclass
class InventoryItemDTO:
    """Inventory item DTO for API responses.

    Optimized for JSON serialization with all computed fields.
    """

    id: str  # UUID as string for JSON
    product_id: str  # UUID as string
    quantity: int
    reserved: int
    available: int  # Computed field
    reorder_point: int
    reorder_quantity: int
    warehouse_location: str
    status: str  # StockStatus as string
    needs_reorder: bool  # Computed field
    last_restock_date: Optional[str]  # datetime as ISO string
    updated_at: str  # datetime as ISO string

    @classmethod
    def from_domain(cls, inventory: InventoryItem) -> "InventoryItemDTO":
        """Convert domain model to DTO.

        Args:
            inventory: Domain inventory entity

        Returns:
            Inventory item DTO
        """
        return cls(
            id=str(inventory.id),
            product_id=str(inventory.product_id),
            quantity=inventory.quantity,
            reserved=inventory.reserved,
            available=inventory.available,
            reorder_point=inventory.reorder_point,
            reorder_quantity=inventory.reorder_quantity,
            warehouse_location=inventory.warehouse_location,
            status=inventory.status.value,
            needs_reorder=inventory.needs_reorder,
            last_restock_date=(
                inventory.last_restock_date.isoformat()
                if inventory.last_restock_date
                else None
            ),
            updated_at=inventory.updated_at.isoformat(),
        )


@dataclass
class CreateInventoryDTO:
    """DTO for creating inventory for a product."""

    product_id: UUID
    quantity: int
    reorder_point: int
    reorder_quantity: int
    warehouse_location: str


@dataclass
class UpdateInventoryDTO:
    """DTO for updating inventory settings."""

    reorder_point: Optional[int] = None
    reorder_quantity: Optional[int] = None
    warehouse_location: Optional[str] = None


@dataclass
class StockOperationDTO:
    """DTO for stock operations (reserve, add, remove, etc.)."""

    quantity: int


@dataclass
class TransferStockDTO:
    """DTO for stock transfer operations."""

    from_location: str
    to_location: str
    quantity: int


@dataclass
class InventoryListDTO:
    """DTO for paginated inventory list responses."""

    items: List[InventoryItemDTO]
    total: int
    skip: int
    limit: int
    has_more: bool

    @classmethod
    def from_domain_list(
        cls,
        inventory_items: List[InventoryItem],
        total: int,
        skip: int,
        limit: int,
    ) -> "InventoryListDTO":
        """Convert domain list to DTO.

        Args:
            inventory_items: List of domain inventory items
            total: Total count of items
            skip: Number of items skipped
            limit: Maximum items per page

        Returns:
            Inventory list DTO
        """
        return cls(
            items=[InventoryItemDTO.from_domain(i) for i in inventory_items],
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + len(inventory_items)) < total,
        )
