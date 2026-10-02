from __future__ import annotations

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .constants import PaymentStatus
from .models import Invoice, Payment, Receipt
from .services.ledger_service import LedgerService


@receiver(post_save, sender=Invoice)
@receiver(post_delete, sender=Invoice)
def update_ledger_on_invoice(sender, instance, **kwargs):
    if kwargs.get("signal") is post_save:
        LedgerService.recalculate_invoice(instance.pk)
    LedgerService.recalculate_account(instance.student_id)


@receiver(post_save, sender=Payment)
def update_ledger_on_payment(sender, instance, **kwargs):
    if instance.status == PaymentStatus.SUCCESSFUL:
        Receipt.objects.get_or_create(
            payment=instance,
            defaults={"school": instance.school, "student": instance.student, "amount": instance.amount, "issued_by": instance.received_by},
        )
    LedgerService.recalculate_invoice(instance.invoice_id)
    LedgerService.recalculate_account(instance.student_id)


@receiver(post_delete, sender=Payment)
def update_ledger_on_payment_delete(sender, instance, **kwargs):
    LedgerService.recalculate_invoice(instance.invoice_id)
    LedgerService.recalculate_account(instance.student_id)
