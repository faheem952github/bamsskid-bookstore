from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.account.models import User


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).options(joinedload(User.profile)).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_username_or_email(db: Session, username_or_email: str) -> Optional[User]:
    """Get user by username or email"""
    return db.query(User).filter(or_(User.username == username_or_email, User.email == username_or_email)).first()
