from __future__ import annotations

from django.db import models


class StudentStatus(models.TextChoices):
    APPLICANT = "APPLICANT", "Applicant"
    ACTIVE = "ACTIVE", "Active"
    TRANSFERRED = "TRANSFERRED", "Transferred"
    GRADUATED = "GRADUATED", "Graduated"
    SUSPENDED = "SUSPENDED", "Suspended"
    ALUMNI = "ALUMNI", "Alumni"
    WITHDRAWN = "WITHDRAWN", "Withdrawn"


class RelationshipType(models.TextChoices):
    MOTHER = "MOTHER", "Mother"
    FATHER = "FATHER", "Father"
    GUARDIAN = "GUARDIAN", "Guardian"
    SPONSOR = "SPONSOR", "Sponsor"
    OTHER = "OTHER", "Other"


class DocumentType(models.TextChoices):
    BIRTH_CERTIFICATE = "BIRTH_CERTIFICATE", "Birth Certificate"
    PASSPORT = "PASSPORT", "Passport"
    NATIONAL_ID = "NATIONAL_ID", "National ID"
    MEDICAL_RECORD = "MEDICAL_RECORD", "Medical Record"
    REPORT_CARD = "REPORT_CARD", "Report Card"
    TRANSFER_LETTER = "TRANSFER_LETTER", "Transfer Letter"
    ADMISSION_LETTER = "ADMISSION_LETTER", "Admission Letter"


class Gender(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"
    OTHER = "OTHER", "Other"
    NOT_SPECIFIED = "NOT_SPECIFIED", "Not Specified"
