"""Database connection discovery for detecting service-to-database dependencies."""

import re
from typing import Any
from urllib.parse import urlparse

from unistax.discovery.base import (
    DependencyDiscoverer,
    DiscoveryResult,
    DiscoverySource,
)


class DatabaseConnectionDiscoverer(DependencyDiscoverer):
    """Discovers database connection dependencies."""

    def __init__(
        self,
        service_name: str,
        connection_strings: list[str] | None = None,
        config_data: dict[str, Any] | None = None,
    ) -> None:
        """Initialize database connection discoverer.

        Args:
            service_name: Name of the service being analyzed
            connection_strings: List of database connection strings
            config_data: Configuration data that may contain DB settings
        """
        super().__init__(service_name)
        self.connection_strings = connection_strings or []
        self.config_data = config_data or {}

    async def discover(self) -> list[DiscoveryResult]:
        """Discover database dependencies.

        Returns:
            List of discovered database dependencies
        """
        results: list[DiscoveryResult] = []

        # Discover from connection strings
        results.extend(self._discover_from_connection_strings())

        # Discover from configuration
        results.extend(self._discover_from_config())

        # Update cache
        self._discovered.update(results)

        return results

    def _discover_from_connection_strings(self) -> list[DiscoveryResult]:
        """Extract database dependencies from connection strings."""
        results: list[DiscoveryResult] = []

        for conn_str in self.connection_strings:
            db_info = self._parse_connection_string(conn_str)

            if db_info:
                # Use database type + host as service name
                target_service = f"{db_info['type']}-{db_info['host']}"

                result = DiscoveryResult(
                    source_service=self.service_name,
                    target_service=target_service,
                    dependency_type="database",
                    source=DiscoverySource.DATABASE,
                    confidence=1.0,  # High confidence from connection strings
                    metadata=db_info,
                )
                results.append(result)

        return results

    def _discover_from_config(self) -> list[DiscoveryResult]:
        """Extract database dependencies from configuration."""
        results: list[DiscoveryResult] = []

        # Common database config keys
        db_keys = [
            "database", "db", "postgres", "postgresql", "mysql",
            "mongodb", "redis", "elasticsearch", "cassandra",
        ]

        for key in db_keys:
            if key in self.config_data:
                db_config = self.config_data[key]

                # Handle dict config
                if isinstance(db_config, dict):
                    host = db_config.get("host", "unknown")
                    db_type = db_config.get("type", key)
                    port = db_config.get("port", "")

                    target_service = f"{db_type}-{host}"
                    if port:
                        target_service += f":{port}"

                    result = DiscoveryResult(
                        source_service=self.service_name,
                        target_service=target_service,
                        dependency_type="database",
                        source=DiscoverySource.CONFIGURATION,
                        confidence=0.9,
                        metadata={
                            "type": db_type,
                            "host": host,
                            "port": port,
                            "database": db_config.get("database"),
                        },
                    )
                    results.append(result)

        return results

    def _parse_connection_string(self, conn_str: str) -> dict[str, Any] | None:
        """Parse a database connection string.

        Supports common formats:
        - postgresql://user:pass@host:port/dbname
        - mysql://host:port/dbname
        - mongodb://host:port/dbname
        - redis://host:port/db
        """
        try:
            # Try URL parsing first
            parsed = urlparse(conn_str)

            if parsed.scheme:
                return {
                    "type": parsed.scheme,
                    "host": parsed.hostname or "localhost",
                    "port": parsed.port or self._get_default_port(parsed.scheme),
                    "database": parsed.path.lstrip("/") if parsed.path else None,
                    "username": parsed.username,
                }

            # Try key=value format (e.g., "host=localhost port=5432 dbname=mydb")
            kv_pattern = r'(\w+)=([^\s]+)'
            matches = dict(re.findall(kv_pattern, conn_str))

            if matches:
                db_type = matches.get("dbtype", "postgresql")
                return {
                    "type": db_type,
                    "host": matches.get("host", "localhost"),
                    "port": matches.get("port", self._get_default_port(db_type)),
                    "database": matches.get("dbname") or matches.get("database"),
                    "username": matches.get("user") or matches.get("username"),
                }

        except Exception:
            pass

        return None

    def _get_default_port(self, db_type: str) -> str:
        """Get default port for database type."""
        default_ports = {
            "postgresql": "5432",
            "postgres": "5432",
            "mysql": "3306",
            "mongodb": "27017",
            "mongo": "27017",
            "redis": "6379",
            "elasticsearch": "9200",
            "cassandra": "9042",
        }
        return default_ports.get(db_type.lower(), "")
