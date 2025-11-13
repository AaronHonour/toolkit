"""Impact analysis for assessing effects of changes and failures."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from unistax.algorithms.graph import BlastRadiusResult, calculate_blast_radius
from unistax.graph.structures import ServiceDependencyGraph


class ChangeType(str, Enum):
    """Type of change being analyzed."""

    SERVICE_FAILURE = "service_failure"
    SERVICE_DEPLOYMENT = "service_deployment"
    SERVICE_DEGRADATION = "service_degradation"
    DEPENDENCY_CHANGE = "dependency_change"
    BREAKING_CHANGE = "breaking_change"


@dataclass
class ChangeImpact:
    """Impact of a change on a single service."""

    service: str
    impact_level: int  # Distance from change source (0 = direct)
    impact_type: str  # "direct", "indirect", "cascading"
    probability: float  # 0.0 to 1.0
    estimated_downtime_minutes: float | None = None
    mitigation: str | None = None


@dataclass
class ImpactReport:
    """Comprehensive impact analysis report."""

    change_type: ChangeType
    source_service: str
    generated_at: datetime = field(default_factory=datetime.utcnow)

    # Impact results
    total_affected: int = 0
    direct_impact: list[ChangeImpact] = field(default_factory=list)
    indirect_impact: list[ChangeImpact] = field(default_factory=list)
    cascading_impact: list[ChangeImpact] = field(default_factory=list)

    # Risk assessment
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
    blast_radius: BlastRadiusResult | None = None

    # Recommendations
    pre_change_actions: list[str] = field(default_factory=list)
    monitoring_required: list[str] = field(default_factory=list)
    rollback_plan: str | None = None

    @property
    def affected_services(self) -> set[str]:
        """Get all affected service names."""
        services = set()
        for impact in self.direct_impact + self.indirect_impact + self.cascading_impact:
            services.add(impact.service)
        return services


class ImpactAnalyzer:
    """Analyzes the impact of changes and failures on service dependencies."""

    def __init__(self, graph: ServiceDependencyGraph) -> None:
        """Initialize impact analyzer.

        Args:
            graph: Service dependency graph to analyze
        """
        self.graph = graph

    def analyze_service_failure(
        self,
        service_name: str,
        failure_probability: float = 1.0,
    ) -> ImpactReport:
        """Analyze the impact of a service failure.

        Args:
            service_name: Service that fails
            failure_probability: Probability of failure (0.0 to 1.0)

        Returns:
            Impact report with affected services and recommendations
        """
        report = ImpactReport(
            change_type=ChangeType.SERVICE_FAILURE,
            source_service=service_name,
        )

        # Calculate blast radius
        adj_list = self._build_adj_list()
        blast_result = calculate_blast_radius(adj_list, service_name)
        report.blast_radius = blast_result

        # Categorize impacts by level
        for affected_service, level in blast_result.impact_levels.items():
            if affected_service == service_name:
                continue  # Skip the failed service itself

            # Determine impact type and probability
            if level == 1:
                impact_type = "direct"
                probability = failure_probability * 0.9  # High propagation
            elif level == 2:
                impact_type = "indirect"
                probability = failure_probability * 0.6  # Medium propagation
            else:
                impact_type = "cascading"
                probability = failure_probability * 0.3  # Lower propagation

            impact = ChangeImpact(
                service=affected_service,
                impact_level=level,
                impact_type=impact_type,
                probability=probability,
            )

            # Add to appropriate category
            if impact_type == "direct":
                report.direct_impact.append(impact)
            elif impact_type == "indirect":
                report.indirect_impact.append(impact)
            else:
                report.cascading_impact.append(impact)

        report.total_affected = blast_result.total_affected

        # Assess risk level
        report.risk_level = self._assess_risk_level(report)

        # Generate recommendations
        self._generate_failure_recommendations(report)

        return report

    def analyze_deployment_impact(
        self,
        service_name: str,
        is_breaking_change: bool = False,
        expected_downtime_minutes: float = 0.0,
    ) -> ImpactReport:
        """Analyze the impact of deploying a service.

        Args:
            service_name: Service being deployed
            is_breaking_change: Whether deployment includes breaking changes
            expected_downtime_minutes: Expected downtime during deployment

        Returns:
            Impact report for deployment
        """
        change_type = (
            ChangeType.BREAKING_CHANGE if is_breaking_change else ChangeType.SERVICE_DEPLOYMENT
        )

        report = ImpactReport(
            change_type=change_type,
            source_service=service_name,
        )

        # Get downstream services (those that depend on this service)
        downstream = self.graph.get_downstream_services(service_name)

        for dependent in downstream:
            # Direct impact on all downstream services
            impact_prob = 1.0 if is_breaking_change else 0.3

            impact = ChangeImpact(
                service=dependent,
                impact_level=1,
                impact_type="direct",
                probability=impact_prob,
                estimated_downtime_minutes=expected_downtime_minutes if is_breaking_change else 0,
                mitigation="Update client code" if is_breaking_change else "Monitor for errors",
            )
            report.direct_impact.append(impact)

        report.total_affected = len(downstream)

        # Assess risk
        report.risk_level = self._assess_deployment_risk(
            report,
            is_breaking_change,
            expected_downtime_minutes,
        )

        # Generate recommendations
        self._generate_deployment_recommendations(report, is_breaking_change)

        return report

    def analyze_degradation_impact(
        self,
        service_name: str,
        degradation_factor: float = 0.5,
    ) -> ImpactReport:
        """Analyze the impact of service degradation (slowdown, partial failure).

        Args:
            service_name: Service experiencing degradation
            degradation_factor: Severity of degradation (0.0 = complete failure, 1.0 = normal)

        Returns:
            Impact report for degradation
        """
        report = ImpactReport(
            change_type=ChangeType.SERVICE_DEGRADATION,
            source_service=service_name,
        )

        # Get downstream services
        downstream = self.graph.get_downstream_services(service_name)

        for dependent in downstream:
            # Impact depends on degradation factor
            impact = ChangeImpact(
                service=dependent,
                impact_level=1,
                impact_type="direct",
                probability=1.0 - degradation_factor,  # Worse degradation = higher probability
                mitigation="Implement circuit breaker or timeout",
            )
            report.direct_impact.append(impact)

        report.total_affected = len(downstream)
        report.risk_level = self._assess_degradation_risk(report, degradation_factor)

        # Generate recommendations
        self._generate_degradation_recommendations(report)

        return report

    def _build_adj_list(self) -> dict[str, set[str]]:
        """Build adjacency list from graph."""
        adj_list: dict[str, set[str]] = {}
        underlying = self.graph.get_underlying_graph()

        for service in self.graph.get_all_services():
            adj_list[service.name] = underlying.get_successors(service.name)

        return adj_list

    def _assess_risk_level(self, report: ImpactReport) -> str:
        """Assess risk level based on impact scope."""
        total = report.total_affected

        if total == 0:
            return "LOW"
        elif total <= 2:
            return "MEDIUM"
        elif total <= 5:
            return "HIGH"
        else:
            return "CRITICAL"

    def _assess_deployment_risk(
        self,
        report: ImpactReport,
        is_breaking: bool,
        downtime: float,
    ) -> str:
        """Assess deployment risk level."""
        if is_breaking and report.total_affected > 3:
            return "CRITICAL"
        elif is_breaking or downtime > 5:
            return "HIGH"
        elif report.total_affected > 2:
            return "MEDIUM"
        else:
            return "LOW"

    def _assess_degradation_risk(self, report: ImpactReport, factor: float) -> str:
        """Assess degradation risk level."""
        if factor < 0.3 and report.total_affected > 2:
            return "CRITICAL"
        elif factor < 0.5:
            return "HIGH"
        elif report.total_affected > 2:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_failure_recommendations(self, report: ImpactReport) -> None:
        """Generate recommendations for service failure."""
        report.pre_change_actions.append(
            "Verify circuit breakers are configured for dependent services"
        )
        report.pre_change_actions.append("Ensure monitoring alerts are active")

        if report.total_affected > 0:
            report.monitoring_required.append("Monitor error rates in dependent services")
            report.monitoring_required.append("Watch for cascading failures")

        if report.risk_level in ("HIGH", "CRITICAL"):
            report.pre_change_actions.append("Consider implementing fallback mechanisms")
            report.rollback_plan = "Restore service from backup or previous version"

    def _generate_deployment_recommendations(
        self,
        report: ImpactReport,
        is_breaking: bool,
    ) -> None:
        """Generate recommendations for deployment."""
        report.pre_change_actions.append("Deploy to staging environment first")

        if is_breaking:
            report.pre_change_actions.append("Coordinate with owners of dependent services")
            report.pre_change_actions.append(
                "Version API and maintain backward compatibility temporarily"
            )
            report.rollback_plan = "Rollback to previous version with compatible API"
        else:
            report.pre_change_actions.append("Use blue-green or canary deployment strategy")
            report.rollback_plan = "Quick rollback to previous version"

        report.monitoring_required.append("Monitor error rates and latency")
        report.monitoring_required.append("Check dependent service health")

    def _generate_degradation_recommendations(self, report: ImpactReport) -> None:
        """Generate recommendations for degradation."""
        report.pre_change_actions.append("Verify timeout configurations in dependent services")
        report.monitoring_required.append("Monitor latency metrics")
        report.monitoring_required.append("Watch for timeout errors in dependents")

        if report.risk_level in ("HIGH", "CRITICAL"):
            report.pre_change_actions.append(
                "Enable circuit breakers to prevent cascading slowness"
            )
