"""Product Data Transfer Objects for API layer.

DTOs are optimized for JSON serialization and API responses.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from src.domain.models.product import (
    Product,
    ProductStatus,
)


@dataclass
class ProductDTO:
    """Product DTO for API responses.

    Optimized for JSON serialization with all computed fields.
    """

    id: str  # UUID as string for JSON
    sku: str
    name: str
    description: str
    category: str
    price: str  # Decimal as string to avoid precision loss
    cost: str  # Decimal as string
    margin: str  # Decimal as string
    status: str  # ProductStatus as string
    tags: List[str]
    metadata: dict
    created_at: str  # datetime as ISO string
    updated_at: str  # datetime as ISO string

    @classmethod
    def from_domain(cls, product: Product) -> "ProductDTO":
        """Convert domain model to DTO.

        Args:
            product: Domain product entity

        Returns:
            Product DTO
        """
        return cls(
            id=str(product.id),
            sku=product.sku,
            name=product.name,
            description=product.description,
            category=product.category,
            price=str(product.price),
            cost=str(product.cost),
            margin=str(product.margin),
            status=product.status.value,
            tags=product.tags.copy(),
            metadata=product.metadata.copy(),
            created_at=product.created_at.isoformat(),
            updated_at=product.updated_at.isoformat(),
        )


@dataclass
class CreateProductDTO:
    """DTO for creating a new product."""

    sku: str
    name: str
    description: str
    category: str
    price: Decimal
    cost: Decimal
    tags: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class UpdateProductDTO:
    """DTO for updating an existing product."""

    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    status: Optional[ProductStatus] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


@dataclass
class ProductListDTO:
    """DTO for paginated product list responses."""

    items: List[ProductDTO]
    total: int
    skip: int
    limit: int
    has_more: bool

    @classmethod
    def from_domain_list(
        cls,
        products: List[Product],
        total: int,
        skip: int,
        limit: int,
    ) -> "ProductListDTO":
        """Convert domain list to DTO.

        Args:
            products: List of domain products
            total: Total count of products
            skip: Number of items skipped
            limit: Maximum items per page

        Returns:
            Product list DTO
        """
        return cls(
            items=[ProductDTO.from_domain(p) for p in products],
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + len(products)) < total,
        )
