from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Request
import json

from app.account.models import AuditLog


def log_action(
        db: Session,
        action: str,
        resource: str,
        user_id: Optional[int] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request: Optional[Request] = None
):
    """Log any action to audit trail"""
    try:
        # Extract IP and User Agent from request if provided
        ip_address = request.client.host if request else None
        user_agent = request.headers.get("user-agent") if request else None

        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=str(resource_id) if resource_id else None,
            details=json.dumps(details) if details else None,
            ip_address=ip_address,
            user_agent=user_agent
        )

        db.add(audit_log)
        db.commit()

    except Exception as e:
        db.rollback()
        # Log error but don't fail the main operation
        print(f"Audit logging failed: {str(e)}")
