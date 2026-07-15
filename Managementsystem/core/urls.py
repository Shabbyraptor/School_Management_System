from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuditLogViewSet, SchoolViewSet

router = DefaultRouter()
router.register(r"schools", SchoolViewSet, basename="school")
router.register(r"audit-logs", AuditLogViewSet, basename="auditlog")

urlpatterns = [
    path("", include(router.urls)),
]
