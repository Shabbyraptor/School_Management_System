from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    PermissionViewSet,
    ProfileDetailView,
    ProfileUpdateView,
    RoleViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"permissions", PermissionViewSet, basename="permission")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/password-reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path("auth/password-reset-confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("profile/", ProfileDetailView.as_view(), name="profile_detail"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile_update"),
]
