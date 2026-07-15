from __future__ import annotations

from datetime import date

from django.core.exceptions import ValidationError


def validate_birth_date(date_of_birth: date | None) -> None:
    if date_of_birth and date_of_birth > date.today():
        raise ValidationError("Date of birth cannot be in the future.")


def validate_admission_date(admission_date: date | None, date_of_birth: date | None) -> None:
    if admission_date and date_of_birth and admission_date < date_of_birth:
        raise ValidationError("Admission date cannot precede the date of birth.")


def validate_relationship(relationship: str | None) -> None:
    if relationship and relationship.upper() not in {choice[0] for choice in [
        ("MOTHER", "Mother"),
        ("FATHER", "Father"),
        ("GUARDIAN", "Guardian"),
        ("SPONSOR", "Sponsor"),
        ("OTHER", "Other"),
    ]}:
        raise ValidationError("Invalid relationship type.")
