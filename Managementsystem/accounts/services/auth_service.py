from __future__ import annotations

from typing import Any, Optional

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class AuthenticationService:
    """Handles JWT login, refresh, and logout operations."""

    @staticmethod
    def login(email: str, password: str) -> dict[str, str]:
        user = authenticate(email=email, password=password)
        if user is None or not user.is_active:
            raise ValueError("Invalid credentials or inactive user.")
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def logout(refresh_token: str) -> None:
        token = RefreshToken(refresh_token)
        token.blacklist()

    @staticmethod
    def refresh_token(refresh_token: str) -> dict[str, str]:
        token = RefreshToken(refresh_token)
        return {
            "access": str(token.access_token),
            "refresh": str(token),
        }
