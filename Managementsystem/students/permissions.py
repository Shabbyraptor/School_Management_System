from __future__ import annotations

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSchoolAdminOrAdmissionsOfficer(BasePermission):
    def has_permission(self, request, view) -> bool:
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.has_role("SCHOOL_ADMIN") or request.user.has_role("ADMISSIONS_OFFICER")


class IsStudentOwner(BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj) -> bool:
        if request.user.is_superuser:
            return True
        if request.user.has_role("SCHOOL_ADMIN") or request.user.has_role("ADMISSIONS_OFFICER"):
            return True
        if hasattr(obj, "user") and obj.user_id == request.user.id:
            return True
        return False


class IsParentLinked(BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj) -> bool:
        if request.user.is_superuser:
            return True
        if request.user.has_role("SCHOOL_ADMIN") or request.user.has_role("ADMISSIONS_OFFICER"):
            return True
        return any(link.parent.user_id == request.user.id for link in getattr(obj, "parent_links", []))
