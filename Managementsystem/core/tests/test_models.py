from __future__ import annotations

from django.test import TestCase
from django.utils import timezone

from core.models import AuditLog, School


class SchoolModelTests(TestCase):
    def setUp(self) -> None:
        self.school = School.objects.create(
            name="Springfield Academy",
            code="SPRING001",
            registration_number="REG-12345",
            email="info@springfield.edu",
            phone_number="+15551234567",
            address="742 Evergreen Terrace",
            city="Springfield",
            country="US",
            website="https://springfield.edu",
        )

    def test_school_created_successfully(self) -> None:
        self.assertEqual(self.school.name, "Springfield Academy")
        self.assertFalse(self.school.is_deleted)
        self.assertTrue(self.school.is_active)
        self.assertIsNotNone(self.school.created_at)
        self.assertIsNotNone(self.school.updated_at)

    def test_activate_toggle(self) -> None:
        self.school.deactivate()
        self.assertFalse(self.school.is_active)
        self.school.activate()
        self.assertTrue(self.school.is_active)

    def test_soft_delete_and_restore(self) -> None:
        self.school.soft_delete()
        self.assertTrue(self.school.is_deleted)
        self.assertIsNotNone(self.school.deleted_at)
        self.assertFalse(School.objects.filter(pk=self.school.pk).exists())
        self.assertTrue(School.all_objects.filter(pk=self.school.pk).exists())

        self.school.restore()
        self.assertFalse(self.school.is_deleted)
        self.assertIsNone(self.school.deleted_at)
        self.assertTrue(School.objects.filter(pk=self.school.pk).exists())

    def test_hard_delete(self) -> None:
        pk = self.school.pk
        self.school.hard_delete()
        self.assertFalse(School.all_objects.filter(pk=pk).exists())


class AuditLogModelTests(TestCase):
    def test_log_creation(self) -> None:
        audit = AuditLog.objects.create(
            action="CREATE",
            model_name="School",
            object_id="1",
            description="Created school for test case",
        )
        self.assertEqual(audit.action, "CREATE")
        self.assertEqual(audit.model_name, "School")
        self.assertIsNotNone(audit.timestamp)
        self.assertTrue(audit.timestamp <= timezone.now())
