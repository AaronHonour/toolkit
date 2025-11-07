"""Product query handlers for read operations.

Implements CQRS pattern - queries are optimized for reading.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from examples.01_high_performance_rest_api.src.domain.models.product import (
    Product,
    ProductStatus,
)
from examples.01_high_performance_rest_api.src.domain.repositories.product_repository import (
    ProductRepository,
)


# Query models (intent to read data)


@dataclass
class GetProductByIdQuery:
    """Query to get product by ID."""

    product_id: UUID


@dataclass
class GetProductBySkuQuery:
    """Query to get product by SKU."""

    sku: str


@dataclass
class GetAllProductsQuery:
    """Query to get all products with pagination."""

    skip: int = 0
    limit: int = 100
    status: Optional[ProductStatus] = None


@dataclass
class GetProductsByCategoryQuery:
    """Query to get products by category."""

    category: str
    skip: int = 0
    limit: int = 100
    status: Optional[ProductStatus] = None


@dataclass
class SearchProductsQuery:
    """Query to search products."""

    query: str
    skip: int = 0
    limit: int = 100
    status: Optional[ProductStatus] = None


@dataclass
class GetProductsByTagsQuery:
    """Query to get products by tags."""

    tags: List[str]
    match_all: bool = False
    skip: int = 0
    limit: int = 100


@dataclass
class GetProductsByPriceRangeQuery:
    """Query to get products by price range."""

    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    skip: int = 0
    limit: int = 100
    status: Optional[ProductStatus] = None


@dataclass
class GetLowMarginProductsQuery:
    """Query to get low margin products."""

    margin_threshold: Decimal
    skip: int = 0
    limit: int = 100


# Query handler


class ProductQueryHandler:
    """Handles product read operations.

    Optimized for read performance with caching and efficient queries.
    """

    __slots__ = ("_repository",)

    def __init__(self, repository: ProductRepository):
        """Initialize query handler.

        Args:
            repository: Product repository implementation
        """
        self._repository = repository

    async def handle_get_by_id(self, query: GetProductByIdQuery) -> Optional[Product]:
        """Handle get product by ID query.

        Args:
            query: Get by ID query

        Returns:
            Product if found, None otherwise
        """
        return await self._repository.get_by_id(query.product_id)

    async def handle_get_by_sku(self, query: GetProductBySkuQuery) -> Optional[Product]:
        """Handle get product by SKU query.

        Args:
            query: Get by SKU query

        Returns:
            Product if found, None otherwise
        """
        return await self._repository.get_by_sku(query.sku)

    async def handle_get_all(self, query: GetAllProductsQuery) -> List[Product]:
        """Handle get all products query.

        Args:
            query: Get all query

        Returns:
            List of products
        """
        return await self._repository.get_all(
            skip=query.skip,
            limit=query.limit,
            status=query.status,
        )

    async def handle_get_by_category(
        self, query: GetProductsByCategoryQuery
    ) -> List[Product]:
        """Handle get products by category query.

        Args:
            query: Get by category query

        Returns:
            List of products in category
        """
        return await self._repository.get_by_category(
            category=query.category,
            skip=query.skip,
            limit=query.limit,
            status=query.status,
        )

    async def handle_search(self, query: SearchProductsQuery) -> List[Product]:
        """Handle search products query.

        Args:
            query: Search query

        Returns:
            List of matching products
        """
        return await self._repository.search(
            query=query.query,
            skip=query.skip,
            limit=query.limit,
            status=query.status,
        )

    async def handle_get_by_tags(
        self, query: GetProductsByTagsQuery
    ) -> List[Product]:
        """Handle get products by tags query.

        Args:
            query: Get by tags query

        Returns:
            List of products with matching tags
        """
        return await self._repository.get_by_tags(
            tags=query.tags,
            match_all=query.match_all,
            skip=query.skip,
            limit=query.limit,
        )

    async def handle_get_by_price_range(
        self, query: GetProductsByPriceRangeQuery
    ) -> List[Product]:
        """Handle get products by price range query.

        Args:
            query: Get by price range query

        Returns:
            List of products in price range
        """
        return await self._repository.get_by_price_range(
            min_price=query.min_price,
            max_price=query.max_price,
            skip=query.skip,
            limit=query.limit,
            status=query.status,
        )

    async def handle_get_low_margin(
        self, query: GetLowMarginProductsQuery
    ) -> List[Product]:
        """Handle get low margin products query.

        Args:
            query: Get low margin query

        Returns:
            List of low margin products
        """
        return await self._repository.get_low_margin_products(
            margin_threshold=query.margin_threshold,
            skip=query.skip,
            limit=query.limit,
        )

    async def handle_count(self, status: Optional[ProductStatus] = None) -> int:
        """Handle count products query.

        Args:
            status: Filter by status (optional)

        Returns:
            Number of products
        """
        return await self._repository.count(status=status)

    async def handle_exists(self, product_id: UUID) -> bool:
        """Handle product exists query.

        Args:
            product_id: Product ID

        Returns:
            True if exists, False otherwise
        """
        return await self._repository.exists(product_id)
