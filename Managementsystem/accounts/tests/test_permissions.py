from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Role
from accounts.permissions import IsSchoolAdmin, IsSuperAdmin

User = get_user_model()


class PermissionClassesTest(TestCase):
    def setUp(self) -> None:
        self.super_user = User.objects.create_superuser(
            email="super@test.com",
            username="superuser",
            password="password123",
        )
        self.school_admin = User.objects.create_user(
            email="admin@test.com",
            username="schooladmin",
            password="password123",
        )
        self.role = Role.objects.create(name="School Admin", code="SCHOOL_ADMIN")
        self.school_admin.roles.add(self.role)

    def test_is_super_admin_permission(self) -> None:
        request = type("Request", (), {"user": self.super_user})
        perm = IsSuperAdmin()
        self.assertTrue(perm.has_permission(request, None))

    def test_is_school_admin_permission(self) -> None:
        request = type("Request", (), {"user": self.school_admin})
        perm = IsSchoolAdmin()
        self.assertTrue(perm.has_permission(request, None))
