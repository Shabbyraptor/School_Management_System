from __future__ import annotations

from django.core.exceptions import ValidationError


def validate_exam_dates(start_date, end_date):
    if start_date and end_date and end_date <= start_date:
        raise ValidationError("End date must be after the start date.")


def validate_mark(mark, total_marks):
    if mark is None:
        return
    if mark < 0:
        raise ValidationError("Marks cannot be negative.")
    if total_marks is not None and mark > total_marks:
        raise ValidationError("Marks cannot exceed the total marks for the exam.")


def validate_grade_scale_ranges(minimum_mark, maximum_mark, previous_maximum=None):
    if minimum_mark is None or maximum_mark is None:
        return
    if minimum_mark > maximum_mark:
        raise ValidationError("Minimum mark cannot be greater than maximum mark.")
    if previous_maximum is not None and minimum_mark <= previous_maximum:
        raise ValidationError("Grade scale ranges must not overlap.")
