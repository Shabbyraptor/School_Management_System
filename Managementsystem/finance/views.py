from __future__ import annotations

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Discount, FeeCategory, FeeStructure, Invoice, InvoiceItem, Payment, PaymentPlan, Receipt, Scholarship, StudentAccount
from .permissions import CanManageFinance, CanViewFinanceOwnData
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


class FeeCategoryViewSet(viewsets.ModelViewSet):
    queryset = FeeCategory.objects.select_related("school")
    serializer_class = FeeCategorySerializer
    permission_classes = [IsAuthenticated, CanManageFinance]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["display_order", "name"]


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.select_related("school", "academic_year", "term", "class_field", "fee_category")
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAuthenticated, CanManageFinance]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["fee_category__name", "class_field__name"]
    ordering_fields = ["effective_date", "amount"]


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related("school", "student", "academic_year", "term")
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, CanManageFinance]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["invoice_number", "student__first_name", "student__last_name"]
    ordering_fields = ["issue_date", "due_date", "total_amount"]

    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request):
        return Response({"status": "generated"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="email")
    def email_invoice(self, request, pk=None):
        return Response({"status": "emailed"}, status=status.HTTP_200_OK)


class InvoiceItemViewSet(viewsets.ModelViewSet):
    queryset = InvoiceItem.objects.select_related("invoice", "fee_category")
    serializer_class = InvoiceItemSerializer
    permission_classes = [IsAuthenticated, CanManageFinance]


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("school", "invoice", "student", "received_by")
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, CanManageFinance]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["payment_reference", "transaction_reference"]
    ordering_fields = ["payment_date", "amount"]

    @action(detail=False, methods=["post"], url_path="reverse")
    def reverse(self, request):
        return Response({"status": "reversed"}, status=status.HTTP_200_OK)


class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.select_related("school", "payment", "student", "issued_by")
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated, CanManageFinance]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["receipt_number"]
    ordering_fields = ["issued_at", "amount"]

    @action(detail=True, methods=["get"], url_path="print")
    def print_receipt(self, request, pk=None):
        return Response({"status": "printed"}, status=status.HTTP_200_OK)


class StudentAccountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StudentAccount.objects.select_related("student")
    serializer_class = StudentAccountSerializer
    permission_classes = [IsAuthenticated, CanManageFinance]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["student__first_name", "student__last_name"]
    ordering_fields = ["current_balance", "total_paid"]

    @action(detail=True, methods=["get"], url_path="statement")
    def statement(self, request, pk=None):
        return Response({"student_id": pk, "statement": "generated"}, status=status.HTTP_200_OK)


class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.select_related("school", "student")
    serializer_class = DiscountSerializer
    permission_classes = [IsAuthenticated, CanManageFinance]


class ScholarshipViewSet(viewsets.ModelViewSet):
    queryset = Scholarship.objects.select_related("school", "student")
    serializer_class = ScholarshipSerializer
    permission_classes = [IsAuthenticated, CanManageFinance]


class PaymentPlanViewSet(viewsets.ModelViewSet):
    queryset = PaymentPlan.objects.select_related("student", "invoice")
    serializer_class = PaymentPlanSerializer
    permission_classes = [IsAuthenticated, CanManageFinance]
