"""Inventory API endpoints.

High-performance REST API for inventory management with:
- Stock operations (reserve, release, fulfill)
- Inventory queries and reporting
- Atomic operations for concurrency safety
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.inventory_service import (
    InventoryService,
)
from src.application.dtos.inventory_dtos import (
    CreateInventoryDTO,
    UpdateInventoryDTO,
)
from src.domain.models.inventory import (
    StockStatus,
)
from src.presentation.dependencies import (
    get_db_session,
    get_inventory_service,
)
from src.presentation.schemas.inventory_schemas import (
    InventoryCreate,
    InventoryUpdate,
    InventoryResponse,
    InventoryListResponse,
    StockOperation,
    TransferStock,
)


router = APIRouter()


def _to_response(dto) -> dict:
    """Convert DTO to response dict."""
    return {
        "id": dto.id,
        "product_id": dto.product_id,
        "quantity": dto.quantity,
        "reserved": dto.reserved,
        "available": dto.available,
        "reorder_point": dto.reorder_point,
        "reorder_quantity": dto.reorder_quantity,
        "warehouse_location": dto.warehouse_location,
        "status": dto.status,
        "needs_reorder": dto.needs_reorder,
        "last_restock_date": dto.last_restock_date,
        "updated_at": dto.updated_at,
    }


@router.get(
    "",
    response_model=InventoryListResponse,
    summary="List all inventory",
    description="Get paginated list of inventory items with optional status filtering",
)
async def list_inventory(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum items to return"),
    status: Optional[StockStatus] = Query(None, description="Filter by status"),
    session: AsyncSession = Depends(get_db_session),
) -> InventoryListResponse:
    """List all inventory with pagination."""
    service = await get_inventory_service(session)
    result = await service.get_all(skip=skip, limit=limit, status=status)

    return InventoryListResponse(
        items=[InventoryResponse(**_to_response(item)) for item in result.items],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
        has_more=result.has_more,
    )


@router.get(
    "/{inventory_id}",
    response_model=InventoryResponse,
    summary="Get inventory by ID",
    description="Retrieve a single inventory item by its unique identifier",
)
async def get_inventory(
    inventory_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> InventoryResponse:
    """Get inventory by ID."""
    service = await get_inventory_service(session)
    inventory = await service.get_by_id(inventory_id)

    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory {inventory_id} not found",
        )

    return InventoryResponse(**_to_response(inventory))


@router.get(
    "/product/{product_id}",
    response_model=InventoryResponse,
    summary="Get inventory by product ID",
    description="Retrieve inventory for a specific product",
)
async def get_inventory_by_product(
    product_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> InventoryResponse:
    """Get inventory by product ID."""
    service = await get_inventory_service(session)
    inventory = await service.get_by_product_id(product_id)

    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory for product {product_id} not found",
        )

    return InventoryResponse(**_to_response(inventory))


@router.get(
    "/location/{warehouse_location}",
    response_model=InventoryListResponse,
    summary="Get inventory by location",
    description="Retrieve inventory items at a specific warehouse location",
)
async def get_inventory_by_location(
    warehouse_location: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db_session),
) -> InventoryListResponse:
    """Get inventory by warehouse location."""
    service = await get_inventory_service(session)
    result = await service.get_by_location(
        warehouse_location=warehouse_location, skip=skip, limit=limit
    )

    return InventoryListResponse(
        items=[InventoryResponse(**_to_response(item)) for item in result.items],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
        has_more=result.has_more,
    )


@router.get(
    "/alerts/low-stock",
    response_model=InventoryListResponse,
    summary="Get low stock items",
    description="Retrieve items with stock below reorder point",
)
async def get_low_stock_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db_session),
) -> InventoryListResponse:
    """Get low stock items."""
    service = await get_inventory_service(session)
    result = await service.get_low_stock_items(skip=skip, limit=limit)

    return InventoryListResponse(
        items=[InventoryResponse(**_to_response(item)) for item in result.items],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
        has_more=result.has_more,
    )


@router.get(
    "/alerts/out-of-stock",
    response_model=InventoryListResponse,
    summary="Get out of stock items",
    description="Retrieve items that are completely out of stock",
)
async def get_out_of_stock_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db_session),
) -> InventoryListResponse:
    """Get out of stock items."""
    service = await get_inventory_service(session)
    result = await service.get_out_of_stock_items(skip=skip, limit=limit)

    return InventoryListResponse(
        items=[InventoryResponse(**_to_response(item)) for item in result.items],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
        has_more=result.has_more,
    )


@router.get(
    "/alerts/needs-restock",
    response_model=InventoryListResponse,
    summary="Get items needing restock",
    description="Retrieve items at or below reorder point",
)
async def get_items_needing_restock(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db_session),
) -> InventoryListResponse:
    """Get items needing restock."""
    service = await get_inventory_service(session)
    result = await service.get_items_needing_restock(skip=skip, limit=limit)

    return InventoryListResponse(
        items=[InventoryResponse(**_to_response(item)) for item in result.items],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
        has_more=result.has_more,
    )


@router.post(
    "",
    response_model=InventoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create inventory",
    description="Create inventory for a product",
)
async def create_inventory(
    inventory: InventoryCreate,
    session: AsyncSession = Depends(get_db_session),
) -> InventoryResponse:
    """Create inventory for a product."""
    service = await get_inventory_service(session)

    dto = CreateInventoryDTO(
        product_id=inventory.product_id,
        quantity=inventory.quantity,
        reorder_point=inventory.reorder_point,
        reorder_quantity=inventory.reorder_quantity,
        warehouse_location=inventory.warehouse_location,
    )

    try:
        created = await service.create(dto)
        return InventoryResponse(**_to_response(created))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/{inventory_id}",
    response_model=InventoryResponse,
    summary="Update inventory settings",
    description="Update inventory settings (not stock levels)",
)
async def update_inventory(
    inventory_id: UUID,
    inventory: InventoryUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> InventoryResponse:
    """Update inventory settings."""
    service = await get_inventory_service(session)

    dto = UpdateInventoryDTO(
        reorder_point=inventory.reorder_point,
        reorder_quantity=inventory.reorder_quantity,
        warehouse_location=inventory.warehouse_location,
    )

    try:
        updated = await service.update(inventory_id, dto)
        return InventoryResponse(**_to_response(updated))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/product/{product_id}/reserve",
    response_model=InventoryResponse,
    summary="Reserve stock",
    description="Reserve stock for an order (atomic operation)",
)
async def reserve_stock(
    product_id: UUID,
    operation: StockOperation,
    session: AsyncSession = Depends(get_db_session),
) -> InventoryResponse:
    """Reserve stock for a product."""
    service = await get_inventory_service(session)

    try:
        updated = await service.reserve_stock(product_id, operation.quantity)
        return InventoryResponse(**_to_response(updated))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/product/{product_id}/release",
    response_model=InventoryResponse,
    summary="Release reservation",
    description="Release previously reserved stock",
)
async def release_reservation(
    product_id: UUID,
    operation: StockOperation,
    session: AsyncSession = Depends(get_db_session),
) -> InventoryResponse:
    """Release reserved stock."""
    service = await get_inventory_service(session)

    try:
        updated = await service.release_reservation(product_id, operation.quantity)
        return InventoryResponse(**_to_response(updated))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/product/{product_id}/fulfill",
    response_model=InventoryResponse,
    summary="Fulfill reservation",
    description="Fulfill reservation (ship order, atomic operation)",
)
async def fulfill_reservation(
    product_id: UUID,
    operation: StockOperation,
    session: AsyncSession = Depends(get_db_session),
) -> InventoryResponse:
    """Fulfill reservation (convert reservation to shipment)."""
    service = await get_inventory_service(session)

    try:
        updated = await service.fulfill_reservation(product_id, operation.quantity)
        return InventoryResponse(**_to_response(updated))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/product/{product_id}/add",
    response_model=InventoryResponse,
    summary="Add stock",
    description="Add stock (restock operation)",
)
async def add_stock(
    product_id: UUID,
    operation: StockOperation,
    session: AsyncSession = Depends(get_db_session),
) -> InventoryResponse:
    """Add stock to inventory."""
    service = await get_inventory_service(session)

    try:
        updated = await service.add_stock(product_id, operation.quantity)
        return InventoryResponse(**_to_response(updated))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/product/{product_id}/remove",
    response_model=InventoryResponse,
    summary="Remove stock",
    description="Remove stock (shrinkage, damage, etc.)",
)
async def remove_stock(
    product_id: UUID,
    operation: StockOperation,
    session: AsyncSession = Depends(get_db_session),
) -> InventoryResponse:
    """Remove stock from inventory."""
    service = await get_inventory_service(session)

    try:
        updated = await service.remove_stock(product_id, operation.quantity)
        return InventoryResponse(**_to_response(updated))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/product/{product_id}/transfer",
    summary="Transfer stock",
    description="Transfer stock between warehouse locations",
)
async def transfer_stock(
    product_id: UUID,
    transfer: TransferStock,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Transfer stock between locations."""
    service = await get_inventory_service(session)

    try:
        success = await service.transfer_stock(
            product_id=product_id,
            from_location=transfer.from_location,
            to_location=transfer.to_location,
            quantity=transfer.quantity,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock transfer failed",
            )

        return {
            "success": True,
            "product_id": str(product_id),
            "from": transfer.from_location,
            "to": transfer.to_location,
            "quantity": transfer.quantity,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/reports/snapshot",
    summary="Get inventory snapshot",
    description="Get comprehensive inventory snapshot for reporting",
)
async def get_inventory_snapshot(
    session: AsyncSession = Depends(get_db_session),
) -> List[dict]:
    """Get inventory snapshot for reporting."""
    service = await get_inventory_service(session)
    return await service.get_snapshot()


@router.get(
    "/reports/total-value",
    summary="Get total inventory value",
    description="Calculate total inventory value",
)
async def get_total_inventory_value(
    warehouse_location: Optional[str] = Query(None, description="Filter by location"),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get total inventory value."""
    service = await get_inventory_service(session)
    total = await service.get_total_value(warehouse_location=warehouse_location)

    return {
        "total_value": total,
        "warehouse_location": warehouse_location,
    }
