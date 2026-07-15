from __future__ import annotations

from django.db import models


class InvoiceStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    ISSUED = "ISSUED", "Issued"
    PARTIALLY_PAID = "PARTIALLY_PAID", "Partially Paid"
    PAID = "PAID", "Paid"
    OVERDUE = "OVERDUE", "Overdue"
    CANCELLED = "CANCELLED", "Cancelled"


class PaymentMethod(models.TextChoices):
    CASH = "CASH", "Cash"
    BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
    CHEQUE = "CHEQUE", "Cheque"
    CREDIT_CARD = "CREDIT_CARD", "Credit Card"
    DEBIT_CARD = "DEBIT_CARD", "Debit Card"
    MOBILE_MONEY = "MOBILE_MONEY", "Mobile Money"
    ONLINE_PAYMENT = "ONLINE_PAYMENT", "Online Payment"


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SUCCESSFUL = "SUCCESSFUL", "Successful"
    FAILED = "FAILED", "Failed"
    REVERSED = "REVERSED", "Reversed"


class DiscountType(models.TextChoices):
    PERCENTAGE = "PERCENTAGE", "Percentage"
    FIXED_AMOUNT = "FIXED_AMOUNT", "Fixed Amount"


class Currency(models.TextChoices):
    KES = "KES", "KES"
    USD = "USD", "USD"
    EUR = "EUR", "EUR"
