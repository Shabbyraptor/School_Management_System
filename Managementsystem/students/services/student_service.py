from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from core.models import School
from academics.models import AcademicYear, Class, Stream, Term

from ..constants import StudentStatus
from ..models import Enrollment, Student
from ..utils import generate_admission_number


class StudentService:
    @staticmethod
    @transaction.atomic
    def admit_student(data: dict[str, Any], school: School) -> Student:
        admission_count = Student.objects.filter(school=school).count() + 1
        data.setdefault("admission_number", generate_admission_number(school.code, admission_count))
        data.setdefault("status", StudentStatus.APPLICANT)
        data.setdefault("admission_date", timezone.localdate())
        return Student.objects.create(school=school, **data)

    @staticmethod
    @transaction.atomic
    def promote_student(student: Student, *, target_class: Class | None = None, target_stream: Stream | None = None, academic_year: AcademicYear | None = None, term: Term | None = None) -> Enrollment:
        if student.status == StudentStatus.GRADUATED:
            raise ValueError("Graduated students cannot be promoted.")
        if academic_year is None:
            academic_year = AcademicYear.objects.filter(school=student.school, is_current=True).first()
        if term is None:
            term = Term.objects.filter(academic_year=academic_year, is_current=True).first() if academic_year else None
        if target_class is None:
            target_class = student.current_class
        if target_stream is None:
            target_stream = student.current_stream
        enrollment = Enrollment.objects.create(
            student=student,
            academic_year=academic_year,
            term=term,
            class_field=target_class,
            stream=target_stream,
            enrollment_date=timezone.localdate(),
            status="ACTIVE",
        )
        student.current_class = target_class
        student.current_stream = target_stream
        student.status = StudentStatus.ACTIVE
        student.save(update_fields=["current_class", "current_stream", "status", "updated_at"])
        return enrollment

    @staticmethod
    @transaction.atomic
    def transfer_student(student: Student, *, target_class: Class | None = None, target_stream: Stream | None = None, academic_year: AcademicYear | None = None, term: Term | None = None, internal: bool = True) -> Enrollment:
        if academic_year is None:
            academic_year = AcademicYear.objects.filter(school=student.school, is_current=True).first()
        if term is None:
            term = Term.objects.filter(academic_year=academic_year, is_current=True).first() if academic_year else None
        enrollment = Enrollment.objects.create(
            student=student,
            academic_year=academic_year,
            term=term,
            class_field=target_class or student.current_class,
            stream=target_stream or student.current_stream,
            enrollment_date=timezone.localdate(),
            status="TRANSFERRED",
        )
        student.status = StudentStatus.TRANSFERRED
        student.current_class = target_class or student.current_class
        student.current_stream = target_stream or student.current_stream
        student.save(update_fields=["status", "current_class", "current_stream", "updated_at"])
        return enrollment

    @staticmethod
    @transaction.atomic
    def graduate_student(student: Student) -> Student:
        student.status = StudentStatus.GRADUATED
        student.save(update_fields=["status", "updated_at"])
        return student

    @staticmethod
    @transaction.atomic
    def archive_student(student: Student) -> Student:
        student.status = StudentStatus.ALUMNI
        student.save(update_fields=["status", "updated_at"])
        return student

    @staticmethod
    @transaction.atomic
    def update_profile(student: Student, data: dict[str, Any]) -> Student:
        for field, value in data.items():
            setattr(student, field, value)
        student.save()
        return student
