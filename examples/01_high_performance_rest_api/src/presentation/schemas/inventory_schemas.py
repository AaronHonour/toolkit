"""Pydantic schemas for inventory API endpoints.

Provides request validation and response serialization with FastAPI.
"""

from typing import List, Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class InventoryBase(BaseModel):
    """Base inventory schema with common fields."""

    quantity: int = Field(..., ge=0, description="Total quantity in stock")
    reorder_point: int = Field(..., ge=0, description="Reorder point threshold")
    reorder_quantity: int = Field(..., ge=0, description="Quantity to order when restocking")
    warehouse_location: str = Field(..., min_length=1, max_length=50, description="Warehouse location")


class InventoryCreate(InventoryBase):
    """Schema for creating inventory for a product."""

    product_id: UUID = Field(..., description="Product unique identifier")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": "550e8400-e29b-41d4-a716-446655440000",
                "quantity": 100,
                "reorder_point": 20,
                "reorder_quantity": 50,
                "warehouse_location": "A-101"
            }
        }
    )


class InventoryUpdate(BaseModel):
    """Schema for updating inventory settings."""

    reorder_point: Optional[int] = Field(None, ge=0)
    reorder_quantity: Optional[int] = Field(None, ge=0)
    warehouse_location: Optional[str] = Field(None, min_length=1, max_length=50)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reorder_point": 25,
                "reorder_quantity": 60
            }
        }
    )


class StockOperation(BaseModel):
    """Schema for stock operations (reserve, add, remove)."""

    quantity: int = Field(..., gt=0, description="Quantity for operation")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quantity": 10
            }
        }
    )


class TransferStock(BaseModel):
    """Schema for stock transfer operations."""

    from_location: str = Field(..., min_length=1, max_length=50, description="Source location")
    to_location: str = Field(..., min_length=1, max_length=50, description="Destination location")
    quantity: int = Field(..., gt=0, description="Quantity to transfer")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "from_location": "A-101",
                "to_location": "B-202",
                "quantity": 25
            }
        }
    )


class InventoryResponse(InventoryBase):
    """Schema for inventory API responses."""

    id: str = Field(..., description="Inventory unique identifier")
    product_id: str = Field(..., description="Product unique identifier")
    reserved: int = Field(..., description="Reserved quantity")
    available: int = Field(..., description="Available quantity (calculated)")
    status: str = Field(..., description="Inventory status")
    needs_reorder: bool = Field(..., description="Whether item needs reorder")
    last_restock_date: Optional[str] = Field(None, description="Last restock date (ISO 8601)")
    updated_at: str = Field(..., description="Last update timestamp (ISO 8601)")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "product_id": "550e8400-e29b-41d4-a716-446655440000",
                "quantity": 100,
                "reserved": 10,
                "available": 90,
                "reorder_point": 20,
                "reorder_quantity": 50,
                "warehouse_location": "A-101",
                "status": "in_stock",
                "needs_reorder": False,
                "last_restock_date": "2025-01-05T10:00:00Z",
                "updated_at": "2025-01-07T10:00:00Z"
            }
        }
    )


class InventoryListResponse(BaseModel):
    """Schema for paginated inventory list responses."""

    items: List[InventoryResponse] = Field(..., description="List of inventory items")
    total: int = Field(..., description="Total number of items")
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
