from __future__ import annotations

from typing import Any

from django.db import transaction

from ..models import Subject, SubjectAssignment


class SubjectService:
    @staticmethod
    @transaction.atomic
    def create_subject(data: dict[str, Any]) -> Subject:
        return Subject.objects.create(**data)
