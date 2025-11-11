"""Pydantic schemas for service API endpoints."""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class ServiceCreate(BaseModel):
    """Schema for creating a new service."""

    name: str = Field(..., description="Unique service name")
    service_type: str = Field(..., description="Type of service (api, database, cache, queue, etc.)")
    endpoints: List[str] = Field(default_factory=list, description="List of service endpoints")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ServiceResponse(BaseModel):
    """Schema for service response."""

    id: str
    name: str
    service_type: str
    endpoints: List[str]
    metadata: Dict[str, Any]
    health_score: float
    created_at: datetime
    updated_at: datetime


class ServiceUpdate(BaseModel):
    """Schema for updating a service."""

    service_type: Optional[str] = None
    endpoints: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    health_score: Optional[float] = None
