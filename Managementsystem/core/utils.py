from __future__ import annotations

import random
import string
from datetime import datetime
from typing import Optional
from uuid import uuid4

from django.http import HttpRequest
from django.utils import timezone


def generate_school_code() -> str:
    """Generate a short unique school code for tenant identification."""
    return f"SCH-{uuid4().hex[:8].upper()}"


def generate_reference_number(prefix: str = "REF") -> str:
    """Generate a stable short reference number for external records."""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    token = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{timestamp}-{token}"


def get_client_ip(request: HttpRequest) -> Optional[str]:
    """Retrieve the originating client IP address from a Django request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
