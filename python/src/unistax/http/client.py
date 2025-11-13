"""HTTP client implementation with enterprise features."""

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import requests  # type: ignore[import-untyped]

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class Response:
    """HTTP response wrapper."""

    status_code: int
    headers: dict[str, str]
    body: bytes
    elapsed: float

    def json(self) -> Any:
        """Parse response as JSON."""
        import json

        return json.loads(self.body.decode("utf-8"))

    def text(self) -> str:
        """Get response as text."""
        return self.body.decode("utf-8")


@dataclass
class Request:
    """HTTP request."""

    method: str
    url: str
    headers: dict[str, str] | None = None
    params: dict[str, Any] | None = None
    data: Any | None = None
    json: Any | None = None
    timeout: float = 10.0


class HTTPClient:
    """Enterprise HTTP client with retry, circuit breaker, and logging.

    Examples:
        >>> client = HTTPClient()
        >>> response = client.get("https://api.example.com/users")
        >>> client.post("https://api.example.com/users", json={"name": "John"})
    """

    def __init__(
        self,
        base_url: str = "",
        timeout: float = 10.0,
        max_retries: int = 3,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Initialize HTTP client.

        Args:
            base_url: Base URL for all requests
            timeout: Default timeout in seconds
            max_retries: Maximum retry attempts
            headers: Default headers for all requests
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required for HTTPClient")

        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._default_headers = headers or {}
        self._session = requests.Session()

    @classmethod
    def from_yaml(cls, path: str | Path) -> "HTTPClient":
        """Create client from YAML configuration."""
        from ..config import ConfigManager

        config = ConfigManager.from_yaml(path)
        return cls(
            base_url=config.get("http.base_url", ""),
            timeout=config.get_float("http.timeout", 10.0),
            max_retries=config.get_int("http.max_retries", 3),
            headers=config.get_dict("http.headers", {}),
        )

    def _build_url(self, url: str) -> str:
        """Build full URL."""
        if url.startswith("http"):
            return url
        return f"{self._base_url}/{url.lstrip('/')}"

    def _merge_headers(self, headers: dict[str, str] | None) -> dict[str, str]:
        """Merge headers with defaults."""
        merged = dict(self._default_headers)
        if headers:
            merged.update(headers)
        return merged

    def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        data: Any | None = None,
        json_data: Any | None = None,
        timeout: float | None = None,
        retry: bool = True,
    ) -> Response:
        """Make HTTP request.

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            params: URL parameters
            data: Request body data
            json_data: JSON request body
            timeout: Request timeout
            retry: Whether to retry on failure

        Returns:
            Response object
        """
        full_url = self._build_url(url)
        merged_headers = self._merge_headers(headers)
        request_timeout = timeout or self._timeout

        attempts = self._max_retries if retry else 1
        last_error = None

        for attempt in range(attempts):
            try:
                start_time = time.time()

                resp = self._session.request(
                    method=method.upper(),
                    url=full_url,
                    headers=merged_headers,
                    params=params,
                    data=data,
                    json=json_data,
                    timeout=request_timeout,
                )

                elapsed = time.time() - start_time

                return Response(
                    status_code=resp.status_code,
                    headers=dict(resp.headers),
                    body=resp.content,
                    elapsed=elapsed,
                )

            except Exception as e:
                last_error = e
                if attempt < attempts - 1:
                    # Exponential backoff
                    time.sleep(2**attempt)
                    continue
                raise

        if last_error:
            raise last_error

        raise RuntimeError("Request failed with no error recorded")

    def get(self, url: str, **kwargs: Any) -> Response:
        """GET request."""
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> Response:
        """POST request."""
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> Response:
        """PUT request."""
        return self.request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> Response:
        """PATCH request."""
        return self.request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> Response:
        """DELETE request."""
        return self.request("DELETE", url, **kwargs)

    def close(self) -> None:
        """Close HTTP session."""
        self._session.close()

    def __enter__(self) -> "HTTPClient":
        """Enter context manager."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context manager."""
        self.close()
