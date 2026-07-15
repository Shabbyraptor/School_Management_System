from __future__ import annotations

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.urls import reverse
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.services.audit_service import AuditLogService
from core.models import AuditLog
from .models import Permission, Role, User, UserProfile, UserRole
from .services.user_service import UserService
from .services.role_service import RoleService

UserModel = get_user_model()


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name", "code", "description", "module"]


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(source="role_permissions", many=True, read_only=True)

    class Meta:
        model = Role
        fields = ["id", "name", "code", "description", "is_system_role", "permissions"]
        read_only_fields = ["permissions"]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["gender", "date_of_birth", "nationality", "address", "city", "country", "bio"]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    roles = serializers.SerializerMethodField()

    class Meta:
        model = UserModel
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "profile_photo",
            "is_active",
            "is_staff",
            "is_verified",
            "date_joined",
            "school",
            "profile",
            "roles",
        ]
        read_only_fields = ["id", "date_joined", "profile", "roles"]

    def get_roles(self, obj: UserModel) -> list[str]:
        return obj.roles_list


class UserCreateSerializer(serializers.ModelSerializer):
    role_codes = serializers.ListField(
        child=serializers.CharField(max_length=64),
        write_only=True,
        required=False,
    )

    class Meta:
        model = UserModel
        fields = [
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
            "phone_number",
            "profile_photo",
            "school",
            "is_active",
            "is_staff",
            "is_verified",
            "role_codes",
        ]
        extra_kwargs = {"password": {"write_only": True, "min_length": 8}}

    def create(self, validated_data: dict[str, object]) -> UserModel:
        role_codes = validated_data.pop("role_codes", [])
        password = validated_data.pop("password")
        user = UserService.create_user(password=password, **validated_data)
        if role_codes:
            RoleService.assign_roles(user, role_codes)
        AuditLogService.log_action(
            action="CREATE",
            model_name="User",
            object_id=str(user.pk),
            description=f"Created user {user.email}",
            user=user,
            school=user.school,
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "profile_photo",
            "is_active",
            "is_verified",
        ]

    def update(self, instance: UserModel, validated_data: dict[str, object]) -> UserModel:
        instance = UserService.update_user(instance, validated_data)
        AuditLogService.log_action(
            action="UPDATE",
            model_name="User",
            object_id=str(instance.pk),
            description=f"Updated user {instance.email}",
            user=self.context["request"].user,
            school=instance.school,
        )
        return instance


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: UserModel):
        token = super().get_token(user)
        token["email"] = user.email
        token["username"] = user.username
        return token


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        if not UserModel.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def save(self) -> None:
        user = UserModel.objects.get(email=self.validated_data["email"])
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        reset_url = reverse("accounts:password_reset_confirm")
        subject = "Password reset request"
        message = (
            f"Use the following token to reset your password:\n\n"
            f"Email: {user.email}\n"
            f"Token: {token}\n"
            f"Confirm URL: {reset_url}\n"
        )
        send_mail(subject, message, None, [user.email], fail_silently=False)
        AuditLogService.log_action(
            action="EXPORT",
            model_name="User",
            object_id=str(user.pk),
            description="Password reset requested",
            user=user,
            school=user.school,
        )


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        try:
            user = UserModel.objects.get(email=attrs["email"])
        except UserModel.DoesNotExist:
            raise serializers.ValidationError("Invalid email or token.")
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError("Invalid or expired token.")
        attrs["user"] = user
        return attrs

    def save(self) -> UserModel:
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password", "updated_at"])
        AuditLogService.log_action(
            action="UPDATE",
            model_name="User",
            object_id=str(user.pk),
            description="Password reset completed",
            user=user,
            school=user.school,
        )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)

    def validate_old_password(self, value: str) -> str:
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def save(self) -> UserModel:
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password", "updated_at"])
        AuditLogService.log_action(
            action="UPDATE",
            model_name="User",
            object_id=str(user.pk),
            description="Password changed",
            user=user,
            school=user.school,
        )
        return user
