from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from academics.models import AcademicYear, Class, Stream, Subject, Term
from core.models import BaseModel, School
from students.models import Student

from .constants import AssessmentType, ExamStatus, ResultStatus
from .utils import calculate_percentage, generate_exam_code, generate_report_card_number
from .validators import validate_exam_dates, validate_grade_scale_ranges, validate_mark


class ExamType(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="exam_types")
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Exam Type"
        verbose_name_plural = "Exam Types"

    def __str__(self) -> str:
        return self.name


class Exam(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="exams")
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE, related_name="exams")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="exams")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="exams")
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="exams")
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name="exams", blank=True, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="exams")
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=100, blank=True)
    assessment_type = models.CharField(max_length=30, choices=AssessmentType.choices, default=AssessmentType.END_TERM)
    total_marks = models.PositiveIntegerField(default=100)
    pass_mark = models.PositiveIntegerField(default=40)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=ExamStatus.choices, default=ExamStatus.DRAFT)
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="created_exams", null=True, blank=True)

    class Meta:
        ordering = ["-start_date", "-created_at"]
        verbose_name = "Exam"
        verbose_name_plural = "Exams"

    def clean(self) -> None:
        validate_exam_dates(self.start_date, self.end_date)
        if self.pass_mark > self.total_marks:
            raise ValidationError("Pass mark cannot be greater than total marks.")
        super().clean()

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_exam_code(self.school.code, self.exam_type.code)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class GradeScale(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="grade_scales")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    minimum_mark = models.PositiveIntegerField()
    maximum_mark = models.PositiveIntegerField()
    grade = models.CharField(max_length=10)
    remarks = models.CharField(max_length=250, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "minimum_mark"]
        verbose_name = "Grade Scale"
        verbose_name_plural = "Grade Scales"

    def clean(self) -> None:
        validate_grade_scale_ranges(self.minimum_mark, self.maximum_mark)
        super().clean()

    def __str__(self) -> str:
        return f"{self.grade} ({self.minimum_mark}-{self.maximum_mark})"


class Mark(BaseModel):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="marks")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="marks")
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    total_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100.00)
    percentage = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    grade = models.CharField(max_length=10, blank=True)
    remarks = models.CharField(max_length=250, blank=True)
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="entered_marks", null=True, blank=True)

    class Meta:
        unique_together = ("exam", "student")
        verbose_name = "Mark"
        verbose_name_plural = "Marks"

    def clean(self) -> None:
        validate_mark(float(self.marks_obtained), float(self.total_marks))
        super().clean()

    def save(self, *args, **kwargs):
        self.percentage = calculate_percentage(float(self.marks_obtained), float(self.total_marks))
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.student} - {self.exam}"


class Result(BaseModel):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="results")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="results")
    total_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    percentage = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    grade = models.CharField(max_length=10, blank=True)
    rank = models.PositiveIntegerField(default=0)
    remarks = models.CharField(max_length=250, blank=True)
    status = models.CharField(max_length=20, choices=ResultStatus.choices, default=ResultStatus.DRAFT)
    report_card_number = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ("exam", "student")
        verbose_name = "Result"
        verbose_name_plural = "Results"

    def save(self, *args, **kwargs):
        self.percentage = calculate_percentage(float(self.marks_obtained), float(self.total_marks))
        if not self.report_card_number:
            self.report_card_number = generate_report_card_number(self.student_id, self.exam_id)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.student} - {self.exam}"


class Ranking(BaseModel):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="rankings")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="rankings")
    rank = models.PositiveIntegerField()
    score = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ("exam", "student")
        verbose_name = "Ranking"
        verbose_name_plural = "Rankings"

    def __str__(self) -> str:
        return f"{self.student} - Rank {self.rank}"
