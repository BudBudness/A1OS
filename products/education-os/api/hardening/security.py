from __future__ import annotations

from typing import Any

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'",
}


def validate_required_fields(payload: dict[str, Any], required: list[str]) -> list[str]:
    return [
        field for field in required
        if payload.get(field) is None or payload.get(field) == ""
    ]


def sanitize_text(value: Any, max_length: int = 500) -> str:
    if value is None:
        return ""
    return str(value).strip()[:max_length]
