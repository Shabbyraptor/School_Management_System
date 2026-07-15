from enum import Enum
from typing import Final, List, Tuple

COUNTRIES: Final[List[Tuple[str, str]]] = [
    ("US", "United States"),
    ("GB", "United Kingdom"),
    ("CA", "Canada"),
    ("AU", "Australia"),
    ("NG", "Nigeria"),
    ("KE", "Kenya"),
    ("IN", "India"),
    ("ZA", "South Africa"),
    ("UG", "Uganda"),
    ("TZ", "Tanzania"),
]


class UserRoleChoices(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    SCHOOL_ADMIN = "SCHOOL_ADMIN"
    STAFF = "STAFF"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"

    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        return [(choice.value, choice.name.replace("_", " ").title()) for choice in cls]


class AuditActionChoices(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"

    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        return [(action.value, action.name.title()) for action in cls]


AUDIT_ACTIONS: Final[List[Tuple[str, str]]] = AuditActionChoices.choices()
USER_ROLES: Final[List[Tuple[str, str]]] = UserRoleChoices.choices()
