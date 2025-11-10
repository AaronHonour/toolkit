"""Validation utilities."""

import re
from typing import Any, Callable, Dict, List, Optional


class ValidationRules:
    """Collection of validation rules."""

    @staticmethod
    def email(value: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, value))

    @staticmethod
    def url(value: str) -> bool:
        """Validate URL format."""
        pattern = r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b'
        return bool(re.match(pattern, value))

    @staticmethod
    def phone(value: str) -> bool:
        """Validate phone number format."""
        pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(pattern, value))

    @staticmethod
    def length(value: str, min_len: int = 0, max_len: int = float('inf')) -> bool:
        """Validate string length."""
        return min_len <= len(value) <= max_len

    @staticmethod
    def range_check(value: float, min_val: float = float('-inf'), max_val: float = float('inf')) -> bool:
        """Validate numeric range."""
        return min_val <= value <= max_val


class Validator:
    """
    Base validator class.

    Examples:
        >>> validator = Validator()
        >>> validator.add_rule("email", ValidationRules.email)
        >>> validator.validate({"email": "test@example.com"})
    """

    def __init__(self):
        self.rules: Dict[str, List[Callable]] = {}
        self.errors: Dict[str, List[str]] = {}

    def add_rule(self, field: str, rule: Callable, error_message: str = "Validation failed"):
        """Add validation rule for field."""
        if field not in self.rules:
            self.rules[field] = []
        self.rules[field].append((rule, error_message))

    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate data against rules.

        Args:
            data: Data to validate

        Returns:
            True if valid
        """
        self.errors = {}
        is_valid = True

        for field, rules in self.rules.items():
            if field not in data:
                self.errors[field] = ["Field is required"]
                is_valid = False
                continue

            value = data[field]
            for rule, error_msg in rules:
                if not rule(value):
                    if field not in self.errors:
                        self.errors[field] = []
                    self.errors[field].append(error_msg)
                    is_valid = False

        return is_valid

    def get_errors(self) -> Dict[str, List[str]]:
        """Get validation errors."""
        return self.errors
