from enum import Enum
from typing import List, Tuple


class AccountRoleChoices(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    SCHOOL_ADMIN = "SCHOOL_ADMIN"
    TEACHER = "TEACHER"
    PARENT = "PARENT"
    STUDENT = "STUDENT"

    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        return [(choice.value, choice.name.replace("_", " ").title()) for choice in cls]
