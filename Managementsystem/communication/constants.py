from __future__ import annotations

from django.db import models


class AnnouncementCategory(models.TextChoices):
    ACADEMIC = "ACADEMIC", "Academic"
    FINANCE = "FINANCE", "Finance"
    ADMINISTRATION = "ADMINISTRATION", "Administration"
    EXAMINATIONS = "EXAMINATIONS", "Examinations"
    SPORTS = "SPORTS", "Sports"
    EVENTS = "EVENTS", "Events"
    EMERGENCY = "EMERGENCY", "Emergency"
    GENERAL = "GENERAL", "General"


class AudienceType(models.TextChoices):
    ALL = "ALL", "All"
    STUDENTS = "STUDENTS", "Students"
    PARENTS = "PARENTS", "Parents"
    TEACHERS = "TEACHERS", "Teachers"
    FINANCE_STAFF = "FINANCE_STAFF", "Finance Staff"
    ADMINISTRATORS = "ADMINISTRATORS", "Administrators"
    SPECIFIC_CLASSES = "SPECIFIC_CLASSES", "Specific Classes"
    SPECIFIC_STREAMS = "SPECIFIC_STREAMS", "Specific Streams"


class NotificationType(models.TextChoices):
    FEE_REMINDER = "FEE_REMINDER", "Fee Reminder"
    ATTENDANCE_ALERT = "ATTENDANCE_ALERT", "Attendance Alert"
    EXAM_RESULT = "EXAM_RESULT", "Exam Result"
    EXAM_NOTICE = "EXAM_NOTICE", "Exam Notice"
    ASSIGNMENT = "ASSIGNMENT", "Assignment"
    GENERAL_NOTICE = "GENERAL_NOTICE", "General Notice"
    ADMISSION = "ADMISSION", "Admission"
    PROMOTION = "PROMOTION", "Promotion"
    TRANSFER = "TRANSFER", "Transfer"
    SYSTEM_ALERT = "SYSTEM_ALERT", "System Alert"


class NotificationPriority(models.TextChoices):
    LOW = "LOW", "Low"
    NORMAL = "NORMAL", "Normal"
    HIGH = "HIGH", "High"
    URGENT = "URGENT", "Urgent"


class DeliveryChannel(models.TextChoices):
    IN_APP = "IN_APP", "In-App"
    EMAIL = "EMAIL", "Email"
    SMS = "SMS", "SMS"
    PUSH = "PUSH", "Push Notification"


class DeliveryStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    QUEUED = "QUEUED", "Queued"
    SENT = "SENT", "Sent"
    DELIVERED = "DELIVERED", "Delivered"
    FAILED = "FAILED", "Failed"
    BOUNCED = "BOUNCED", "Bounced"
    RETRYING = "RETRYING", "Retrying"


class MessageStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    SENT = "SENT", "Sent"
    DELIVERED = "DELIVERED", "Delivered"
    READ = "READ", "Read"
    ARCHIVED = "ARCHIVED", "Archived"


class SourceModule(models.TextChoices):
    """Identifies the originating application module for cross-app notification triggers."""

    COMMUNICATION = "communication", "Communication"
    ACCOUNTS = "accounts", "Accounts"
    STUDENTS = "students", "Students"
    ACADEMICS = "academics", "Academics"
    ATTENDANCE = "attendance", "Attendance"
    FINANCE = "finance", "Finance"
    EXAMINATIONS = "examinations", "Examinations"
    REPORTS = "reports", "Reports"
    SYSTEM = "system", "System"
