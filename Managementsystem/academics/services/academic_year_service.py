from __future__ import annotations

from typing import Any

from django.db import transaction

from ..models import AcademicYear


class AcademicYearService:
    @staticmethod
    @transaction.atomic
    def create_year(data: dict[str, Any]) -> AcademicYear:
        return AcademicYear.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def activate_year(year: AcademicYear) -> AcademicYear:
        year.activate()
        return year

    @staticmethod
    @transaction.atomic
    def close_year(year: AcademicYear) -> AcademicYear:
        year.deactivate()
        return year
