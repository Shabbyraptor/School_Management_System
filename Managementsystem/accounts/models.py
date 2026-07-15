from __future__ import annotations

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from core.models import BaseModel, School
from core.validators import phone_number_validator
from .managers import UserManager


class Role(models.Model):
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    is_system_role = models.BooleanField(default=False)
    permissions = models.ManyToManyField(
        "Permission",
        through="RolePermission",
        related_name="roles",
        blank=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Permission(models.Model):
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)
    module = models.CharField(max_length=128)

    class Meta:
        ordering = ["module", "code"]

    def __str__(self) -> str:
        return self.code


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_permissions")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="permission_roles")

    class Meta:
        unique_together = (("role", "permission"),)
        ordering = ["role__name", "permission__code"]

    def __str__(self) -> str:
        return f"{self.role.code} -> {self.permission.code}"


class UserRole(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_assignments")

    class Meta:
        unique_together = (("user", "role"),)
        ordering = ["user__email", "role__code"]

    def __str__(self) -> str:
        return f"{self.user.email} - {self.role.code}"


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
        ("unspecified", "Unspecified"),
    ]

    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="profile")
    gender = models.CharField(max_length=12, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=120, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=2, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"Profile for {self.user.email}"


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True, related_name="users")
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=120, blank=True)
    last_name = models.CharField(max_length=120, blank=True)
    phone_number = models.CharField(max_length=20, validators=[phone_number_validator], blank=True)
    profile_photo = models.ImageField(upload_to="users/photos/", blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_staff = models.BooleanField(default=False, db_index=True)
    is_verified = models.BooleanField(default=False, db_index=True)
    date_joined = models.DateTimeField(default=timezone.now)
    roles = models.ManyToManyField(Role, through="UserRole", related_name="users", blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        ordering = ["email"]

    def __str__(self) -> str:
        return self.email

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self) -> str:
        return self.first_name or self.email

    def activate(self) -> None:
        self.is_active = True
        self.save(update_fields=["is_active", "updated_at"])

    def deactivate(self) -> None:
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])

    @property
    def roles_list(self) -> list[str]:
        return list(self.roles.values_list("code", flat=True))

    def has_role(self, role_code: str) -> bool:
        return self.roles.filter(code=role_code).exists()

    def has_permission(self, permission_code: str) -> bool:
        return self.roles.filter(permissions__code=permission_code).exists()
