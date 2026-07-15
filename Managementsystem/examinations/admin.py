from django.contrib import admin

from .models import Exam, ExamType, GradeScale, Mark, Ranking, Result


@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    search_fields = ("name", "code")


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("name", "exam_type", "subject", "status", "is_published")
    search_fields = ("name", "code")


@admin.register(GradeScale)
class GradeScaleAdmin(admin.ModelAdmin):
    list_display = ("name", "grade", "minimum_mark", "maximum_mark", "order")
    search_fields = ("name", "grade")


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ("student", "exam", "marks_obtained", "percentage", "grade")
    search_fields = ("student__first_name", "student__last_name", "exam__name")


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("student", "exam", "grade", "rank", "status")
    search_fields = ("student__first_name", "student__last_name", "exam__name")


@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ("student", "exam", "rank", "score")
    search_fields = ("student__first_name", "student__last_name")
