"""API call discovery for detecting service-to-service HTTP dependencies."""

import re
from typing import List, Optional, Dict, Any
from unistax.discovery.base import (
    DependencyDiscoverer,
    DiscoveryResult,
    DiscoverySource,
)


class APICallDiscoverer(DependencyDiscoverer):
    """Discovers API call dependencies from various sources."""

    def __init__(
        self,
        service_name: str,
        trace_data: Optional[List[Dict[str, Any]]] = None,
        log_data: Optional[List[str]] = None,
    ) -> None:
        """Initialize API call discoverer.

        Args:
            service_name: Name of the service being analyzed
            trace_data: Optional trace/span data from distributed tracing
            log_data: Optional log lines to parse for HTTP calls
        """
        super().__init__(service_name)
        self.trace_data = trace_data or []
        self.log_data = log_data or []

    async def discover(self) -> List[DiscoveryResult]:
        """Discover API call dependencies.

        Returns:
            List of discovered API dependencies
        """
        results: List[DiscoveryResult] = []

        # Discover from traces
        results.extend(self._discover_from_traces())

        # Discover from logs
        results.extend(self._discover_from_logs())

        # Update cache
        self._discovered.update(results)

        return results

    def _discover_from_traces(self) -> List[DiscoveryResult]:
        """Extract dependencies from distributed trace data."""
        results: List[DiscoveryResult] = []

        for trace in self.trace_data:
            # Extract service name from trace metadata
            target_service = self._extract_service_from_trace(trace)

            if target_service and target_service != self.service_name:
                result = DiscoveryResult(
                    source_service=self.service_name,
                    target_service=target_service,
                    dependency_type="api_call",
                    source=DiscoverySource.RUNTIME_TRACE,
                    confidence=0.95,  # High confidence from traces
                    metadata={
                        "method": trace.get("http.method"),
                        "endpoint": trace.get("http.url"),
                        "status_code": trace.get("http.status_code"),
                    },
                )
                results.append(result)

        return results

    def _discover_from_logs(self) -> List[DiscoveryResult]:
        """Extract dependencies from log analysis."""
        results: List[DiscoveryResult] = []

        # Patterns to match HTTP calls in logs
        patterns = [
            # Common HTTP client patterns
            r"(?:GET|POST|PUT|DELETE|PATCH)\s+(?:https?://)?([a-z0-9\-]+(?:\.[a-z0-9\-]+)*)",
            # Service name patterns
            r"calling service[:\s]+([a-z0-9\-]+)",
            r"request to[:\s]+([a-z0-9\-]+)",
        ]

        for log_line in self.log_data:
            for pattern in patterns:
                matches = re.finditer(pattern, log_line, re.IGNORECASE)
                for match in matches:
                    target_service = match.group(1)

                    # Filter out common non-service domains
                    if self._is_likely_service(target_service):
                        result = DiscoveryResult(
                            source_service=self.service_name,
                            target_service=target_service,
                            dependency_type="api_call",
                            source=DiscoverySource.LOG_ANALYSIS,
                            confidence=0.7,  # Medium confidence from logs
                            metadata={"log_line": log_line[:200]},
                        )
                        results.append(result)

        return results

    def _extract_service_from_trace(self, trace: Dict[str, Any]) -> Optional[str]:
        """Extract service name from trace metadata."""
        # Try various common fields
        service_fields = [
            "service.name",
            "peer.service",
            "http.host",
            "net.peer.name",
        ]

        for field in service_fields:
            if field in trace:
                return str(trace[field])

        return None

    def _is_likely_service(self, name: str) -> bool:
        """Check if a name is likely a service (not a public domain)."""
        # Exclude common public domains
        excluded = {
            "localhost", "example.com", "google.com", "amazonaws.com",
            "cloudflare.com", "cdn", "static",
        }

        name_lower = name.lower()
        return not any(excl in name_lower for excl in excluded)
