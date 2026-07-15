from __future__ import annotations


def generate_class_code(name: str, school_code: str | None = None) -> str:
    base = "".join(ch for ch in name.upper() if ch.isalnum())[:6]
    if school_code:
        return f"{school_code[:3]}-{base}"
    return base


def generate_subject_code(name: str) -> str:
    return "".join(ch for ch in name.upper() if ch.isalnum())[:8]
