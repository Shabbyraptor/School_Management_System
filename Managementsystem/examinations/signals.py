from __future__ import annotations

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Mark, Result
from .services import ResultService


@receiver(post_save, sender=Mark)
def update_result_on_mark(sender, instance, **kwargs):
    ResultService.generate_result(instance)
    ResultService.rank_exam(instance.exam_id)


@receiver(post_delete, sender=Mark)
def remove_result_on_mark_delete(sender, instance, **kwargs):
    Result.objects.filter(exam_id=instance.exam_id, student_id=instance.student_id).delete()
    ResultService.rank_exam(instance.exam_id)
