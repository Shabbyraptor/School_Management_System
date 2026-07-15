from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AcademicYear, Term


@receiver(post_save, sender=AcademicYear)
def deactivate_previous_academic_year(sender, instance, **kwargs):
    if instance.is_active:
        AcademicYear.objects.filter(school=instance.school, is_active=True).exclude(pk=instance.pk).update(is_active=False, is_current=False)


@receiver(post_save, sender=Term)
def deactivate_previous_term(sender, instance, **kwargs):
    if instance.is_active:
        Term.objects.filter(academic_year=instance.academic_year, is_active=True).exclude(pk=instance.pk).update(is_active=False, is_current=False)
