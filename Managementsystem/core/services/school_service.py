from __future__ import annotations

from typing import Any, Dict

from ..models import School


class SchoolService:
    """Encapsulates business logic for school management."""

    @staticmethod
    def create_school(data: Dict[str, Any]) -> School:
        school = School.objects.create(
            name=data["name"].strip(),
            code=data["code"].strip().upper(),
            registration_number=data["registration_number"].strip().upper(),
            email=data["email"].strip().lower(),
            phone_number=data["phone_number"].strip(),
            address=data.get("address", "").strip(),
            city=data.get("city", "").strip(),
            country=data.get("country", ""),
            website=data.get("website", "").strip(),
            logo=data.get("logo"),
            is_active=data.get("is_active", True),
        )
        return school

    @staticmethod
    def update_school(school: School, data: Dict[str, Any]) -> School:
        for field in [
            "name",
            "email",
            "phone_number",
            "address",
            "city",
            "country",
            "website",
            "logo",
            "is_active",
        ]:
            if field in data:
                setattr(school, field, data[field])
        if "email" in data and data["email"]:
            school.email = data["email"].strip().lower()
        if "name" in data and data["name"]:
            school.name = data["name"].strip()
        school.save()
        return school

    @staticmethod
    def activate_school(school: School) -> School:
        school.activate()
        return school

    @staticmethod
    def deactivate_school(school: School) -> School:
        school.deactivate()
        return school
