from __future__ import annotations

from typing import Iterable

from django.utils import timezone


def calculate_attendance_percentage(present_days: int, total_days: int) -> float:
    if total_days <= 0:
        return 0.0
    return round((present_days / total_days) * 100, 2)


def calculate_absence_rate(absent_days: int, total_days: int) -> float:
    if total_days <= 0:
        return 0.0
    return round((absent_days / total_days) * 100, 2)


def generate_attendance_reference(school_code: str, attendance_date, session_type: str) -> str:
    date_part = attendance_date.strftime("%Y%m%d")
    return f"{school_code}-{date_part}-{session_type.lower()}"


def get_student_attendance_history(student_id: int, queryset) -> list[dict]:
    return list(queryset.filter(student_id=student_id).values("attendance_session__attendance_date", "status"))
