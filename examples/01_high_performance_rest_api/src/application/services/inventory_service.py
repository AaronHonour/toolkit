"""Inventory application service.

Orchestrates inventory operations between commands, queries, and DTOs.
"""

from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from examples.01_high_performance_rest_api.src.application.commands.inventory_commands import (
    CreateInventoryCommand,
    UpdateInventoryCommand,
    ReserveStockCommand,
    ReleaseReservationCommand,
    FulfillReservationCommand,
    AddStockCommand,
    RemoveStockCommand,
    TransferStockCommand,
    BulkUpdateReorderPointsCommand,
    InventoryCommandHandler,
)
from examples.01_high_performance_rest_api.src.application.queries.inventory_queries import (
    GetInventoryByIdQuery,
    GetInventoryByProductIdQuery,
    GetAllInventoryQuery,
    GetInventoryByLocationQuery,
    GetLowStockItemsQuery,
    GetOutOfStockItemsQuery,
    GetItemsNeedingRestockQuery,
    GetInventorySnapshotQuery,
    InventoryQueryHandler,
)
from examples.01_high_performance_rest_api.src.application.dtos.inventory_dtos import (
    InventoryItemDTO,
    CreateInventoryDTO,
    UpdateInventoryDTO,
    InventoryListDTO,
)
from examples.01_high_performance_rest_api.src.domain.models.inventory import (
    InventoryStatus,
)
from examples.01_high_performance_rest_api.src.domain.repositories.inventory_repository import (
    InventoryRepository,
)


class InventoryService:
    """Application service for inventory operations.

    Provides high-level API for inventory management, coordinating
    between commands, queries, and DTOs.
    """

    __slots__ = ("_command_handler", "_query_handler")

    def __init__(self, repository: InventoryRepository):
        """Initialize inventory service.

        Args:
            repository: Inventory repository implementation
        """
        self._command_handler = InventoryCommandHandler(repository)
        self._query_handler = InventoryQueryHandler(repository)

    # Query operations

    async def get_by_id(self, inventory_id: UUID) -> Optional[InventoryItemDTO]:
        """Get inventory by ID.

        Args:
            inventory_id: Inventory unique identifier

        Returns:
            Inventory DTO if found, None otherwise
        """
        query = GetInventoryByIdQuery(inventory_id=inventory_id)
        inventory = await self._query_handler.handle_get_by_id(query)

        if not inventory:
            return None

        return InventoryItemDTO.from_domain(inventory)

    async def get_by_product_id(self, product_id: UUID) -> Optional[InventoryItemDTO]:
        """Get inventory by product ID.

        Args:
            product_id: Product unique identifier

        Returns:
            Inventory DTO if found, None otherwise
        """
        query = GetInventoryByProductIdQuery(product_id=product_id)
        inventory = await self._query_handler.handle_get_by_product_id(query)

        if not inventory:
            return None

        return InventoryItemDTO.from_domain(inventory)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[InventoryStatus] = None,
    ) -> InventoryListDTO:
        """Get all inventory with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            status: Filter by status (optional)

        Returns:
            Paginated inventory list DTO
        """
        query = GetAllInventoryQuery(skip=skip, limit=limit, status=status)
        items = await self._query_handler.handle_get_all(query)
        total = await self._query_handler.handle_count(status=status)

        return InventoryListDTO.from_domain_list(
            inventory_items=items,
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_by_location(
        self,
        warehouse_location: str,
        skip: int = 0,
        limit: int = 100,
    ) -> InventoryListDTO:
        """Get inventory by warehouse location.

        Args:
            warehouse_location: Warehouse location code
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            Paginated inventory list DTO
        """
        query = GetInventoryByLocationQuery(
            warehouse_location=warehouse_location, skip=skip, limit=limit
        )
        items = await self._query_handler.handle_get_by_location(query)

        total = len(items) if len(items) < limit else skip + limit + 1

        return InventoryListDTO.from_domain_list(
            inventory_items=items,
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_low_stock_items(
        self, skip: int = 0, limit: int = 100
    ) -> InventoryListDTO:
        """Get items with low stock.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            Paginated inventory list DTO
        """
        query = GetLowStockItemsQuery(skip=skip, limit=limit)
        items = await self._query_handler.handle_get_low_stock(query)

        total = len(items) if len(items) < limit else skip + limit + 1

        return InventoryListDTO.from_domain_list(
            inventory_items=items,
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_out_of_stock_items(
        self, skip: int = 0, limit: int = 100
    ) -> InventoryListDTO:
        """Get items that are out of stock.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            Paginated inventory list DTO
        """
        query = GetOutOfStockItemsQuery(skip=skip, limit=limit)
        items = await self._query_handler.handle_get_out_of_stock(query)

        total = len(items) if len(items) < limit else skip + limit + 1

        return InventoryListDTO.from_domain_list(
            inventory_items=items,
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_items_needing_restock(
        self, skip: int = 0, limit: int = 100
    ) -> InventoryListDTO:
        """Get items that need restocking.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            Paginated inventory list DTO
        """
        query = GetItemsNeedingRestockQuery(skip=skip, limit=limit)
        items = await self._query_handler.handle_get_items_needing_restock(query)

        total = len(items) if len(items) < limit else skip + limit + 1

        return InventoryListDTO.from_domain_list(
            inventory_items=items,
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_snapshot(
        self, as_of_date: Optional[datetime] = None
    ) -> List[dict]:
        """Get inventory snapshot for reporting.

        Args:
            as_of_date: Date for snapshot (defaults to now)

        Returns:
            List of inventory snapshots
        """
        query = GetInventorySnapshotQuery(as_of_date=as_of_date)
        return await self._query_handler.handle_get_snapshot(query)

    async def get_total_value(
        self, warehouse_location: Optional[str] = None
    ) -> float:
        """Get total inventory value.

        Args:
            warehouse_location: Filter by location (optional)

        Returns:
            Total inventory value
        """
        return await self._query_handler.handle_get_total_value(
            warehouse_location=warehouse_location
        )

    # Command operations

    async def create(self, dto: CreateInventoryDTO) -> InventoryItemDTO:
        """Create inventory for a product.

        Args:
            dto: Create inventory DTO

        Returns:
            Created inventory DTO

        Raises:
            ValueError: If inventory already exists or data is invalid
        """
        command = CreateInventoryCommand(
            product_id=dto.product_id,
            quantity=dto.quantity,
            reorder_point=dto.reorder_point,
            reorder_quantity=dto.reorder_quantity,
            warehouse_location=dto.warehouse_location,
        )

        inventory = await self._command_handler.handle_create(command)
        return InventoryItemDTO.from_domain(inventory)

    async def update(
        self, inventory_id: UUID, dto: UpdateInventoryDTO
    ) -> InventoryItemDTO:
        """Update inventory settings.

        Args:
            inventory_id: Inventory unique identifier
            dto: Update inventory DTO

        Returns:
            Updated inventory DTO

        Raises:
            ValueError: If inventory not found or data is invalid
        """
        command = UpdateInventoryCommand(
            inventory_id=inventory_id,
            reorder_point=dto.reorder_point,
            reorder_quantity=dto.reorder_quantity,
            warehouse_location=dto.warehouse_location,
        )

        inventory = await self._command_handler.handle_update(command)
        return InventoryItemDTO.from_domain(inventory)

    async def reserve_stock(
        self, product_id: UUID, quantity: int
    ) -> InventoryItemDTO:
        """Reserve stock for an order.

        Args:
            product_id: Product unique identifier
            quantity: Quantity to reserve

        Returns:
            Updated inventory DTO

        Raises:
            ValueError: If insufficient stock
        """
        command = ReserveStockCommand(product_id=product_id, quantity=quantity)
        inventory = await self._command_handler.handle_reserve_stock(command)
        return InventoryItemDTO.from_domain(inventory)

    async def release_reservation(
        self, product_id: UUID, quantity: int
    ) -> InventoryItemDTO:
        """Release reserved stock.

        Args:
            product_id: Product unique identifier
            quantity: Quantity to release

        Returns:
            Updated inventory DTO

        Raises:
            ValueError: If inventory not found or invalid quantity
        """
        command = ReleaseReservationCommand(product_id=product_id, quantity=quantity)
        inventory = await self._command_handler.handle_release_reservation(command)
        return InventoryItemDTO.from_domain(inventory)

    async def fulfill_reservation(
        self, product_id: UUID, quantity: int
    ) -> InventoryItemDTO:
        """Fulfill reservation (ship order).

        Args:
            product_id: Product unique identifier
            quantity: Quantity to fulfill

        Returns:
            Updated inventory DTO

        Raises:
            ValueError: If inventory not found or invalid quantity
        """
        command = FulfillReservationCommand(product_id=product_id, quantity=quantity)
        inventory = await self._command_handler.handle_fulfill_reservation(command)
        return InventoryItemDTO.from_domain(inventory)

    async def add_stock(self, product_id: UUID, quantity: int) -> InventoryItemDTO:
        """Add stock (restock).

        Args:
            product_id: Product unique identifier
            quantity: Quantity to add

        Returns:
            Updated inventory DTO

        Raises:
            ValueError: If inventory not found or invalid quantity
        """
        command = AddStockCommand(product_id=product_id, quantity=quantity)
        inventory = await self._command_handler.handle_add_stock(command)
        return InventoryItemDTO.from_domain(inventory)

    async def remove_stock(self, product_id: UUID, quantity: int) -> InventoryItemDTO:
        """Remove stock (shrinkage, damage).

        Args:
            product_id: Product unique identifier
            quantity: Quantity to remove

        Returns:
            Updated inventory DTO

        Raises:
            ValueError: If inventory not found or insufficient stock
        """
        command = RemoveStockCommand(product_id=product_id, quantity=quantity)
        inventory = await self._command_handler.handle_remove_stock(command)
        return InventoryItemDTO.from_domain(inventory)

    async def transfer_stock(
        self,
        product_id: UUID,
        from_location: str,
        to_location: str,
        quantity: int,
    ) -> bool:
        """Transfer stock between locations.

        Args:
            product_id: Product unique identifier
            from_location: Source warehouse location
            to_location: Destination warehouse location
            quantity: Quantity to transfer

        Returns:
            True if successful

        Raises:
            ValueError: If locations are same or transfer fails
        """
        command = TransferStockCommand(
            product_id=product_id,
            from_location=from_location,
            to_location=to_location,
            quantity=quantity,
        )
        return await self._command_handler.handle_transfer_stock(command)

    async def bulk_update_reorder_points(
        self, updates: List[Tuple[UUID, int]]
    ) -> int:
        """Bulk update reorder points.

        Args:
            updates: List of (product_id, new_reorder_point) tuples

        Returns:
            Number of items updated
        """
        command = BulkUpdateReorderPointsCommand(updates=updates)
        return await self._command_handler.handle_bulk_update_reorder_points(command)
