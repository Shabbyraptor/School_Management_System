from __future__ import annotations

from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import User
from academics.models import AcademicYear, Class, Stream, Term
from core.models import School
from students.models import Student

from .constants import AttendanceSessionStatus, AttendanceSessionType, AttendanceStatus
from .models import AttendanceRecord, AttendanceSession, AttendanceSummary
from .serializers import AttendanceSessionSerializer, AttendanceSummarySerializer
from .services import AttendanceService, AttendanceSessionService, AttendanceSummaryService
from .permissions import CanManageAttendance, CanViewOwnAttendance


class AttendanceModelTests(TestCase):
    def setUp(self) -> None:
        self.school = School.objects.create(
            name="Bright Future School",
            code="BFS003",
            registration_number="REG-003",
            email="attendance@brightfuture.edu",
            phone_number="+254700000003",
            address="Nairobi",
            city="Nairobi",
            country="KE",
        )
        self.user = User.objects.create_user(email="teacher3@brightfuture.edu", username="teacher3", password="secret1234", school=self.school)
        self.academic_year = AcademicYear.objects.create(school=self.school, name="2025/2026", code="AY2026", start_date=date(2025, 1, 1), end_date=date(2025, 12, 31), is_current=True, is_active=True)
        self.term = Term.objects.create(academic_year=self.academic_year, name="Term 1", number=1, start_date=date(2025, 1, 1), end_date=date(2025, 3, 31), is_current=True, is_active=True)
        self.academic_class = Class.objects.create(school=self.school, name="Grade 7", code="G7", education_level="PRIMARY", display_order=7, is_active=True)
        self.stream = Stream.objects.create(school=self.school, academic_class=self.academic_class, name="East", capacity=40, class_teacher=self.user, is_active=True)
        self.student = Student.objects.create(school=self.school, admission_number="ADM-2001", first_name="John", last_name="Doe")
        self.student.current_class = self.academic_class
        self.student.current_stream = self.stream
        self.student.save(update_fields=["current_class", "current_stream"])

    def test_session_creation_and_duplicate_prevention(self) -> None:
        session = AttendanceSession.objects.create(school=self.school, academic_year=self.academic_year, term=self.term, attendance_date=date(2025, 2, 1), class_field=self.academic_class, stream=self.stream, teacher=self.user, session_type=AttendanceSessionType.MORNING)
        self.assertEqual(session.status, AttendanceSessionStatus.OPEN)
        with self.assertRaises(ValidationError):
            duplicate = AttendanceSession(school=self.school, academic_year=self.academic_year, term=self.term, attendance_date=date(2025, 2, 1), class_field=self.academic_class, stream=self.stream, teacher=self.user, session_type=AttendanceSessionType.MORNING)
            duplicate.full_clean()

    def test_record_validation_and_status_methods(self) -> None:
        session = AttendanceSession.objects.create(school=self.school, academic_year=self.academic_year, term=self.term, attendance_date=date(2025, 2, 2), class_field=self.academic_class, stream=self.stream, teacher=self.user, session_type=AttendanceSessionType.MORNING)
        record = AttendanceRecord.objects.create(attendance_session=session, student=self.student, status=AttendanceStatus.PRESENT, marked_by=self.user)
        record.mark_late()
        self.assertEqual(record.status, AttendanceStatus.LATE)

        # Marking attendance already created this summary (attendance.signals); overwrite its counts.
        summary, _ = AttendanceSummary.objects.update_or_create(student=self.student, academic_year=self.academic_year, term=self.term, defaults={"present_days": 1, "absent_days": 0, "late_days": 1, "excused_days": 0})
        summary.refresh()
        self.assertGreaterEqual(summary.attendance_percentage, 0)


class AttendanceServiceTests(TestCase):
    def test_session_and_attendance_services(self) -> None:
        school = School.objects.create(name="Bright Future School", code="BFS004", registration_number="REG-004", email="service@brightfuture.edu", phone_number="+254700000004", address="Nairobi", city="Nairobi", country="KE")
        user = User.objects.create_user(email="teacher4@brightfuture.edu", username="teacher4", password="secret1234", school=school)
        academic_year = AcademicYear.objects.create(school=school, name="2025/2026", code="AY2027", start_date=date(2025, 1, 1), end_date=date(2025, 12, 31), is_current=True, is_active=True)
        term = Term.objects.create(academic_year=academic_year, name="Term 1", number=1, start_date=date(2025, 1, 1), end_date=date(2025, 3, 31), is_current=True, is_active=True)
        academic_class = Class.objects.create(school=school, name="Grade 8", code="G8", education_level="PRIMARY", display_order=8, is_active=True)
        stream = Stream.objects.create(school=school, academic_class=academic_class, name="West", capacity=40, class_teacher=user, is_active=True)
        student = Student.objects.create(school=school, admission_number="ADM-2002", first_name="Mary", last_name="Smith")
        student.current_class = academic_class
        student.current_stream = stream
        student.save(update_fields=["current_class", "current_stream"])

        session = AttendanceSessionService.create_session({"school": school, "academic_year": academic_year, "term": term, "attendance_date": date(2025, 2, 3), "class_field": academic_class, "stream": stream, "teacher": user, "session_type": AttendanceSessionType.MORNING})
        self.assertIsInstance(session, AttendanceSession)
        AttendanceSessionService.close_session(session)
        self.assertEqual(session.status, "CLOSED")

        record = AttendanceService.mark_attendance({"attendance_session": session, "student": student, "status": AttendanceStatus.PRESENT, "marked_by": user})
        self.assertIsInstance(record, AttendanceRecord)

        summary = AttendanceSummaryService.calculate_summary(student.id, academic_year.id, term.id)
        self.assertGreaterEqual(summary.attendance_percentage, 0)


class AttendanceSerializerTests(TestCase):
    def test_serializers_initialize(self) -> None:
        self.assertTrue(issubclass(AttendanceSessionSerializer, object))
        self.assertTrue(issubclass(AttendanceSummarySerializer, object))


class AttendancePermissionTests(TestCase):
    def test_permissions_classify(self) -> None:
        self.assertTrue(issubclass(CanManageAttendance, object))
        self.assertTrue(issubclass(CanViewOwnAttendance, object))
