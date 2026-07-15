from __future__ import annotations

from django.test import TestCase

from core.models import School
from core.services.audit_service import AuditLogService
from core.services.school_service import SchoolService


class SchoolServiceTests(TestCase):
    def test_create_school(self) -> None:
        payload = {
            "name": "Eastside High",
            "code": "EAST001",
            "registration_number": "REG-98765",
            "email": "hello@eastside.edu",
            "phone_number": "+15557654321",
            "address": "12 Elm Street",
            "city": "Easton",
            "country": "GB",
            "website": "https://eastside.edu",
            "is_active": True,
        }
        school = SchoolService.create_school(payload)
        self.assertIsInstance(school, School)
        self.assertEqual(school.code, "EAST001")
        self.assertEqual(school.registration_number, "REG-98765")

    def test_update_school(self) -> None:
        school = School.objects.create(
            name="North High",
            code="NORTH001",
            registration_number="REG-11111",
            email="contact@north.edu",
            phone_number="+15550001111",
            country="CA",
        )
        updated = SchoolService.update_school(school, {"name": "North High Updated", "email": "new@north.edu"})
        self.assertEqual(updated.name, "North High Updated")
        self.assertEqual(updated.email, "new@north.edu")

    def test_activate_deactivate_school(self) -> None:
        school = School.objects.create(
            name="South High",
            code="SOUTH001",
            registration_number="REG-22222",
            email="info@south.edu",
            phone_number="+15552223333",
            country="AU",
            is_active=False,
        )
        SchoolService.activate_school(school)
        self.assertTrue(school.is_active)
        SchoolService.deactivate_school(school)
        self.assertFalse(school.is_active)


class AuditLogServiceTests(TestCase):
    def test_log_action_creates_audit_entry(self) -> None:
        audit = AuditLogService.log_action(
            action="CREATE",
            model_name="School",
            object_id="1",
            description="Created a school record",
            user=None,
            school=None,
            ip_address="127.0.0.1",
        )

        self.assertEqual(audit.action, "CREATE")
        self.assertEqual(audit.model_name, "School")
        self.assertEqual(audit.object_id, "1")
        self.assertEqual(audit.ip_address, "127.0.0.1")
