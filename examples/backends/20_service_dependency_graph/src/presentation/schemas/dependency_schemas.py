"""Pydantic schemas for dependency API endpoints."""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class DependencyCreate(BaseModel):
    """Schema for creating a new dependency."""

    source: str = Field(..., description="Source service name")
    target: str = Field(..., description="Target service name")
    dependency_type: str = Field(..., description="Type of dependency (api_call, database, message_queue, etc.)")
    weight: float = Field(default=1.0, description="Dependency weight/importance")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DependencyResponse(BaseModel):
    """Schema for dependency response."""

    id: str
    source: str
    target: str
    dependency_type: str
    weight: float
    latency_p99: Optional[float]
    error_rate: float
    request_rate: float
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class DependencyMetricsUpdate(BaseModel):
    """Schema for updating dependency metrics."""

    latency_p99: Optional[float] = None
    error_rate: Optional[float] = None
    request_rate: Optional[float] = None
