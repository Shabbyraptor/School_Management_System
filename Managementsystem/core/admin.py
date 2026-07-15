from django.contrib import admin

from .models import AuditLog, School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "code",
        "registration_number",
        "email",
        "phone_number",
        "city",
        "country",
        "is_active",
        "is_deleted",
        "created_at",
    ]
    list_filter = ["is_active", "is_deleted", "country"]
    search_fields = ["name", "code", "registration_number", "email", "city"]
    ordering = ["name"]
    readonly_fields = ["created_at", "updated_at", "deleted_at"]
    fieldsets = (
        (None, {
            "fields": (
                "name",
                "code",
                "registration_number",
                "email",
                "phone_number",
                "website",
                "address",
                "city",
                "country",
                "logo",
                "is_active",
            )
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at", "deleted_at"),
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        "timestamp",
        "action",
        "model_name",
        "object_id",
        "user",
        "school",
        "ip_address",
    ]
    list_filter = ["action", "model_name", "school"]
    search_fields = ["model_name", "object_id", "description", "user__username", "school__name"]
    ordering = ["-timestamp"]
    readonly_fields = [
        "user",
        "school",
        "action",
        "model_name",
        "object_id",
        "description",
        "ip_address",
        "timestamp",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
