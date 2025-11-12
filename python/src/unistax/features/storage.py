"""Feature storage backends."""

from abc import ABC, abstractmethod

from unistax.features.manager import Feature


class FeatureStorage(ABC):
    """Base feature storage interface."""

    @abstractmethod
    def get(self, name: str) -> Feature | None:
        """Get feature by name."""
        pass

    @abstractmethod
    def save(self, feature: Feature):
        """Save feature."""
        pass

    @abstractmethod
    def delete(self, name: str):
        """Delete feature."""
        pass

    @abstractmethod
    def list_all(self) -> dict[str, Feature]:
        """List all features."""
        pass


class InMemoryFeatureStorage(FeatureStorage):
    """In-memory feature storage."""

    def __init__(self):
        """Initialize storage."""
        self.features: dict[str, Feature] = {}

    def get(self, name: str) -> Feature | None:
        """Get feature from memory."""
        return self.features.get(name)

    def save(self, feature: Feature):
        """Save feature to memory."""
        self.features[feature.name] = feature

    def delete(self, name: str):
        """Delete feature from memory."""
        if name in self.features:
            del self.features[name]

    def list_all(self) -> dict[str, Feature]:
        """List all features."""
        return self.features.copy()
