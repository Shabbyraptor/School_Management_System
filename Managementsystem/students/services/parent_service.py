from __future__ import annotations

from typing import Any

from django.db import transaction

from ..models import Guardian, Parent, ParentStudent, Student


class ParentService:
    @staticmethod
    @transaction.atomic
    def link_parent(student: Student, parent: Parent, relationship: str) -> ParentStudent:
        return ParentStudent.objects.create(student=student, parent=parent, relationship=relationship)

    @staticmethod
    @transaction.atomic
    def unlink_parent(student: Student, parent: Parent) -> None:
        ParentStudent.objects.filter(student=student, parent=parent).delete()

    @staticmethod
    @transaction.atomic
    def add_guardian(student: Student, data: dict[str, Any]) -> Guardian:
        guardian = Guardian.objects.create(school=student.school, **data)
        student.guardians.add(guardian)
        return guardian
