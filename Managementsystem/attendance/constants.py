from __future__ import annotations

from django.db import models


class AttendanceStatus(models.TextChoices):
    PRESENT = "PRESENT", "Present"
    ABSENT = "ABSENT", "Absent"
    LATE = "LATE", "Late"
    EXCUSED = "EXCUSED", "Excused"


class AttendanceSessionType(models.TextChoices):
    MORNING = "MORNING", "Morning"
    AFTERNOON = "AFTERNOON", "Afternoon"
    EVENING = "EVENING", "Evening"
    FULL_DAY = "FULL_DAY", "Full Day"


class AttendanceSessionStatus(models.TextChoices):
    OPEN = "OPEN", "Open"
    CLOSED = "CLOSED", "Closed"
    ARCHIVED = "ARCHIVED", "Archived"
