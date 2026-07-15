from __future__ import annotations

from django.db import models


class EducationLevel(models.TextChoices):
    PRIMARY = "PRIMARY", "Primary"
    JUNIOR_SECONDARY = "JUNIOR_SECONDARY", "Junior Secondary"
    SENIOR_SECONDARY = "SENIOR_SECONDARY", "Senior Secondary"
    COLLEGE = "COLLEGE", "College"
    UNIVERSITY = "UNIVERSITY", "University"


class SubjectCategory(models.TextChoices):
    LANGUAGES = "LANGUAGES", "Languages"
    SCIENCES = "SCIENCES", "Sciences"
    MATHEMATICS = "MATHEMATICS", "Mathematics"
    HUMANITIES = "HUMANITIES", "Humanities"
    TECHNICAL = "TECHNICAL", "Technical"
    BUSINESS = "BUSINESS", "Business"
    CREATIVE_ARTS = "CREATIVE_ARTS", "Creative Arts"
    SPORTS = "SPORTS", "Sports"
