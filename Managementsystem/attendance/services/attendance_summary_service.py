from __future__ import annotations

from collections import Counter
from typing import Any

from django.db import transaction

from ..constants import AttendanceStatus
from ..models import AttendanceRecord, AttendanceSession, AttendanceSummary
from ..utils import calculate_absence_rate, calculate_attendance_percentage


class AttendanceSummaryService:
    @staticmethod
    def calculate_summary(student_id: int, academic_year_id: int, term_id: int) -> AttendanceSummary:
        summary, _ = AttendanceSummary.objects.get_or_create(
            student_id=student_id,
            academic_year_id=academic_year_id,
            term_id=term_id,
        )
        records = AttendanceRecord.objects.filter(
            student_id=student_id,
            attendance_session__academic_year_id=academic_year_id,
            attendance_session__term_id=term_id,
        )
        counts = Counter(record.status for record in records)
        summary.present_days = counts.get(AttendanceStatus.PRESENT, 0)
        summary.absent_days = counts.get(AttendanceStatus.ABSENT, 0)
        summary.late_days = counts.get(AttendanceStatus.LATE, 0)
        summary.excused_days = counts.get(AttendanceStatus.EXCUSED, 0)
        summary.attendance_percentage = calculate_attendance_percentage(summary.present_days, max(1, summary.present_days + summary.absent_days + summary.late_days + summary.excused_days))
        summary.save()
        return summary

    @staticmethod
    def calculate_percentage(present_days: int, total_days: int) -> float:
        return calculate_attendance_percentage(present_days, total_days)

    @staticmethod
    def rebuild_summary(student_id: int, academic_year_id: int, term_id: int) -> AttendanceSummary:
        return AttendanceSummaryService.calculate_summary(student_id, academic_year_id, term_id)

    @staticmethod
    def generate_reports(*args, **kwargs) -> dict[str, Any]:
        return {"status": "ok"}
