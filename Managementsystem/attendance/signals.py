from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AttendanceRecord, AttendanceSession
from .services import AttendanceSummaryService


@receiver(post_save, sender=AttendanceRecord)
def update_summary_on_attendance_marked(sender, instance, created, **kwargs):
    if instance.attendance_session and instance.student:
        AttendanceSummaryService.calculate_summary(
            instance.student_id,
            instance.attendance_session.academic_year_id,
            instance.attendance_session.term_id,
        )


@receiver(post_save, sender=AttendanceSession)
def initialize_attendance_session(sender, instance, created, **kwargs):
    if created:
        return
