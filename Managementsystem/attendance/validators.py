from __future__ import annotations

from datetime import date

from django.core.exceptions import ValidationError


def validate_attendance_date(attendance_date: date | None) -> None:
    if attendance_date is None:
        return
    if attendance_date > date.today():
        raise ValidationError("Attendance date cannot be in the future.")


def validate_session_uniqueness(existing_sessions, attendance_date, class_obj, stream, session_type) -> None:
    if existing_sessions.filter(
        attendance_date=attendance_date,
        class_field=class_obj,
        stream=stream,
        session_type=session_type,
    ).exists():
        raise ValidationError("An attendance session already exists for this class, stream, date, and session type.")


def validate_student_class(student, class_obj, stream) -> None:
    if student.current_class_id != class_obj.id:
        raise ValidationError("Student does not belong to the selected class.")
    if stream and student.current_stream_id != stream.id:
        raise ValidationError("Student does not belong to the selected stream.")
