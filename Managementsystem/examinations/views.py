from __future__ import annotations

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.access import ScopedQuerysetMixin
from .models import Exam, ExamType, GradeScale, Mark, Ranking, Result
from .services import ResultService
from .serializers import (
    ExamSerializer,
    ExamTypeSerializer,
    GradeScaleSerializer,
    MarkSerializer,
    RankingSerializer,
    ResultSerializer,
)


class ExamTypeViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "exams"
    school_path = "school"
    queryset = ExamType.objects.all()
    serializer_class = ExamTypeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]


class ExamViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "exams"
    school_path = "school"
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "start_date", "created_at"]
    ordering = ["-start_date", "-id"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        """Publish all results of this exam so students and parents can see them."""
        exam = self.get_object()
        count = ResultService.publish_exam(exam)
        return Response({"published": count, "exam": ExamSerializer(exam).data}, status=status.HTTP_200_OK)


class GradeScaleViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "exams"
    school_path = "school"
    queryset = GradeScale.objects.all()
    serializer_class = GradeScaleSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "grade"]
    ordering_fields = ["order", "minimum_mark"]
    ordering = ["order", "-minimum_mark"]


class MarkViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "marks"
    school_path = "exam__school"
    queryset = Mark.objects.all()
    serializer_class = MarkSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["student__first_name", "student__last_name", "exam__name"]
    ordering_fields = ["created_at", "percentage"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(entered_by=self.request.user)


class ResultViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "results"
    school_path = "exam__school"
    student_path = "student"
    portal_filter = {"status": "PUBLISHED"}
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["student__first_name", "student__last_name", "exam__name"]
    ordering_fields = ["rank", "percentage", "created_at"]
    ordering = ["exam", "rank"]


class RankingViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "results"
    school_path = "exam__school"
    student_path = "student"
    portal_filter = {"exam__is_published": True}
    queryset = Ranking.objects.all()
    serializer_class = RankingSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["student__first_name", "student__last_name"]
    ordering_fields = ["rank", "score"]
    ordering = ["exam", "rank"]
