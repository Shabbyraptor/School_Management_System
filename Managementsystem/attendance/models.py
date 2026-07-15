from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from academics.models import AcademicYear, Class, Stream, Term
from core.models import BaseModel, School
from students.models import Student

from .constants import AttendanceSessionStatus, AttendanceSessionType, AttendanceStatus
from .utils import calculate_absence_rate, calculate_attendance_percentage, generate_attendance_reference
from .validators import validate_attendance_date, validate_session_uniqueness, validate_student_class


class AttendanceSession(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="attendance_sessions")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="attendance_sessions")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="attendance_sessions")
    attendance_date = models.DateField()
    class_field = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="attendance_sessions", db_column="class_id")
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name="attendance_sessions", db_column="stream_id", null=True, blank=True)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="recorded_sessions", null=True, blank=True)
    session_type = models.CharField(max_length=20, choices=AttendanceSessionType.choices, default=AttendanceSessionType.MORNING)
    status = models.CharField(max_length=20, choices=AttendanceSessionStatus.choices, default=AttendanceSessionStatus.OPEN)
    remarks = models.TextField(blank=True)
    reference = models.CharField(max_length=100, unique=True, blank=True)

    class Meta:
        ordering = ["-attendance_date", "class_field__name", "stream__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["school", "attendance_date", "class_field", "stream", "session_type"],
                name="unique_attendance_session",
            )
        ]

    def __str__(self) -> str:
        return f"{self.class_field.name} - {self.attendance_date} - {self.session_type}"

    def clean(self) -> None:
        super().clean()
        validate_attendance_date(self.attendance_date)

        existing_sessions = AttendanceSession.objects.filter(school=self.school)
        if self.pk:
            existing_sessions = existing_sessions.exclude(pk=self.pk)

        validate_session_uniqueness(
            existing_sessions,
            self.attendance_date,
            self.class_field,
            self.stream,
            self.session_type,
        )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        if not self.reference:
            self.reference = generate_attendance_reference(self.school.code, self.attendance_date, self.session_type)
        return super().save(*args, **kwargs)

    def open_session(self) -> None:
        self.status = AttendanceSessionStatus.OPEN
        self.save(update_fields=["status", "updated_at"])

    def close_session(self) -> None:
        self.status = AttendanceSessionStatus.CLOSED
        self.save(update_fields=["status", "updated_at"])

    def archive_session(self) -> None:
        self.status = AttendanceSessionStatus.ARCHIVED
        self.save(update_fields=["status", "updated_at"])


class AttendanceRecord(BaseModel):
    attendance_session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name="records")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_records")
    status = models.CharField(max_length=20, choices=AttendanceStatus.choices, default=AttendanceStatus.PRESENT)
    time_marked = models.DateTimeField(auto_now_add=True)
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="marked_attendance", null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["student__first_name", "student__last_name"]
        constraints = [
            models.UniqueConstraint(fields=["attendance_session", "student"], name="unique_student_session_record")
        ]

    def __str__(self) -> str:
        return f"{self.student.full_name} - {self.attendance_session.reference}"

    def clean(self) -> None:
        super().clean()
        if self.attendance_session_id and self.student_id:
            validate_student_class(self.student, self.attendance_session.class_field, self.attendance_session.stream)
            if self.attendance_session.status == AttendanceSessionStatus.CLOSED and not self._state.adding:
                raise ValidationError("Closed sessions cannot be edited.")

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)

    def mark_present(self) -> None:
        self.status = AttendanceStatus.PRESENT
        self.save(update_fields=["status", "updated_at"])

    def mark_absent(self) -> None:
        self.status = AttendanceStatus.ABSENT
        self.save(update_fields=["status", "updated_at"])

    def mark_late(self) -> None:
        self.status = AttendanceStatus.LATE
        self.save(update_fields=["status", "updated_at"])

    def mark_excused(self) -> None:
        self.status = AttendanceStatus.EXCUSED
        self.save(update_fields=["status", "updated_at"])


class AttendanceSummary(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_summaries")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="attendance_summaries")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="attendance_summaries")
    present_days = models.PositiveIntegerField(default=0)
    absent_days = models.PositiveIntegerField(default=0)
    late_days = models.PositiveIntegerField(default=0)
    excused_days = models.PositiveIntegerField(default=0)
    attendance_percentage = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_updated"]
        constraints = [
            models.UniqueConstraint(fields=["student", "academic_year", "term"], name="unique_student_summary")
        ]

    def __str__(self) -> str:
        return f"{self.student.full_name} - {self.academic_year.code}"

    def refresh(self) -> None:
        total_days = self.present_days + self.absent_days + self.late_days + self.excused_days
        self.attendance_percentage = calculate_attendance_percentage(self.present_days, total_days)
        self.save(update_fields=["present_days", "absent_days", "late_days", "excused_days", "attendance_percentage", "last_updated"])
