from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import Role
from core.models import School

User = get_user_model()


class AccountsAPITest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.school = School.objects.create(
            name="APITest School",
            code="APIT001",
            registration_number="REG-12345",
            email="schoolapi@test.com",
            phone_number="+15550123456",
            address="100 Api Street",
            city="ApiCity",
            country="US",
        )
        self.superuser = User.objects.create_superuser(
            email="superapi@test.com",
            username="superapi",
            password="password123",
        )
        self.client.force_authenticate(self.superuser)

    def test_create_user_endpoint(self) -> None:
        response = self.client.post(
            "/api/accounts/users/",
            {
                "email": "newuser@test.com",
                "username": "newuser",
                "password": "password123",
                "school": self.school.pk,
                "role_codes": ["SCHOOL_ADMIN"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["email"], "newuser@test.com")

    def test_list_roles_endpoint(self) -> None:
        Role.objects.create(name="Teacher", code="TEACHER")
        response = self.client.get("/api/accounts/roles/")
        self.assertEqual(response.status_code, 200)
