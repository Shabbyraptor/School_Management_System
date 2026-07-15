from __future__ import annotations

from django.db import transaction

from ..constants import ResultStatus
from ..models import GradeScale, Result


class ResultService:
    @staticmethod
    @transaction.atomic
    def generate_result(mark) -> Result:
        grade_scale = GradeScale.objects.filter(
            school=mark.exam.school,
            minimum_mark__lte=mark.percentage,
            maximum_mark__gte=mark.percentage,
        ).order_by("order").first()
        result = Result.objects.create(
            exam=mark.exam,
            student=mark.student,
            total_marks=mark.total_marks,
            marks_obtained=mark.marks_obtained,
            percentage=mark.percentage,
            grade=grade_scale.grade if grade_scale else "",
            remarks=grade_scale.remarks if grade_scale else "",
            status=ResultStatus.DRAFT,
        )
        return result

    @staticmethod
    @transaction.atomic
    def publish_result(result: Result) -> Result:
        result.status = ResultStatus.PUBLISHED
        result.save(update_fields=["status", "updated_at"])
        return result
