"""Code scaffolding utilities."""

from pathlib import Path


class Scaffolder:
    """Code scaffolding generator.

    Examples:
        >>> scaffolder = Scaffolder()
        >>> scaffolder.create_service("UserService")
        >>> scaffolder.create_repository("UserRepository")
    """

    def __init__(self, base_path: Path | None = None):
        """Initialize Scaffolder.

        Args:
            base_path: Base path for scaffolding (defaults to current directory)
        """
        self.base_path = base_path or Path.cwd()

    def create_service(self, name: str) -> None:
        """Create a new service class.

        Args:
            name: Service name
        """
        content = f'''"""
{name} service.

Implements business logic for {name.lower().replace("service", "")}.
"""

from typing import Optional


class {name}:
    """
    {name} business logic.

    Examples:
        >>> service = {name}()
        >>> result = await service.process()
    """

    def __init__(self):
        pass

    async def process(self):
        """Process business logic."""
        pass
'''

        filename = self.base_path / f"{self._to_snake_case(name)}.py"
        filename.write_text(content)
        print(f"Created service: {filename}")

    def create_repository(self, name: str) -> None:
        """Create a new repository class.

        Args:
            name: Repository name
        """
        entity_name = name.replace("Repository", "")

        content = f'''"""
{name} repository.

Implements data access for {entity_name}.
"""

from typing import List, Optional
from unistax.repository import Repository


class {name}(Repository[{entity_name}]):
    """
    Repository for {entity_name} entities.

    Examples:
        >>> repo = {name}()
        >>> entity = await repo.get(123)
    """

    async def find_by_name(self, name: str) -> Optional[{entity_name}]:
        """Find entity by name."""
        return await self.find_one(name=name)
'''

        filename = self.base_path / f"{self._to_snake_case(name)}.py"
        filename.write_text(content)
        print(f"Created repository: {filename}")

    def _to_snake_case(self, name: str) -> str:
        """Convert CamelCase to snake_case."""
        import re

        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
