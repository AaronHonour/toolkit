"""Graph service for managing the service dependency graph."""

from typing import List, Optional, Dict, Any
from unistax.graph.structures import (
    ServiceDependencyGraph,
    ServiceNode,
    DependencyEdge,
    ServiceType,
    DependencyType,
)
from unistax.analysis.dependency_analyzer import DependencyAnalyzer, AnalysisReport, AnalysisType
from unistax.analysis.impact_analyzer import ImpactAnalyzer, ImpactReport, ChangeType
from unistax.graph.visualizer import GraphVisualizer, VisualizationFormat


class GraphService:
    """Service for managing service dependency graph operations."""

    def __init__(self):
        """Initialize the graph service with an empty graph."""
        self._graph = ServiceDependencyGraph()

    def add_service(
        self,
        name: str,
        service_type: str,
        endpoints: List[str],
        metadata: Dict[str, Any],
    ) -> ServiceNode:
        """Add a service to the graph."""
        service_type_enum = ServiceType(service_type)
        service = ServiceNode.create(
            name=name,
            service_type=service_type_enum,
            endpoints=endpoints,
            metadata=metadata,
        )
        self._graph.add_service(service)
        return service

    def get_service(self, name: str) -> Optional[ServiceNode]:
        """Get a service by name."""
        return self._graph.get_service(name)

    def get_all_services(self) -> List[ServiceNode]:
        """Get all services."""
        return self._graph.get_all_services()

    def add_dependency(
        self,
        source: str,
        target: str,
        dependency_type: str,
        weight: float = 1.0,
        metadata: Dict[str, Any] = None,
    ) -> DependencyEdge:
        """Add a dependency between services."""
        dep_type_enum = DependencyType(dependency_type)
        dependency = DependencyEdge.create(
            source=source,
            target=target,
            dependency_type=dep_type_enum,
            weight=weight,
            metadata=metadata or {},
        )
        self._graph.add_dependency(dependency)
        return dependency

    def get_dependency(self, source: str, target: str) -> Optional[DependencyEdge]:
        """Get a specific dependency."""
        return self._graph.get_dependency(source, target)

    def get_all_dependencies(self) -> List[DependencyEdge]:
        """Get all dependencies."""
        return self._graph.get_all_dependencies()

    def analyze(
        self,
        analysis_type: str = "full_analysis",
        criticality_threshold: float = 0.7,
    ) -> AnalysisReport:
        """Perform dependency analysis."""
        analyzer = DependencyAnalyzer(self._graph)
        analysis_type_enum = AnalysisType(analysis_type)
        return analyzer.analyze(analysis_type_enum, criticality_threshold)

    def calculate_blast_radius(self, service_name: str):
        """Calculate blast radius for a service."""
        analyzer = DependencyAnalyzer(self._graph)
        return analyzer.calculate_blast_radius_for_service(service_name)

    def analyze_impact(
        self,
        service_name: str,
        change_type: str,
        failure_probability: float = 1.0,
        is_breaking_change: bool = False,
        expected_downtime_minutes: float = 0.0,
        degradation_factor: float = 0.5,
    ) -> ImpactReport:
        """Analyze the impact of a change."""
        analyzer = ImpactAnalyzer(self._graph)

        change_type_enum = ChangeType(change_type)

        if change_type_enum == ChangeType.SERVICE_FAILURE:
            return analyzer.analyze_service_failure(service_name, failure_probability)
        elif change_type_enum in (ChangeType.SERVICE_DEPLOYMENT, ChangeType.BREAKING_CHANGE):
            return analyzer.analyze_deployment_impact(
                service_name,
                is_breaking_change,
                expected_downtime_minutes,
            )
        elif change_type_enum == ChangeType.SERVICE_DEGRADATION:
            return analyzer.analyze_degradation_impact(service_name, degradation_factor)
        else:
            # Default to failure analysis
            return analyzer.analyze_service_failure(service_name, failure_probability)

    def visualize(self, format: str) -> Any:
        """Export graph for visualization."""
        format_enum = VisualizationFormat(format)
        return GraphVisualizer.export(self._graph, format_enum)

    def get_service_count(self) -> int:
        """Get the number of services."""
        return self._graph.get_service_count()

    def get_dependency_count(self) -> int:
        """Get the number of dependencies."""
        return self._graph.get_dependency_count()


# Singleton instance
_graph_service_instance: Optional[GraphService] = None


def get_graph_service() -> GraphService:
    """Get the graph service singleton instance."""
    global _graph_service_instance
    if _graph_service_instance is None:
        _graph_service_instance = GraphService()
    return _graph_service_instance
