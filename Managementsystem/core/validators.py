import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

phone_number_validator = RegexValidator(
    regex=r"^\+?[1-9]\d{1,14}$",
    message=(
        "Enter a valid phone number in E.164 format, for example +15551234567 or 15551234567."
    ),
)

school_code_validator = RegexValidator(
    regex=r"^[A-Z0-9]{3,12}$",
    message=(
        "School code must be 3-12 characters long and contain only uppercase letters and numbers."
    ),
)

registration_number_validator = RegexValidator(
    regex=r"^[A-Z0-9\-]{5,20}$",
    message=(
        "Registration number must be 5-20 characters and contain only uppercase letters, numbers, and hyphens."
    ),
)


def validate_phone_number(value: str) -> None:
    phone_number_validator(value)


def validate_school_code(value: str) -> None:
    value = value.strip().upper()
    if not re.fullmatch(r"^[A-Z0-9]{3,12}$", value):
        raise ValidationError(
            "School code must be 3-12 characters and contain only uppercase letters and numbers."
        )


def validate_registration_number(value: str) -> None:
    value = value.strip().upper()
    if not re.fullmatch(r"^[A-Z0-9\-]{5,20}$", value):
        raise ValidationError(
            "Registration number must be 5-20 characters and contain only uppercase letters, numbers, and hyphens."
        )
