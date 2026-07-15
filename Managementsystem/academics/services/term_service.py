from __future__ import annotations

from typing import Any

from django.db import transaction

from ..models import Term


class TermService:
    @staticmethod
    @transaction.atomic
    def create_term(data: dict[str, Any]) -> Term:
        return Term.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def activate_term(term: Term) -> Term:
        term.activate()
        return term

    @staticmethod
    @transaction.atomic
    def close_term(term: Term) -> Term:
        term.close()
        return term
