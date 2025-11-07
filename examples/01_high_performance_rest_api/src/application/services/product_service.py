"""Product application service.

Orchestrates product operations between commands, queries, and DTOs.
"""

from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from examples.01_high_performance_rest_api.src.application.commands.product_commands import (
    CreateProductCommand,
    UpdateProductCommand,
    DeleteProductCommand,
    BulkCreateProductsCommand,
    BulkUpdateProductStatusCommand,
    ProductCommandHandler,
)
from examples.01_high_performance_rest_api.src.application.queries.product_queries import (
    GetProductByIdQuery,
    GetProductBySkuQuery,
    GetAllProductsQuery,
    GetProductsByCategoryQuery,
    SearchProductsQuery,
    GetProductsByTagsQuery,
    GetProductsByPriceRangeQuery,
    GetLowMarginProductsQuery,
    ProductQueryHandler,
)
from examples.01_high_performance_rest_api.src.application.dtos.product_dtos import (
    ProductDTO,
    CreateProductDTO,
    UpdateProductDTO,
    ProductListDTO,
)
from examples.01_high_performance_rest_api.src.domain.models.product import (
    ProductStatus,
)
from examples.01_high_performance_rest_api.src.domain.repositories.product_repository import (
    ProductRepository,
)


class ProductService:
    """Application service for product operations.

    Provides high-level API for product management, coordinating
    between commands, queries, and DTOs.
    """

    __slots__ = ("_command_handler", "_query_handler")

    def __init__(self, repository: ProductRepository):
        """Initialize product service.

        Args:
            repository: Product repository implementation
        """
        self._command_handler = ProductCommandHandler(repository)
        self._query_handler = ProductQueryHandler(repository)

    # Query operations

    async def get_by_id(self, product_id: UUID) -> Optional[ProductDTO]:
        """Get product by ID.

        Args:
            product_id: Product unique identifier

        Returns:
            Product DTO if found, None otherwise
        """
        query = GetProductByIdQuery(product_id=product_id)
        product = await self._query_handler.handle_get_by_id(query)

        if not product:
            return None

        return ProductDTO.from_domain(product)

    async def get_by_sku(self, sku: str) -> Optional[ProductDTO]:
        """Get product by SKU.

        Args:
            sku: Product SKU

        Returns:
            Product DTO if found, None otherwise
        """
        query = GetProductBySkuQuery(sku=sku)
        product = await self._query_handler.handle_get_by_sku(query)

        if not product:
            return None

        return ProductDTO.from_domain(product)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProductStatus] = None,
    ) -> ProductListDTO:
        """Get all products with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            status: Filter by status (optional)

        Returns:
            Paginated product list DTO
        """
        query = GetAllProductsQuery(skip=skip, limit=limit, status=status)
        products = await self._query_handler.handle_get_all(query)
        total = await self._query_handler.handle_count(status=status)

        return ProductListDTO.from_domain_list(
            products=products,
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProductStatus] = None,
    ) -> ProductListDTO:
        """Get products by category.

        Args:
            category: Product category
            skip: Number of records to skip
            limit: Maximum number of records
            status: Filter by status (optional)

        Returns:
            Paginated product list DTO
        """
        query = GetProductsByCategoryQuery(
            category=category, skip=skip, limit=limit, status=status
        )
        products = await self._query_handler.handle_get_by_category(query)

        # For category filtering, we need to count filtered results
        # This could be optimized with a dedicated count query
        total = len(products) if len(products) < limit else skip + limit + 1

        return ProductListDTO.from_domain_list(
            products=products,
            total=total,
            skip=skip,
            limit=limit,
        )

    async def search(
        self,
        query_text: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProductStatus] = None,
    ) -> ProductListDTO:
        """Search products by name or description.

        Args:
            query_text: Search query
            skip: Number of records to skip
            limit: Maximum number of records
            status: Filter by status (optional)

        Returns:
            Paginated product list DTO
        """
        query = SearchProductsQuery(
            query=query_text, skip=skip, limit=limit, status=status
        )
        products = await self._query_handler.handle_search(query)

        total = len(products) if len(products) < limit else skip + limit + 1

        return ProductListDTO.from_domain_list(
            products=products,
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_by_tags(
        self,
        tags: List[str],
        match_all: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> ProductListDTO:
        """Get products by tags.

        Args:
            tags: List of tags to match
            match_all: If True, match all tags; if False, match any
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            Paginated product list DTO
        """
        query = GetProductsByTagsQuery(
            tags=tags, match_all=match_all, skip=skip, limit=limit
        )
        products = await self._query_handler.handle_get_by_tags(query)

        total = len(products) if len(products) < limit else skip + limit + 1

        return ProductListDTO.from_domain_list(
            products=products,
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_by_price_range(
        self,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProductStatus] = None,
    ) -> ProductListDTO:
        """Get products within price range.

        Args:
            min_price: Minimum price (inclusive)
            max_price: Maximum price (inclusive)
            skip: Number of records to skip
            limit: Maximum number of records
            status: Filter by status (optional)

        Returns:
            Paginated product list DTO
        """
        query = GetProductsByPriceRangeQuery(
            min_price=min_price,
            max_price=max_price,
            skip=skip,
            limit=limit,
            status=status,
        )
        products = await self._query_handler.handle_get_by_price_range(query)

        total = len(products) if len(products) < limit else skip + limit + 1

        return ProductListDTO.from_domain_list(
            products=products,
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_low_margin_products(
        self,
        margin_threshold: Decimal,
        skip: int = 0,
        limit: int = 100,
    ) -> ProductListDTO:
        """Get products with low profit margins.

        Args:
            margin_threshold: Margin threshold (e.g., 0.20 for 20%)
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            Paginated product list DTO
        """
        query = GetLowMarginProductsQuery(
            margin_threshold=margin_threshold, skip=skip, limit=limit
        )
        products = await self._query_handler.handle_get_low_margin(query)

        total = len(products) if len(products) < limit else skip + limit + 1

        return ProductListDTO.from_domain_list(
            products=products,
            total=total,
            skip=skip,
            limit=limit,
        )

    # Command operations

    async def create(self, dto: CreateProductDTO) -> ProductDTO:
        """Create new product.

        Args:
            dto: Create product DTO

        Returns:
            Created product DTO

        Raises:
            ValueError: If SKU already exists or data is invalid
        """
        command = CreateProductCommand(
            sku=dto.sku,
            name=dto.name,
            description=dto.description,
            category=dto.category,
            price=dto.price,
            cost=dto.cost,
            tags=dto.tags,
            metadata=dto.metadata,
        )

        product = await self._command_handler.handle_create(command)
        return ProductDTO.from_domain(product)

    async def update(self, product_id: UUID, dto: UpdateProductDTO) -> ProductDTO:
        """Update existing product.

        Args:
            product_id: Product unique identifier
            dto: Update product DTO

        Returns:
            Updated product DTO

        Raises:
            ValueError: If product not found or data is invalid
        """
        command = UpdateProductCommand(
            product_id=product_id,
            name=dto.name,
            description=dto.description,
            category=dto.category,
            price=dto.price,
            cost=dto.cost,
            status=dto.status,
            tags=dto.tags,
            metadata=dto.metadata,
        )

        product = await self._command_handler.handle_update(command)
        return ProductDTO.from_domain(product)

    async def delete(self, product_id: UUID) -> bool:
        """Delete product.

        Args:
            product_id: Product unique identifier

        Returns:
            True if deleted, False if not found
        """
        command = DeleteProductCommand(product_id=product_id)
        return await self._command_handler.handle_delete(command)

    async def bulk_create(self, dtos: List[CreateProductDTO]) -> List[ProductDTO]:
        """Create multiple products in batch.

        Args:
            dtos: List of create product DTOs

        Returns:
            List of created product DTOs
        """
        commands = [
            CreateProductCommand(
                sku=dto.sku,
                name=dto.name,
                description=dto.description,
                category=dto.category,
                price=dto.price,
                cost=dto.cost,
                tags=dto.tags,
                metadata=dto.metadata,
            )
            for dto in dtos
        ]

        bulk_command = BulkCreateProductsCommand(products=commands)
        products = await self._command_handler.handle_bulk_create(bulk_command)

        return [ProductDTO.from_domain(p) for p in products]

    async def bulk_update_status(
        self, product_ids: List[UUID], status: ProductStatus
    ) -> int:
        """Bulk update product status.

        Args:
            product_ids: List of product IDs
            status: New status

        Returns:
            Number of products updated
        """
        command = BulkUpdateProductStatusCommand(
            product_ids=product_ids, status=status
        )
        return await self._command_handler.handle_bulk_update_status(command)
