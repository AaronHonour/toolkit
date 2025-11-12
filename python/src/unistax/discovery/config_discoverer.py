"""Configuration-based discovery for detecting dependencies from config files."""

import re
from pathlib import Path
from typing import Any

from unistax.discovery.base import (
    DependencyDiscoverer,
    DiscoveryResult,
    DiscoverySource,
)


class ConfigurationDiscoverer(DependencyDiscoverer):
    """Discovers dependencies from configuration files and environment variables."""

    def __init__(
        self,
        service_name: str,
        config_data: dict[str, Any] | None = None,
        env_vars: dict[str, str] | None = None,
        config_files: list[Path] | None = None,
    ) -> None:
        """Initialize configuration discoverer.

        Args:
            service_name: Name of the service being analyzed
            config_data: Parsed configuration data
            env_vars: Environment variables
            config_files: Paths to configuration files to parse
        """
        super().__init__(service_name)
        self.config_data = config_data or {}
        self.env_vars = env_vars or {}
        self.config_files = config_files or []

    async def discover(self) -> list[DiscoveryResult]:
        """Discover dependencies from configuration.

        Returns:
            List of discovered dependencies
        """
        results: list[DiscoveryResult] = []

        # Discover from structured config data
        results.extend(self._discover_from_config_data())

        # Discover from environment variables
        results.extend(self._discover_from_env_vars())

        # Update cache
        self._discovered.update(results)

        return results

    def _discover_from_config_data(self) -> list[DiscoveryResult]:
        """Extract dependencies from configuration data."""
        results: list[DiscoveryResult] = []

        # Common service configuration patterns
        service_keys = [
            "services", "dependencies", "upstreams", "backends",
            "external_services", "integrations",
        ]

        for key in service_keys:
            if key in self.config_data:
                services_config = self.config_data[key]

                if isinstance(services_config, dict):
                    # Handle dict of services
                    for svc_name, svc_config in services_config.items():
                        result = self._create_dependency_from_config(
                            svc_name,
                            svc_config,
                        )
                        if result:
                            results.append(result)

                elif isinstance(services_config, list):
                    # Handle list of service names or configs
                    for svc in services_config:
                        if isinstance(svc, str):
                            result = DiscoveryResult(
                                source_service=self.service_name,
                                target_service=svc,
                                dependency_type="api_call",
                                source=DiscoverySource.CONFIGURATION,
                                confidence=0.8,
                                metadata={"declared_in": key},
                            )
                            results.append(result)
                        elif isinstance(svc, dict):
                            svc_name = svc.get("name") or svc.get("service")
                            if svc_name:
                                result = self._create_dependency_from_config(
                                    svc_name,
                                    svc,
                                )
                                if result:
                                    results.append(result)

        return results

    def _discover_from_env_vars(self) -> list[DiscoveryResult]:
        """Extract dependencies from environment variables."""
        results: list[DiscoveryResult] = []

        # Patterns for service URLs in env vars
        url_pattern = re.compile(
            r'(?:https?://)?([a-z0-9\-]+(?:\.[a-z0-9\-]+)*):?(\d+)?',
            re.IGNORECASE,
        )

        # Common env var patterns
        service_env_patterns = [
            r'.*_SERVICE_URL',
            r'.*_API_URL',
            r'.*_ENDPOINT',
            r'.*_HOST',
        ]

        for env_var, value in self.env_vars.items():
            # Check if env var matches service patterns
            is_service_var = any(
                re.match(pattern, env_var)
                for pattern in service_env_patterns
            )

            if is_service_var:
                # Try to extract service name from URL
                match = url_pattern.search(value)
                if match:
                    target_service = match.group(1)

                    # Filter out common non-service domains
                    if self._is_likely_service(target_service):
                        result = DiscoveryResult(
                            source_service=self.service_name,
                            target_service=target_service,
                            dependency_type="api_call",
                            source=DiscoverySource.CONFIGURATION,
                            confidence=0.75,
                            metadata={
                                "env_var": env_var,
                                "url": value,
                            },
                        )
                        results.append(result)

        return results

    def _create_dependency_from_config(
        self,
        target_service: str,
        config: Any,
    ) -> DiscoveryResult | None:
        """Create a dependency result from service configuration."""
        if not target_service:
            return None

        # Determine dependency type from config
        dep_type = "api_call"  # Default
        metadata: dict[str, Any] = {}

        if isinstance(config, dict):
            # Check for explicit type
            if "type" in config:
                dep_type = config["type"]

            # Extract useful metadata
            metadata = {
                "url": config.get("url"),
                "host": config.get("host"),
                "port": config.get("port"),
                "protocol": config.get("protocol"),
            }

            # Infer type from config keys
            if any(k in config for k in ["database", "db_name", "connection_string"]):
                dep_type = "database"
            elif any(k in config for k in ["topic", "queue", "channel"]):
                dep_type = "message_queue"
            elif any(k in config for k in ["cache", "redis", "memcached"]):
                dep_type = "cache"

        return DiscoveryResult(
            source_service=self.service_name,
            target_service=target_service,
            dependency_type=dep_type,
            source=DiscoverySource.CONFIGURATION,
            confidence=0.9,
            metadata=metadata,
        )

    def _is_likely_service(self, name: str) -> bool:
        """Check if a name is likely a service (not a public domain)."""
        # Exclude common public domains
        excluded = {
            "localhost", "example.com", "google.com", "amazonaws.com",
            "cloudflare.com", "cdn", "static", "www",
        }

        name_lower = name.lower()
        return not any(excl in name_lower for excl in excluded)
