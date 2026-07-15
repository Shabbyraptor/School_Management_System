from __future__ import annotations

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Enrollment, Guardian, Parent, Student, StudentDocument
from .permissions import IsParentLinked, IsSchoolAdminOrAdmissionsOfficer, IsStudentOwner
from .serializers import (
    EnrollmentSerializer,
    GuardianSerializer,
    ParentSerializer,
    StudentCreateSerializer,
    StudentDocumentSerializer,
    StudentSerializer,
    StudentUpdateSerializer,
)
from .services import EnrollmentService, ParentService, StudentService


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related("school", "user", "current_class", "current_stream").all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "admission_number", "email"]
    ordering_fields = ["admission_number", "first_name", "created_at"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy", "promote", "transfer", "graduate", "archive"}:
            return [IsAuthenticated(), IsSchoolAdminOrAdmissionsOfficer()]
        return [IsAuthenticated(), IsStudentOwner() | IsParentLinked()]

    def get_serializer_class(self):
        if self.action == "create":
            return StudentCreateSerializer
        if self.action in {"update", "partial_update"}:
            return StudentUpdateSerializer
        return StudentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = StudentService.admit_student(serializer.validated_data, request.user.school)
        return Response(StudentSerializer(student, context={"request": request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="promote")
    def promote(self, request, pk=None):
        student = self.get_object()
        enrollment = StudentService.promote_student(student)
        return Response({"enrollment_id": enrollment.id}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="transfer")
    def transfer(self, request, pk=None):
        student = self.get_object()
        enrollment = StudentService.transfer_student(student)
        return Response({"enrollment_id": enrollment.id}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="graduate")
    def graduate(self, request, pk=None):
        student = self.get_object()
        StudentService.graduate_student(student)
        return Response({"status": "graduated"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request, pk=None):
        student = self.get_object()
        StudentService.archive_student(student)
        return Response({"status": "archived"}, status=status.HTTP_200_OK)


class ParentViewSet(viewsets.ModelViewSet):
    queryset = Parent.objects.select_related("school", "user").all()
    serializer_class = ParentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email"]
    ordering_fields = ["first_name", "last_name"]
    ordering = ["first_name"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAuthenticated(), IsSchoolAdminOrAdmissionsOfficer()]
        return [IsAuthenticated(), IsParentLinked() | IsSchoolAdminOrAdmissionsOfficer()]


class GuardianViewSet(viewsets.ModelViewSet):
    queryset = Guardian.objects.select_related("school").all()
    serializer_class = GuardianSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email"]
    ordering_fields = ["first_name", "last_name"]
    ordering = ["first_name"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAuthenticated(), IsSchoolAdminOrAdmissionsOfficer()]
        return [IsAuthenticated(), IsParentLinked() | IsSchoolAdminOrAdmissionsOfficer()]


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.select_related("student", "academic_year", "term", "class_field", "stream").all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["student__first_name", "student__last_name"]
    ordering_fields = ["enrollment_date", "status"]
    ordering = ["-enrollment_date"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAuthenticated(), IsSchoolAdminOrAdmissionsOfficer()]
        return [IsAuthenticated(), IsParentLinked() | IsStudentOwner() | IsSchoolAdminOrAdmissionsOfficer()]


class StudentDocumentViewSet(viewsets.ModelViewSet):
    queryset = StudentDocument.objects.select_related("student").all()
    serializer_class = StudentDocumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["student__first_name", "student__last_name", "document_type"]
    ordering_fields = ["uploaded_at", "document_type"]
    ordering = ["-uploaded_at"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAuthenticated(), IsSchoolAdminOrAdmissionsOfficer()]
        return [IsAuthenticated(), IsParentLinked() | IsStudentOwner() | IsSchoolAdminOrAdmissionsOfficer()]
