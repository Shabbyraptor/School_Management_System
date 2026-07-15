from __future__ import annotations

from typing import Any

from django.db import transaction

from ..models import Exam


class ExamService:
    @staticmethod
    @transaction.atomic
    def create_exam(data: dict[str, Any]) -> Exam:
        return Exam.objects.create(**data)
