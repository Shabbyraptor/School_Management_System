from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Invoice, Payment, Receipt, Scholarship, Discount


@receiver(post_save, sender=Invoice)
def update_student_account_on_invoice(sender, instance, created, **kwargs):
    if created:
        return


@receiver(post_save, sender=Payment)
def generate_receipt_on_payment(sender, instance, created, **kwargs):
    if created and instance.status == "SUCCESSFUL":
        Receipt.objects.get_or_create(
            payment=instance,
            defaults={"school": instance.school, "student": instance.student, "amount": instance.amount, "issued_by": instance.received_by},
        )


@receiver(post_save, sender=Discount)
def recalculate_invoice_on_discount(sender, instance, created, **kwargs):
    return None


@receiver(post_save, sender=Scholarship)
def recalculate_fees_on_scholarship(sender, instance, created, **kwargs):
    return None
