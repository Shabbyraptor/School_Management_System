from __future__ import annotations

from typing import Any

from rest_framework import filters, status, viewsets
from rest_framework.response import Response

from core.access import ScopedQuerysetMixin
from .models import AcademicYear, Class, Stream, Subject, SubjectAssignment, Term
from .serializers import (
    AcademicYearCreateSerializer,
    AcademicYearSerializer,
    ClassSerializer,
    StreamSerializer,
    SubjectAssignmentSerializer,
    SubjectSerializer,
    TermSerializer,
)
from .services import (
    AcademicYearService,
    ClassService,
    SubjectAssignmentService,
    SubjectService,
    TermService,
)


class AcademicYearViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "academics"
    school_path = "school"
    queryset = AcademicYear.objects.select_related("school").all()
    serializer_class = AcademicYearSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["start_date", "end_date", "name"]
    ordering = ["-start_date"]

    def get_serializer_class(self) -> Any:
        if self.action == "create":
            return AcademicYearCreateSerializer
        return AcademicYearSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        year = AcademicYearService.create_year(serializer.validated_data)
        return Response(AcademicYearSerializer(year, context={"request": request}).data, status=status.HTTP_201_CREATED)


class TermViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "academics"
    school_path = "academic_year__school"
    queryset = Term.objects.select_related("academic_year").all()
    serializer_class = TermSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["number", "start_date", "end_date"]
    ordering = ["number"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        term = TermService.create_term(serializer.validated_data)
        return Response(TermSerializer(term, context={"request": request}).data, status=status.HTTP_201_CREATED)


class ClassViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "academics"
    school_path = "school"
    queryset = Class.objects.select_related("school").all()
    serializer_class = ClassSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["display_order", "name"]
    ordering = ["display_order", "name"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        academic_class = ClassService.create_class(serializer.validated_data)
        return Response(ClassSerializer(academic_class, context={"request": request}).data, status=status.HTTP_201_CREATED)


class StreamViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "academics"
    school_path = "school"
    queryset = Stream.objects.select_related("academic_class", "school", "class_teacher").all()
    serializer_class = StreamSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "capacity"]
    ordering = ["name"]


class SubjectViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "academics"
    school_path = "school"
    queryset = Subject.objects.select_related("school").all()
    serializer_class = SubjectSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subject = SubjectService.create_subject(serializer.validated_data)
        return Response(SubjectSerializer(subject, context={"request": request}).data, status=status.HTTP_201_CREATED)


class SubjectAssignmentViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "subject_assignments"
    school_path = "academic_year__school"
    queryset = SubjectAssignment.objects.select_related("teacher", "subject", "academic_class", "stream", "academic_year", "term").all()
    serializer_class = SubjectAssignmentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["subject__name", "teacher__email"]
    ordering_fields = ["subject__name", "academic_class__name"]
    ordering = ["subject__name"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignment = SubjectAssignmentService.assign_teacher(serializer.validated_data)
        return Response(SubjectAssignmentSerializer(assignment, context={"request": request}).data, status=status.HTTP_201_CREATED)
