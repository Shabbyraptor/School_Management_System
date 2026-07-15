from __future__ import annotations

from rest_framework import serializers

from .models import AttendanceRecord, AttendanceSession, AttendanceSummary


class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = ["id", "attendance_session", "student", "status", "time_marked", "marked_by", "remarks"]


class AttendanceSessionSerializer(serializers.ModelSerializer):
    records = AttendanceRecordSerializer(many=True, read_only=True)

    class Meta:
        model = AttendanceSession
        fields = ["id", "school", "academic_year", "term", "attendance_date", "class_field", "stream", "teacher", "session_type", "status", "remarks", "reference", "records"]


class AttendanceSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceSession
        fields = ["school", "academic_year", "term", "attendance_date", "class_field", "stream", "teacher", "session_type", "remarks"]


class BulkAttendanceSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    records = serializers.ListField(child=serializers.DictField(), allow_empty=False)


class AttendanceSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceSummary
        fields = ["id", "student", "academic_year", "term", "present_days", "absent_days", "late_days", "excused_days", "attendance_percentage", "last_updated"]
