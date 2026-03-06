"""
Shared dependencies and helpers used across routers.
"""
from typing import Optional
import html

from fastapi import Request
from sqlalchemy.orm import Session

import models
from auth import TokenData


# ============================================
# INPUT SANITIZATION HELPERS
# ============================================
def sanitize_string(value: Optional[str]) -> Optional[str]:
    """Sanitize string input to prevent XSS."""
    if value is None:
        return None
    return html.escape(value.strip())


def sanitize_dict(data: dict, fields: list[str]) -> dict:
    """Sanitize specific string fields in a dictionary."""
    for field in fields:
        if field in data and isinstance(data[field], str):
            data[field] = sanitize_string(data[field])
    return data


# ============================================
# ACTIVITY LOG HELPER
# ============================================
def log_activity(
    db: Session,
    user: Optional[TokenData],
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    entity_name: Optional[str] = None,
    details: Optional[str] = None,
    request: Optional[Request] = None,
) -> None:
    """Log user activity for audit trail."""
    try:
        ip_address = None
        if request:
            ip_address = request.client.host if request.client else None

        log = models.ActivityLog(
            user_id=None,
            username=user.username if user else "anonymous",
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            details=details,
            ip_address=ip_address,
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")
