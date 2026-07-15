from __future__ import annotations

from django.core.exceptions import ValidationError


def validate_future_dates(start_date, end_date):
    if end_date <= start_date:
        raise ValidationError("End date must be after start date.")


def validate_positive_capacity(capacity):
    if capacity <= 0:
        raise ValidationError("Capacity must be greater than zero.")
