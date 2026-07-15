from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import AuditLog, School

User = get_user_model()


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "code",
            "registration_number",
            "email",
            "phone_number",
            "address",
            "city",
            "country",
            "website",
            "logo",
            "is_active",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]


class SchoolCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = [
            "name",
            "code",
            "registration_number",
            "email",
            "phone_number",
            "address",
            "city",
            "country",
            "website",
            "logo",
            "is_active",
        ]
        extra_kwargs = {
            "code": {"required": True},
            "registration_number": {"required": True},
            "email": {"required": True},
            "phone_number": {"required": True},
        }


class SchoolUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = [
            "name",
            "email",
            "phone_number",
            "address",
            "city",
            "country",
            "website",
            "logo",
            "is_active",
        ]


class AuditLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    school = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user",
            "school",
            "action",
            "model_name",
            "object_id",
            "description",
            "ip_address",
            "timestamp",
        ]
        read_only_fields = fields
