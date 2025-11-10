"""Product repository interface.

Defines the contract for product data access operations.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from src.domain.models.product import (
    Product,
    ProductStatus,
)


class ProductRepository(ABC):
    """Abstract repository for Product entities.

    Defines the port for product data access in hexagonal architecture.
    Implementations (adapters) will be in the infrastructure layer.
    """

    @abstractmethod
    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        """Get product by ID.

        Args:
            product_id: Product unique identifier

        Returns:
            Product if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """Get product by SKU.

        Args:
            sku: Product SKU (stock keeping unit)

        Returns:
            Product if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProductStatus] = None
    ) -> List[Product]:
        """Get all products with pagination and filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by product status (optional)

        Returns:
            List of products
        """
        pass

    @abstractmethod
    async def get_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProductStatus] = None
    ) -> List[Product]:
        """Get products by category.

        Args:
            category: Product category
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by product status (optional)

        Returns:
            List of products in category
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProductStatus] = None
    ) -> List[Product]:
        """Search products by name or description.

        Args:
            query: Search query (searches name and description)
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by product status (optional)

        Returns:
            List of matching products
        """
        pass

    @abstractmethod
    async def get_by_tags(
        self,
        tags: List[str],
        match_all: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Get products by tags.

        Args:
            tags: List of tags to match
            match_all: If True, match all tags; if False, match any tag
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of products with matching tags
        """
        pass

    @abstractmethod
    async def get_by_price_range(
        self,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProductStatus] = None
    ) -> List[Product]:
        """Get products within price range.

        Args:
            min_price: Minimum price (inclusive)
            max_price: Maximum price (inclusive)
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by product status (optional)

        Returns:
            List of products in price range
        """
        pass

    @abstractmethod
    async def get_low_margin_products(
        self,
        margin_threshold: Decimal,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Get products with margin below threshold.

        Args:
            margin_threshold: Margin threshold (e.g., 0.20 for 20%)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of low-margin products
        """
        pass

    @abstractmethod
    async def create(self, product: Product) -> Product:
        """Create new product.

        Args:
            product: Product to create

        Returns:
            Created product with generated ID and timestamps
        """
        pass

    @abstractmethod
    async def update(self, product: Product) -> Product:
        """Update existing product.

        Args:
            product: Product with updated data

        Returns:
            Updated product

        Raises:
            ValueError: If product not found
        """
        pass

    @abstractmethod
    async def delete(self, product_id: UUID) -> bool:
        """Delete product by ID.

        Args:
            product_id: Product unique identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def count(self, status: Optional[ProductStatus] = None) -> int:
        """Count products.

        Args:
            status: Filter by product status (optional)

        Returns:
            Number of products
        """
        pass

    @abstractmethod
    async def exists(self, product_id: UUID) -> bool:
        """Check if product exists.

        Args:
            product_id: Product unique identifier

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def bulk_create(self, products: List[Product]) -> List[Product]:
        """Create multiple products in batch.

        Optimized for bulk operations with batching and transactions.

        Args:
            products: List of products to create

        Returns:
            List of created products
        """
        pass

    @abstractmethod
    async def bulk_update_status(
        self,
        product_ids: List[UUID],
        status: ProductStatus
    ) -> int:
        """Bulk update product status.

        Args:
            product_ids: List of product IDs
            status: New status

        Returns:
            Number of products updated
        """
        pass
