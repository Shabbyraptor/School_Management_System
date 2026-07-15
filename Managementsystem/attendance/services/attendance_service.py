from __future__ import annotations

from typing import Any

from django.db import transaction

from ..models import AttendanceRecord, AttendanceSession


class AttendanceService:
    @staticmethod
    @transaction.atomic
    def mark_attendance(data: dict[str, Any]) -> AttendanceRecord:
        return AttendanceRecord.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def bulk_mark_attendance(session: AttendanceSession, records: list[dict[str, Any]]) -> list[AttendanceRecord]:
        created = []
        for record_data in records:
            created.append(AttendanceRecord(attendance_session=session, **record_data))
        return list(AttendanceRecord.objects.bulk_create(created))

    @staticmethod
    @transaction.atomic
    def update_attendance(record: AttendanceRecord, data: dict[str, Any]) -> AttendanceRecord:
        for field, value in data.items():
            setattr(record, field, value)
        record.save()
        return record

    @staticmethod
    @transaction.atomic
    def delete_attendance(record: AttendanceRecord) -> None:
        record.delete()
