from __future__ import annotations

from typing import Any, Optional

from ..models import AuditLog, School
from django.contrib.auth import get_user_model

User = get_user_model()


class AuditLogService:
    """Encapsulates audit log creation and reporting logic."""

    @staticmethod
    def log_action(
        action: str,
        model_name: str,
        object_id: str,
        description: str,
        user: Optional[User] = None,
        school: Optional[School] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        return AuditLog.objects.create(
            user=user,
            school=school,
            action=action,
            model_name=model_name,
            object_id=object_id,
            description=description,
            ip_address=ip_address,
        )
