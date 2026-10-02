"""Role-based access policy for the whole API.

One table (POLICY) says which role codes may read and which may write each area of the
API. `RolePolicy` enforces it on every viewset, `ScopedQuerysetMixin` limits rows to the
user's school (and, for parents/students, to their own children/themselves), and
`access_for()` hands the same table to the frontend so the UI shows exactly what the
API allows. Superusers bypass all of it.
"""
from __future__ import annotations

from typing import Any

from rest_framework.permissions import SAFE_METHODS, BasePermission, IsAuthenticated

SCHOOL_ADMIN = "SCHOOL_ADMIN"
ADMISSIONS = "ADMISSIONS_OFFICER"
EXAMS = "EXAM_ADMIN"
FINANCE = "FINANCE_OFFICER"
TEACHER = "TEACHER"
PARENT = "PARENT"
STUDENT = "STUDENT"

STAFF = frozenset({SCHOOL_ADMIN, ADMISSIONS, EXAMS, FINANCE, TEACHER})
PORTAL = frozenset({PARENT, STUDENT})
NONE: frozenset[str] = frozenset()

# area -> (roles that may read, roles that may write)
POLICY: dict[str, tuple[frozenset[str], frozenset[str]]] = {
    "schools": (STAFF | PORTAL, NONE),  # creating/editing schools is superuser-only
    "audit_logs": (frozenset({SCHOOL_ADMIN}), NONE),
    "users": (frozenset({SCHOOL_ADMIN}), frozenset({SCHOOL_ADMIN})),
    "roles": (frozenset({SCHOOL_ADMIN}), NONE),
    "academics": (STAFF | PORTAL, frozenset({SCHOOL_ADMIN})),
    "subject_assignments": (frozenset({SCHOOL_ADMIN, EXAMS, TEACHER}), frozenset({SCHOOL_ADMIN})),
    "students": (STAFF | PORTAL, frozenset({SCHOOL_ADMIN, ADMISSIONS})),
    "guardians": (frozenset({SCHOOL_ADMIN, ADMISSIONS, TEACHER}), frozenset({SCHOOL_ADMIN, ADMISSIONS})),
    "enrollments": (frozenset({SCHOOL_ADMIN, ADMISSIONS, TEACHER}) | PORTAL, frozenset({SCHOOL_ADMIN, ADMISSIONS})),
    "documents": (frozenset({SCHOOL_ADMIN, ADMISSIONS}) | PORTAL, frozenset({SCHOOL_ADMIN, ADMISSIONS})),
    "attendance": (frozenset({SCHOOL_ADMIN, TEACHER}), frozenset({SCHOOL_ADMIN, TEACHER})),
    "attendance_summaries": (frozenset({SCHOOL_ADMIN, TEACHER}) | PORTAL, NONE),
    "exams": (frozenset({SCHOOL_ADMIN, EXAMS, TEACHER}) | PORTAL, frozenset({SCHOOL_ADMIN, EXAMS})),
    "marks": (frozenset({SCHOOL_ADMIN, EXAMS, TEACHER}), frozenset({SCHOOL_ADMIN, EXAMS, TEACHER})),
    "results": (frozenset({SCHOOL_ADMIN, EXAMS, TEACHER}) | PORTAL, frozenset({SCHOOL_ADMIN, EXAMS})),
    "finance": (frozenset({SCHOOL_ADMIN, FINANCE}), frozenset({SCHOOL_ADMIN, FINANCE})),
    # Invoices, payments, receipts and accounts: portal users also see their own.
    "finance_ledger": (frozenset({SCHOOL_ADMIN, FINANCE}) | PORTAL, frozenset({SCHOOL_ADMIN, FINANCE})),
}


def user_roles(user: Any) -> frozenset[str]:
    """Role codes of a user, cached on the instance for the rest of the request."""
    cached = getattr(user, "_role_codes", None)
    if cached is None:
        cached = frozenset(user.roles_list) if user and user.is_authenticated else NONE
        user._role_codes = cached
    return cached


def can(user: Any, area: str, write: bool = False) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    read_roles, write_roles = POLICY[area]
    return bool(user_roles(user) & (write_roles if write else read_roles))


def access_for(user: Any) -> dict[str, dict[str, bool]]:
    """The policy evaluated for one user, for the frontend."""
    return {area: {"read": can(user, area), "write": can(user, area, write=True)} for area in POLICY}


def is_portal_only(user: Any) -> bool:
    """Parents/students with no staff role see only their own records."""
    return not user.is_superuser and not (user_roles(user) & STAFF)


def portal_student_ids(user: Any) -> list[int]:
    """Students a portal user may see: themselves, and children linked to them as parent."""
    from students.models import ParentStudent, Student

    own = Student.objects.filter(user=user).values_list("id", flat=True)
    children = ParentStudent.objects.filter(parent__user=user).values_list("student_id", flat=True)
    return list(set(own) | set(children))


class RolePolicy(BasePermission):
    """Checks POLICY[view.policy] for the request method (safe = read, otherwise write)."""

    message = "Your role does not allow this action."

    def has_permission(self, request, view) -> bool:
        user = request.user
        write = request.method not in SAFE_METHODS
        if not can(user, view.policy, write=write):
            return False
        # Staff may only write records for their own school.
        if write and not user.is_superuser and isinstance(request.data, dict) and "school" in request.data:
            if str(request.data.get("school")) != str(user.school_id):
                self.message = "You can only manage records for your own school."
                return False
        return True


class ScopedQuerysetMixin:
    """Limits rows to the user's school, and portal users to their own students.

    Set on the viewset:
      policy        POLICY key
      school_path   lookup from the model to School ("school", "student__school", ...);
                    None for global tables
      student_path  lookup from the model to Student, for parent/student scoping; None
                    means the rows are shared reference data (classes, subjects, ...)
      portal_filter extra filter applied for portal users (e.g. published results only)
    """

    policy: str
    school_path: str | None = "school"
    student_path: str | None = None
    portal_filter: dict[str, Any] | None = None
    permission_classes = [IsAuthenticated, RolePolicy]

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return self.scope(queryset)

    def scope(self, queryset):
        user = self.request.user
        if user.is_superuser:
            return queryset
        if self.school_path:
            if not user.school_id:
                return queryset.none()
            queryset = queryset.filter(**{self.school_path: user.school_id})
        if is_portal_only(user) and self.student_path:
            queryset = queryset.filter(**{f"{self.student_path}__in": portal_student_ids(user)})
            if self.portal_filter:
                queryset = queryset.filter(**self.portal_filter)
        return queryset
