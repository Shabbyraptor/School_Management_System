from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from academics.models import AcademicYear, Class, Stream, Subject, Term
from accounts.models import Role, UserRole
from core.models import School
from examinations.models import Exam, ExamType, GradeScale, Mark
from finance.models import Invoice
from students.models import Parent, ParentStudent, Student

User = get_user_model()


class RolePolicyTests(TestCase):
    """API-level checks of core.access: role policy, school scoping and portal scoping."""

    def setUp(self) -> None:
        self.school = School.objects.create(name="Alpha School", code="ALPHA", registration_number="REG-A-001", email="a@alpha.test", phone_number="+254700000101")
        self.other = School.objects.create(name="Beta School", code="BETA", registration_number="REG-B-001", email="b@beta.test", phone_number="+254700000102")
        self.users = {}
        for code in ["SCHOOL_ADMIN", "ADMISSIONS_OFFICER", "EXAM_ADMIN", "FINANCE_OFFICER", "TEACHER", "PARENT", "STUDENT"]:
            role = Role.objects.create(code=code, name=code.title())
            user = User.objects.create_user(email=f"{code.lower()}@alpha.test", username=code.lower(), password="secret1234", school=self.school)
            UserRole.objects.create(user=user, role=role)
            self.users[code] = user

        self.year = AcademicYear.objects.create(school=self.school, name="2026", code="AY26A", start_date=date(2026, 1, 1), end_date=date(2026, 11, 30), is_current=True, is_active=True)
        self.term = Term.objects.create(academic_year=self.year, name="Term 1", number=1, start_date=date(2026, 1, 5), end_date=date(2026, 4, 1), is_current=True, is_active=True)
        self.klass = Class.objects.create(school=self.school, name="Form 1", code="AF1")
        self.stream = Stream.objects.create(school=self.school, academic_class=self.klass, name="East")
        self.subject = Subject.objects.create(school=self.school, name="Maths", code="AMAT")

        self.child = Student.objects.create(school=self.school, admission_number="A-001", first_name="Child", last_name="One", user=self.users["STUDENT"], current_class=self.klass, current_stream=self.stream)
        self.classmate = Student.objects.create(school=self.school, admission_number="A-002", first_name="Class", last_name="Mate", current_class=self.klass, current_stream=self.stream)
        self.outsider = Student.objects.create(school=self.other, admission_number="B-001", first_name="Other", last_name="School")
        parent = Parent.objects.create(school=self.school, user=self.users["PARENT"], first_name="Pat", last_name="One")
        ParentStudent.objects.create(parent=parent, student=self.child, relationship="MOTHER")

    def client_for(self, code: str) -> APIClient:
        client = APIClient()
        client.force_authenticate(self.users[code])
        return client

    def test_profile_reports_access_per_role(self) -> None:
        teacher = self.client_for("TEACHER").get("/api/accounts/profile/").json()
        self.assertTrue(teacher["access"]["attendance"]["write"])
        self.assertFalse(teacher["access"]["finance"]["read"])
        self.assertFalse(teacher["portal_only"])
        parent = self.client_for("PARENT").get("/api/accounts/profile/").json()
        self.assertTrue(parent["portal_only"])
        self.assertTrue(parent["access"]["results"]["read"])
        self.assertFalse(parent["access"]["marks"]["read"])

    def test_write_access_follows_role(self) -> None:
        payload = {"school": self.school.id, "name": "Form 2", "code": "AF2", "education_level": "SENIOR_SECONDARY"}
        self.assertEqual(self.client_for("TEACHER").post("/api/academics/classes/", payload).status_code, 403)
        self.assertEqual(self.client_for("SCHOOL_ADMIN").post("/api/academics/classes/", payload).status_code, 201)

        exam_type = {"school": self.school.id, "name": "Opener", "code": "OPEN"}
        self.assertEqual(self.client_for("FINANCE_OFFICER").post("/api/examinations/exam-types/", exam_type).status_code, 403)
        self.assertEqual(self.client_for("EXAM_ADMIN").post("/api/examinations/exam-types/", exam_type).status_code, 201)

        self.assertEqual(self.client_for("TEACHER").get("/api/finance/invoices/").status_code, 403)
        self.assertEqual(self.client_for("ADMISSIONS_OFFICER").get("/api/academics/classes/").status_code, 200)

    def test_staff_cannot_write_for_another_school(self) -> None:
        payload = {"school": self.other.id, "name": "Intruder", "code": "INTR", "education_level": "PRIMARY"}
        self.assertEqual(self.client_for("SCHOOL_ADMIN").post("/api/academics/classes/", payload).status_code, 403)

    def test_staff_see_only_their_school(self) -> None:
        ids = [s["id"] for s in self.client_for("SCHOOL_ADMIN").get("/api/students/").json()["results"]]
        self.assertIn(self.classmate.id, ids)
        self.assertNotIn(self.outsider.id, ids)

    def test_portal_users_see_only_their_students(self) -> None:
        for code in ["PARENT", "STUDENT"]:
            ids = [s["id"] for s in self.client_for(code).get("/api/students/").json()["results"]]
            self.assertEqual(ids, [self.child.id])
        self.assertEqual(self.client_for("PARENT").get(f"/api/students/{self.classmate.id}/").status_code, 404)

    def test_portal_results_require_publishing(self) -> None:
        GradeScale.objects.create(school=self.school, name="Std", grade="A", minimum_mark=70, maximum_mark=100, order=1)
        exam_type = ExamType.objects.create(school=self.school, name="End term", code="AEND")
        exam = Exam.objects.create(school=self.school, exam_type=exam_type, academic_year=self.year, term=self.term, class_name=self.klass, subject=self.subject, name="Maths End Term")
        Mark.objects.create(exam=exam, student=self.child, marks_obtained=Decimal("75"), total_marks=Decimal("100"))
        Mark.objects.create(exam=exam, student=self.classmate, marks_obtained=Decimal("90"), total_marks=Decimal("100"))

        staff = self.client_for("EXAM_ADMIN").get("/api/examinations/results/").json()["results"]
        self.assertEqual(sorted((r["rank"], r["grade"]) for r in staff), [(1, "A"), (2, "A")])
        self.assertEqual(self.client_for("PARENT").get("/api/examinations/results/").json()["results"], [])

        self.assertEqual(self.client_for("TEACHER").post(f"/api/examinations/exams/{exam.id}/publish/").status_code, 403)
        self.assertEqual(self.client_for("EXAM_ADMIN").post(f"/api/examinations/exams/{exam.id}/publish/").status_code, 200)
        visible = self.client_for("PARENT").get("/api/examinations/results/").json()["results"]
        self.assertEqual([r["student"] for r in visible], [self.child.id])

    def test_admin_sets_multiple_roles_but_not_own(self) -> None:
        admin = self.client_for("SCHOOL_ADMIN")
        teacher = self.users["TEACHER"]
        response = admin.post(f"/api/accounts/users/{teacher.id}/roles/", {"role_codes": ["TEACHER", "PARENT"]}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(sorted(response.json()["roles"]), ["PARENT", "TEACHER"])
        access = self.client_for("TEACHER").get("/api/accounts/profile/").json()
        self.assertFalse(access["portal_only"])  # still staff: sees the school, not just own children
        own = admin.post(f"/api/accounts/users/{self.users['SCHOOL_ADMIN'].id}/roles/", {"role_codes": []}, format="json")
        self.assertEqual(own.status_code, 403)
        self.assertEqual(self.client_for("TEACHER").post(f"/api/accounts/users/{teacher.id}/roles/", {"role_codes": []}, format="json").status_code, 403)

    def test_payments_update_invoice_and_account(self) -> None:
        finance = self.client_for("FINANCE_OFFICER")
        invoice = finance.post(
            "/api/finance/invoices/",
            {"school": self.school.id, "student": self.child.id, "academic_year": self.year.id, "term": self.term.id, "subtotal": "1000", "status": "ISSUED", "due_date": "2099-01-01"},
        ).json()
        payment = {"school": self.school.id, "invoice": invoice["id"], "student": self.child.id, "amount": "400", "status": "SUCCESSFUL"}
        self.assertEqual(finance.post("/api/finance/payments/", payment).status_code, 201)
        refreshed = Invoice.objects.get(pk=invoice["id"])
        self.assertEqual(refreshed.balance, Decimal("600.00"))
        self.assertEqual(refreshed.status, "PARTIALLY_PAID")

        overpay = finance.post("/api/finance/payments/", {**payment, "amount": "700"})
        self.assertEqual(overpay.status_code, 400)

        self.assertEqual(finance.post("/api/finance/payments/", {**payment, "amount": "600"}).status_code, 201)
        self.assertEqual(Invoice.objects.get(pk=invoice["id"]).status, "PAID")
        account = self.client_for("PARENT").get("/api/finance/accounts/").json()["results"][0]
        self.assertEqual(Decimal(account["total_paid"]), Decimal("1000.00"))
        self.assertEqual(Decimal(account["current_balance"]), Decimal("0.00"))
