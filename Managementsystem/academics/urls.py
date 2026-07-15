from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AcademicYearViewSet,
    ClassViewSet,
    StreamViewSet,
    SubjectAssignmentViewSet,
    SubjectViewSet,
    TermViewSet,
)

router = DefaultRouter()
router.register(r"academic-years", AcademicYearViewSet, basename="academicyear")
router.register(r"terms", TermViewSet, basename="term")
router.register(r"classes", ClassViewSet, basename="class")
router.register(r"streams", StreamViewSet, basename="stream")
router.register(r"subjects", SubjectViewSet, basename="subject")
router.register(r"subject-assignments", SubjectAssignmentViewSet, basename="subjectassignment")

urlpatterns = [path("", include(router.urls))]
