from __future__ import annotations

from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Exam, ExamType, GradeScale, Mark, Ranking, Result
from .permissions import IsExamAdminOrSuperAdmin
from .serializers import (
    ExamSerializer,
    ExamTypeSerializer,
    GradeScaleSerializer,
    MarkSerializer,
    RankingSerializer,
    ResultSerializer,
)


class ExamTypeViewSet(viewsets.ModelViewSet):
    queryset = ExamType.objects.all()
    serializer_class = ExamTypeSerializer
    permission_classes = [IsAuthenticated, IsExamAdminOrSuperAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "created_at"]


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated, IsExamAdminOrSuperAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "start_date", "created_at"]


class GradeScaleViewSet(viewsets.ModelViewSet):
    queryset = GradeScale.objects.all()
    serializer_class = GradeScaleSerializer
    permission_classes = [IsAuthenticated, IsExamAdminOrSuperAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "grade"]
    ordering_fields = ["order", "minimum_mark"]


class MarkViewSet(viewsets.ModelViewSet):
    queryset = Mark.objects.all()
    serializer_class = MarkSerializer
    permission_classes = [IsAuthenticated, IsExamAdminOrSuperAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["student__first_name", "student__last_name", "exam__name"]
    ordering_fields = ["created_at", "percentage"]


class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated, IsExamAdminOrSuperAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["student__first_name", "student__last_name", "exam__name"]
    ordering_fields = ["rank", "percentage", "created_at"]


class RankingViewSet(viewsets.ModelViewSet):
    queryset = Ranking.objects.all()
    serializer_class = RankingSerializer
    permission_classes = [IsAuthenticated, IsExamAdminOrSuperAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["student__first_name", "student__last_name"]
    ordering_fields = ["rank", "score"]
