"""Core dependency analyzer combining graph algorithms and analysis."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from unistax.algorithms.graph import (
    BlastRadiusResult,
    CircularDependency,
    CriticalityScore,
    calculate_blast_radius,
    calculate_service_criticality,
    compute_betweenness_centrality,
    detect_circular_dependencies,
    topological_sort,
)
from unistax.graph.structures import ServiceDependencyGraph


class AnalysisType(str, Enum):
    """Types of dependency analysis."""

    CIRCULAR_DEPENDENCIES = "circular_dependencies"
    BLAST_RADIUS = "blast_radius"
    SERVICE_CRITICALITY = "service_criticality"
    BOTTLENECK_DETECTION = "bottleneck_detection"
    DEPLOYMENT_ORDER = "deployment_order"
    FULL_ANALYSIS = "full_analysis"


@dataclass
class AnalysisReport:
    """Comprehensive analysis report for a service dependency graph."""

    analysis_type: AnalysisType
    generated_at: datetime = field(default_factory=datetime.utcnow)
    service_count: int = 0
    dependency_count: int = 0

    # Analysis results
    circular_dependencies: list[CircularDependency] = field(default_factory=list)
    critical_services: list[CriticalityScore] = field(default_factory=list)
    bottlenecks: dict[str, float] = field(default_factory=dict)
    deployment_order: list[str] | None = None
    blast_radius_cache: dict[str, BlastRadiusResult] = field(default_factory=dict)

    # Insights and recommendations
    insights: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def has_circular_dependencies(self) -> bool:
        """Check if circular dependencies were found."""
        return len(self.circular_dependencies) > 0

    @property
    def critical_service_count(self) -> int:
        """Get count of critical services."""
        return sum(1 for s in self.critical_services if s.is_critical)

    def get_most_critical_services(self, top_n: int = 5) -> list[CriticalityScore]:
        """Get the top N most critical services."""
        return self.critical_services[:top_n]

    def get_top_bottlenecks(self, top_n: int = 5) -> list[tuple[str, float]]:
        """Get the top N bottleneck services."""
        sorted_bottlenecks = sorted(
            self.bottlenecks.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        return sorted_bottlenecks[:top_n]


class DependencyAnalyzer:
    """Analyzes service dependency graphs for issues and insights."""

    def __init__(self, graph: ServiceDependencyGraph) -> None:
        """Initialize dependency analyzer.

        Args:
            graph: Service dependency graph to analyze
        """
        self.graph = graph
        self._underlying_graph = graph.get_underlying_graph()

    def analyze(
        self,
        analysis_type: AnalysisType = AnalysisType.FULL_ANALYSIS,
        criticality_threshold: float = 0.7,
    ) -> AnalysisReport:
        """Perform dependency analysis.

        Args:
            analysis_type: Type of analysis to perform
            criticality_threshold: Threshold for marking services as critical

        Returns:
            Comprehensive analysis report
        """
        report = AnalysisReport(
            analysis_type=analysis_type,
            service_count=self.graph.get_service_count(),
            dependency_count=self.graph.get_dependency_count(),
        )

        # Build adjacency lists
        adj_list = self._build_adj_list()
        reverse_adj_list = self._build_reverse_adj_list()

        # Perform requested analysis
        if analysis_type in (AnalysisType.CIRCULAR_DEPENDENCIES, AnalysisType.FULL_ANALYSIS):
            report.circular_dependencies = self._analyze_circular_dependencies(adj_list)

        if analysis_type in (AnalysisType.SERVICE_CRITICALITY, AnalysisType.FULL_ANALYSIS):
            report.critical_services = self._analyze_criticality(
                adj_list,
                reverse_adj_list,
                criticality_threshold,
            )

        if analysis_type in (AnalysisType.BOTTLENECK_DETECTION, AnalysisType.FULL_ANALYSIS):
            report.bottlenecks = self._analyze_bottlenecks(adj_list)

        if analysis_type in (AnalysisType.DEPLOYMENT_ORDER, AnalysisType.FULL_ANALYSIS):
            report.deployment_order = self._calculate_deployment_order(adj_list)

        # Generate insights and recommendations
        self._generate_insights(report)
        self._generate_recommendations(report)

        return report

    def calculate_blast_radius_for_service(self, service_name: str) -> BlastRadiusResult:
        """Calculate blast radius for a specific service failure.

        Args:
            service_name: Name of the service to analyze

        Returns:
            Blast radius result showing impact of failure
        """
        adj_list = self._build_adj_list()
        return calculate_blast_radius(adj_list, service_name)

    def find_service_dependencies(
        self,
        service_name: str,
        direction: str = "both",
    ) -> dict[str, set[str]]:
        """Find dependencies for a specific service.

        Args:
            service_name: Service to analyze
            direction: "upstream", "downstream", or "both"

        Returns:
            Dictionary with upstream and/or downstream dependencies
        """
        result: dict[str, set[str]] = {}

        if direction in ("upstream", "both"):
            result["upstream"] = self.graph.get_upstream_services(service_name)

        if direction in ("downstream", "both"):
            result["downstream"] = self.graph.get_downstream_services(service_name)

        return result

    def _build_adj_list(self) -> dict[str, set[str]]:
        """Build adjacency list from graph."""
        adj_list: dict[str, set[str]] = {}

        for service in self.graph.get_all_services():
            adj_list[service.name] = self._underlying_graph.get_successors(service.name)

        return adj_list

    def _build_reverse_adj_list(self) -> dict[str, set[str]]:
        """Build reverse adjacency list from graph."""
        reverse_adj_list: dict[str, set[str]] = {}

        for service in self.graph.get_all_services():
            reverse_adj_list[service.name] = self._underlying_graph.get_predecessors(service.name)

        return reverse_adj_list

    def _analyze_circular_dependencies(
        self,
        adj_list: dict[str, set[str]],
    ) -> list[CircularDependency]:
        """Detect circular dependencies."""
        return detect_circular_dependencies(adj_list)

    def _analyze_criticality(
        self,
        adj_list: dict[str, set[str]],
        reverse_adj_list: dict[str, set[str]],
        threshold: float,
    ) -> list[CriticalityScore]:
        """Analyze service criticality."""
        return calculate_service_criticality(adj_list, reverse_adj_list, threshold)

    def _analyze_bottlenecks(self, adj_list: dict[str, set[str]]) -> dict[str, float]:
        """Identify bottleneck services."""
        return compute_betweenness_centrality(adj_list)

    def _calculate_deployment_order(
        self,
        adj_list: dict[str, set[str]],
    ) -> list[str] | None:
        """Calculate safe deployment order."""
        return topological_sort(adj_list)

    def _generate_insights(self, report: AnalysisReport) -> None:
        """Generate insights from analysis results."""
        # Circular dependency insights
        if report.circular_dependencies:
            report.insights.append(
                f"Found {len(report.circular_dependencies)} circular "
                f"{'dependency' if len(report.circular_dependencies) == 1 else 'dependencies'}"
            )
            report.warnings.append(
                "Circular dependencies can cause deployment issues and runtime failures"
            )

        # Criticality insights
        if report.critical_services:
            critical_count = report.critical_service_count
            if critical_count > 0:
                report.insights.append(f"{critical_count} services identified as critical")

                # Check for single point of failure
                top_critical = report.get_most_critical_services(3)
                if top_critical and top_critical[0].score > 0.9:
                    report.warnings.append(
                        f"Service '{top_critical[0].service}' is highly critical "
                        f"(score: {top_critical[0].score:.2f})"
                    )

        # Bottleneck insights
        if report.bottlenecks:
            top_bottlenecks = report.get_top_bottlenecks(3)
            if top_bottlenecks and top_bottlenecks[0][1] > 0.5:
                report.insights.append(
                    f"Service '{top_bottlenecks[0][0]}' is a major bottleneck "
                    f"(centrality: {top_bottlenecks[0][1]:.2f})"
                )

        # Deployment order insights
        if report.deployment_order is None and report.service_count > 0:
            report.warnings.append(
                "Cannot determine safe deployment order due to circular dependencies"
            )

    def _generate_recommendations(self, report: AnalysisReport) -> None:
        """Generate recommendations based on analysis."""
        # Circular dependency recommendations
        if report.circular_dependencies:
            report.recommendations.append(
                "Break circular dependencies by introducing interfaces or event-driven patterns"
            )

        # Critical service recommendations
        critical_count = report.critical_service_count
        if critical_count > 0:
            report.recommendations.append("Add redundancy and failover for critical services")
            report.recommendations.append(
                "Implement circuit breakers for dependencies on critical services"
            )

        # Bottleneck recommendations
        if report.bottlenecks:
            top_bottlenecks = report.get_top_bottlenecks(1)
            if top_bottlenecks and top_bottlenecks[0][1] > 0.5:
                report.recommendations.append(
                    f"Consider scaling '{top_bottlenecks[0][0]}' horizontally "
                    "to reduce bottleneck risk"
                )

        # General recommendations
        if report.service_count > 20:
            report.recommendations.append(
                "Consider organizing services into domain-based modules or bounded contexts"
            )
