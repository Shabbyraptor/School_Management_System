from __future__ import annotations

from typing import Any

from django.db import transaction

from ..models import AttendanceSession


class AttendanceSessionService:
    @staticmethod
    @transaction.atomic
    def create_session(data: dict[str, Any]) -> AttendanceSession:
        return AttendanceSession.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def open_session(session: AttendanceSession) -> AttendanceSession:
        session.open_session()
        return session

    @staticmethod
    @transaction.atomic
    def close_session(session: AttendanceSession) -> AttendanceSession:
        session.close_session()
        return session

    @staticmethod
    @transaction.atomic
    def archive_session(session: AttendanceSession) -> AttendanceSession:
        session.archive_session()
        return session
