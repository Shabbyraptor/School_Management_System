from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from .constants import AuditActionChoices, COUNTRIES
from .managers import AllObjectsManager, SoftDeleteManager
from .validators import (
    phone_number_validator,
    registration_number_validator,
    school_code_validator,
)


class TimeStampedModel(models.Model):
    """Abstract model that provides created and updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """Abstract model that supports soft deletion and custom queryset behavior."""

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False) -> None:
        self.soft_delete()

    def soft_delete(self) -> None:
        if not self.is_deleted:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

    def restore(self) -> None:
        if self.is_deleted:
            self.is_deleted = False
            self.deleted_at = None
            self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

    def hard_delete(self, using=None, keep_parents=False) -> None:
        super().delete(using=using, keep_parents=keep_parents)


class BaseModel(TimeStampedModel, SoftDeleteModel):
    """Base model for shared behaviors across the domain."""

    class Meta:
        abstract = True


class School(BaseModel):
    """Represents a school tenant that other modules will rely on."""

    name = models.CharField(max_length=255)
    code = models.CharField(
        max_length=12,
        unique=True,
        validators=[school_code_validator],
        help_text="Unique school identifier used for tenant and integration lookups.",
    )
    registration_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[registration_number_validator],
        help_text="Official registration number assigned by the education authority.",
    )
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=20,
        validators=[phone_number_validator],
        help_text="E.164-formatted school contact number.",
    )
    address = models.TextField(blank=True)
    city = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=2, choices=COUNTRIES, blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to="schools/logos/", blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["registration_number"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"

    def activate(self) -> None:
        if not self.is_active:
            self.is_active = True
            self.save(update_fields=["is_active", "updated_at"])

    def deactivate(self) -> None:
        if self.is_active:
            self.is_active = False
            self.save(update_fields=["is_active", "updated_at"])

    def soft_delete(self) -> None:
        super().soft_delete()

    def restore(self) -> None:
        super().restore()

    def hard_delete(self, using=None, keep_parents=False) -> None:
        super().hard_delete(using=using, keep_parents=keep_parents)


class AuditLog(models.Model):
    """Captures audit events for key application operations."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    school = models.ForeignKey(
        School,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=16, choices=AuditActionChoices.choices())
    model_name = models.CharField(max_length=120)
    object_id = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["action"]),
            models.Index(fields=["model_name"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} - {self.model_name} - {self.object_id or self.pk}"
