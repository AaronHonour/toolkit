"""Product API endpoints.

High-performance REST API for product management with:
- Full CRUD operations
- Search and filtering
- Bulk operations
- Query result caching
"""

from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.product_service import (
    ProductService,
)
from src.application.dtos.product_dtos import (
    CreateProductDTO,
    UpdateProductDTO,
)
from src.domain.models.product import (
    ProductStatus,
)
from src.presentation.dependencies import (
    get_db_session,
    get_product_service,
)
from src.presentation.schemas.product_schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)


router = APIRouter()


def _to_response(dto) -> dict:
    """Convert DTO to response dict."""
    return {
        "id": dto.id,
        "sku": dto.sku,
        "name": dto.name,
        "description": dto.description,
        "category": dto.category,
        "price": dto.price,
        "cost": dto.cost,
        "margin": dto.margin,
        "status": dto.status,
        "tags": dto.tags,
        "metadata": dto.metadata,
        "created_at": dto.created_at,
        "updated_at": dto.updated_at,
    }


@router.get(
    "",
    response_model=ProductListResponse,
    summary="List all products",
    description="Get paginated list of products with optional status filtering",
)
async def list_products(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum items to return"),
    status: Optional[ProductStatus] = Query(None, description="Filter by status"),
    session: AsyncSession = Depends(get_db_session),
) -> ProductListResponse:
    """List all products with pagination."""
    service = await get_product_service(session)
    result = await service.get_all(skip=skip, limit=limit, status=status)

    return ProductListResponse(
        items=[ProductResponse(**_to_response(item)) for item in result.items],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
        has_more=result.has_more,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product by ID",
    description="Retrieve a single product by its unique identifier",
)
async def get_product(
    product_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> ProductResponse:
    """Get product by ID."""
    service = await get_product_service(session)
    product = await service.get_by_id(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found",
        )

    return ProductResponse(**_to_response(product))


@router.get(
    "/sku/{sku}",
    response_model=ProductResponse,
    summary="Get product by SKU",
    description="Retrieve a single product by its SKU",
)
async def get_product_by_sku(
    sku: str,
    session: AsyncSession = Depends(get_db_session),
) -> ProductResponse:
    """Get product by SKU."""
    service = await get_product_service(session)
    product = await service.get_by_sku(sku)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU {sku} not found",
        )

    return ProductResponse(**_to_response(product))


@router.get(
    "/category/{category}",
    response_model=ProductListResponse,
    summary="Get products by category",
    description="Retrieve products filtered by category",
)
async def get_products_by_category(
    category: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[ProductStatus] = Query(None),
    session: AsyncSession = Depends(get_db_session),
) -> ProductListResponse:
    """Get products by category."""
    service = await get_product_service(session)
    result = await service.get_by_category(
        category=category, skip=skip, limit=limit, status=status
    )

    return ProductListResponse(
        items=[ProductResponse(**_to_response(item)) for item in result.items],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
        has_more=result.has_more,
    )


@router.get(
    "/search/query",
    response_model=ProductListResponse,
    summary="Search products",
    description="Search products by name or description",
)
async def search_products(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[ProductStatus] = Query(None),
    session: AsyncSession = Depends(get_db_session),
) -> ProductListResponse:
    """Search products by name or description."""
    service = await get_product_service(session)
    result = await service.search(
        query_text=q, skip=skip, limit=limit, status=status
    )

    return ProductListResponse(
        items=[ProductResponse(**_to_response(item)) for item in result.items],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
        has_more=result.has_more,
    )


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create product",
    description="Create a new product",
)
async def create_product(
    product: ProductCreate,
    session: AsyncSession = Depends(get_db_session),
) -> ProductResponse:
    """Create new product."""
    service = await get_product_service(session)

    dto = CreateProductDTO(
        sku=product.sku,
        name=product.name,
        description=product.description,
        category=product.category,
        price=product.price,
        cost=product.cost,
        tags=product.tags,
        metadata=product.metadata,
    )

    try:
        created = await service.create(dto)
        return ProductResponse(**_to_response(created))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product",
    description="Update an existing product",
)
async def update_product(
    product_id: UUID,
    product: ProductUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> ProductResponse:
    """Update existing product."""
    service = await get_product_service(session)

    dto = UpdateProductDTO(
        name=product.name,
        description=product.description,
        category=product.category,
        price=product.price,
        cost=product.cost,
        status=product.status,
        tags=product.tags,
        metadata=product.metadata,
    )

    try:
        updated = await service.update(product_id, dto)
        return ProductResponse(**_to_response(updated))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product",
    description="Delete a product by ID",
)
async def delete_product(
    product_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """Delete product."""
    service = await get_product_service(session)
    deleted = await service.delete(product_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found",
        )
