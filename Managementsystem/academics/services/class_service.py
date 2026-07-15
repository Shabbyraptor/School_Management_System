from __future__ import annotations

from typing import Any

from django.db import transaction

from ..models import Class


class ClassService:
    @staticmethod
    @transaction.atomic
    def create_class(data: dict[str, Any]) -> Class:
        return Class.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def archive_class(academic_class: Class) -> Class:
        academic_class.archive()
        return academic_class
