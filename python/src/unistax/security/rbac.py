"""Role-Based Access Control."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Permission:
    """Permission definition."""

    name: str
    resource: str
    action: str

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.resource}:{self.action}"


@dataclass
class Role:
    """Role with permissions."""

    name: str
    permissions: set[str] = field(default_factory=set)

    def has_permission(self, permission: str) -> bool:
        """Check if role has permission."""
        return permission in self.permissions or "*" in self.permissions


class RBAC:
    """Role-Based Access Control system.

    Examples:
        >>> rbac = RBAC()
        >>> rbac.define_role("admin", ["users:read", "users:write"])
        >>> rbac.define_role("user", ["users:read"])
        >>>
        >>> @rbac.requires("users:write")
        ... async def update_user():
        ...     pass
    """

    def __init__(self) -> None:
        """Initialize RBAC."""
        self._roles: dict[str, Role] = {}

    def define_role(self, role_name: str, permissions: list[str]) -> None:
        """Define a role with permissions.

        Args:
            role_name: Role name
            permissions: List of permission strings
        """
        self._roles[role_name] = Role(role_name, set(permissions))

    def has_permission(self, role_name: str, permission: str) -> bool:
        """Check if role has permission.

        Args:
            role_name: Role name
            permission: Permission string

        Returns:
            True if role has permission
        """
        role = self._roles.get(role_name)
        return role.has_permission(permission) if role else False

    def requires(self, permission: str) -> Any:
        """Decorator to require permission.

        Args:
            permission: Required permission

        Returns:
            Decorator function
        """

        def decorator(func: Any) -> Any:
            from functools import wraps

            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                # In production, get user role from context/request
                # user_role = get_current_user_role()
                # if not self.has_permission(user_role, permission):
                #     raise PermissionDenied()

                return await func(*args, **kwargs)

            return wrapper

        return decorator
