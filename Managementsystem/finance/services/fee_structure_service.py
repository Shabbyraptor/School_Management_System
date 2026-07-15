from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from ..models import FeeStructure


class FeeStructureService:
    @staticmethod
    @transaction.atomic
    def create_fee_structure(data: dict[str, Any]) -> FeeStructure:
        return FeeStructure.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def update_fee_structure(structure: FeeStructure, data: dict[str, Any]) -> FeeStructure:
        for field, value in data.items():
            setattr(structure, field, value)
        structure.save()
        return structure

    @staticmethod
    @transaction.atomic
    def activate_fee_structure(structure: FeeStructure) -> FeeStructure:
        structure.activate()
        return structure
