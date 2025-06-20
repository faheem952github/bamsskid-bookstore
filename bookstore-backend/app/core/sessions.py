from fastapi import Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import uuid
import json

from app.account.models import UserSession
from config.database import get_db


def create_user_session(user_id: int, device_info: dict, ip_address: str, user_agent: str, expires_in_minutes: int = 60 * 24 * 7, db: Session = Depends(get_db)) -> UserSession:
    session_token = str(uuid.uuid4())
    refresh_token = str(uuid.uuid4())

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)

    session = UserSession(
        user_id=user_id,
        session_token=session_token,
        refresh_token=refresh_token,
        device_info=json.dumps(device_info),
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=expires_at,
    )

    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def expire_user_session(session_token: str, db: Session = Depends(get_db)):
    session = db.query(UserSession).filter_by(session_token=session_token).first()
    if session:
        session.is_active = False
        db.commit()


def get_active_session(session_token: str, db: Session = Depends(get_db)):
    session = db.query(UserSession).filter_by(session_token=session_token, is_active=True).first()
    if session and not session.is_expired:
        return session
    return None
