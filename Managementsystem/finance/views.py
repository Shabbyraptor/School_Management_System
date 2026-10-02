from __future__ import annotations

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.access import ScopedQuerysetMixin
from .models import Discount, FeeCategory, FeeStructure, Invoice, InvoiceItem, Payment, PaymentPlan, Receipt, Scholarship, StudentAccount
from .serializers import (
    DiscountSerializer,
    FeeCategorySerializer,
    FeeStructureSerializer,
    InvoiceItemSerializer,
    InvoiceSerializer,
    PaymentPlanSerializer,
    PaymentSerializer,
    ReceiptSerializer,
    ScholarshipSerializer,
    StudentAccountSerializer,
)


class FeeCategoryViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "finance"
    school_path = "school"
    queryset = FeeCategory.objects.select_related("school")
    serializer_class = FeeCategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["display_order", "name"]


class FeeStructureViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "finance"
    school_path = "school"
    queryset = FeeStructure.objects.select_related("school", "academic_year", "term", "class_field", "fee_category")
    serializer_class = FeeStructureSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["fee_category__name", "class_field__name"]
    ordering_fields = ["effective_date", "amount"]


class InvoiceViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "finance_ledger"
    school_path = "school"
    student_path = "student"
    queryset = Invoice.objects.select_related("school", "student", "academic_year", "term")
    serializer_class = InvoiceSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["invoice_number", "student__first_name", "student__last_name"]
    ordering_fields = ["issue_date", "due_date", "total_amount"]

    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request):
        return Response({"status": "generated"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="email")
    def email_invoice(self, request, pk=None):
        return Response({"status": "emailed"}, status=status.HTTP_200_OK)


class InvoiceItemViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "finance"
    school_path = "invoice__school"
    queryset = InvoiceItem.objects.select_related("invoice", "fee_category")
    serializer_class = InvoiceItemSerializer


class PaymentViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "finance_ledger"
    school_path = "school"
    student_path = "student"
    queryset = Payment.objects.select_related("school", "invoice", "student", "received_by")
    serializer_class = PaymentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["payment_reference", "transaction_reference"]
    ordering_fields = ["payment_date", "amount"]

    def perform_create(self, serializer):
        serializer.save(received_by=self.request.user)

    @action(detail=False, methods=["post"], url_path="reverse")
    def reverse(self, request):
        return Response({"status": "reversed"}, status=status.HTTP_200_OK)


class ReceiptViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "finance_ledger"
    school_path = "school"
    student_path = "student"
    queryset = Receipt.objects.select_related("school", "payment", "student", "issued_by")
    serializer_class = ReceiptSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["receipt_number"]
    ordering_fields = ["issued_at", "amount"]

    @action(detail=True, methods=["get"], url_path="print")
    def print_receipt(self, request, pk=None):
        return Response({"status": "printed"}, status=status.HTTP_200_OK)


class StudentAccountViewSet(ScopedQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    policy = "finance_ledger"
    school_path = "student__school"
    student_path = "student"
    queryset = StudentAccount.objects.select_related("student")
    serializer_class = StudentAccountSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["student__first_name", "student__last_name"]
    ordering_fields = ["current_balance", "total_paid"]

    @action(detail=True, methods=["get"], url_path="statement")
    def statement(self, request, pk=None):
        return Response({"student_id": pk, "statement": "generated"}, status=status.HTTP_200_OK)


class DiscountViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "finance"
    school_path = "school"
    queryset = Discount.objects.select_related("school", "student")
    serializer_class = DiscountSerializer


class ScholarshipViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "finance"
    school_path = "school"
    queryset = Scholarship.objects.select_related("school", "student")
    serializer_class = ScholarshipSerializer


class PaymentPlanViewSet(ScopedQuerysetMixin, viewsets.ModelViewSet):
    policy = "finance"
    school_path = "student__school"
    queryset = PaymentPlan.objects.select_related("student", "invoice")
    serializer_class = PaymentPlanSerializer
