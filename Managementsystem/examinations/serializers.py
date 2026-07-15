from __future__ import annotations

from rest_framework import serializers

from .models import Exam, ExamType, GradeScale, Mark, Ranking, Result


class ExamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamType
        fields = ["id", "name", "code", "description", "is_active"]


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ["id", "name", "code", "assessment_type", "total_marks", "pass_mark", "start_date", "end_date", "status", "is_published"]


class GradeScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeScale
        fields = ["id", "name", "minimum_mark", "maximum_mark", "grade", "remarks", "order"]


class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark
        fields = ["id", "exam", "student", "marks_obtained", "total_marks", "percentage", "grade", "remarks"]


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ["id", "exam", "student", "marks_obtained", "total_marks", "percentage", "grade", "rank", "remarks", "status", "report_card_number"]


class RankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ranking
        fields = ["id", "exam", "student", "rank", "score"]
