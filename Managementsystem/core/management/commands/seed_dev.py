"""Seed a local development database with a sign-in account and a small base dataset.

    python manage.py seed_dev

Idempotent: re-running it skips anything that already exists. For local development
only; never run it against a real deployment.

Dev logins (all use the same password; override with SEED_ADMIN_PASSWORD):
    password:               Scholaris-dev-2026
    admin@scholaris.local       superuser (all schools)
    schooladmin@scholaris.local SCHOOL_ADMIN
    admissions@scholaris.local  ADMISSIONS_OFFICER
    exams@scholaris.local       EXAM_ADMIN
    finance@scholaris.local     FINANCE_OFFICER
    teacher@scholaris.local     TEACHER
    parent@scholaris.local      PARENT (linked to Achieng Otieno)
    student@scholaris.local     STUDENT (Achieng Otieno's login)
"""
from __future__ import annotations

import os
from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from academics.models import AcademicYear, Class, Stream, Subject, Term
from accounts.models import Role, UserRole
from core.models import School
from examinations.models import GradeScale
from finance.services import LedgerService
from students.models import Parent, ParentStudent, Student

ADMIN_EMAIL = os.environ.get("SEED_ADMIN_EMAIL", "admin@scholaris.local")
ADMIN_PASSWORD = os.environ.get("SEED_ADMIN_PASSWORD", "Scholaris-dev-2026")

ROLES = [
    ("SCHOOL_ADMIN", "School Admin"),
    ("ADMISSIONS_OFFICER", "Admissions Officer"),
    ("EXAM_ADMIN", "Exam Admin"),
    ("FINANCE_OFFICER", "Finance Officer"),
    ("TEACHER", "Teacher"),
    ("PARENT", "Parent"),
    ("STUDENT", "Student"),
]

ROLE_USERS = {
    "SCHOOL_ADMIN": ("schooladmin@scholaris.local", "Sarah", "Mwangi"),
    "ADMISSIONS_OFFICER": ("admissions@scholaris.local", "Peter", "Kiprop"),
    "EXAM_ADMIN": ("exams@scholaris.local", "Ruth", "Akinyi"),
    "FINANCE_OFFICER": ("finance@scholaris.local", "James", "Ouma"),
    "TEACHER": ("teacher@scholaris.local", "Lucy", "Chebet"),
    "PARENT": ("parent@scholaris.local", "Mary", "Otieno"),
    "STUDENT": ("student@scholaris.local", "Achieng", "Otieno"),
}

GRADES = [
    ("A", 80, 100, "Excellent"),
    ("B", 65, 79, "Good"),
    ("C", 50, 64, "Average"),
    ("D", 40, 49, "Below average"),
    ("E", 0, 39, "Needs support"),
]

STUDENTS = [
    ("Achieng", "Otieno", "FEMALE"),
    ("Brian", "Kamau", "MALE"),
    ("Cynthia", "Wanjiru", "FEMALE"),
    ("David", "Mutua", "MALE"),
    ("Esther", "Njeri", "FEMALE"),
    ("Felix", "Odhiambo", "MALE"),
]


class Command(BaseCommand):
    help = "Create a dev superuser and a small base dataset for local development."

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()

        for code, name in ROLES:
            Role.objects.get_or_create(code=code, defaults={"name": name, "is_system_role": True})

        school, _ = School.objects.get_or_create(
            code="RIVERSIDE",
            defaults={
                "name": "Riverside Academy",
                "registration_number": "REG-2026-001",
                "email": "info@riverside.local",
                "phone_number": "+254700000001",
                "city": "Nairobi",
                "country": "KE",
            },
        )

        if not User.objects.filter(email=ADMIN_EMAIL).exists():
            User.objects.create_superuser(
                email=ADMIN_EMAIL,
                password=ADMIN_PASSWORD,
                username="admin",
                first_name="Dev",
                last_name="Admin",
                school=school,
            )
            self.stdout.write(f"Created superuser {ADMIN_EMAIL}")

        year, _ = AcademicYear.objects.get_or_create(
            code="AY2026",
            defaults={
                "school": school,
                "name": "2026",
                "start_date": date(2026, 1, 5),
                "end_date": date(2026, 11, 27),
                "is_current": True,
                "is_active": True,
            },
        )
        for number, (start, end) in enumerate(
            [(date(2026, 1, 5), date(2026, 4, 2)), (date(2026, 4, 27), date(2026, 7, 31)), (date(2026, 8, 24), date(2026, 11, 27))],
            start=1,
        ):
            Term.objects.get_or_create(
                academic_year=year,
                number=number,
                defaults={
                    "name": f"Term {number}",
                    "start_date": start,
                    "end_date": end,
                    "is_current": number == 3,
                    "is_active": True,
                },
            )

        streams = []
        for order, (name, code) in enumerate([("Form 1", "F1"), ("Form 2", "F2")], start=1):
            academic_class, _ = Class.objects.get_or_create(
                code=code,
                defaults={"school": school, "name": name, "education_level": "SENIOR_SECONDARY", "display_order": order},
            )
            for stream_name in ("East", "West"):
                stream, _ = Stream.objects.get_or_create(
                    academic_class=academic_class,
                    name=stream_name,
                    defaults={"school": school, "capacity": 40},
                )
                streams.append(stream)

        for name, code, category in [
            ("Mathematics", "MAT", "MATHEMATICS"),
            ("English", "ENG", "LANGUAGES"),
            ("Kiswahili", "KIS", "LANGUAGES"),
            ("Biology", "BIO", "SCIENCES"),
        ]:
            Subject.objects.get_or_create(code=code, defaults={"school": school, "name": name, "category": category})

        if not Student.objects.filter(school=school).exists():
            for i, (first, last, gender) in enumerate(STUDENTS):
                stream = streams[i % len(streams)]
                Student.objects.create(
                    school=school,
                    admission_number=f"RIV/2026/{i + 1:03d}",
                    first_name=first,
                    last_name=last,
                    gender=gender,
                    status="ACTIVE",
                    current_class=stream.academic_class,
                    current_stream=stream,
                )

        # One account per role, all at Riverside.
        accounts = {}
        for code, (email, first, last) in ROLE_USERS.items():
            user = User.objects.filter(email=email).first()
            if user is None:
                user = User.objects.create_user(
                    email=email,
                    password=ADMIN_PASSWORD,
                    username=email.split("@")[0],
                    first_name=first,
                    last_name=last,
                    school=school,
                )
                self.stdout.write(f"Created {code} user {email}")
            UserRole.objects.get_or_create(user=user, role=Role.objects.get(code=code))
            accounts[code] = user

        # The student login is Achieng; the parent login is her mother.
        achieng = Student.objects.filter(school=school, first_name="Achieng").first()
        if achieng:
            if achieng.user_id is None:
                Student.objects.filter(pk=achieng.pk).update(user=accounts["STUDENT"])
            parent, _ = Parent.objects.get_or_create(
                user=accounts["PARENT"],
                defaults={"school": school, "first_name": "Mary", "last_name": "Otieno", "relationship": "MOTHER", "phone_number": "+254711000001"},
            )
            ParentStudent.objects.get_or_create(parent=parent, student=achieng, relationship="MOTHER")

        for order, (grade, low, high, remark) in enumerate(GRADES, start=1):
            GradeScale.objects.get_or_create(
                school=school,
                grade=grade,
                defaults={"name": "Standard", "minimum_mark": low, "maximum_mark": high, "remarks": remark, "order": order},
            )

        LedgerService.rebuild_all()
        self.stdout.write(self.style.SUCCESS("Dev data ready."))
