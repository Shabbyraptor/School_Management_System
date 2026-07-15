from django.contrib import admin

from .models import Permission, Role, RolePermission, User, UserProfile, UserRole


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "username", "first_name", "last_name", "is_active", "is_staff", "is_verified", "date_joined"]
    list_filter = ["is_active", "is_staff", "is_verified", "school"]
    search_fields = ["email", "username", "first_name", "last_name"]
    ordering = ["email"]
    readonly_fields = ["date_joined"]
    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone_number", "profile_photo", "school")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_verified", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "is_system_role"]
    search_fields = ["name", "code"]
    ordering = ["name"]


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "module"]
    search_fields = ["name", "code", "module"]
    ordering = ["module", "code"]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "city", "country", "nationality"]
    search_fields = ["user__email", "user__username", "city", "country"]
    ordering = ["user__email"]


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ["role", "permission"]
    search_fields = ["role__code", "permission__code"]
    ordering = ["role__code", "permission__code"]


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ["user", "role"]
    search_fields = ["user__email", "role__code"]
    ordering = ["user__email", "role__code"]
