from __future__ import annotations

from rest_framework import serializers

from .models import EmergencyContact, Enrollment, Guardian, Parent, ParentStudent, Student, StudentDocument


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Student
        fields = [
            "id",
            "school",
            "user",
            "admission_number",
            "first_name",
            "middle_name",
            "last_name",
            "full_name",
            "gender",
            "date_of_birth",
            "nationality",
            "birth_certificate_number",
            "national_id",
            "passport_number",
            "admission_date",
            "email",
            "phone_number",
            "photo",
            "religion",
            "blood_group",
            "medical_conditions",
            "allergies",
            "address",
            "city",
            "county",
            "country",
            "status",
            "current_class",
            "current_stream",
            "created_at",
            "updated_at",
        ]


class StudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "school",
            "user",
            "first_name",
            "middle_name",
            "last_name",
            "gender",
            "date_of_birth",
            "nationality",
            "birth_certificate_number",
            "national_id",
            "passport_number",
            "admission_date",
            "email",
            "phone_number",
            "photo",
            "religion",
            "blood_group",
            "medical_conditions",
            "allergies",
            "address",
            "city",
            "county",
            "country",
            "current_class",
            "current_stream",
        ]


class StudentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["status", "current_class", "current_stream", "phone_number", "address", "city", "country"]


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = ["id", "school", "user", "first_name", "last_name", "relationship", "occupation", "employer", "email", "phone_number", "address", "city", "country", "created_at", "updated_at"]


class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = ["id", "school", "first_name", "last_name", "relationship", "phone_number", "email", "address", "occupation", "created_at", "updated_at"]


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["id", "student", "academic_year", "term", "class_field", "stream", "enrollment_date", "status", "created_at", "updated_at"]


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ["id", "student", "name", "relationship", "phone", "email", "address", "created_at", "updated_at"]


class StudentDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDocument
        fields = ["id", "student", "document_type", "file", "uploaded_at", "created_at", "updated_at"]


class ParentStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentStudent
        fields = ["id", "parent", "student", "relationship", "created_at", "updated_at"]
