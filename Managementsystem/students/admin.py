from django.contrib import admin

from .models import EmergencyContact, Enrollment, Guardian, Parent, ParentStudent, Student, StudentDocument


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1


class EmergencyContactInline(admin.TabularInline):
    model = EmergencyContact
    extra = 1


class StudentDocumentInline(admin.TabularInline):
    model = StudentDocument
    extra = 1


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("admission_number", "full_name", "school", "status", "current_class", "current_stream")
    search_fields = ("admission_number", "first_name", "last_name", "email")
    list_filter = ("status", "school", "current_class")
    readonly_fields = ("created_at", "updated_at")
    inlines = [EnrollmentInline, EmergencyContactInline, StudentDocumentInline]


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "school", "relationship", "email", "phone_number")
    search_fields = ("first_name", "last_name", "email")
    list_filter = ("school", "relationship")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "school", "relationship", "phone_number", "email")
    search_fields = ("first_name", "last_name", "email")
    list_filter = ("school", "relationship")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "academic_year", "term", "class_field", "stream", "status")
    list_filter = ("status", "academic_year", "term")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ParentStudent)
class ParentStudentAdmin(admin.ModelAdmin):
    list_display = ("student", "parent", "relationship")
    list_filter = ("relationship",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ("student", "name", "relationship", "phone")
    readonly_fields = ("created_at", "updated_at")


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ("student", "document_type", "uploaded_at")
    list_filter = ("document_type",)
    readonly_fields = ("created_at", "updated_at")
