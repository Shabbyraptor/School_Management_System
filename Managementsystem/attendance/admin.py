from django.contrib import admin

from .models import AttendanceRecord, AttendanceSession, AttendanceSummary


class AttendanceRecordInline(admin.TabularInline):
    model = AttendanceRecord
    extra = 0


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ("reference", "attendance_date", "class_field", "stream", "session_type", "status", "teacher")
    list_filter = ("status", "session_type", "attendance_date")
    search_fields = ("reference", "remarks")
    inlines = [AttendanceRecordInline]


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "attendance_session", "status", "marked_by", "time_marked")
    list_filter = ("status", "attendance_session__attendance_date")
    search_fields = ("student__first_name", "student__last_name", "remarks")


@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ("student", "academic_year", "term", "present_days", "absent_days", "attendance_percentage", "last_updated")
    list_filter = ("academic_year", "term")
    search_fields = ("student__first_name", "student__last_name")
