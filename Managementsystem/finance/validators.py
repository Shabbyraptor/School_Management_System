from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError


def validate_non_negative_amount(value: Decimal | int | float) -> None:
    if Decimal(str(value)) < 0:
        raise ValidationError("Amount cannot be negative.")


def validate_discount_value(value: Decimal | int | float, discount_type: str) -> None:
    if Decimal(str(value)) < 0:
        raise ValidationError("Discount value cannot be negative.")
    if discount_type == "PERCENTAGE" and Decimal(str(value)) > Decimal("100"):
        raise ValidationError("Percentage discount cannot exceed 100%.")


def validate_invoice_totals(subtotal: Decimal, discount_amount: Decimal, scholarship_amount: Decimal, penalty_amount: Decimal) -> None:
    if subtotal < 0 or discount_amount < 0 or scholarship_amount < 0 or penalty_amount < 0:
        raise ValidationError("Financial totals cannot be negative.")


def validate_payment_amount(amount: Decimal, balance: Decimal, allow_overpayment: bool = False) -> None:
    if Decimal(str(amount)) <= 0:
        raise ValidationError("Payment amount must be positive.")
    if not allow_overpayment and Decimal(str(amount)) > balance:
        raise ValidationError("Payment amount cannot exceed invoice balance.")
