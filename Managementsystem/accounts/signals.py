from __future__ import annotations

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, UserProfile
from core.services.audit_service import AuditLogService


@receiver(post_save, sender=User)
def create_user_profile(sender, instance: User, created: bool, **kwargs) -> None:
    if created:
        UserProfile.objects.create(user=instance)
        AuditLogService.log_action(
            action="CREATE",
            model_name="User",
            object_id=str(instance.pk),
            description=f"Created user {instance.email}",
            user=instance,
            school=instance.school,
        )
