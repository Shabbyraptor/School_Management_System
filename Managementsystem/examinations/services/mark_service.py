from __future__ import annotations

from typing import Any

from django.db import transaction

from ..models import Mark


class MarkService:
    @staticmethod
    @transaction.atomic
    def record_mark(data: dict[str, Any]) -> Mark:
        return Mark.objects.create(**data)
