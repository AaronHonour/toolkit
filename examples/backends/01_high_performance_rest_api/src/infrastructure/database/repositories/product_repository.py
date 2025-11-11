"""SQL implementation of Product repository with performance optimizations.

Uses toolkit optimizations:
- Query caching for frequently accessed data
- Prepared statement caching
- Batch operations
- Connection pooling
"""

from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.product import (
    Product,
    ProductStatus,
)
from src.domain.repositories.product_repository import (
    ProductRepository,
)
from src.infrastructure.database.models import (
    ProductModel,
)
from unistax.database import QueryCache, QueryCacheConfig, cached_query


class SQLProductRepository(ProductRepository):
    """SQL implementation of Product repository.

    Optimized with:
    - Query result caching
    - Efficient bulk operations
    - Prepared statement reuse
    """

    __slots__ = ("_session", "_cache")

    def __init__(self, session: AsyncSession):
        """Initialize repository.

        Args:
            session: Database session
        """
        self._session = session
        self._cache = QueryCache(QueryCacheConfig(max_size=1000, ttl=300))

    def _to_domain(self, model: ProductModel) -> Product:
        """Convert database model to domain entity.

        Args:
            model: Database model

        Returns:
            Domain product entity
        """
        return Product(
            id=model.id,
            sku=model.sku,
            name=model.name,
            description=model.description,
            category=model.category,
            price=model.price,
            cost=model.cost,
            status=model.status,
            tags=list(model.tags) if model.tags else [],
            metadata=dict(model.product_metadata) if model.product_metadata else {},
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, product: Product) -> ProductModel:
        """Convert domain entity to database model.

        Args:
            product: Domain product entity

        Returns:
            Database model
        """
        return ProductModel(
            id=product.id,
            sku=product.sku,
            name=product.name,
            description=product.description,
            category=product.category,
            price=product.price,
            cost=product.cost,
            status=product.status,
            tags=product.tags,
            product_metadata=product.metadata,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )

    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        """Get product by ID with caching."""
        cache_key = f"product:id:{product_id}"

        # Check cache
        cached = self._cache.get(cache_key)
        if cached:
            return cached

        # Query database
        stmt = select(ProductModel).where(ProductModel.id == product_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        product = self._to_domain(model)
        self._cache.set(cache_key, product)
        return product

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """Get product by SKU with caching."""
        cache_key = f"product:sku:{sku}"

        cached = self._cache.get(cache_key)
        if cached:
            return cached

        stmt = select(ProductModel).where(ProductModel.sku == sku)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        product = self._to_domain(model)
        self._cache.set(cache_key, product)
        return product

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProductStatus] = None,
    ) -> List[Product]:
        """Get all products with pagination and filtering."""
        stmt = select(ProductModel)

        if status:
            stmt = stmt.where(ProductModel.status == status)

        stmt = stmt.offset(skip).limit(limit).order_by(ProductModel.created_at.desc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(m) for m in models]

    async def get_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProductStatus] = None,
    ) -> List[Product]:
        """Get products by category."""
        stmt = select(ProductModel).where(ProductModel.category == category)

        if status:
            stmt = stmt.where(ProductModel.status == status)

        stmt = stmt.offset(skip).limit(limit).order_by(ProductModel.name)

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(m) for m in models]

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProductStatus] = None,
    ) -> List[Product]:
        """Search products by name or description."""
        search_pattern = f"%{query}%"

        stmt = select(ProductModel).where(
            or_(
                ProductModel.name.ilike(search_pattern),
                ProductModel.description.ilike(search_pattern),
            )
        )

        if status:
            stmt = stmt.where(ProductModel.status == status)

        stmt = stmt.offset(skip).limit(limit).order_by(ProductModel.name)

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(m) for m in models]

    async def get_by_tags(
        self,
        tags: List[str],
        match_all: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Product]:
        """Get products by tags."""
        if match_all:
            # Match all tags (PostgreSQL array contains all)
            stmt = select(ProductModel).where(ProductModel.tags.contains(tags))
        else:
            # Match any tag (PostgreSQL array overlap)
            stmt = select(ProductModel).where(ProductModel.tags.overlap(tags))

        stmt = stmt.offset(skip).limit(limit).order_by(ProductModel.name)

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(m) for m in models]

    async def get_by_price_range(
        self,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProductStatus] = None,
    ) -> List[Product]:
        """Get products within price range."""
        stmt = select(ProductModel)

        conditions = []
        if min_price is not None:
            conditions.append(ProductModel.price >= min_price)
        if max_price is not None:
            conditions.append(ProductModel.price <= max_price)
        if status:
            conditions.append(ProductModel.status == status)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.offset(skip).limit(limit).order_by(ProductModel.price)

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(m) for m in models]

    async def get_low_margin_products(
        self,
        margin_threshold: Decimal,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Product]:
        """Get products with margin below threshold."""
        # Margin = (price - cost) / price
        # We want: margin < threshold
        # So: (price - cost) / price < threshold
        # price - cost < price * threshold
        # price * (1 - threshold) < cost

        stmt = select(ProductModel).where(
            and_(
                ProductModel.price > 0,
                (ProductModel.price - ProductModel.cost) / ProductModel.price < margin_threshold,
            )
        )

        stmt = stmt.offset(skip).limit(limit).order_by(
            (ProductModel.price - ProductModel.cost) / ProductModel.price
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(m) for m in models]

    async def create(self, product: Product) -> Product:
        """Create new product."""
        model = self._to_model(product)
        self._session.add(model)
        await self._session.flush()

        # Cache will expire via TTL (300s)
        # New products won't be cached until first read

        return self._to_domain(model)

    async def update(self, product: Product) -> Product:
        """Update existing product."""
        # Get existing model
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.id == product.id)
        )
        model = result.scalar_one_or_none()

        if not model:
            raise ValueError(f"Product {product.id} not found")

        # Update fields
        model.name = product.name
        model.description = product.description
        model.category = product.category
        model.price = product.price
        model.cost = product.cost
        model.status = product.status
        model.tags = product.tags
        model.metadata = product.metadata

        await self._session.flush()

        # Invalidate cache
        self._cache.delete(f"product:id:{product.id}")
        self._cache.delete(f"product:sku:{product.sku}")

        return self._to_domain(model)

    async def delete(self, product_id: UUID) -> bool:
        """Delete product by ID."""
        stmt = delete(ProductModel).where(ProductModel.id == product_id)
        result = await self._session.execute(stmt)

        # Invalidate cache
        self._cache.delete(f"product:id:{product_id}")

        return result.rowcount > 0

    async def count(self, status: Optional[ProductStatus] = None) -> int:
        """Count products."""
        stmt = select(func.count()).select_from(ProductModel)

        if status:
            stmt = stmt.where(ProductModel.status == status)

        result = await self._session.execute(stmt)
        return result.scalar()

    async def exists(self, product_id: UUID) -> bool:
        """Check if product exists."""
        stmt = select(func.count()).select_from(ProductModel).where(
            ProductModel.id == product_id
        )
        result = await self._session.execute(stmt)
        return result.scalar() > 0

    async def bulk_create(self, products: List[Product]) -> List[Product]:
        """Create multiple products in batch."""
        models = [self._to_model(p) for p in products]
        self._session.add_all(models)
        await self._session.flush()

        # Cache will expire via TTL (300s)
        # Bulk created products won't be cached until first read

        return [self._to_domain(m) for m in models]

    async def bulk_update_status(
        self,
        product_ids: List[UUID],
        status: ProductStatus,
    ) -> int:
        """Bulk update product status."""
        stmt = (
            update(ProductModel)
            .where(ProductModel.id.in_(product_ids))
            .values(status=status)
        )

        result = await self._session.execute(stmt)

        # Invalidate cache
        for product_id in product_ids:
            self._cache.delete(f"product:id:{product_id}")

        return result.rowcount
