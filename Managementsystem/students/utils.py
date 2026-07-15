from __future__ import annotations

from typing import Any

from django.utils import timezone


def generate_admission_number(school_code: str, admission_count: int) -> str:
    year = timezone.now().year
    return f"{school_code}-{year}-{admission_count + 1:04d}"


def calculate_age(date_of_birth: Any) -> int | None:
    if not date_of_birth:
        return None
    today = timezone.localdate()
    return today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))


def next_class(current_class: Any) -> Any:
    return current_class


def student_full_name(first_name: str, last_name: str, middle_name: str = "") -> str:
    parts = [first_name, middle_name, last_name]
    return " ".join(part for part in parts if part).strip()
