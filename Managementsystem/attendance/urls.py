from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AttendanceBulkViewSet,
    AttendanceRecordViewSet,
    AttendanceReportViewSet,
    AttendanceSessionViewSet,
    AttendanceSummaryViewSet,
)

router = DefaultRouter()
router.register(r"sessions", AttendanceSessionViewSet, basename="attendance-session")
router.register(r"records", AttendanceRecordViewSet, basename="attendance-record")
router.register(r"summaries", AttendanceSummaryViewSet, basename="attendance-summary")
router.register(r"reports", AttendanceReportViewSet, basename="attendance-report")

urlpatterns = router.urls + [
    path("bulk/", AttendanceBulkViewSet.as_view({"post": "bulk"}), name="attendance-bulk"),
]
