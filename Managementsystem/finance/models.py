from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from academics.models import AcademicYear, Class, Term
from core.models import BaseModel, School
from students.models import Student

from .constants import Currency, DiscountType, InvoiceStatus, PaymentMethod, PaymentStatus
from .utils import calculate_balance, calculate_invoice_total, default_due_date, generate_invoice_number, generate_receipt_number
from .validators import validate_discount_value, validate_invoice_totals, validate_non_negative_amount, validate_payment_amount


def placeholder_number() -> str:
    """Unique stand-in for a number that is derived from the pk once the row exists."""
    return f"TMP-{uuid4().hex}"


class FeeCategory(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="fee_categories")
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, db_index=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "name"]
        constraints = [models.UniqueConstraint(fields=["school", "code"], name="unique_fee_category_code_per_school")]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class FeeStructure(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="fee_structures")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="fee_structures")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="fee_structures")
    class_field = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="fee_structures", db_column="class_id")
    fee_category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE, related_name="fee_structures")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=10, choices=Currency.choices, default=Currency.KES)
    effective_date = models.DateField(default=date.today)
    expiry_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["-effective_date", "fee_category__name"]
        constraints = [
            models.UniqueConstraint(fields=["school", "academic_year", "term", "class_field", "fee_category", "effective_date"], name="unique_fee_structure")
        ]

    def __str__(self) -> str:
        return f"{self.fee_category.name} - {self.class_field.name}"

    def clean(self) -> None:
        super().clean()
        validate_non_negative_amount(self.amount)
        if self.is_active and self.school_id and self.academic_year_id and self.term_id and self.class_field_id and self.fee_category_id:
            duplicate = FeeStructure.objects.filter(
                school=self.school,
                academic_year=self.academic_year,
                term=self.term,
                class_field=self.class_field,
                fee_category=self.fee_category,
                is_active=True,
            ).exclude(pk=self.pk)
            if duplicate.exists():
                raise ValidationError("An active fee structure already exists for this class and category.")

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)

    def activate(self) -> None:
        self.is_active = True
        self.save(update_fields=["is_active", "updated_at"])

    def deactivate(self) -> None:
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])

    def calculate_total_fee(self) -> Decimal:
        return self.amount


class Invoice(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="invoices")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="invoices")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="invoices")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="invoices")
    invoice_number = models.CharField(max_length=40, unique=True, db_index=True, blank=True)
    issue_date = models.DateField(default=date.today)
    due_date = models.DateField(default=default_due_date)
    status = models.CharField(max_length=24, choices=InvoiceStatus.choices, default=InvoiceStatus.DRAFT)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    scholarship_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    penalty_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-issue_date", "-id"]
        indexes = [models.Index(fields=["student", "status"])]

    def __str__(self) -> str:
        return self.invoice_number

    def clean(self) -> None:
        super().clean()
        validate_invoice_totals(self.subtotal, self.discount_amount, self.scholarship_amount, self.penalty_amount)
        if self.total_amount < 0 or self.balance < 0:
            raise ValidationError("Invoice totals cannot be negative.")

    def save(self, *args, **kwargs) -> None:
        # The number embeds the pk, which only exists after the first insert, so save
        # under a unique placeholder and then write the real number.
        assign_number = not self.invoice_number
        if assign_number:
            self.invoice_number = placeholder_number()
        if not self.total_amount:
            self.total_amount = calculate_invoice_total(self.subtotal, self.discount_amount, self.scholarship_amount, self.penalty_amount)
        if self.balance == Decimal("0.00"):
            self.balance = self.total_amount
        self.full_clean()
        result = super().save(*args, **kwargs)
        if assign_number:
            self.invoice_number = generate_invoice_number(self.school.code, self.academic_year.code, self.pk)
            super().save(update_fields=["invoice_number"])
        return result

    def calculate_balance(self) -> Decimal:
        return calculate_balance(self.total_amount, sum(self.payments.values_list("amount", flat=True)))

    def mark_paid(self) -> None:
        self.status = InvoiceStatus.PAID
        self.balance = Decimal("0.00")
        self.save(update_fields=["status", "balance", "updated_at"])

    def mark_overdue(self) -> None:
        self.status = InvoiceStatus.OVERDUE
        self.save(update_fields=["status", "updated_at"])

    def cancel(self) -> None:
        self.status = InvoiceStatus.CANCELLED
        self.save(update_fields=["status", "updated_at"])


class InvoiceItem(BaseModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    fee_category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE, related_name="invoice_items")
    description = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ["fee_category__name"]

    def __str__(self) -> str:
        return f"{self.fee_category.name} - {self.invoice.invoice_number}"

    def clean(self) -> None:
        super().clean()
        validate_non_negative_amount(self.unit_price)
        validate_non_negative_amount(self.quantity)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        if not self.total:
            self.total = self.unit_price * self.quantity
        return super().save(*args, **kwargs)


class Payment(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="payments")
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="payments")
    payment_reference = models.CharField(max_length=40, unique=True, db_index=True, blank=True)
    transaction_reference = models.CharField(max_length=80, blank=True)
    payment_method = models.CharField(max_length=24, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    payment_date = models.DateField(default=date.today)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="received_payments")
    remarks = models.TextField(blank=True)
    status = models.CharField(max_length=24, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)

    class Meta:
        ordering = ["-payment_date", "-id"]
        indexes = [models.Index(fields=["invoice", "status"])]

    def __str__(self) -> str:
        return self.payment_reference

    def clean(self) -> None:
        super().clean()
        validate_non_negative_amount(self.amount)
        if self.invoice_id and self.amount is not None:
            # The invoice balance is kept current by LedgerService; when editing an existing
            # successful payment, its own amount is already deducted from that balance.
            balance = self.invoice.balance
            if self.pk:
                previous = Payment.objects.filter(pk=self.pk, status=PaymentStatus.SUCCESSFUL).values_list("amount", flat=True).first()
                balance += previous or Decimal("0.00")
            validate_payment_amount(self.amount, balance)

    def save(self, *args, **kwargs) -> None:
        # Same pk-after-insert issue as Invoice.save.
        assign_reference = not self.payment_reference
        if assign_reference:
            self.payment_reference = placeholder_number()
        self.full_clean()
        result = super().save(*args, **kwargs)
        if assign_reference:
            self.payment_reference = generate_receipt_number(self.school.code, self.pk)
            super().save(update_fields=["payment_reference"])
        return result

    def validate_payment(self) -> None:
        self.status = PaymentStatus.SUCCESSFUL
        self.save(update_fields=["status", "updated_at"])

    def apply_payment(self) -> None:
        self.status = PaymentStatus.SUCCESSFUL
        self.save(update_fields=["status", "updated_at"])

    def reverse_payment(self) -> None:
        self.status = PaymentStatus.REVERSED
        self.save(update_fields=["status", "updated_at"])


class Receipt(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="receipts")
    receipt_number = models.CharField(max_length=40, unique=True, db_index=True, blank=True)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name="receipt")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="receipts")
    issued_at = models.DateTimeField(auto_now_add=True)
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="issued_receipts")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ["-issued_at"]

    def __str__(self) -> str:
        return self.receipt_number

    def clean(self) -> None:
        super().clean()
        validate_non_negative_amount(self.amount)

    def save(self, *args, **kwargs) -> None:
        if not self.receipt_number:
            self.receipt_number = generate_receipt_number(self.school.code, self.payment_id)
        self.full_clean()
        return super().save(*args, **kwargs)


class StudentAccount(BaseModel):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="finance_account")
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_invoiced = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    last_payment_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ["student__first_name", "student__last_name"]

    def __str__(self) -> str:
        return f"{self.student.full_name} account"


class Discount(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="discounts")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="discounts")
    name = models.CharField(max_length=120)
    discount_type = models.CharField(max_length=24, choices=DiscountType.choices, default=DiscountType.PERCENTAGE)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        validate_discount_value(self.value, self.discount_type)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)


class Scholarship(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="scholarships")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="scholarships")
    name = models.CharField(max_length=120)
    sponsor = models.CharField(max_length=120, blank=True)
    coverage_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        if self.coverage_percentage < 0 or self.coverage_percentage > Decimal("100"):
            raise ValidationError("Scholarship coverage must be between 0 and 100%.")

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)


class PaymentPlan(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="payment_plans")
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payment_plans")
    installment_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    installment_date = models.DateField(default=date.today)
    status = models.CharField(max_length=24, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)

    class Meta:
        ordering = ["installment_date"]

    def __str__(self) -> str:
        return f"{self.student.full_name} - {self.installment_date}"

    def clean(self) -> None:
        super().clean()
        validate_non_negative_amount(self.installment_amount)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)
