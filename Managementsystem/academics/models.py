from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.models import BaseModel, School

from .constants import EducationLevel, SubjectCategory
from .validators import validate_future_dates, validate_positive_capacity


class AcademicYear(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="academic_years")
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-start_date"]
        indexes = [models.Index(fields=["school", "is_active"])]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"

    def clean(self) -> None:
        super().clean()
        validate_future_dates(self.start_date, self.end_date)
        if self.school_id:
            overlapping = AcademicYear.objects.filter(school=self.school).exclude(pk=self.pk)
            if self.start_date and self.end_date:
                overlapping = overlapping.filter(start_date__lte=self.end_date, end_date__gte=self.start_date)
            if overlapping.exists():
                raise ValidationError("Academic years cannot overlap for the same school.")
            if self.is_current:
                current_years = AcademicYear.objects.filter(school=self.school, is_current=True).exclude(pk=self.pk)
                if current_years.exists():
                    raise ValidationError("Only one current academic year per school is allowed.")
            if self.is_active:
                active_years = AcademicYear.objects.filter(school=self.school, is_active=True).exclude(pk=self.pk)
                if active_years.exists():
                    raise ValidationError("Only one active academic year per school is allowed.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def activate(self) -> None:
        if not self.is_active:
            self.is_active = True
            self.is_current = True
            self.save(update_fields=["is_active", "is_current", "updated_at"])

    def deactivate(self) -> None:
        if self.is_active:
            self.is_active = False
            self.save(update_fields=["is_active", "updated_at"])

    def is_open(self) -> bool:
        today = timezone.localdate()
        return self.is_active and self.start_date <= today <= self.end_date


class Term(BaseModel):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="terms")
    name = models.CharField(max_length=120)
    number = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["number"]
        indexes = [models.Index(fields=["academic_year", "is_current"])]

    def __str__(self) -> str:
        return f"{self.academic_year.name} - {self.name}"

    def clean(self) -> None:
        super().clean()
        validate_future_dates(self.start_date, self.end_date)
        if self.academic_year_id:
            if not (self.academic_year.start_date <= self.start_date <= self.academic_year.end_date):
                raise ValidationError("Term dates must fall within the academic year.")
            if not (self.academic_year.start_date <= self.end_date <= self.academic_year.end_date):
                raise ValidationError("Term dates must fall within the academic year.")
            overlapping = Term.objects.filter(academic_year=self.academic_year).exclude(pk=self.pk)
            if overlapping.filter(start_date__lte=self.end_date, end_date__gte=self.start_date).exists():
                raise ValidationError("Terms cannot overlap within the same academic year.")
            if self.is_current:
                current_terms = Term.objects.filter(academic_year=self.academic_year, is_current=True).exclude(pk=self.pk)
                if current_terms.exists():
                    raise ValidationError("Only one current term per academic year is allowed.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def activate(self) -> None:
        if not self.is_active:
            self.is_active = True
            self.is_current = True
            self.save(update_fields=["is_active", "is_current", "updated_at"])

    def close(self) -> None:
        if self.is_active:
            self.is_active = False
            self.save(update_fields=["is_active", "updated_at"])


class Class(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="classes")
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, unique=True)
    education_level = models.CharField(max_length=30, choices=EducationLevel.choices, default=EducationLevel.PRIMARY)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["display_order", "name"]
        indexes = [models.Index(fields=["school", "name"])]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        if self.school_id:
            if Class.objects.filter(school=self.school, name__iexact=self.name).exclude(pk=self.pk).exists():
                raise ValidationError("Class names must be unique within a school.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def archive(self) -> None:
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])


class Stream(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="streams")
    academic_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="streams", db_column="class_id")
    name = models.CharField(max_length=120)
    capacity = models.PositiveIntegerField(default=30)
    class_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teaching_streams",
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["academic_class", "name"], name="unique_stream_name_per_class")]

    def __str__(self) -> str:
        return f"{self.academic_class.name} - {self.name}"

    def clean(self) -> None:
        super().clean()
        validate_positive_capacity(self.capacity)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Subject(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, unique=True)
    short_name = models.CharField(max_length=20, blank=True)
    category = models.CharField(max_length=30, choices=SubjectCategory.choices, default=SubjectCategory.LANGUAGES)
    description = models.TextField(blank=True)
    is_compulsory = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["school", "code"])]

    def __str__(self) -> str:
        return self.name


class SubjectAssignment(BaseModel):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subject_assignments")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="assignments")
    academic_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="subject_assignments", db_column="class_id")
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name="subject_assignments", db_column="stream_id")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="subject_assignments")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="subject_assignments")

    class Meta:
        ordering = ["subject__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "subject", "academic_class", "stream", "academic_year", "term"],
                name="unique_subject_assignment",
            )
        ]

    def __str__(self) -> str:
        return f"{self.subject.code} -> {self.academic_class.name}"
