from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from academics.models import AcademicYear, Class, Stream, Term

from ..constants import StudentStatus
from ..models import Enrollment, Student


class EnrollmentService:
    @staticmethod
    @transaction.atomic
    def enroll_student(student: Student, *, academic_year: AcademicYear | None = None, term: Term | None = None, academic_class: Class | None = None, stream: Stream | None = None) -> Enrollment:
        if academic_year is None:
            academic_year = AcademicYear.objects.filter(school=student.school, is_current=True).first()
        if term is None:
            term = Term.objects.filter(academic_year=academic_year, is_current=True).first() if academic_year else None
        if academic_class is None:
            academic_class = student.current_class
        if stream is None:
            stream = student.current_stream
        return Enrollment.objects.create(
            student=student,
            academic_year=academic_year,
            term=term,
            class_field=academic_class,
            stream=stream,
            enrollment_date=timezone.localdate(),
            status="ACTIVE",
        )

    @staticmethod
    @transaction.atomic
    def change_stream(enrollment: Enrollment, stream: Stream) -> Enrollment:
        enrollment.stream = stream
        enrollment.save(update_fields=["stream", "updated_at"])
        return enrollment

    @staticmethod
    @transaction.atomic
    def change_class(enrollment: Enrollment, academic_class: Class) -> Enrollment:
        enrollment.class_field = academic_class
        enrollment.save(update_fields=["class_field", "updated_at"])
        return enrollment

    @staticmethod
    @transaction.atomic
    def withdraw_enrollment(enrollment: Enrollment) -> Enrollment:
        enrollment.status = "COMPLETED"
        enrollment.save(update_fields=["status", "updated_at"])
        return enrollment
