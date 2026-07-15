from __future__ import annotations

from django.test import TestCase

from accounts.models import Permission, Role, RolePermission, User, UserProfile, UserRole
from core.models import School


class AccountModelsTest(TestCase):
    def setUp(self) -> None:
        self.school = School.objects.create(
            name="Test School",
            code="TEST001",
            registration_number="REG-99999",
            email="school@test.com",
            phone_number="+15550009999",
            address="123 Test Lane",
            city="Testville",
            country="US",
        )

    def test_user_creation_and_profile_auto_created(self) -> None:
        user = User.objects.create_user(
            email="user@test.com",
            username="user1",
            password="password123",
            school=self.school,
        )
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        self.assertFalse(user.is_staff)

    def test_role_permission_assignment(self) -> None:
        role = Role.objects.create(name="Teacher", code="TEACHER")
        permission = Permission.objects.create(name="View Students", code="student.view", module="student")
        RolePermission.objects.create(role=role, permission=permission)
        self.assertTrue(role.permissions.filter(code="student.view").exists())

    def test_user_role_relationship(self) -> None:
        role = Role.objects.create(name="Parent", code="PARENT")
        user = User.objects.create_user(
            email="parent@test.com",
            username="parent1",
            password="password123",
            school=self.school,
        )
        UserRole.objects.create(user=user, role=role)
        self.assertTrue(user.has_role("PARENT"))
