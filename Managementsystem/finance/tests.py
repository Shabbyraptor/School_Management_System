from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from academics.models import AcademicYear, Class, Term
from accounts.models import User
from core.models import School
from students.models import Student

from .constants import DiscountType, InvoiceStatus, PaymentMethod, PaymentStatus
from .models import Discount, FeeCategory, FeeStructure, Invoice, Payment, PaymentPlan, Scholarship


class FinanceDomainTests(TestCase):
    def setUp(self) -> None:
        self.school = School.objects.create(
            name="Bright Finance School",
            code="BFS900",
            registration_number="REG-900",
            email="finance@bright.edu",
            phone_number="+254700000900",
            address="Nairobi",
            city="Nairobi",
            country="KE",
        )
        self.user = User.objects.create_user(email="finance@bright.edu", username="financeuser", password="secret123", school=self.school)
        self.academic_year = AcademicYear.objects.create(school=self.school, name="2025/2026", code="AY900", start_date=date(2025, 1, 1), end_date=date(2025, 12, 31), is_current=True, is_active=True)
        self.term = Term.objects.create(academic_year=self.academic_year, name="Term 1", number=1, start_date=date(2025, 1, 1), end_date=date(2025, 3, 31), is_current=True, is_active=True)
        self.academic_class = Class.objects.create(school=self.school, name="Grade 9", code="G9", education_level="PRIMARY", display_order=9, is_active=True)
        self.student = Student.objects.create(school=self.school, admission_number="ADM-9001", first_name="Jane", last_name="Doe")
        self.category = FeeCategory.objects.create(school=self.school, name="Tuition", code="TUITION", is_mandatory=True, display_order=1)

    def test_fee_structure_and_invoice_flow(self) -> None:
        structure = FeeStructure.objects.create(
            school=self.school,
            academic_year=self.academic_year,
            term=self.term,
            class_field=self.academic_class,
            fee_category=self.category,
            amount="12000.00",
            is_active=True,
        )
        self.assertEqual(structure.calculate_total_fee(), 12000)

        invoice = Invoice.objects.create(
            school=self.school,
            student=self.student,
            academic_year=self.academic_year,
            term=self.term,
            subtotal="12000.00",
            discount_amount="0.00",
            scholarship_amount="0.00",
            penalty_amount="0.00",
            total_amount="12000.00",
            balance="12000.00",
        )
        self.assertEqual(invoice.status, InvoiceStatus.DRAFT)
        self.assertTrue(invoice.invoice_number.startswith("INV-"))

        payment = Payment.objects.create(
            school=self.school,
            invoice=invoice,
            student=self.student,
            payment_method=PaymentMethod.CASH,
            amount="5000.00",
            received_by=self.user,
            status=PaymentStatus.SUCCESSFUL,
        )
        self.assertEqual(payment.status, PaymentStatus.SUCCESSFUL)

        with self.assertRaises(ValidationError):
            Payment.objects.create(
                school=self.school,
                invoice=invoice,
                student=self.student,
                payment_method=PaymentMethod.CASH,
                amount="20000.00",
                received_by=self.user,
                status=PaymentStatus.SUCCESSFUL,
            )

    def test_discount_scholarship_and_payment_plan_validation(self) -> None:
        discount = Discount.objects.create(
            school=self.school,
            student=self.student,
            name="Sibling Discount",
            discount_type=DiscountType.PERCENTAGE,
            value="10.00",
            is_active=True,
        )
        self.assertTrue(discount.is_active)

        scholarship = Scholarship.objects.create(
            school=self.school,
            student=self.student,
            name="Merit Scholarship",
            sponsor="Education Fund",
            coverage_percentage="25.00",
        )
        self.assertEqual(scholarship.coverage_percentage, 25)

        plan = PaymentPlan.objects.create(
            student=self.student,
            invoice=Invoice.objects.create(
                school=self.school,
                student=self.student,
                academic_year=self.academic_year,
                term=self.term,
                subtotal="6000.00",
                discount_amount="0.00",
                scholarship_amount="0.00",
                penalty_amount="0.00",
                total_amount="6000.00",
                balance="6000.00",
            ),
            installment_amount="2000.00",
            installment_date=date(2025, 2, 15),
            status=PaymentStatus.PENDING,
        )
        self.assertEqual(plan.installment_amount, 2000)
