from __future__ import annotations

from django.core.exceptions import NON_FIELD_ERRORS
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def exception_handler(exc, context):
    """DRF's handler, plus: model-level ValidationErrors (from clean()/save()) become 400s.

    Without this, business rules enforced in models (e.g. "Payment amount cannot exceed
    invoice balance") surface as 500 errors instead of a message the client can show.
    """
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, "message_dict"):
            data = {
                ("non_field_errors" if field == NON_FIELD_ERRORS else field): messages
                for field, messages in exc.message_dict.items()
            }
        else:
            data = {"non_field_errors": exc.messages}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    return drf_exception_handler(exc, context)
