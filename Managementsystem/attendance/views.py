from __future__ import annotations

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import AttendanceRecord, AttendanceSession, AttendanceSummary
from .permissions import CanManageAttendance
from .serializers import (
    AttendanceRecordSerializer,
    AttendanceSessionCreateSerializer,
    AttendanceSessionSerializer,
    AttendanceSummarySerializer,
    BulkAttendanceSerializer,
)
from .services import AttendanceService, AttendanceSessionService


class AttendanceSessionViewSet(viewsets.ModelViewSet):
    queryset = AttendanceSession.objects.select_related("school", "academic_year", "term", "class_field", "stream", "teacher").prefetch_related("records")
    serializer_class = AttendanceSessionSerializer
    permission_classes = [IsAuthenticated, CanManageAttendance]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["reference", "remarks"]
    ordering_fields = ["attendance_date", "created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return AttendanceSessionCreateSerializer
        return AttendanceSessionSerializer

    @action(detail=True, methods=["post"], url_path="open")
    def open_session(self, request, pk=None):
        session = self.get_object()
        AttendanceSessionService.open_session(session)
        return Response(AttendanceSessionSerializer(session).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="close")
    def close_session(self, request, pk=None):
        session = self.get_object()
        AttendanceSessionService.close_session(session)
        return Response(AttendanceSessionSerializer(session).data, status=status.HTTP_200_OK)


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.select_related("attendance_session", "student", "marked_by")
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated, CanManageAttendance]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["student__first_name", "student__last_name", "status"]
    ordering_fields = ["time_marked", "status"]


class AttendanceSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AttendanceSummary.objects.select_related("student", "academic_year", "term")
    serializer_class = AttendanceSummarySerializer
    permission_classes = [IsAuthenticated, CanManageAttendance]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["student__first_name", "student__last_name"]
    ordering_fields = ["attendance_percentage", "last_updated"]


class AttendanceReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, CanManageAttendance]

    @action(detail=False, methods=["get"], url_path="daily")
    def daily(self, request):
        return Response({"status": "ok", "report": "daily"})

    @action(detail=False, methods=["get"], url_path="monthly")
    def monthly(self, request):
        return Response({"status": "ok", "report": "monthly"})

    @action(detail=False, methods=["get"], url_path="term")
    def term(self, request):
        return Response({"status": "ok", "report": "term"})


class AttendanceBulkViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, CanManageAttendance]

    @action(detail=False, methods=["post"], url_path="bulk")
    def bulk(self, request):
        serializer = BulkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = AttendanceSession.objects.get(pk=serializer.validated_data["session_id"])
        records = AttendanceService.bulk_mark_attendance(session, serializer.validated_data["records"])
        return Response({"created": len(records)}, status=status.HTTP_201_CREATED)
