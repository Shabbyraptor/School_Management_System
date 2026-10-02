from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db.models import Max, Sum

from ..constants import InvoiceStatus, PaymentStatus
from ..models import Invoice, Payment, StudentAccount

ZERO = Decimal("0.00")


class LedgerService:
    """Keeps invoice balances/statuses and student accounts in step with payments.

    Writes go through queryset.update() so recalculating never re-triggers the
    post_save signals that call it.
    """

    @staticmethod
    def recalculate_invoice(invoice_id: int) -> None:
        invoice = Invoice.objects.filter(pk=invoice_id).first()
        if invoice is None:
            return
        paid = (
            Payment.objects.filter(invoice_id=invoice_id, status=PaymentStatus.SUCCESSFUL).aggregate(total=Sum("amount"))["total"]
            or ZERO
        )
        balance = max(invoice.total_amount - paid, ZERO)
        status = invoice.status
        if status not in (InvoiceStatus.CANCELLED, InvoiceStatus.DRAFT):
            if invoice.total_amount > ZERO and balance == ZERO:
                status = InvoiceStatus.PAID
            elif invoice.due_date and invoice.due_date < date.today():
                status = InvoiceStatus.OVERDUE
            elif paid > ZERO:
                status = InvoiceStatus.PARTIALLY_PAID
            else:
                status = InvoiceStatus.ISSUED
        Invoice.objects.filter(pk=invoice_id).update(balance=balance, status=status)

    @staticmethod
    def recalculate_account(student_id: int) -> StudentAccount:
        invoices = Invoice.objects.filter(student_id=student_id).exclude(status=InvoiceStatus.CANCELLED)
        totals = invoices.aggregate(
            invoiced=Sum("total_amount"),
            balance=Sum("balance"),
            discount=Sum("discount_amount"),
            scholarship=Sum("scholarship_amount"),
        )
        payments = Payment.objects.filter(student_id=student_id, status=PaymentStatus.SUCCESSFUL).aggregate(
            paid=Sum("amount"), last=Max("payment_date")
        )
        account, _ = StudentAccount.objects.get_or_create(student_id=student_id)
        StudentAccount.objects.filter(pk=account.pk).update(
            total_invoiced=totals["invoiced"] or ZERO,
            current_balance=totals["balance"] or ZERO,
            total_discount=(totals["discount"] or ZERO) + (totals["scholarship"] or ZERO),
            total_paid=payments["paid"] or ZERO,
            last_payment_date=payments["last"],
        )
        account.refresh_from_db()
        return account

    @staticmethod
    def rebuild_all() -> int:
        """Recalculate every invoice and account (for existing data)."""
        for invoice_id in Invoice.objects.values_list("id", flat=True):
            LedgerService.recalculate_invoice(invoice_id)
        student_ids = set(Invoice.objects.values_list("student_id", flat=True))
        student_ids |= set(Payment.objects.values_list("student_id", flat=True))
        for student_id in student_ids:
            LedgerService.recalculate_account(student_id)
        return len(student_ids)
