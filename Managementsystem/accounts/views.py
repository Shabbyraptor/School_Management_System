from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.access import ScopedQuerysetMixin, access_for, is_portal_only
from .models import Permission, Role, UserProfile
from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    PermissionSerializer,
    RoleSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from .services.auth_service import AuthenticationService
from .services.role_service import RoleService


User = get_user_model()


class UserViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "users"
    school_path = "school"
    queryset = User.objects.select_related("school").prefetch_related("roles").all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["email", "username", "first_name", "last_name", "phone_number"]
    ordering_fields = ["email", "date_joined"]
    ordering = ["email"]

    def get_serializer_class(self) -> Any:
        if self.action == "create":
            return UserCreateSerializer
        if self.action in {"update", "partial_update"}:
            return UserUpdateSerializer
        return UserSerializer

    @action(detail=True, methods=["post"], url_path="roles")
    def set_roles(self, request: Any, pk: Any = None) -> Response:
        """Replace a user's roles: {"role_codes": ["TEACHER", "PARENT"]}."""
        user = self.get_object()
        if user.pk == request.user.pk and not request.user.is_superuser:
            return Response({"detail": "You cannot change your own roles."}, status=status.HTTP_403_FORBIDDEN)
        codes = request.data.get("role_codes")
        if not isinstance(codes, list):
            return Response({"role_codes": ["Send a list of role codes."]}, status=status.HTTP_400_BAD_REQUEST)
        RoleService.set_roles(user, codes)
        return Response(UserSerializer(user, context={"request": request}).data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def profile(self, request: Any) -> Response:
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def change_password(self, request: Any) -> Response:
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password updated successfully."})


class RoleViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "roles"
    school_path = None
    queryset = Role.objects.prefetch_related("permissions").all()
    serializer_class = RoleSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code", "description"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]


class PermissionViewSet(ScopedQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    policy = "roles"
    school_path = None
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code", "module"]
    ordering_fields = ["module", "code"]
    ordering = ["module", "code"]


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Any) -> Response:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            AuthenticationService.logout(refresh_token)
        except Exception:
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_204_NO_CONTENT)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Any) -> Response:
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password reset email sent."})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Any) -> Response:
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password has been reset."})


class ProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Any) -> Response:
        data = UserSerializer(request.user, context={"request": request}).data
        # What this user may read/write, so the frontend can mirror the API's policy.
        data["access"] = access_for(request.user)
        data["portal_only"] = is_portal_only(request.user)
        return Response(data)


class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request: Any) -> Response:
        serializer = UserUpdateSerializer(
            request.user, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user, context={"request": request}).data)
