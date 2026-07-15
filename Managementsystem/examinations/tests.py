from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.test import TestCase

from accounts.models import User
from academics.models import AcademicYear, Class, Stream, Subject, Term
from core.models import School
from students.models import Student

from .constants import ResultStatus
from .models import Exam, ExamType, GradeScale, Mark, Result
from .services import ExamService, MarkService, ResultService


class ExaminationsDomainTests(TestCase):
    def setUp(self) -> None:
        self.school = School.objects.create(
            name="Bright Future School",
            code="BFS002",
            registration_number="REG-002",
            email="exam@brightfuture.edu",
            phone_number="+254700000002",
            address="Nairobi",
            city="Nairobi",
            country="KE",
        )
        self.user = User.objects.create_user(
            email="examiner@brightfuture.edu",
            username="examiner1",
            password="secret1234",
            school=self.school,
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
        self.academic_class = Class.objects.create(
            school=self.school,
            name="Grade 4",
            code="G4",
            education_level="PRIMARY",
            display_order=4,
            is_active=True,
        )
        self.stream = Stream.objects.create(
            school=self.school,
            academic_class=self.academic_class,
            name="A",
            capacity=30,
            class_teacher=self.user,
            is_active=True,
        )
        self.subject = Subject.objects.create(
            school=self.school,
            name="English",
            code="ENG",
            short_name="ENG",
            category="LANGUAGES",
            description="English subject",
            is_compulsory=True,
            is_active=True,
        )
        self.student = Student.objects.create(
            school=self.school,
            admission_number="ADM-1001",
            first_name="Jane",
            last_name="Doe",
        )
        self.exam_type = ExamType.objects.create(
            school=self.school,
            name="End Term",
            code="ET1",
            description="End term assessment",
            is_active=True,
        )
        GradeScale.objects.create(
            school=self.school,
            name="Distinction",
            minimum_mark=80,
            maximum_mark=100,
            grade="A",
            remarks="Excellent",
            order=1,
        )
        GradeScale.objects.create(
            school=self.school,
            name="Credit",
            minimum_mark=60,
            maximum_mark=79,
            grade="B",
            remarks="Good",
            order=2,
        )

    def test_exam_mark_and_result_workflow(self) -> None:
        exam = ExamService.create_exam(
            {
                "school": self.school,
                "exam_type": self.exam_type,
                "academic_year": self.academic_year,
                "term": self.term,
                "class_name": self.academic_class,
                "stream": self.stream,
                "subject": self.subject,
                "name": "English Midterm",
                "assessment_type": "MIDTERM",
                "total_marks": 100,
                "pass_mark": 40,
                "start_date": date(2025, 2, 1),
                "end_date": date(2025, 2, 5),
                "status": "OPEN",
                "created_by": self.user,
            }
        )

        self.assertIsInstance(exam, Exam)
        self.assertTrue(exam.code.startswith(self.school.code))

        mark = MarkService.record_mark(
            {
                "exam": exam,
                "student": self.student,
                "marks_obtained": Decimal("80"),
                "total_marks": Decimal("100"),
                "entered_by": self.user,
            }
        )

        self.assertIsInstance(mark, Mark)
        self.assertEqual(mark.percentage, Decimal("80.00"))

        result = ResultService.generate_result(mark)
        self.assertIsInstance(result, Result)
        self.assertEqual(result.grade, "A")
        self.assertEqual(result.status, ResultStatus.DRAFT)

        published_result = ResultService.publish_result(result)
        self.assertEqual(published_result.status, ResultStatus.PUBLISHED)
        self.assertTrue(published_result.report_card_number.startswith("RC-"))
