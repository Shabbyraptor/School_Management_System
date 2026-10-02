from __future__ import annotations

from django.db import transaction

from ..constants import ExamStatus, ResultStatus
from ..models import GradeScale, Mark, Ranking, Result


class ResultService:
    @staticmethod
    def grade_for(school_id: int, percentage) -> GradeScale | None:
        return (
            GradeScale.objects.filter(school_id=school_id, minimum_mark__lte=percentage, maximum_mark__gte=percentage)
            .order_by("order")
            .first()
        )

    @staticmethod
    @transaction.atomic
    def generate_result(mark) -> Result:
        """Create or refresh the result for a mark (the mark's grade is set too)."""
        grade_scale = ResultService.grade_for(mark.exam.school_id, mark.percentage)
        grade = grade_scale.grade if grade_scale else ""
        remarks = grade_scale.remarks if grade_scale else ""
        Mark.objects.filter(pk=mark.pk).update(grade=grade)
        result, created = Result.objects.get_or_create(
            exam=mark.exam,
            student=mark.student,
            defaults={
                "total_marks": mark.total_marks,
                "marks_obtained": mark.marks_obtained,
                "grade": grade,
                "remarks": remarks,
                "status": ResultStatus.DRAFT,
            },
        )
        if not created:
            result.total_marks = mark.total_marks
            result.marks_obtained = mark.marks_obtained
            result.grade = grade
            result.remarks = remarks
            result.save()
        return result

    @staticmethod
    @transaction.atomic
    def rank_exam(exam_id: int) -> None:
        """Competition ranking (1, 2, 2, 4) by percentage, mirrored into Ranking."""
        results = list(Result.objects.filter(exam_id=exam_id).order_by("-percentage", "id"))
        previous, rank = None, 0
        for position, result in enumerate(results, start=1):
            if result.percentage != previous:
                rank, previous = position, result.percentage
            Result.objects.filter(pk=result.pk).update(rank=rank)
            Ranking.objects.update_or_create(
                exam_id=exam_id, student_id=result.student_id, defaults={"rank": rank, "score": result.percentage}
            )
        Ranking.objects.filter(exam_id=exam_id).exclude(student_id__in=[r.student_id for r in results]).delete()

    @staticmethod
    @transaction.atomic
    def publish_result(result: Result) -> Result:
        result.status = ResultStatus.PUBLISHED
        result.save(update_fields=["status", "updated_at"])
        return result

    @staticmethod
    @transaction.atomic
    def publish_exam(exam) -> int:
        """Publish every result of an exam and mark the exam published."""
        results = list(Result.objects.filter(exam=exam))
        for result in results:
            ResultService.publish_result(result)
        exam.status = ExamStatus.PUBLISHED
        exam.is_published = True
        exam.save(update_fields=["status", "is_published", "updated_at"])
        return len(results)
