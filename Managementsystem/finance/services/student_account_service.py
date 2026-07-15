from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from ..models import StudentAccount


class StudentAccountService:
    @staticmethod
    @transaction.atomic
    def update_balance(account: StudentAccount, amount: Decimal) -> StudentAccount:
        account.current_balance += amount
        account.save(update_fields=["current_balance", "updated_at"])
        return account

    @staticmethod
    def calculate_statement(account: StudentAccount) -> dict[str, Any]:
        return {
            "student": account.student_id,
            "current_balance": account.current_balance,
            "total_invoiced": account.total_invoiced,
            "total_paid": account.total_paid,
            "total_discount": account.total_discount,
        }

    @staticmethod
    def generate_account_summary(account: StudentAccount) -> dict[str, Any]:
        return StudentAccountService.calculate_statement(account)
