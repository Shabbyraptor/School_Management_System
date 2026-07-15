from __future__ import annotations

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from academics.models import Class, Stream
from core.models import BaseModel, School

from .constants import (
    AnnouncementCategory,
    AudienceType,
    DeliveryChannel,
    DeliveryStatus,
    MessageStatus,
    NotificationPriority,
    NotificationType,
    SourceModule,
)
from .managers import AnnouncementManager, DeliveryLogManager, MessageManager, NotificationManager


class Announcement(BaseModel):
    """
    School-wide or targeted announcement with scheduled publishing and expiry.

    Integrates with core.School for multi-tenant scoping and academics.Class/Stream
    for audience targeting. Historical records are preserved via BaseModel soft-delete.
    """

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="announcements")
    title = models.CharField(max_length=255)
    content = models.TextField(help_text="Rich text / HTML announcement body.")
    category = models.CharField(
        max_length=20,
        choices=AnnouncementCategory.choices,
        default=AnnouncementCategory.GENERAL,
        db_index=True,
    )
    audience = models.CharField(
        max_length=20,
        choices=AudienceType.choices,
        default=AudienceType.ALL,
        db_index=True,
    )
    target_classes = models.ManyToManyField(
        Class,
        blank=True,
        related_name="announcements",
        help_text="Required when audience is Specific Classes.",
    )
    target_streams = models.ManyToManyField(
        Stream,
        blank=True,
        related_name="announcements",
        help_text="Required when audience is Specific Streams.",
    )
    priority = models.CharField(
        max_length=10,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
        db_index=True,
    )
    publish_date = models.DateTimeField(db_index=True)
    expiry_date = models.DateTimeField(blank=True, null=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_announcements",
    )
    is_published = models.BooleanField(default=False, db_index=True)
    is_archived = models.BooleanField(default=False, db_index=True)
    published_at = models.DateTimeField(blank=True, null=True)

    objects = AnnouncementManager()

    class Meta:
        ordering = ["-publish_date", "-created_at"]
        indexes = [
            models.Index(fields=["school", "is_published", "is_archived"]),
            models.Index(fields=["school", "category"]),
            models.Index(fields=["publish_date", "expiry_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.school.code})"

    def clean(self) -> None:
        super().clean()
        if self.expiry_date and self.publish_date and self.expiry_date <= self.publish_date:
            raise ValidationError({"expiry_date": "Expiry date must be after the publish date."})

        if self.audience == AudienceType.SPECIFIC_CLASSES and self.pk:
            if not self.target_classes.exists():
                raise ValidationError({"target_classes": "Select at least one class for this audience."})

        if self.audience == AudienceType.SPECIFIC_STREAMS and self.pk:
            if not self.target_streams.exists():
                raise ValidationError({"target_streams": "Select at least one stream for this audience."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)

    def publish(self) -> None:
        """Publish the announcement immediately or confirm a scheduled publication."""
        now = timezone.now()
        self.is_published = True
        self.is_archived = False
        self.published_at = now
        if self.publish_date > now:
            self.publish_date = now
        self.save(update_fields=["is_published", "is_archived", "published_at", "publish_date", "updated_at"])

    def unpublish(self) -> None:
        """Remove the announcement from active publication without archiving."""
        self.is_published = False
        self.published_at = None
        self.save(update_fields=["is_published", "published_at", "updated_at"])

    def archive(self) -> None:
        """Archive the announcement while preserving historical data."""
        self.is_archived = True
        self.is_published = False
        self.save(update_fields=["is_archived", "is_published", "updated_at"])


class AnnouncementAttachment(BaseModel):
    """File attachment linked to a school announcement."""

    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    file = models.FileField(upload_to="communication/announcements/%Y/%m/")
    original_filename = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    content_type = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return self.original_filename or self.file.name

    def save(self, *args, **kwargs) -> None:
        if self.file and not self.original_filename:
            self.original_filename = self.file.name.rsplit("/", maxsplit=1)[-1]
        if self.file and hasattr(self.file, "size"):
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class Notification(BaseModel):
    """
    Per-recipient notification record linked to an originating module.

    Other apps (students, finance, attendance, examinations) create notifications
    via NotificationService using source_module and reference_id for traceability.
    """

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="notifications")
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL_NOTICE,
        db_index=True,
    )
    source_module = models.CharField(
        max_length=32,
        choices=SourceModule.choices,
        default=SourceModule.COMMUNICATION,
        db_index=True,
    )
    reference_id = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        help_text="Primary key or business reference of the originating record.",
    )
    reference = models.CharField(
        max_length=40,
        unique=True,
        blank=True,
        db_index=True,
        help_text="Unique notification tracking reference.",
    )
    priority = models.CharField(
        max_length=10,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
        db_index=True,
    )
    delivery_channel = models.CharField(
        max_length=10,
        choices=DeliveryChannel.choices,
        default=DeliveryChannel.IN_APP,
        db_index=True,
    )
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True, db_index=True)
    expires_at = models.DateTimeField(blank=True, null=True, db_index=True)

    objects = NotificationManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["school", "recipient", "is_read"]),
            models.Index(fields=["recipient", "is_read", "-created_at"]),
            models.Index(fields=["source_module", "reference_id"]),
            models.Index(fields=["notification_type", "priority"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} → {self.recipient_id}"

    def clean(self) -> None:
        super().clean()
        if not self.recipient_id:
            raise ValidationError({"recipient": "Recipient is required."})
        if self.recipient and self.recipient.is_deleted:
            raise ValidationError({"recipient": "Cannot send notifications to deleted users."})

    def save(self, *args, **kwargs) -> None:
        if not self.reference:
            self.reference = self._generate_reference()
        self.full_clean()
        return super().save(*args, **kwargs)

    @staticmethod
    def _generate_reference() -> str:
        return f"NTF-{uuid.uuid4().hex[:12].upper()}"

    def mark_read(self) -> None:
        if not self.is_read:
            now = timezone.now()
            self.is_read = True
            self.read_at = now
            self.save(update_fields=["is_read", "read_at", "updated_at"])

    def mark_unread(self) -> None:
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save(update_fields=["is_read", "read_at", "updated_at"])

    def resend(self) -> None:
        """Reset delivery timestamps to allow NotificationService to re-dispatch."""
        self.sent_at = None
        self.save(update_fields=["sent_at", "updated_at"])

    @property
    def is_expired(self) -> bool:
        return bool(self.expires_at and self.expires_at <= timezone.now())


class Message(BaseModel):
    """
    Internal user-to-user message with thread-ready architecture.

    thread_root groups conversation messages; reply_to links the immediate parent.
    """

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_messages",
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(
        max_length=12,
        choices=MessageStatus.choices,
        default=MessageStatus.DRAFT,
        db_index=True,
    )
    sent_at = models.DateTimeField(blank=True, null=True, db_index=True)
    read_at = models.DateTimeField(blank=True, null=True)
    thread_root = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="thread_messages",
        help_text="Root message of the conversation thread.",
    )
    reply_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies",
        help_text="Direct parent message when replying.",
    )

    objects = MessageManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["school", "recipient", "status"]),
            models.Index(fields=["school", "sender", "status"]),
            models.Index(fields=["thread_root", "created_at"]),
            models.Index(fields=["recipient", "status", "-sent_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.subject} ({self.sender_id} → {self.recipient_id})"

    def clean(self) -> None:
        super().clean()
        if self.sender_id and self.recipient_id and self.sender_id == self.recipient_id:
            raise ValidationError("Sender and recipient must be different users.")
        if self.recipient and self.recipient.is_deleted:
            raise ValidationError({"recipient": "Cannot message deleted users."})
        if self.sender and self.sender.is_deleted:
            raise ValidationError({"sender": "Deleted users cannot send messages."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        if self.reply_to_id and not self.thread_root_id:
            self.thread_root = self.reply_to.thread_root or self.reply_to
        return super().save(*args, **kwargs)

    def mark_sent(self) -> None:
        now = timezone.now()
        self.status = MessageStatus.SENT
        self.sent_at = now
        self.save(update_fields=["status", "sent_at", "updated_at"])

    def mark_delivered(self) -> None:
        self.status = MessageStatus.DELIVERED
        self.save(update_fields=["status", "updated_at"])

    def mark_read(self) -> None:
        now = timezone.now()
        self.status = MessageStatus.READ
        self.read_at = now
        self.save(update_fields=["status", "read_at", "updated_at"])

    def archive(self) -> None:
        self.status = MessageStatus.ARCHIVED
        self.save(update_fields=["status", "updated_at"])


class MessageAttachment(BaseModel):
    """File attachment for an internal message."""

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="communication/messages/%Y/%m/")
    original_filename = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    content_type = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return self.original_filename or self.file.name

    def save(self, *args, **kwargs) -> None:
        if self.file and not self.original_filename:
            self.original_filename = self.file.name.rsplit("/", maxsplit=1)[-1]
        if self.file and hasattr(self.file, "size"):
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class CommunicationTemplate(BaseModel):
    """
    Reusable communication template with placeholder variables.

    Designed for multi-language expansion via the language field and JSON variables.
    """

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="communication_templates")
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=60)
    channel = models.CharField(max_length=10, choices=DeliveryChannel.choices, db_index=True)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    variables = models.JSONField(
        default=list,
        blank=True,
        help_text="List of placeholder variable names, e.g. ['student_name', 'amount_due'].",
    )
    language = models.CharField(max_length=10, default="en", db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["school", "code"], name="unique_template_code_per_school"),
        ]
        indexes = [
            models.Index(fields=["school", "channel", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"

    def clean(self) -> None:
        super().clean()
        if self.code and self.school_id:
            duplicate = CommunicationTemplate.objects.filter(school=self.school, code=self.code).exclude(pk=self.pk)
            if duplicate.exists():
                raise ValidationError({"code": "Template code must be unique within a school."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)


class NotificationPreference(BaseModel):
    """Per-user notification channel preferences."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    type_preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="Optional per-notification-type channel overrides.",
    )

    class Meta:
        verbose_name = "Notification Preference"
        verbose_name_plural = "Notification Preferences"

    def __str__(self) -> str:
        return f"Preferences for {self.user_id}"

    def is_channel_enabled(self, channel: str) -> bool:
        channel_map = {
            DeliveryChannel.EMAIL: self.email_enabled,
            DeliveryChannel.SMS: self.sms_enabled,
            DeliveryChannel.PUSH: self.push_enabled,
            DeliveryChannel.IN_APP: self.in_app_enabled,
        }
        return channel_map.get(channel, False)


class DeliveryLog(models.Model):
    """
    Immutable delivery audit record for notification channel dispatch.

    DeliveryLog intentionally does not inherit BaseModel — logs are permanent
    and must never be soft-deleted or modified after creation.
    """

    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="delivery_logs",
    )
    channel = models.CharField(max_length=10, choices=DeliveryChannel.choices, db_index=True)
    status = models.CharField(
        max_length=12,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING,
        db_index=True,
    )
    provider = models.CharField(max_length=60, blank=True, help_text="Delivery provider identifier.")
    provider_reference = models.CharField(max_length=255, blank=True, db_index=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = DeliveryLogManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["notification", "channel"]),
            models.Index(fields=["status", "channel"]),
            models.Index(fields=["provider", "provider_reference"]),
        ]

    def __str__(self) -> str:
        return f"{self.channel} {self.status} — notification {self.notification_id}"

    def save(self, *args, **kwargs) -> None:
        if self.pk is not None:
            raise ValidationError("Delivery logs are immutable after creation.")
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False) -> None:
        raise ValidationError("Delivery logs cannot be deleted.")
