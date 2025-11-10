"""Inventory command handlers for write operations.

Implements CQRS pattern - commands represent intent to change state.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from uuid import UUID

from src.domain.models.inventory import (
    InventoryItem,
)
from src.domain.repositories.inventory_repository import (
    InventoryRepository,
)


# Command models


@dataclass
class CreateInventoryCommand:
    """Command to create inventory for a product."""

    product_id: UUID
    quantity: int
    reorder_point: int
    reorder_quantity: int
    warehouse_location: str


@dataclass
class UpdateInventoryCommand:
    """Command to update inventory settings."""

    inventory_id: UUID
    reorder_point: Optional[int] = None
    reorder_quantity: Optional[int] = None
    warehouse_location: Optional[str] = None


@dataclass
class ReserveStockCommand:
    """Command to reserve stock for an order."""

    product_id: UUID
    quantity: int


@dataclass
class ReleaseReservationCommand:
    """Command to release reserved stock."""

    product_id: UUID
    quantity: int


@dataclass
class FulfillReservationCommand:
    """Command to fulfill reservation (ship order)."""

    product_id: UUID
    quantity: int


@dataclass
class AddStockCommand:
    """Command to add stock (restock)."""

    product_id: UUID
    quantity: int


@dataclass
class RemoveStockCommand:
    """Command to remove stock (shrinkage, damage)."""

    product_id: UUID
    quantity: int


@dataclass
class TransferStockCommand:
    """Command to transfer stock between locations."""

    product_id: UUID
    from_location: str
    to_location: str
    quantity: int


@dataclass
class BulkUpdateReorderPointsCommand:
    """Command to bulk update reorder points."""

    updates: List[Tuple[UUID, int]]  # (product_id, new_reorder_point)


# Command handler


class InventoryCommandHandler:
    """Handles inventory write operations.

    Orchestrates domain logic and repository operations for commands.
    """

    __slots__ = ("_repository",)

    def __init__(self, repository: InventoryRepository):
        """Initialize command handler.

        Args:
            repository: Inventory repository implementation
        """
        self._repository = repository

    async def handle_create(self, command: CreateInventoryCommand) -> InventoryItem:
        """Handle create inventory command.

        Args:
            command: Create inventory command

        Returns:
            Created inventory item

        Raises:
            ValueError: If inventory already exists for product
        """
        # Check if inventory already exists
        existing = await self._repository.get_by_product_id(command.product_id)
        if existing:
            raise ValueError(
                f"Inventory already exists for product {command.product_id}"
            )

        # Create domain entity
        inventory = InventoryItem.create(
            product_id=command.product_id,
            quantity=command.quantity,
            reorder_point=command.reorder_point,
            reorder_quantity=command.reorder_quantity,
            warehouse_location=command.warehouse_location,
        )

        # Persist
        return await self._repository.create(inventory)

    async def handle_update(self, command: UpdateInventoryCommand) -> InventoryItem:
        """Handle update inventory command.

        Args:
            command: Update inventory command

        Returns:
            Updated inventory item

        Raises:
            ValueError: If inventory not found
        """
        # Get existing inventory
        inventory = await self._repository.get_by_id(command.inventory_id)
        if not inventory:
            raise ValueError(f"Inventory {command.inventory_id} not found")

        # Apply updates
        if command.reorder_point is not None:
            inventory.reorder_point = command.reorder_point

        if command.reorder_quantity is not None:
            inventory.reorder_quantity = command.reorder_quantity

        if command.warehouse_location is not None:
            inventory.warehouse_location = command.warehouse_location

        # Status might change based on reorder point
        inventory._update_status()

        # Persist
        return await self._repository.update(inventory)

    async def handle_reserve_stock(
        self, command: ReserveStockCommand
    ) -> InventoryItem:
        """Handle reserve stock command.

        Args:
            command: Reserve stock command

        Returns:
            Updated inventory item

        Raises:
            ValueError: If insufficient stock or command invalid
        """
        # Use repository atomic operation to prevent race conditions
        result = await self._repository.reserve_stock(
            command.product_id, command.quantity
        )

        if not result:
            raise ValueError(
                f"Insufficient stock for product {command.product_id}: "
                f"requested {command.quantity}"
            )

        return result

    async def handle_release_reservation(
        self, command: ReleaseReservationCommand
    ) -> InventoryItem:
        """Handle release reservation command.

        Args:
            command: Release reservation command

        Returns:
            Updated inventory item

        Raises:
            ValueError: If inventory not found or command invalid
        """
        result = await self._repository.release_reservation(
            command.product_id, command.quantity
        )

        if not result:
            raise ValueError(f"Inventory not found for product {command.product_id}")

        return result

    async def handle_fulfill_reservation(
        self, command: FulfillReservationCommand
    ) -> InventoryItem:
        """Handle fulfill reservation command.

        Args:
            command: Fulfill reservation command

        Returns:
            Updated inventory item

        Raises:
            ValueError: If inventory not found or command invalid
        """
        result = await self._repository.fulfill_reservation(
            command.product_id, command.quantity
        )

        if not result:
            raise ValueError(f"Inventory not found for product {command.product_id}")

        return result

    async def handle_add_stock(self, command: AddStockCommand) -> InventoryItem:
        """Handle add stock command.

        Args:
            command: Add stock command

        Returns:
            Updated inventory item

        Raises:
            ValueError: If inventory not found or command invalid
        """
        result = await self._repository.add_stock(command.product_id, command.quantity)

        if not result:
            raise ValueError(f"Inventory not found for product {command.product_id}")

        return result

    async def handle_remove_stock(self, command: RemoveStockCommand) -> InventoryItem:
        """Handle remove stock command.

        Args:
            command: Remove stock command

        Returns:
            Updated inventory item

        Raises:
            ValueError: If inventory not found or insufficient stock
        """
        result = await self._repository.remove_stock(
            command.product_id, command.quantity
        )

        if not result:
            raise ValueError(f"Inventory not found for product {command.product_id}")

        return result

    async def handle_transfer_stock(self, command: TransferStockCommand) -> bool:
        """Handle transfer stock command.

        Args:
            command: Transfer stock command

        Returns:
            True if successful

        Raises:
            ValueError: If locations are same or command invalid
        """
        if command.from_location == command.to_location:
            raise ValueError("Cannot transfer stock to same location")

        result = await self._repository.transfer_stock(
            command.product_id,
            command.from_location,
            command.to_location,
            command.quantity,
        )

        if not result:
            raise ValueError("Stock transfer failed")

        return result

    async def handle_bulk_update_reorder_points(
        self, command: BulkUpdateReorderPointsCommand
    ) -> int:
        """Handle bulk update reorder points command.

        Args:
            command: Bulk update command

        Returns:
            Number of items updated
        """
        return await self._repository.bulk_update_reorder_points(command.updates)
