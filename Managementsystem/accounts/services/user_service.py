from __future__ import annotations

from typing import Any, Dict

from django.contrib.auth import get_user_model

User = get_user_model()


class UserService:
    """Handles user lifecycle operations away from views."""

    @staticmethod
    def create_user(password: str, **data: Any) -> User:
        user = User.objects.create_user(password=password, **data)
        return user

    @staticmethod
    def update_user(user: User, data: Dict[str, Any]) -> User:
        for field, value in data.items():
            setattr(user, field, value)
        user.save()
        return user

    @staticmethod
    def deactivate_user(user: User) -> User:
        user.deactivate()
        return user

    @staticmethod
    def activate_user(user: User) -> User:
        user.activate()
        return user

    @staticmethod
    def change_password(user: User, new_password: str) -> User:
        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])
        return user
