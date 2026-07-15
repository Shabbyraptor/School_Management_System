from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from ..models import Invoice, InvoiceItem


class InvoiceService:
    @staticmethod
    @transaction.atomic
    def generate_invoice(data: dict[str, Any]) -> Invoice:
        invoice = Invoice.objects.create(**data)
        return invoice

    @staticmethod
    @transaction.atomic
    def generate_bulk_invoices(invoices_data: list[dict[str, Any]]) -> list[Invoice]:
        invoices = [Invoice(**data) for data in invoices_data]
        return list(Invoice.objects.bulk_create(invoices))

    @staticmethod
    @transaction.atomic
    def cancel_invoice(invoice: Invoice) -> Invoice:
        invoice.cancel()
        return invoice

    @staticmethod
    def calculate_balances(invoice: Invoice) -> Decimal:
        return invoice.calculate_balance()
