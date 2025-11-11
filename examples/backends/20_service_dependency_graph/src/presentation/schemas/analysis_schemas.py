"""Pydantic schemas for analysis API endpoints."""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class CircularDependencyResponse(BaseModel):
    """Schema for circular dependency response."""

    services: List[str]
    cycle_length: int
    cycle_path: str


class BlastRadiusResponse(BaseModel):
    """Schema for blast radius response."""

    failed_service: str
    affected_services: List[str]
    impact_levels: Dict[str, int]
    total_affected: int
    critical_services: List[str]


class CriticalityScoreResponse(BaseModel):
    """Schema for criticality score response."""

    service: str
    score: float
    rank: int
    is_critical: bool
    reasons: List[str]


class AnalysisReportResponse(BaseModel):
    """Schema for comprehensive analysis report."""

    analysis_type: str
    generated_at: datetime
    service_count: int
    dependency_count: int
    has_circular_dependencies: bool
    circular_dependencies: List[CircularDependencyResponse]
    critical_services: List[CriticalityScoreResponse]
    bottlenecks: Dict[str, float]
    deployment_order: Optional[List[str]]
    insights: List[str]
    warnings: List[str]
    recommendations: List[str]


class ImpactAnalysisRequest(BaseModel):
    """Schema for impact analysis request."""

    service_name: str = Field(..., description="Service to analyze")
    change_type: str = Field(..., description="Type of change (service_failure, breaking_change, etc.)")
    failure_probability: float = Field(default=1.0, description="Probability of failure")
    is_breaking_change: bool = Field(default=False, description="Is this a breaking change")
    expected_downtime_minutes: float = Field(default=0.0, description="Expected downtime")
    degradation_factor: float = Field(default=0.5, description="Degradation severity (0-1)")


class ChangeImpactResponse(BaseModel):
    """Schema for change impact response."""

    service: str
    impact_level: int
    impact_type: str
    probability: float
    estimated_downtime_minutes: Optional[float]
    mitigation: Optional[str]


class ImpactReportResponse(BaseModel):
    """Schema for impact report response."""

    change_type: str
    source_service: str
    generated_at: datetime
    total_affected: int
    direct_impact: List[ChangeImpactResponse]
    indirect_impact: List[ChangeImpactResponse]
    cascading_impact: List[ChangeImpactResponse]
    risk_level: str
    pre_change_actions: List[str]
    monitoring_required: List[str]
    rollback_plan: Optional[str]
