from __future__ import annotations

from django.utils import timezone


def calculate_percentage(marks_obtained: float, total_marks: float) -> float:
    if total_marks <= 0:
        return 0.0
    return round((marks_obtained / total_marks) * 100, 2)


def calculate_average(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 2)


def generate_exam_code(school_code: str, exam_type_code: str) -> str:
    year = timezone.now().year
    return f"{school_code}-{exam_type_code}-{year}"


def generate_report_card_number(student_id: int, exam_id: int) -> str:
    return f"RC-{student_id}-{exam_id}"
