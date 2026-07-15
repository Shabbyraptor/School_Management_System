from django.contrib import admin

from .models import (
    Discount,
    FeeCategory,
    FeeStructure,
    Invoice,
    InvoiceItem,
    Payment,
    PaymentPlan,
    Receipt,
    Scholarship,
    StudentAccount,
)


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ("payment_reference", "status")


class ReceiptInline(admin.TabularInline):
    model = Receipt
    extra = 0
    readonly_fields = ("receipt_number", "issued_at")


@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "school", "is_mandatory", "is_active", "display_order")
    list_filter = ("is_mandatory", "is_active", "school")
    search_fields = ("name", "code")
    ordering = ("display_order", "name")


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ("fee_category", "class_field", "academic_year", "term", "amount", "currency", "is_active")
    list_filter = ("school", "academic_year", "term", "class_field", "is_active")
    search_fields = ("fee_category__name", "class_field__name")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "student", "academic_year", "term", "status", "total_amount", "balance", "due_date")
    list_filter = ("status", "school", "academic_year", "term")
    search_fields = ("invoice_number", "student__first_name", "student__last_name")
    inlines = (InvoiceItemInline, PaymentInline)
    readonly_fields = ("invoice_number", "total_amount", "balance")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_reference", "invoice", "student", "payment_method", "amount", "status", "payment_date")
    list_filter = ("status", "payment_method", "school")
    search_fields = ("payment_reference", "transaction_reference", "student__first_name", "student__last_name")
    readonly_fields = ("payment_reference",)


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("receipt_number", "payment", "student", "amount", "issued_at")
    list_filter = ("school", "issued_at")
    search_fields = ("receipt_number", "student__first_name", "student__last_name")
    readonly_fields = ("receipt_number", "issued_at")


@admin.register(StudentAccount)
class StudentAccountAdmin(admin.ModelAdmin):
    list_display = ("student", "current_balance", "total_invoiced", "total_paid", "total_discount", "last_payment_date")
    search_fields = ("student__first_name", "student__last_name")
    readonly_fields = ("current_balance", "total_invoiced", "total_paid", "total_discount", "last_payment_date")


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("name", "student", "discount_type", "value", "start_date", "end_date", "is_active")
    list_filter = ("discount_type", "is_active", "school")
    search_fields = ("name", "student__first_name", "student__last_name")


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ("name", "student", "sponsor", "coverage_percentage", "start_date", "end_date")
    list_filter = ("school",)
    search_fields = ("name", "sponsor", "student__first_name", "student__last_name")


@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ("student", "invoice", "installment_amount", "installment_date", "status")
    list_filter = ("status",)
    search_fields = ("student__first_name", "student__last_name", "invoice__invoice_number")
