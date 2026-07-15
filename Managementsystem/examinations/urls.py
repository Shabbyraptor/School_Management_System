from rest_framework.routers import DefaultRouter

from .views import ExamTypeViewSet, ExamViewSet, GradeScaleViewSet, MarkViewSet, RankingViewSet, ResultViewSet

router = DefaultRouter()
router.register(r"exam-types", ExamTypeViewSet, basename="examtype")
router.register(r"exams", ExamViewSet, basename="exam")
router.register(r"grade-scales", GradeScaleViewSet, basename="gradescale")
router.register(r"marks", MarkViewSet, basename="mark")
router.register(r"results", ResultViewSet, basename="result")
router.register(r"rankings", RankingViewSet, basename="ranking")

urlpatterns = router.urls
