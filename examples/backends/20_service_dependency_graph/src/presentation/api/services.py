"""API endpoints for service management."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List

from src.presentation.schemas.service_schemas import (
    ServiceCreate,
    ServiceResponse,
    ServiceUpdate,
)
from src.application.services.graph_service import get_graph_service, GraphService

router = APIRouter()


@router.post("", response_model=ServiceResponse, status_code=201)
async def create_service(
    service: ServiceCreate,
    graph_service: GraphService = Depends(get_graph_service),
) -> ServiceResponse:
    """Register a new service in the dependency graph."""
    # Check if service already exists
    existing = graph_service.get_service(service.name)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Service '{service.name}' already exists",
        )

    # Create service
    created = graph_service.add_service(
        name=service.name,
        service_type=service.service_type,
        endpoints=service.endpoints,
        metadata=service.metadata,
    )

    return ServiceResponse(
        id=str(created.id),
        name=created.name,
        service_type=created.service_type.value,
        endpoints=created.endpoints,
        metadata=created.metadata,
        health_score=created.health_score,
        created_at=created.created_at,
        updated_at=created.updated_at,
    )


@router.get("", response_model=List[ServiceResponse])
async def list_services(
    graph_service: GraphService = Depends(get_graph_service),
) -> List[ServiceResponse]:
    """List all registered services."""
    services = graph_service.get_all_services()

    return [
        ServiceResponse(
            id=str(s.id),
            name=s.name,
            service_type=s.service_type.value,
            endpoints=s.endpoints,
            metadata=s.metadata,
            health_score=s.health_score,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for s in services
    ]


@router.get("/{service_name}", response_model=ServiceResponse)
async def get_service(
    service_name: str,
    graph_service: GraphService = Depends(get_graph_service),
) -> ServiceResponse:
    """Get details of a specific service."""
    service = graph_service.get_service(service_name)

    if not service:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service_name}' not found",
        )

    return ServiceResponse(
        id=str(service.id),
        name=service.name,
        service_type=service.service_type.value,
        endpoints=service.endpoints,
        metadata=service.metadata,
        health_score=service.health_score,
        created_at=service.created_at,
        updated_at=service.updated_at,
    )
