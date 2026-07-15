from __future__ import annotations

from typing import Any

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .constants import AuditActionChoices
from .models import AuditLog, School
from .permissions import IsSchoolAdmin, IsSuperAdmin
from .serializers import (
    AuditLogSerializer,
    SchoolCreateSerializer,
    SchoolSerializer,
    SchoolUpdateSerializer,
)
from .services.audit_service import AuditLogService
from .services.school_service import SchoolService


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated, IsSchoolAdmin]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code", "registration_number", "email", "city", "country"]
    ordering_fields = ["name", "code", "created_at", "updated_at"]
    ordering = ["name"]

    def get_serializer_class(self) -> Any:
        if self.action == "create":
            return SchoolCreateSerializer
        if self.action in {"update", "partial_update"}:
            return SchoolUpdateSerializer
        return SchoolSerializer

    def get_queryset(self):
        queryset = School.objects.all()
        params = self.request.query_params
        if city := params.get("city"):
            queryset = queryset.filter(city__iexact=city)
        if country := params.get("country"):
            queryset = queryset.filter(country__iexact=country)
        if code := params.get("code"):
            queryset = queryset.filter(code__iexact=code)
        if is_active := params.get("is_active"):
            if is_active.lower() in {"true", "1", "yes"}:
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() in {"false", "0", "no"}:
                queryset = queryset.filter(is_active=False)
        return queryset

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        school = SchoolService.create_school(serializer.validated_data)
        AuditLogService.log_action(
            action=AuditActionChoices.CREATE.value,
            model_name="School",
            object_id=str(school.pk),
            description=f"Created school {school.name}",
            user=request.user,
            school=school,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        output_serializer = SchoolSerializer(school, context={"request": request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        school = SchoolService.update_school(instance, serializer.validated_data)
        AuditLogService.log_action(
            action=AuditActionChoices.UPDATE.value,
            model_name="School",
            object_id=str(school.pk),
            description=f"Updated school {school.name}",
            user=request.user,
            school=school,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        output_serializer = SchoolSerializer(school, context={"request": request})
        return Response(output_serializer.data)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        school = self.get_object()
        school.soft_delete()
        AuditLogService.log_action(
            action=AuditActionChoices.DELETE.value,
            model_name="School",
            object_id=str(school.pk),
            description=f"Soft deleted school {school.name}",
            user=request.user,
            school=school,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request: Request, pk: Any = None) -> Response:
        school = self.get_object()
        SchoolService.activate_school(school)
        AuditLogService.log_action(
            action=AuditActionChoices.UPDATE.value,
            model_name="School",
            object_id=str(school.pk),
            description=f"Activated school {school.name}",
            user=request.user,
            school=school,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        output_serializer = SchoolSerializer(school, context={"request": request})
        return Response(output_serializer.data)

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request: Request, pk: Any = None) -> Response:
        school = self.get_object()
        SchoolService.deactivate_school(school)
        AuditLogService.log_action(
            action=AuditActionChoices.UPDATE.value,
            model_name="School",
            object_id=str(school.pk),
            description=f"Deactivated school {school.name}",
            user=request.user,
            school=school,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        output_serializer = SchoolSerializer(school, context={"request": request})
        return Response(output_serializer.data)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related("user", "school").all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["action", "model_name", "object_id", "description", "ip_address"]
    ordering_fields = ["timestamp", "action", "model_name"]
    ordering = ["-timestamp"]

    def get_queryset(self):
        queryset = AuditLog.objects.select_related("user", "school").all()
        params = self.request.query_params
        if action := params.get("action"):
            queryset = queryset.filter(action__iexact=action)
        if model_name := params.get("model_name"):
            queryset = queryset.filter(model_name__iexact=model_name)
        if school_id := params.get("school_id"):
            queryset = queryset.filter(school_id=school_id)
        return queryset
