"""API router wrapper."""

from collections.abc import Callable
from typing import Any

from fastapi import APIRouter as FastAPIRouter  # type: ignore[import-not-found]


class APIRouter:
    """API router wrapper."""

    def __init__(
        self,
        prefix: str = "",
        tags: list[str] | None = None,
        dependencies: list[Any] | None = None,
    ) -> None:
        """Initialize API router.

        Args:
            prefix: Router prefix
            tags: Router tags
            dependencies: Router dependencies
        """
        self.router = FastAPIRouter(
            prefix=prefix,
            tags=tags or [],
            dependencies=dependencies or [],
        )

    def get(self, path: str, **kwargs: Any) -> Callable[..., Any]:
        """Register GET endpoint.

        Args:
            path: Endpoint path
            **kwargs: Additional arguments

        Returns:
            Route decorator
        """
        return self.router.get(path, **kwargs)  # type: ignore[no-any-return]

    def post(self, path: str, **kwargs: Any) -> Callable[..., Any]:
        """Register POST endpoint.

        Args:
            path: Endpoint path
            **kwargs: Additional arguments

        Returns:
            Route decorator
        """
        return self.router.post(path, **kwargs)  # type: ignore[no-any-return]

    def put(self, path: str, **kwargs: Any) -> Callable[..., Any]:
        """Register PUT endpoint.

        Args:
            path: Endpoint path
            **kwargs: Additional arguments

        Returns:
            Route decorator
        """
        return self.router.put(path, **kwargs)  # type: ignore[no-any-return]

    def patch(self, path: str, **kwargs: Any) -> Callable[..., Any]:
        """Register PATCH endpoint.

        Args:
            path: Endpoint path
            **kwargs: Additional arguments

        Returns:
            Route decorator
        """
        return self.router.patch(path, **kwargs)  # type: ignore[no-any-return]

    def delete(self, path: str, **kwargs: Any) -> Callable[..., Any]:
        """Register DELETE endpoint.

        Args:
            path: Endpoint path
            **kwargs: Additional arguments

        Returns:
            Route decorator
        """
        return self.router.delete(path, **kwargs)  # type: ignore[no-any-return]

    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        methods: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Add API route.

        Args:
            path: Endpoint path
            endpoint: Endpoint function
            methods: HTTP methods
            **kwargs: Additional arguments
        """
        self.router.add_api_route(
            path,
            endpoint,
            methods=methods or ["GET"],
            **kwargs,
        )
