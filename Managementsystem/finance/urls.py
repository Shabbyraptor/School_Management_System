from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DiscountViewSet,
    FeeCategoryViewSet,
    FeeStructureViewSet,
    InvoiceItemViewSet,
    InvoiceViewSet,
    PaymentPlanViewSet,
    PaymentViewSet,
    ReceiptViewSet,
    ScholarshipViewSet,
    StudentAccountViewSet,
)

router = DefaultRouter()
router.register(r"fee-categories", FeeCategoryViewSet, basename="fee-category")
router.register(r"fee-structures", FeeStructureViewSet, basename="fee-structure")
router.register(r"invoices", InvoiceViewSet, basename="invoice")
router.register(r"invoice-items", InvoiceItemViewSet, basename="invoice-item")
router.register(r"payments", PaymentViewSet, basename="payment")
router.register(r"receipts", ReceiptViewSet, basename="receipt")
router.register(r"accounts", StudentAccountViewSet, basename="student-account")
router.register(r"discounts", DiscountViewSet, basename="discount")
router.register(r"scholarships", ScholarshipViewSet, basename="scholarship")
router.register(r"payment-plans", PaymentPlanViewSet, basename="payment-plan")

urlpatterns = [path("", include(router.urls))]
