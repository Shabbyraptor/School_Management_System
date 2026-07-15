from __future__ import annotations

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import School

User = get_user_model()


class SchoolAPITests(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_superuser(
            email="admin@test.com",
            username="admin",
            password="password123",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)
        self.school = School.objects.create(
            name="Central School",
            code="CENTRAL01",
            registration_number="REG-33333",
            email="contact@central.edu",
            phone_number="+15550987654",
            country="US",
        )

    def test_list_schools(self) -> None:
        url = reverse("school-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["results"])

    def test_create_school(self) -> None:
        url = reverse("school-list")
        payload = {
            "name": "Westside School",
            "code": "WEST001",
            "registration_number": "REG-44444",
            "email": "hello@westside.edu",
            "phone_number": "+15559876543",
            "country": "CA",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["code"], "WEST001")

    def test_activate_deactivate_school(self) -> None:
        url = reverse("school-activate", args=[self.school.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_active"])

        url = reverse("school-deactivate", args=[self.school.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_active"])


class AuditLogAPITests(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_superuser(username="superadmin", password="password123", email="superadmin@test.com")
        self.client.force_authenticate(user=self.user)
        self.school = School.objects.create(
            name="East Academy",
            code="EAST002",
            registration_number="REG-55555",
            email="hello@eastacademy.edu",
            phone_number="+15557654322",
            country="GB",
        )

    def test_audit_log_list(self) -> None:
        from core.services.audit_service import AuditLogService

        AuditLogService.log_action(
            action="CREATE",
            model_name="School",
            object_id=str(self.school.pk),
            description="Audit log record",
            user=self.user,
            school=self.school,
            ip_address="127.0.0.1",
        )

        url = reverse("auditlog-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["results"])
