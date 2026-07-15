from __future__ import annotations

from rest_framework.permissions import BasePermission


class IsSchoolAdminOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and (user.is_superuser or user.has_role("SCHOOL_ADMIN")))


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.has_role("TEACHER"))


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.has_role("STUDENT"))


class IsParent(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.has_role("PARENT"))
