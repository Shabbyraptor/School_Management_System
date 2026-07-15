from __future__ import annotations

from rest_framework.permissions import BasePermission


class HasRole(BasePermission):
    def __init__(self, role_code: str) -> None:
        self.role_code = role_code

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.has_role(self.role_code))


class HasPermission(BasePermission):
    def __init__(self, permission_code: str) -> None:
        self.permission_code = permission_code

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.has_permission(self.permission_code))


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.is_superuser)


class IsSchoolAdmin(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or user.has_role("SCHOOL_ADMIN"))
        )


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.has_role("TEACHER"))


class IsParent(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.has_role("PARENT"))


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.has_role("STUDENT"))
