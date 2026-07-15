from __future__ import annotations

from django.db import models
from django.utils import timezone

from core.managers import SoftDeleteManager, SoftDeleteQuerySet


class AnnouncementQuerySet(SoftDeleteQuerySet):
    """Query helpers for school announcement lifecycle and scheduling."""

    def published(self) -> AnnouncementQuerySet:
        return self.filter(is_published=True, is_archived=False)

    def unpublished(self) -> AnnouncementQuerySet:
        return self.filter(is_published=False, is_archived=False)

    def archived(self) -> AnnouncementQuerySet:
        return self.filter(is_archived=True)

    def scheduled(self) -> AnnouncementQuerySet:
        now = timezone.now()
        return self.filter(is_published=False, is_archived=False, publish_date__gt=now)

    def active(self) -> AnnouncementQuerySet:
        """Return published announcements that have not yet expired."""
        now = timezone.now()
        return self.published().filter(
            models.Q(expiry_date__isnull=True) | models.Q(expiry_date__gt=now),
            publish_date__lte=now,
        )

    def for_school(self, school) -> AnnouncementQuerySet:
        return self.filter(school=school)


class AnnouncementManager(SoftDeleteManager):
    def get_queryset(self) -> AnnouncementQuerySet:
        return AnnouncementQuerySet(self.model, using=self._db).filter(is_deleted=False)


class NotificationQuerySet(SoftDeleteQuerySet):
    """Optimized query patterns for per-recipient notification delivery."""

    def unread(self) -> NotificationQuerySet:
        return self.filter(is_read=False)

    def read(self) -> NotificationQuerySet:
        return self.filter(is_read=True)

    def for_recipient(self, user) -> NotificationQuerySet:
        return self.filter(recipient=user)

    def for_school(self, school) -> NotificationQuerySet:
        return self.filter(school=school)

    def active(self) -> NotificationQuerySet:
        now = timezone.now()
        return self.filter(models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now))

    def expired(self) -> NotificationQuerySet:
        now = timezone.now()
        return self.filter(expires_at__lte=now)

    def by_type(self, notification_type: str) -> NotificationQuerySet:
        return self.filter(notification_type=notification_type)

    def by_source(self, source_module: str, reference_id: str = "") -> NotificationQuerySet:
        qs = self.filter(source_module=source_module)
        if reference_id:
            qs = qs.filter(reference_id=reference_id)
        return qs


class NotificationManager(SoftDeleteManager):
    def get_queryset(self) -> NotificationQuerySet:
        return NotificationQuerySet(self.model, using=self._db).filter(is_deleted=False)


class MessageQuerySet(SoftDeleteQuerySet):
    """Inbox, outbox, and thread query helpers for internal messaging."""

    def inbox(self, user) -> MessageQuerySet:
        from .constants import MessageStatus

        return self.filter(recipient=user).exclude(status=MessageStatus.DRAFT)

    def sent(self, user) -> MessageQuerySet:
        from .constants import MessageStatus

        return self.filter(sender=user).exclude(status=MessageStatus.DRAFT)

    def drafts(self, user) -> MessageQuerySet:
        from .constants import MessageStatus

        return self.filter(sender=user, status=MessageStatus.DRAFT)

    def unread(self, user) -> MessageQuerySet:
        from .constants import MessageStatus

        return self.filter(recipient=user, status__in=[MessageStatus.SENT, MessageStatus.DELIVERED])

    def in_thread(self, thread_root) -> MessageQuerySet:
        return self.filter(models.Q(pk=thread_root.pk) | models.Q(thread_root=thread_root))

    def for_school(self, school) -> MessageQuerySet:
        return self.filter(school=school)


class MessageManager(SoftDeleteManager):
    def get_queryset(self) -> MessageQuerySet:
        return MessageQuerySet(self.model, using=self._db).filter(is_deleted=False)


class DeliveryLogQuerySet(models.QuerySet):
    """Delivery audit trail queries — DeliveryLog is not soft-deleted."""

    def pending(self) -> DeliveryLogQuerySet:
        from .constants import DeliveryStatus

        return self.filter(status__in=[DeliveryStatus.PENDING, DeliveryStatus.QUEUED, DeliveryStatus.RETRYING])

    def failed(self) -> DeliveryLogQuerySet:
        from .constants import DeliveryStatus

        return self.filter(status__in=[DeliveryStatus.FAILED, DeliveryStatus.BOUNCED])

    def for_notification(self, notification) -> DeliveryLogQuerySet:
        return self.filter(notification=notification)

    def by_channel(self, channel: str) -> DeliveryLogQuerySet:
        return self.filter(channel=channel)


class DeliveryLogManager(models.Manager):
    def get_queryset(self) -> DeliveryLogQuerySet:
        return DeliveryLogQuerySet(self.model, using=self._db)
