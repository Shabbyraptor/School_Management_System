from __future__ import annotations

from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    """Allow access only to superusers."""

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.is_superuser)


class IsSchoolAdmin(BasePermission):
    """Allow access to users with school administrator privileges."""

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return bool(
            getattr(user, "is_school_admin", False)
            or getattr(user, "role", None) == "SCHOOL_ADMIN"
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
