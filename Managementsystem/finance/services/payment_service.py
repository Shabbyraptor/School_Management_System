from __future__ import annotations

from typing import Any

from django.db import transaction

from ..models import Payment


class PaymentService:
    @staticmethod
    @transaction.atomic
    def record_payment(data: dict[str, Any]) -> Payment:
        return Payment.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def reverse_payment(payment: Payment) -> Payment:
        payment.reverse_payment()
        return payment

    @staticmethod
    def validate_payment(payment: Payment) -> Payment:
        payment.validate_payment()
        return payment
