from __future__ import annotations

from typing import Any

from django.db import transaction

from ..models import SubjectAssignment


class SubjectAssignmentService:
    @staticmethod
    @transaction.atomic
    def assign_teacher(data: dict[str, Any]) -> SubjectAssignment:
        return SubjectAssignment.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def remove_assignment(assignment: SubjectAssignment) -> None:
        assignment.delete()
