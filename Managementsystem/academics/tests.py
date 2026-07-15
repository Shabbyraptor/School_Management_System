from __future__ import annotations

from datetime import date, timedelta

from django.test import TestCase

from accounts.models import User
from core.models import School

from .models import AcademicYear, Class, Stream, Subject, SubjectAssignment, Term
from .services import AcademicYearService, ClassService, SubjectAssignmentService, SubjectService


class AcademicsDomainTests(TestCase):
    def setUp(self) -> None:
        self.school = School.objects.create(
            name="Bright Future School",
            code="BFS001",
            registration_number="REG-001",
            email="admin@brightfuture.edu",
            phone_number="+254700000001",
            address="Nairobi",
            city="Nairobi",
            country="KE",
        )
        self.user = User.objects.create_user(
            email="teacher@brightfuture.edu",
            username="teacher1",
            password="secret1234",
            school=self.school,
        )

    def test_academic_year_service_creates_and_activates_year(self) -> None:
        year = AcademicYearService.create_year(
            {
                "school": self.school,
                "name": "2024/2025",
                "code": "AY2024",
                "start_date": date(2024, 1, 1),
                "end_date": date(2024, 12, 31),
                "is_current": False,
                "is_active": False,
            }
        )

        self.assertTrue(AcademicYear.objects.filter(pk=year.pk).exists())
        self.assertFalse(year.is_current)

        activated = AcademicYearService.activate_year(year)
        self.assertTrue(activated.is_current)
        self.assertTrue(activated.is_active)

    def test_class_and_subject_services_create_related_records(self) -> None:
        academic_class = ClassService.create_class(
            {
                "school": self.school,
                "name": "Grade 1",
                "code": "G1",
                "education_level": "PRIMARY",
                "display_order": 1,
                "is_active": True,
            }
        )
        subject = SubjectService.create_subject(
            {
                "school": self.school,
                "name": "Mathematics",
                "code": "MATH",
                "short_name": "MTH",
                "category": "LANGUAGES",
                "description": "Core mathematics",
                "is_compulsory": True,
                "is_active": True,
            }
        )
        stream = Stream.objects.create(
            school=self.school,
            academic_class=academic_class,
            name="A",
            capacity=30,
            class_teacher=self.user,
            is_active=True,
        )
        academic_year = AcademicYear.objects.create(
            school=self.school,
            name="2025/2026",
            code="AY2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            is_current=True,
            is_active=True,
        )
        term = Term.objects.create(
            academic_year=academic_year,
            name="Term 1",
            number=1,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
            is_current=True,
            is_active=True,
        )
        assignment = SubjectAssignmentService.assign_teacher(
            {
                "teacher": self.user,
                "subject": subject,
                "academic_class": academic_class,
                "stream": stream,
                "academic_year": academic_year,
                "term": term,
            }
        )

        self.assertIsInstance(academic_class, Class)
        self.assertIsInstance(subject, Subject)
        self.assertEqual(stream.academic_class, academic_class)
        self.assertEqual(assignment.subject, subject)
        self.assertEqual(assignment.term, term)
