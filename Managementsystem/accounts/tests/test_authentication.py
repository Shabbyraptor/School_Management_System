from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AuthenticationAPITest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="apitest@test.com",
            username="apitest",
            password="password123",
        )

    def test_login_endpoint(self) -> None:
        response = self.client.post("/api/accounts/auth/login/", {"email": self.user.email, "password": "password123"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_logout_endpoint(self) -> None:
        refresh = str(RefreshToken.for_user(self.user))
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(self.user).access_token}")
        response = self.client.post("/api/accounts/auth/logout/", {"refresh": refresh}, format="json")
        self.assertEqual(response.status_code, 204)
