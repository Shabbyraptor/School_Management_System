from __future__ import annotations

from rest_framework.permissions import BasePermission

from accounts.permissions import IsParent, IsSchoolAdmin, IsStudent, IsSuperAdmin, IsTeacher


class CanManageAttendance(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return user.is_superuser or user.has_role("SCHOOL_ADMIN") or user.has_role("TEACHER")


class CanViewOwnAttendance(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return user.has_role("STUDENT") or user.has_role("PARENT")
