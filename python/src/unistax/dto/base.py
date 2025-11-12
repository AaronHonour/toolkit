"""Base DTO classes."""

from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class DTOConfig(ConfigDict):
    """DTO configuration."""

    from_attributes = True
    validate_assignment = True
    arbitrary_types_allowed = True
    str_strip_whitespace = True


class BaseDTO(BaseModel):
    """Base Data Transfer Object."""

    model_config = DTOConfig

    def to_dict(self, exclude_none: bool = False, exclude_unset: bool = False) -> dict[str, Any]:
        """Convert DTO to dictionary.

        Args:
            exclude_none: Exclude None values
            exclude_unset: Exclude unset values

        Returns:
            Dictionary representation
        """
        return self.model_dump(exclude_none=exclude_none, exclude_unset=exclude_unset)

    def to_json(self, exclude_none: bool = False, exclude_unset: bool = False) -> str:
        """Convert DTO to JSON string.

        Args:
            exclude_none: Exclude None values
            exclude_unset: Exclude unset values

        Returns:
            JSON string
        """
        return self.model_dump_json(exclude_none=exclude_none, exclude_unset=exclude_unset)

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        """Create DTO from dictionary.

        Args:
            data: Dictionary data

        Returns:
            DTO instance
        """
        return cls(**data)

    @classmethod
    def from_json(cls: type[T], json_str: str) -> T:
        """Create DTO from JSON string.

        Args:
            json_str: JSON string

        Returns:
            DTO instance
        """
        return cls.model_validate_json(json_str)

    @classmethod
    def from_orm(cls: type[T], obj: Any) -> T:
        """Create DTO from ORM model.

        Args:
            obj: ORM model instance

        Returns:
            DTO instance
        """
        return cls.model_validate(obj)
