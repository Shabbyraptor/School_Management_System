from __future__ import annotations

from rest_framework import serializers

from .models import Discount, FeeCategory, FeeStructure, Invoice, InvoiceItem, Payment, PaymentPlan, Receipt, Scholarship, StudentAccount


class FeeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeCategory
        fields = ["id", "school", "name", "code", "description", "is_mandatory", "is_active", "display_order"]


class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = ["id", "school", "academic_year", "term", "class_field", "fee_category", "amount", "currency", "effective_date", "expiry_date", "is_active"]


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ["id", "invoice", "fee_category", "description", "quantity", "unit_price", "total"]


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = ["id", "school", "student", "academic_year", "term", "invoice_number", "issue_date", "due_date", "status", "subtotal", "discount_amount", "scholarship_amount", "penalty_amount", "total_amount", "balance", "remarks", "items"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "school", "invoice", "student", "payment_reference", "transaction_reference", "payment_method", "payment_date", "amount", "received_by", "remarks", "status"]


class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ["id", "school", "receipt_number", "payment", "student", "issued_at", "issued_by", "amount"]


class StudentAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAccount
        fields = ["id", "student", "current_balance", "total_invoiced", "total_paid", "total_discount", "last_payment_date"]


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ["id", "school", "student", "name", "discount_type", "value", "start_date", "end_date", "is_active"]


class ScholarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scholarship
        fields = ["id", "school", "student", "name", "sponsor", "coverage_percentage", "start_date", "end_date"]


class PaymentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentPlan
        fields = ["id", "student", "invoice", "installment_amount", "installment_date", "status"]
