"""Dependency analysis module for service dependency graph analysis.

Provides high-level analysis tools for:
- Circular dependency detection
- Blast radius calculation
- Service criticality scoring
- Bottleneck identification
- Impact analysis
"""

from unistax.analysis.dependency_analyzer import (
    AnalysisReport,
    AnalysisType,
    DependencyAnalyzer,
)
from unistax.analysis.impact_analyzer import (
    ChangeImpact,
    ImpactAnalyzer,
    ImpactReport,
)

__all__ = [
    # Core analyzer
    "DependencyAnalyzer",
    "AnalysisReport",
    "AnalysisType",
    # Impact analysis
    "ImpactAnalyzer",
    "ImpactReport",
    "ChangeImpact",
]
