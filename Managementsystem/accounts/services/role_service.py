from __future__ import annotations

from typing import Iterable

from accounts.models import Permission, Role, User, UserRole


class RoleService:
    """Handles roles and permission relationships."""

    @staticmethod
    def assign_roles(user: User, role_codes: Iterable[str]) -> None:
        roles = Role.objects.filter(code__in=role_codes)
        for role in roles:
            UserRole.objects.get_or_create(user=user, role=role)

    @staticmethod
    def remove_role(user: User, role_code: str) -> None:
        UserRole.objects.filter(user=user, role__code=role_code).delete()

    @staticmethod
    def check_permission(user: User, permission_code: str) -> bool:
        return user.has_permission(permission_code)

    @staticmethod
    def add_permission_to_role(role: Role, permission_code: str) -> Permission:
        permission, _ = Permission.objects.get_or_create(code=permission_code)
        role.permissions.add(permission)
        return permission
