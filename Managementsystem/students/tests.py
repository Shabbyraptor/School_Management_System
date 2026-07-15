from __future__ import annotations

from datetime import date

from django.test import TestCase

from academics.models import AcademicYear, Class, Stream, Term
from core.models import School

from .models import Enrollment, Student
from .services import EnrollmentService, StudentService


class StudentsDomainTests(TestCase):
    def setUp(self) -> None:
        self.school = School.objects.create(
            name="Bright Future School",
            code="BFS002",
            registration_number="REG-002",
            email="students@brightfuture.edu",
            phone_number="+254700000002",
            address="Nairobi",
            city="Nairobi",
            country="KE",
        )
        self.academic_class = Class.objects.create(
            school=self.school,
            name="Grade 1",
            code="G1A",
            education_level="PRIMARY",
            display_order=1,
            is_active=True,
        )
        self.stream = Stream.objects.create(
            school=self.school,
            academic_class=self.academic_class,
            name="A",
            capacity=30,
            is_active=True,
        )
        self.academic_year = AcademicYear.objects.create(
            school=self.school,
            name="2025/2026",
            code="AY2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            is_current=True,
            is_active=True,
        )
        self.term = Term.objects.create(
            academic_year=self.academic_year,
            name="Term 1",
            number=1,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
            is_current=True,
            is_active=True,
        )

    def test_student_admission_and_enrollment_workflow(self) -> None:
        student = StudentService.admit_student(
            {
                "first_name": "Jane",
                "last_name": "Doe",
                "gender": "FEMALE",
                "date_of_birth": date(2015, 3, 1),
                "admission_date": date(2025, 1, 10),
                "email": "jane@example.com",
                "phone_number": "+254700000003",
                "current_class": self.academic_class,
                "current_stream": self.stream,
            },
            self.school,
        )
        enrollment = EnrollmentService.enroll_student(student, academic_year=self.academic_year, term=self.term, academic_class=self.academic_class, stream=self.stream)

        self.assertEqual(student.status, "APPLICANT")
        self.assertTrue(student.admission_number)
        self.assertEqual(enrollment.student, student)
        self.assertEqual(enrollment.status, "ACTIVE")

    def test_student_promotion_and_graduation(self) -> None:
        student = StudentService.admit_student(
            {
                "first_name": "John",
                "last_name": "Smith",
                "gender": "MALE",
                "date_of_birth": date(2014, 5, 5),
                "admission_date": date(2025, 1, 10),
                "email": "john@example.com",
                "phone_number": "+254700000004",
                "current_class": self.academic_class,
                "current_stream": self.stream,
            },
            self.school,
        )
        StudentService.promote_student(student, target_class=self.academic_class, target_stream=self.stream, academic_year=self.academic_year, term=self.term)
        StudentService.graduate_student(student)

        self.assertEqual(student.status, "GRADUATED")
        self.assertTrue(Enrollment.objects.filter(student=student).exists())
