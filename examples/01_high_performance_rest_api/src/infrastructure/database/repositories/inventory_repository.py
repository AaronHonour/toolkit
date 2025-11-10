"""SQL implementation of Inventory repository with performance optimizations.

Uses toolkit optimizations:
- Query caching for frequently accessed data
- Atomic operations for stock management (prevents race conditions)
- Batch operations
- Connection pooling
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.inventory import (
    InventoryItem,
    StockStatus,
)
from src.domain.repositories.inventory_repository import (
    InventoryRepository,
)
from src.infrastructure.database.models import (
    InventoryModel,
    ProductModel,
)
from toolkit.database import QueryCache, QueryCacheConfig


class SQLInventoryRepository(InventoryRepository):
    """SQL implementation of Inventory repository.

    Optimized with:
    - Query result caching
    - Atomic stock operations (no race conditions)
    - Efficient bulk operations
    """

    __slots__ = ("_session", "_cache")

    def __init__(self, session: AsyncSession):
        """Initialize repository.

        Args:
            session: Database session
        """
        self._session = session
        self._cache = QueryCache(QueryCacheConfig(max_size=1000, ttl=300))

    def _to_domain(self, model: InventoryModel) -> InventoryItem:
        """Convert database model to domain entity."""
        return InventoryItem(
            id=model.id,
            product_id=model.product_id,
            quantity=model.quantity,
            reserved=model.reserved,
            reorder_point=model.reorder_point,
            reorder_quantity=model.reorder_quantity,
            warehouse_location=model.warehouse_location,
            status=model.status,
            last_restock_date=model.last_restock_date,
            updated_at=model.updated_at,
        )

    def _to_model(self, inventory: InventoryItem) -> InventoryModel:
        """Convert domain entity to database model."""
        return InventoryModel(
            id=inventory.id,
            product_id=inventory.product_id,
            quantity=inventory.quantity,
            reserved=inventory.reserved,
            reorder_point=inventory.reorder_point,
            reorder_quantity=inventory.reorder_quantity,
            warehouse_location=inventory.warehouse_location,
            status=inventory.status,
            last_restock_date=inventory.last_restock_date,
            updated_at=inventory.updated_at,
        )

    async def get_by_id(self, inventory_id: UUID) -> Optional[InventoryItem]:
        """Get inventory by ID with caching."""
        cache_key = f"inventory:id:{inventory_id}"

        cached = self._cache.get(cache_key)
        if cached:
            return cached

        stmt = select(InventoryModel).where(InventoryModel.id == inventory_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        inventory = self._to_domain(model)
        self._cache.set(cache_key, inventory)
        return inventory

    async def get_by_product_id(self, product_id: UUID) -> Optional[InventoryItem]:
        """Get inventory by product ID with caching."""
        cache_key = f"inventory:product:{product_id}"

        cached = self._cache.get(cache_key)
        if cached:
            return cached

        stmt = select(InventoryModel).where(InventoryModel.product_id == product_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        inventory = self._to_domain(model)
        self._cache.set(cache_key, inventory)
        return inventory

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[StockStatus] = None,
    ) -> List[InventoryItem]:
        """Get all inventory with pagination and filtering."""
        stmt = select(InventoryModel)

        if status:
            stmt = stmt.where(InventoryModel.status == status)

        stmt = stmt.offset(skip).limit(limit).order_by(InventoryModel.updated_at.desc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(m) for m in models]

    async def get_by_warehouse_location(
        self,
        warehouse_location: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[InventoryItem]:
        """Get inventory by warehouse location."""
        stmt = select(InventoryModel).where(
            InventoryModel.warehouse_location == warehouse_location
        )

        stmt = stmt.offset(skip).limit(limit).order_by(InventoryModel.quantity.desc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(m) for m in models]

    async def get_low_stock_items(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[InventoryItem]:
        """Get items with low stock (below reorder point)."""
        stmt = select(InventoryModel).where(
            and_(
                InventoryModel.quantity - InventoryModel.reserved
                < InventoryModel.reorder_point,
                InventoryModel.quantity - InventoryModel.reserved > 0,
            )
        )

        stmt = stmt.offset(skip).limit(limit).order_by(
            (InventoryModel.quantity - InventoryModel.reserved).asc()
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(m) for m in models]

    async def get_out_of_stock_items(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[InventoryItem]:
        """Get items that are out of stock."""
        stmt = select(InventoryModel).where(
            InventoryModel.quantity - InventoryModel.reserved <= 0
        )

        stmt = stmt.offset(skip).limit(limit).order_by(InventoryModel.updated_at.desc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(m) for m in models]

    async def get_items_needing_restock(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[InventoryItem]:
        """Get items that need restocking."""
        stmt = select(InventoryModel).where(
            InventoryModel.quantity - InventoryModel.reserved
            <= InventoryModel.reorder_point
        )

        stmt = stmt.offset(skip).limit(limit).order_by(
            (InventoryModel.quantity - InventoryModel.reserved).asc()
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(m) for m in models]

    async def get_by_status(
        self,
        status: StockStatus,
        skip: int = 0,
        limit: int = 100,
    ) -> List[InventoryItem]:
        """Get inventory items by status."""
        stmt = select(InventoryModel).where(InventoryModel.status == status)

        stmt = stmt.offset(skip).limit(limit).order_by(InventoryModel.updated_at.desc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(m) for m in models]

    async def reserve_stock(
        self,
        product_id: UUID,
        quantity: int,
    ) -> Optional[InventoryItem]:
        """Reserve stock atomically (prevents race conditions)."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        # Atomic update with WHERE clause checking availability
        stmt = (
            update(InventoryModel)
            .where(
                and_(
                    InventoryModel.product_id == product_id,
                    InventoryModel.quantity - InventoryModel.reserved >= quantity,
                )
            )
            .values(reserved=InventoryModel.reserved + quantity)
            .returning(InventoryModel)
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        await self._session.flush()

        # Invalidate cache
        self._cache.delete(f"inventory:product:{product_id}")

        return self._to_domain(model)

    async def release_reservation(
        self,
        product_id: UUID,
        quantity: int,
    ) -> Optional[InventoryItem]:
        """Release reserved stock atomically."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        stmt = (
            update(InventoryModel)
            .where(
                and_(
                    InventoryModel.product_id == product_id,
                    InventoryModel.reserved >= quantity,
                )
            )
            .values(reserved=InventoryModel.reserved - quantity)
            .returning(InventoryModel)
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        await self._session.flush()

        # Invalidate cache
        self._cache.delete(f"inventory:product:{product_id}")

        return self._to_domain(model)

    async def fulfill_reservation(
        self,
        product_id: UUID,
        quantity: int,
    ) -> Optional[InventoryItem]:
        """Fulfill reservation atomically (decrease both reserved and total)."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        stmt = (
            update(InventoryModel)
            .where(
                and_(
                    InventoryModel.product_id == product_id,
                    InventoryModel.reserved >= quantity,
                    InventoryModel.quantity >= quantity,
                )
            )
            .values(
                quantity=InventoryModel.quantity - quantity,
                reserved=InventoryModel.reserved - quantity,
            )
            .returning(InventoryModel)
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        await self._session.flush()

        # Invalidate cache
        self._cache.delete(f"inventory:product:{product_id}")

        return self._to_domain(model)

    async def add_stock(
        self,
        product_id: UUID,
        quantity: int,
    ) -> Optional[InventoryItem]:
        """Add stock (restock operation)."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        stmt = (
            update(InventoryModel)
            .where(InventoryModel.product_id == product_id)
            .values(
                quantity=InventoryModel.quantity + quantity,
                last_restock_date=datetime.utcnow(),
            )
            .returning(InventoryModel)
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        await self._session.flush()

        # Invalidate cache
        self._cache.delete(f"inventory:product:{product_id}")

        return self._to_domain(model)

    async def remove_stock(
        self,
        product_id: UUID,
        quantity: int,
    ) -> Optional[InventoryItem]:
        """Remove stock atomically."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        stmt = (
            update(InventoryModel)
            .where(
                and_(
                    InventoryModel.product_id == product_id,
                    InventoryModel.quantity - InventoryModel.reserved >= quantity,
                )
            )
            .values(quantity=InventoryModel.quantity - quantity)
            .returning(InventoryModel)
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        await self._session.flush()

        # Invalidate cache
        self._cache.delete(f"inventory:product:{product_id}")

        return self._to_domain(model)

    async def transfer_stock(
        self,
        product_id: UUID,
        from_location: str,
        to_location: str,
        quantity: int,
    ) -> bool:
        """Transfer stock between locations (simplified - single product)."""
        if from_location == to_location:
            raise ValueError("Cannot transfer to same location")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        # For simplicity, this updates the location
        # In a real system, you might have separate inventory records per location
        stmt = (
            update(InventoryModel)
            .where(
                and_(
                    InventoryModel.product_id == product_id,
                    InventoryModel.warehouse_location == from_location,
                    InventoryModel.quantity - InventoryModel.reserved >= quantity,
                )
            )
            .values(warehouse_location=to_location)
        )

        result = await self._session.execute(stmt)

        # Invalidate cache
        self._cache.delete(f"inventory:product:{product_id}")

        return result.rowcount > 0

    async def create(self, inventory_item: InventoryItem) -> InventoryItem:
        """Create new inventory item."""
        model = self._to_model(inventory_item)
        self._session.add(model)
        await self._session.flush()

        # Cache will expire via TTL (300s)
        # New inventory won't be cached until first read

        return self._to_domain(model)

    async def update(self, inventory_item: InventoryItem) -> InventoryItem:
        """Update existing inventory item."""
        result = await self._session.execute(
            select(InventoryModel).where(InventoryModel.id == inventory_item.id)
        )
        model = result.scalar_one_or_none()

        if not model:
            raise ValueError(f"Inventory {inventory_item.id} not found")

        # Update fields
        model.reorder_point = inventory_item.reorder_point
        model.reorder_quantity = inventory_item.reorder_quantity
        model.warehouse_location = inventory_item.warehouse_location
        model.status = inventory_item.status

        await self._session.flush()

        # Invalidate cache
        self._cache.delete(f"inventory:id:{inventory_item.id}")
        self._cache.delete(f"inventory:product:{inventory_item.product_id}")

        return self._to_domain(model)

    async def delete(self, inventory_id: UUID) -> bool:
        """Delete inventory item by ID."""
        stmt = delete(InventoryModel).where(InventoryModel.id == inventory_id)
        result = await self._session.execute(stmt)

        # Invalidate cache
        self._cache.delete(f"inventory:id:{inventory_id}")

        return result.rowcount > 0

    async def count(self, status: Optional[StockStatus] = None) -> int:
        """Count inventory items."""
        stmt = select(func.count()).select_from(InventoryModel)

        if status:
            stmt = stmt.where(InventoryModel.status == status)

        result = await self._session.execute(stmt)
        return result.scalar()

    async def exists(self, inventory_id: UUID) -> bool:
        """Check if inventory item exists."""
        stmt = select(func.count()).select_from(InventoryModel).where(
            InventoryModel.id == inventory_id
        )
        result = await self._session.execute(stmt)
        return result.scalar() > 0

    async def get_total_value(
        self,
        warehouse_location: Optional[str] = None,
    ) -> float:
        """Calculate total inventory value (requires join with products)."""
        stmt = (
            select(func.sum(InventoryModel.quantity * ProductModel.cost))
            .join(ProductModel, InventoryModel.product_id == ProductModel.id)
        )

        if warehouse_location:
            stmt = stmt.where(InventoryModel.warehouse_location == warehouse_location)

        result = await self._session.execute(stmt)
        total = result.scalar()

        return float(total) if total else 0.0

    async def bulk_update_reorder_points(
        self,
        updates: List[tuple[UUID, int]],
    ) -> int:
        """Bulk update reorder points."""
        count = 0

        for product_id, new_reorder_point in updates:
            stmt = (
                update(InventoryModel)
                .where(InventoryModel.product_id == product_id)
                .values(reorder_point=new_reorder_point)
            )

            result = await self._session.execute(stmt)
            count += result.rowcount

        await self._session.flush()

        # Invalidate cache
        for product_id, _ in updates:
            self._cache.delete(f"inventory:product:{product_id}")

        return count

    async def get_inventory_snapshot(
        self,
        as_of_date: Optional[datetime] = None,
    ) -> List[dict]:
        """Get inventory snapshot for reporting."""
        # Join with products to get product details
        stmt = (
            select(
                InventoryModel.id,
                InventoryModel.product_id,
                InventoryModel.quantity,
                InventoryModel.reserved,
                InventoryModel.warehouse_location,
                InventoryModel.status,
                ProductModel.sku,
                ProductModel.name,
                ProductModel.cost,
            )
            .join(ProductModel, InventoryModel.product_id == ProductModel.id)
            .order_by(InventoryModel.warehouse_location, ProductModel.name)
        )

        result = await self._session.execute(stmt)
        rows = result.all()

        return [
            {
                "inventory_id": str(row.id),
                "product_id": str(row.product_id),
                "sku": row.sku,
                "name": row.name,
                "quantity": row.quantity,
                "reserved": row.reserved,
                "available": row.quantity - row.reserved,
                "warehouse_location": row.warehouse_location,
                "status": row.status.value,
                "unit_cost": str(row.cost),
                "total_value": str(row.quantity * row.cost),
            }
            for row in rows
        ]
