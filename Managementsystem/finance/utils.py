from __future__ import annotations

from decimal import Decimal
from datetime import date


def generate_invoice_number(school_code: str, academic_year_code: str, invoice_id: int | None = None) -> str:
    suffix = str(invoice_id or 0).zfill(6)
    return f"INV-{school_code}-{academic_year_code}-{suffix}"


def generate_receipt_number(school_code: str, payment_id: int | None = None) -> str:
    suffix = str(payment_id or 0).zfill(6)
    return f"RCPT-{school_code}-{suffix}"


def calculate_invoice_total(subtotal: Decimal, discount_amount: Decimal, scholarship_amount: Decimal, penalty_amount: Decimal) -> Decimal:
    return subtotal - discount_amount - scholarship_amount + penalty_amount


def calculate_balance(total_amount: Decimal, paid_amount: Decimal) -> Decimal:
    return total_amount - paid_amount


def format_currency(value: Decimal, currency_code: str = "KES") -> str:
    return f"{currency_code} {value:,.2f}"


def default_due_date(issue_date: date | None = None) -> date:
    from datetime import timedelta

    base_date = issue_date or date.today()
    return base_date + timedelta(days=30)
