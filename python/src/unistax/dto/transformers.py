"""DTO transformers and field mapping."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

T = TypeVar("T")
U = TypeVar("U")


@dataclass
class FieldMapper:
    """Field mapping configuration."""

    source_field: str
    target_field: str
    transform: Callable[[Any], Any] | None = None


class DTOTransformer:
    """Transform between DTOs and models."""

    def __init__(self):
        """Initialize transformer."""
        self.mappings: dict[tuple, list[FieldMapper]] = {}

    def add_mapping(
        self,
        source_type: type,
        target_type: type,
        field_mapper: FieldMapper,
    ):
        """Add field mapping.

        Args:
            source_type: Source type
            target_type: Target type
            field_mapper: Field mapper
        """
        key = (source_type, target_type)
        if key not in self.mappings:
            self.mappings[key] = []
        self.mappings[key].append(field_mapper)

    def transform(
        self,
        source: Any,
        target_type: type[T],
    ) -> T:
        """Transform source to target type.

        Args:
            source: Source object
            target_type: Target type

        Returns:
            Transformed object
        """
        source_type = type(source)
        key = (source_type, target_type)

        if key not in self.mappings:
            # No custom mappings, use default
            if hasattr(target_type, "from_orm"):
                return target_type.from_orm(source)
            elif hasattr(source, "to_dict"):
                return target_type(**source.to_dict())
            else:
                return target_type(**source.__dict__)

        # Apply custom mappings
        data = {}
        for mapper in self.mappings[key]:
            value = getattr(source, mapper.source_field, None)
            if mapper.transform:
                value = mapper.transform(value)
            data[mapper.target_field] = value

        return target_type(**data)
