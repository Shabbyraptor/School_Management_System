from django.contrib import admin

from .models import AcademicYear, Class, Stream, Subject, SubjectAssignment, Term


class StreamInline(admin.TabularInline):
    model = Stream
    extra = 1


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "school", "start_date", "end_date", "is_current", "is_active")
    list_filter = ("is_current", "is_active", "school")
    search_fields = ("name", "code")
    ordering = ("-start_date",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ("academic_year", "name", "number", "start_date", "end_date", "is_current", "is_active")
    list_filter = ("is_current", "is_active", "academic_year__school")
    search_fields = ("name",)
    ordering = ("academic_year", "number")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "school", "education_level", "display_order", "is_active")
    list_filter = ("education_level", "is_active", "school")
    search_fields = ("name", "code")
    ordering = ("display_order", "name")
    readonly_fields = ("created_at", "updated_at")
    inlines = [StreamInline]


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ("academic_class", "name", "capacity", "class_teacher", "is_active")
    list_filter = ("is_active", "academic_class__school")
    search_fields = ("name", "academic_class__name")
    ordering = ("academic_class", "name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "school", "category", "is_compulsory", "is_active")
    list_filter = ("category", "is_compulsory", "is_active", "school")
    search_fields = ("name", "code")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(SubjectAssignment)
class SubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ("teacher", "subject", "academic_class", "stream", "academic_year", "term")
    list_filter = ("academic_year", "term", "academic_class")
    search_fields = ("teacher__email", "subject__name")
    ordering = ("academic_year", "term", "academic_class")
    readonly_fields = ("created_at", "updated_at")
