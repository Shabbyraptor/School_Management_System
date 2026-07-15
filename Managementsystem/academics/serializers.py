from __future__ import annotations

from rest_framework import serializers

from .models import AcademicYear, Class, Stream, Subject, SubjectAssignment, Term


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ["id", "school", "name", "code", "start_date", "end_date", "is_current", "is_active", "created_at", "updated_at"]


class AcademicYearCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ["school", "name", "code", "start_date", "end_date", "is_current", "is_active"]


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ["id", "academic_year", "name", "number", "start_date", "end_date", "is_current", "is_active", "created_at", "updated_at"]


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ["id", "school", "name", "code", "education_level", "description", "display_order", "is_active", "created_at", "updated_at"]


class StreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = ["id", "school", "academic_class", "name", "capacity", "class_teacher", "is_active", "created_at", "updated_at"]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "school", "name", "code", "short_name", "category", "description", "is_compulsory", "is_active", "created_at", "updated_at"]


class SubjectAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectAssignment
        fields = ["id", "teacher", "subject", "academic_class", "stream", "academic_year", "term", "created_at", "updated_at"]
