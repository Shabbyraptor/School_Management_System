from __future__ import annotations

from typing import Any

from django.db import transaction

from ..models import Receipt


class ReceiptService:
    @staticmethod
    @transaction.atomic
    def generate_receipt(data: dict[str, Any]) -> Receipt:
        return Receipt.objects.create(**data)

    @staticmethod
    def print_receipt(receipt: Receipt) -> Receipt:
        return receipt

    @staticmethod
    def email_receipt(receipt: Receipt) -> Receipt:
        return receipt
