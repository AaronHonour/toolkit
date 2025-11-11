"""Pre-defined validation rules."""

from .validators import ValidationRules


class Rules:
    """Convenient access to validation rules."""

    email = staticmethod(ValidationRules.email)
    url = staticmethod(ValidationRules.url)
    phone = staticmethod(ValidationRules.phone)
    length = staticmethod(ValidationRules.length)
    range_check = staticmethod(ValidationRules.range_check)
