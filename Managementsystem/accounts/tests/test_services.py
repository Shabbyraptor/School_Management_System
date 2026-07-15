from __future__ import annotations

from django.test import TestCase

from accounts.models import Permission, Role, User
from accounts.services.auth_service import AuthenticationService
from accounts.services.role_service import RoleService
from accounts.services.user_service import UserService
from core.models import School


class UserServiceTests(TestCase):
    def setUp(self) -> None:
        self.school = School.objects.create(
            name="Service School",
            code="SERV001",
            registration_number="REG-88888",
            email="service@test.com",
            phone_number="+15558888888",
            address="123 Service Street",
            city="Service City",
            country="US",
        )

    def test_create_user(self) -> None:
        user = UserService.create_user(
            email="testuser@test.com",
            username="testuser",
            password="password123",
            school=self.school,
        )
        self.assertIsInstance(user, User)
        self.assertTrue(user.check_password("password123"))

    def test_deactivate_activate_user(self) -> None:
        user = UserService.create_user(
            email="toggle@test.com",
            username="toggleuser",
            password="password123",
            school=self.school,
        )
        UserService.deactivate_user(user)
        self.assertFalse(user.is_active)
        UserService.activate_user(user)
        self.assertTrue(user.is_active)


class RoleServiceTests(TestCase):
    def setUp(self) -> None:
        self.role = Role.objects.create(name="Teacher", code="TEACHER")
        self.permission = Permission.objects.create(name="Manage Students", code="student.manage", module="student")
        self.user = User.objects.create_user(
            email="roleuser@test.com",
            username="roleuser",
            password="password123",
        )

    def test_assign_role(self) -> None:
        RoleService.assign_roles(self.user, ["TEACHER"])
        self.assertTrue(self.user.has_role("TEACHER"))

    def test_check_permission(self) -> None:
        self.role.permissions.add(self.permission)
        self.user.roles.add(self.role)
        self.assertTrue(RoleService.check_permission(self.user, "student.manage"))


class AuthServiceTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="authuser@test.com",
            username="authuser",
            password="authpassword",
        )

    def test_login_generates_tokens(self) -> None:
        tokens = AuthenticationService.login(email="authuser@test.com", password="authpassword")
        self.assertIn("access", tokens)
        self.assertIn("refresh", tokens)
