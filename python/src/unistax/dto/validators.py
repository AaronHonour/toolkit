"""DTO validation utilities."""

from typing import Any

from pydantic import ValidationError as PydanticValidationError  # type: ignore[import-not-found]

# Re-export Pydantic ValidationError
ValidationError = PydanticValidationError


def validate_dto(dto_class: type, data: Any) -> Any:
    """Validate data against DTO class.

    Args:
        dto_class: DTO class
        data: Data to validate

    Returns:
        Validated DTO instance

    Raises:
        ValidationError: If validation fails
    """
    if isinstance(data, dict):
        return dto_class(**data)
    elif isinstance(data, str):
        return dto_class.model_validate_json(data)  # type: ignore[attr-defined]
    else:
        return dto_class.model_validate(data)  # type: ignore[attr-defined]
