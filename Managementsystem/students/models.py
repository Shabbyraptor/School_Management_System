from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from academics.models import AcademicYear, Class, Stream, Term
from core.models import BaseModel, School

from .constants import DocumentType, Gender, RelationshipType, StudentStatus
from .validators import validate_admission_date, validate_birth_date, validate_relationship


class Student(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="students")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="student")
    admission_number = models.CharField(max_length=40, unique=True, db_index=True)
    first_name = models.CharField(max_length=120)
    middle_name = models.CharField(max_length=120, blank=True)
    last_name = models.CharField(max_length=120)
    gender = models.CharField(max_length=20, choices=Gender.choices, default=Gender.NOT_SPECIFIED)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=120, blank=True)
    birth_certificate_number = models.CharField(max_length=80, blank=True)
    national_id = models.CharField(max_length=40, blank=True)
    passport_number = models.CharField(max_length=40, blank=True)
    admission_date = models.DateField(default=timezone.localdate)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to="students/photos/", blank=True, null=True)
    religion = models.CharField(max_length=80, blank=True)
    blood_group = models.CharField(max_length=10, blank=True)
    medical_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=120, blank=True)
    county = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=StudentStatus.choices, default=StudentStatus.APPLICANT)
    current_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True, related_name="students")
    current_stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True, related_name="students")

    class Meta:
        ordering = ["admission_number"]
        indexes = [models.Index(fields=["school", "status"])]

    def __str__(self) -> str:
        return self.full_name

    @property
    def full_name(self) -> str:
        return " ".join(part for part in [self.first_name, self.middle_name, self.last_name] if part).strip()

    def clean(self) -> None:
        super().clean()
        validate_birth_date(self.date_of_birth)
        validate_admission_date(self.admission_date, self.date_of_birth)
        if self.admission_number and Student.objects.filter(school=self.school, admission_number=self.admission_number).exclude(pk=self.pk).exists():
            raise ValidationError("Admission number must be unique within a school.")

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)

    def activate(self) -> None:
        self.status = StudentStatus.ACTIVE
        self.save(update_fields=["status", "updated_at"])

    def promote(self) -> None:
        self.status = StudentStatus.ACTIVE
        self.save(update_fields=["status", "updated_at"])

    def transfer(self) -> None:
        self.status = StudentStatus.TRANSFERRED
        self.save(update_fields=["status", "updated_at"])

    def graduate(self) -> None:
        self.status = StudentStatus.GRADUATED
        self.save(update_fields=["status", "updated_at"])

    def withdraw(self) -> None:
        self.status = StudentStatus.WITHDRAWN
        self.save(update_fields=["status", "updated_at"])


class Parent(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="parents")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="parent")
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    relationship = models.CharField(max_length=20, choices=RelationshipType.choices, default=RelationshipType.OTHER)
    occupation = models.CharField(max_length=120, blank=True)
    employer = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def clean(self) -> None:
        super().clean()
        validate_relationship(self.relationship)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)


class Guardian(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="guardians")
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    relationship = models.CharField(max_length=20, choices=RelationshipType.choices, default=RelationshipType.GUARDIAN)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    occupation = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def clean(self) -> None:
        super().clean()
        validate_relationship(self.relationship)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)


class ParentStudent(BaseModel):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name="student_links")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="parent_links")
    relationship = models.CharField(max_length=20, choices=RelationshipType.choices, default=RelationshipType.OTHER)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["parent", "student", "relationship"], name="unique_parent_student_relationship")]
        ordering = ["student__first_name", "parent__first_name"]

    def __str__(self) -> str:
        return f"{self.parent} -> {self.student}"

    def clean(self) -> None:
        super().clean()
        validate_relationship(self.relationship)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)


class Enrollment(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="student_enrollments")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="student_enrollments")
    class_field = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="student_enrollments", db_column="class_id")
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name="student_enrollments", db_column="stream_id")
    enrollment_date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=20, choices=[("ACTIVE", "Active"), ("PROMOTED", "Promoted"), ("TRANSFERRED", "Transferred"), ("COMPLETED", "Completed")])

    class Meta:
        ordering = ["-enrollment_date"]

    def __str__(self) -> str:
        return f"{self.student.full_name} - {self.class_field.name}"


class EmergencyContact(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="emergency_contacts")
    name = models.CharField(max_length=120)
    relationship = models.CharField(max_length=20, choices=RelationshipType.choices, default=RelationshipType.OTHER)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class StudentDocument(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=30, choices=DocumentType.choices, default=DocumentType.BIRTH_CERTIFICATE)
    file = models.FileField(upload_to="students/documents/")
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return f"{self.student.full_name} - {self.document_type}"
