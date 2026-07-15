from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EnrollmentViewSet,
    GuardianViewSet,
    ParentViewSet,
    StudentDocumentViewSet,
    StudentViewSet,
)

router = DefaultRouter()
router.register(r"", StudentViewSet, basename="student")
router.register(r"parents", ParentViewSet, basename="parent")
router.register(r"guardians", GuardianViewSet, basename="guardian")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")
router.register(r"documents", StudentDocumentViewSet, basename="document")

urlpatterns = [path("", include(router.urls))]
