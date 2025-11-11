"""Pydantic schemas for product API endpoints.

Provides request validation and response serialization with FastAPI.
"""

from decimal import Decimal
from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from src.domain.models.product import (
    ProductStatus,
)


class ProductBase(BaseModel):
    """Base product schema with common fields."""

    sku: str = Field(..., min_length=1, max_length=50, description="Product SKU")
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: str = Field(..., min_length=1, description="Product description")
    category: str = Field(..., min_length=1, max_length=100, description="Product category")
    price: Decimal = Field(..., gt=0, decimal_places=2, description="Product price")
    cost: Decimal = Field(..., gt=0, decimal_places=2, description="Product cost")


class ProductCreate(ProductBase):
    """Schema for creating a new product."""

    tags: List[str] = Field(default_factory=list, description="Product tags")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sku": "PROD-001",
                "name": "Premium Widget",
                "description": "High-quality widget for industrial use",
                "category": "Widgets",
                "price": "99.99",
                "cost": "45.00",
                "tags": ["premium", "industrial"],
                "metadata": {"manufacturer": "WidgetCo", "warranty_months": 24}
            }
        }
    )


class ProductUpdate(BaseModel):
    """Schema for updating an existing product."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    cost: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    status: Optional[ProductStatus] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Premium Widget",
                "price": "109.99",
                "status": "active"
            }
        }
    )


class ProductResponse(ProductBase):
    """Schema for product API responses."""

    id: str = Field(..., description="Product unique identifier")
    margin: str = Field(..., description="Profit margin (calculated)")
    status: str = Field(..., description="Product status")
    tags: List[str] = Field(..., description="Product tags")
    metadata: dict = Field(..., description="Additional metadata")
    created_at: str = Field(..., description="Creation timestamp (ISO 8601)")
    updated_at: str = Field(..., description="Last update timestamp (ISO 8601)")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "sku": "PROD-001",
                "name": "Premium Widget",
                "description": "High-quality widget for industrial use",
                "category": "Widgets",
                "price": "99.99",
                "cost": "45.00",
                "margin": "0.549549",
                "status": "active",
                "tags": ["premium", "industrial"],
                "metadata": {"manufacturer": "WidgetCo"},
                "created_at": "2025-01-07T10:00:00Z",
                "updated_at": "2025-01-07T10:00:00Z"
            }
        }
    )


class ProductListResponse(BaseModel):
    """Schema for paginated product list responses."""

    items: List[ProductResponse] = Field(..., description="List of products")
    total: int = Field(..., description="Total number of products")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum items per page")
    has_more: bool = Field(..., description="Whether more items are available")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 100,
                "skip": 0,
                "limit": 50,
                "has_more": True
            }
        }
    )
