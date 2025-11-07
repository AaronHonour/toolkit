"""Product domain model."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List


class ProductStatus(str, Enum):
    """Product status enumeration."""

    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"


class ProductCategory(str, Enum):
    """Product category enumeration."""

    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    BOOKS = "books"
    HOME = "home"
    SPORTS = "sports"
    TOYS = "toys"
    FOOD = "food"
    OTHER = "other"


@dataclass
class Product:
    """Product entity.

    Core domain model representing a product in the catalog.
    Optimized with __slots__ for memory efficiency.
    """

    __slots__ = (
        "id",
        "sku",
        "name",
        "description",
        "category",
        "price",
        "cost",
        "status",
        "tags",
        "metadata",
        "created_at",
        "updated_at",
    )

    id: Optional[int]
    sku: str
    name: str
    description: str
    category: ProductCategory
    price: Decimal
    cost: Decimal
    status: ProductStatus
    tags: List[str]
    metadata: dict
    created_at: datetime
    updated_at: datetime

    def __init__(
        self,
        sku: str,
        name: str,
        description: str,
        category: ProductCategory,
        price: Decimal,
        cost: Decimal,
        status: ProductStatus = ProductStatus.DRAFT,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """Initialize product.

        Args:
            sku: Stock keeping unit (unique identifier)
            name: Product name
            description: Product description
            category: Product category
            price: Selling price
            cost: Cost price
            status: Product status
            tags: Product tags for search
            metadata: Additional metadata
            id: Optional ID (set by repository)
            created_at: Creation timestamp
            updated_at: Update timestamp
        """
        self.id = id
        self.sku = sku
        self.name = name
        self.description = description
        self.category = category
        self.price = price
        self.cost = cost
        self.status = status
        self.tags = tags or []
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @property
    def margin(self) -> Decimal:
        """Calculate profit margin.

        Returns:
            Profit margin as decimal
        """
        if self.price <= 0:
            return Decimal("0")
        return (self.price - self.cost) / self.price

    @property
    def margin_percent(self) -> float:
        """Calculate profit margin percentage.

        Returns:
            Profit margin as percentage
        """
        return float(self.margin * 100)

    def is_active(self) -> bool:
        """Check if product is active.

        Returns:
            True if product is active
        """
        return self.status == ProductStatus.ACTIVE

    def is_available(self) -> bool:
        """Check if product is available for sale.

        Returns:
            True if product is available
        """
        return self.status in (ProductStatus.ACTIVE, ProductStatus.DRAFT)

    def activate(self):
        """Activate product for sale."""
        self.status = ProductStatus.ACTIVE
        self.updated_at = datetime.utcnow()

    def deactivate(self):
        """Deactivate product."""
        self.status = ProductStatus.INACTIVE
        self.updated_at = datetime.utcnow()

    def discontinue(self):
        """Discontinue product."""
        self.status = ProductStatus.DISCONTINUED
        self.updated_at = datetime.utcnow()

    def update_price(self, new_price: Decimal):
        """Update product price.

        Args:
            new_price: New selling price
        """
        if new_price < 0:
            raise ValueError("Price cannot be negative")
        self.price = new_price
        self.updated_at = datetime.utcnow()

    def add_tag(self, tag: str):
        """Add tag to product.

        Args:
            tag: Tag to add
        """
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str):
        """Remove tag from product.

        Args:
            tag: Tag to remove
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        """String representation."""
        return f"Product(id={self.id}, sku={self.sku}, name={self.name}, status={self.status})"
