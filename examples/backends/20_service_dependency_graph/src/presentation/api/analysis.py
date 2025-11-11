"""API endpoints for dependency analysis."""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Optional

from src.presentation.schemas.analysis_schemas import (
    AnalysisReportResponse,
    CircularDependencyResponse,
    BlastRadiusResponse,
    CriticalityScoreResponse,
    ImpactAnalysisRequest,
    ImpactReportResponse,
    ChangeImpactResponse,
)
from src.application.services.graph_service import get_graph_service, GraphService

router = APIRouter()


@router.get("/graph", response_model=AnalysisReportResponse)
async def analyze_graph(
    analysis_type: str = Query(default="full_analysis", description="Type of analysis to perform"),
    criticality_threshold: float = Query(default=0.7, ge=0.0, le=1.0),
    graph_service: GraphService = Depends(get_graph_service),
) -> AnalysisReportResponse:
    """Perform comprehensive dependency analysis."""
    report = graph_service.analyze(analysis_type, criticality_threshold)

    return AnalysisReportResponse(
        analysis_type=report.analysis_type.value,
        generated_at=report.generated_at,
        service_count=report.service_count,
        dependency_count=report.dependency_count,
        has_circular_dependencies=report.has_circular_dependencies,
        circular_dependencies=[
            CircularDependencyResponse(
                services=cd.services,
                cycle_length=cd.cycle_length,
                cycle_path=cd.cycle_path,
            )
            for cd in report.circular_dependencies
        ],
        critical_services=[
            CriticalityScoreResponse(
                service=cs.service,
                score=cs.score,
                rank=cs.rank,
                is_critical=cs.is_critical,
                reasons=cs.reasons,
            )
            for cs in report.critical_services
        ],
        bottlenecks=report.bottlenecks,
        deployment_order=report.deployment_order,
        insights=report.insights,
        warnings=report.warnings,
        recommendations=report.recommendations,
    )


@router.get("/circular", response_model=List[CircularDependencyResponse])
async def detect_circular_dependencies(
    graph_service: GraphService = Depends(get_graph_service),
) -> List[CircularDependencyResponse]:
    """Detect circular dependencies in the service graph."""
    report = graph_service.analyze("circular_dependencies")

    return [
        CircularDependencyResponse(
            services=cd.services,
            cycle_length=cd.cycle_length,
            cycle_path=cd.cycle_path,
        )
        for cd in report.circular_dependencies
    ]


@router.get("/blast-radius/{service_name}", response_model=BlastRadiusResponse)
async def calculate_blast_radius(
    service_name: str,
    graph_service: GraphService = Depends(get_graph_service),
) -> BlastRadiusResponse:
    """Calculate the blast radius of a service failure."""
    # Verify service exists
    service = graph_service.get_service(service_name)
    if not service:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service_name}' not found",
        )

    result = graph_service.calculate_blast_radius(service_name)

    return BlastRadiusResponse(
        failed_service=result.failed_service,
        affected_services=list(result.affected_services),
        impact_levels=result.impact_levels,
        total_affected=result.total_affected,
        critical_services=list(result.critical_services),
    )


@router.get("/criticality", response_model=List[CriticalityScoreResponse])
async def calculate_criticality(
    threshold: float = Query(default=0.7, ge=0.0, le=1.0),
    graph_service: GraphService = Depends(get_graph_service),
) -> List[CriticalityScoreResponse]:
    """Calculate service criticality scores."""
    report = graph_service.analyze("service_criticality", threshold)

    return [
        CriticalityScoreResponse(
            service=cs.service,
            score=cs.score,
            rank=cs.rank,
            is_critical=cs.is_critical,
            reasons=cs.reasons,
        )
        for cs in report.critical_services
    ]


@router.get("/bottlenecks", response_model=Dict[str, float])
async def identify_bottlenecks(
    graph_service: GraphService = Depends(get_graph_service),
) -> Dict[str, float]:
    """Identify bottleneck services using betweenness centrality."""
    report = graph_service.analyze("bottleneck_detection")
    return report.bottlenecks


@router.get("/deployment-order", response_model=Optional[List[str]])
async def get_deployment_order(
    graph_service: GraphService = Depends(get_graph_service),
) -> Optional[List[str]]:
    """Get safe deployment order for services."""
    report = graph_service.analyze("deployment_order")
    return report.deployment_order


@router.post("/impact", response_model=ImpactReportResponse)
async def analyze_impact(
    request: ImpactAnalysisRequest,
    graph_service: GraphService = Depends(get_graph_service),
) -> ImpactReportResponse:
    """Analyze the impact of a change or failure."""
    # Verify service exists
    service = graph_service.get_service(request.service_name)
    if not service:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{request.service_name}' not found",
        )

    impact = graph_service.analyze_impact(
        service_name=request.service_name,
        change_type=request.change_type,
        failure_probability=request.failure_probability,
        is_breaking_change=request.is_breaking_change,
        expected_downtime_minutes=request.expected_downtime_minutes,
        degradation_factor=request.degradation_factor,
    )

    return ImpactReportResponse(
        change_type=impact.change_type.value,
        source_service=impact.source_service,
        generated_at=impact.generated_at,
        total_affected=impact.total_affected,
        direct_impact=[
            ChangeImpactResponse(
                service=ci.service,
                impact_level=ci.impact_level,
                impact_type=ci.impact_type,
                probability=ci.probability,
                estimated_downtime_minutes=ci.estimated_downtime_minutes,
                mitigation=ci.mitigation,
            )
            for ci in impact.direct_impact
        ],
        indirect_impact=[
            ChangeImpactResponse(
                service=ci.service,
                impact_level=ci.impact_level,
                impact_type=ci.impact_type,
                probability=ci.probability,
                estimated_downtime_minutes=ci.estimated_downtime_minutes,
                mitigation=ci.mitigation,
            )
            for ci in impact.indirect_impact
        ],
        cascading_impact=[
            ChangeImpactResponse(
                service=ci.service,
                impact_level=ci.impact_level,
                impact_type=ci.impact_type,
                probability=ci.probability,
                estimated_downtime_minutes=ci.estimated_downtime_minutes,
                mitigation=ci.mitigation,
            )
            for ci in impact.cascading_impact
        ],
        risk_level=impact.risk_level,
        pre_change_actions=impact.pre_change_actions,
        monitoring_required=impact.monitoring_required,
        rollback_plan=impact.rollback_plan,
    )
