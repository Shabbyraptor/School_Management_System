from __future__ import annotations

from django.db import models


class ExamStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    OPEN = "OPEN", "Open"
    MARKING = "MARKING", "Marking"
    COMPLETED = "COMPLETED", "Completed"
    PUBLISHED = "PUBLISHED", "Published"
    ARCHIVED = "ARCHIVED", "Archived"


class AssessmentType(models.TextChoices):
    CAT = "CAT", "CAT"
    ASSIGNMENT = "ASSIGNMENT", "Assignment"
    PRACTICAL = "PRACTICAL", "Practical"
    MIDTERM = "MIDTERM", "Midterm"
    PROJECT = "PROJECT", "Project"
    END_TERM = "END_TERM", "End Term"
    MOCK = "MOCK", "Mock"
    FINAL_EXAMINATION = "FINAL_EXAMINATION", "Final Examination"


class ResultStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    PUBLISHED = "PUBLISHED", "Published"
