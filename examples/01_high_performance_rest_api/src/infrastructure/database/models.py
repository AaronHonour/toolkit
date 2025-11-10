"""SQLAlchemy database models.

ORM models that map to database tables with performance optimizations.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Column,
    String,
    Integer,
    Numeric,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Text,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

from src.domain.models.product import (
    ProductStatus,
)
from src.domain.models.inventory import (
    StockStatus,
)

Base = declarative_base()


class ProductModel(Base):
    """Product database model with performance optimizations.

    Includes:
    - Indexes on frequently queried columns
    - ARRAY type for tags (PostgreSQL)
    - JSON type for metadata
    """

    __tablename__ = "products"

    # Primary key
    id = Column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
    )

    # Business key
    sku = Column(String(50), unique=True, nullable=False, index=True)

    # Product information
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)

    # Pricing (using Numeric for precision)
    price = Column(Numeric(10, 2), nullable=False, index=True)
    cost = Column(Numeric(10, 2), nullable=False)

    # Status
    status = Column(
        SQLEnum(ProductStatus),
        nullable=False,
        default=ProductStatus.ACTIVE,
        index=True,
    )

    # Tags and metadata (using JSON for SQLite compatibility)
    tags = Column(JSON, nullable=False, default=list)
    product_metadata = Column("metadata", JSON, nullable=False, default=dict)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    inventory = relationship(
        "InventoryModel",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # Composite indexes for common query patterns
    __table_args__ = (
        Index("idx_products_category_status", "category", "status"),
        Index("idx_products_price_range", "price"),
        Index("idx_products_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ProductModel(id={self.id}, sku={self.sku}, name={self.name})>"


class InventoryModel(Base):
    """Inventory database model with performance optimizations.

    Includes:
    - Foreign key to products
    - Indexes on frequently queried columns
    - Computed columns support
    """

    __tablename__ = "inventory"

    # Primary key
    id = Column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
    )

    # Foreign key to product
    product_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Stock levels
    quantity = Column(Integer, nullable=False, default=0, index=True)
    reserved = Column(Integer, nullable=False, default=0)

    # Reorder settings
    reorder_point = Column(Integer, nullable=False, default=0)
    reorder_quantity = Column(Integer, nullable=False, default=0)

    # Location
    warehouse_location = Column(String(50), nullable=False, index=True)

    # Status
    status = Column(
        SQLEnum(StockStatus),
        nullable=False,
        default=StockStatus.IN_STOCK,
        index=True,
    )

    # Timestamps
    last_restock_date = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    product = relationship("ProductModel", back_populates="inventory")

    # Composite indexes for common query patterns
    __table_args__ = (
        Index("idx_inventory_location_status", "warehouse_location", "status"),
        Index("idx_inventory_quantity", "quantity"),
        Index("idx_inventory_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<InventoryModel(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"
