from typing import Optional, List, Tuple
from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, desc, asc
import json
import uuid
import secrets

from fastapi import HTTPException, Request, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.account.models import User, UserProfile, UserSession
from app.account.repository import (
    get_user_by_email, get_user_by_username,
    get_user_by_id, get_user_by_username_or_email
)
from app.account.request import UserRegisterRequest, UserUpdateRequest, UserListQuery

from app.account.utils.dependencies import get_current_user
from app.baselayer.ResonpseBase import PaginationMeta
from app.core.audit_logs import log_action
from app.core.auth import hash_password, verify_password


def create_user(db: Session, user_data: UserRegisterRequest, request: Request, is_admin_created: bool = False):
    """Create new user"""
    # Check if user exists
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken"
        )

    # Create user
    hashed_password = hash_password(user_data.password)

    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        phone=user_data.phone,
        address=user_data.address,
        is_verified=is_admin_created  # Auto-verify admin created users
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Create user profile
    profile = UserProfile(user_id=user.id)
    db.add(profile)
    db.commit()

    # Log action
    log_action(
        db=db,
        action="CREATE_USER",
        resource="User",
        resource_id=user.id,
        details={
            "username": user.username,
            "email": user.email,
            "created_by_admin": is_admin_created
        },
        request=request
    )

    return user


def update_user(db: Session, user_id: int, update_data: UserUpdateRequest, request: Request, current_user: User):
    """Update user"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Store original values for audit
    original_values = {
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "address": user.address
    }

    # Update fields
    update_dict = update_data.dict(exclude_unset=True)

    # Check for conflicts
    if "email" in update_dict and update_dict["email"] != user.email:
        if get_user_by_email(db, update_dict["email"]):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use"
            )

    if "username" in update_dict and update_dict["username"] != user.username:
        if get_user_by_username(db, update_dict["username"]):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )

    # Apply updates
    for field, value in update_dict.items():
        setattr(user, field, value)

    user.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(user)

    # Log action
    log_action(
        db=db,
        action="UPDATE_USER",
        resource="User",
        user_id=current_user.id,
        resource_id=user.id,
        details={
            "updated_fields": list(update_dict.keys()),
            "original_values": original_values,
            "new_values": update_dict
        },
        request=request
    )

    return user


def delete_user(db: Session, user_id: int, request: Request, current_user: User, permanent: bool = False):
    """Delete user (soft or hard delete)"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if permanent:
        # Hard delete
        db.delete(user)
        action = "DELETE_USER_PERMANENT"
    else:
        # Soft delete
        user.is_active = False
        user.updated_at = datetime.now(UTC)
        action = "DELETE_USER_SOFT"

    db.commit()

    # Log action
    log_action(
        db=db,
        action=action,
        resource="User",
        user_id=current_user.id,
        resource_id=user.id,
        details={
            "username": user.username,
            "email": user.email,
            "permanent": permanent
        },
        request=request
    )


def authenticate_user(db: Session, username_or_email: str, password: str, request: Request) -> Optional[User]:
    """Authenticate user"""
    user = get_user_by_username_or_email(db, username_or_email)

    if not user:
        log_action(
            db=db,
            action="LOGIN_FAILED",
            resource="Auth",
            details={"reason": "user_not_found", "username_or_email": username_or_email},
            request=request
        )
        return None

    if not verify_password(password, user.hashed_password):
        log_action(
            db=db,
            action="LOGIN_FAILED",
            resource="Auth",
            user_id=user.id,
            details={"reason": "invalid_password"},
            request=request
        )
        return None

    if not user.is_active:
        log_action(
            db=db,
            action="LOGIN_FAILED",
            resource="Auth",
            user_id=user.id,
            details={"reason": "account_inactive"},
            request=request
        )
        return None

    # Update last login
    user.last_login = datetime.now(UTC)
    db.commit()

    log_action(
        db=db,
        action="LOGIN_SUCCESS",
        resource="Auth",
        user_id=user.id,
        request=request
    )

    return user


def get_users_paginated(db: Session, query_params: UserListQuery) -> Tuple[List[User], PaginationMeta]:
    """Get paginated users list"""
    # Base query
    query = db.query(User).options(joinedload(User.profile))

    # Apply filters
    if query_params.search:
        search_term = f"%{query_params.search}%"
        query = query.filter(
            or_(
                User.username.ilike(search_term),
                User.email.ilike(search_term)
            )
        )

    if query_params.is_active is not None:
        query = query.filter(User.is_active == query_params.is_active)

    if query_params.is_verified is not None:
        query = query.filter(User.is_verified == query_params.is_verified)

    if query_params.is_staff is not None:
        query = query.filter(User.is_staff == query_params.is_staff)

    if query_params.is_superuser is not None:
        query = query.filter(User.is_superuser == query_params.is_superuser)

    # Apply sorting
    sort_column = getattr(User, query_params.sort_by, User.id)
    if query_params.sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    # Get total count
    total_items = query.count()

    # Apply pagination
    offset = (query_params.page - 1) * query_params.limit
    users = query.offset(offset).limit(query_params.limit).all()

    # Create pagination meta
    total_pages = (total_items + query_params.limit - 1) // query_params.limit
    meta = PaginationMeta(
        current_page=query_params.page,
        per_page=query_params.limit,
        total_pages=total_pages,
        total_items=total_items,
        has_next=query_params.page < total_pages,
        has_prev=query_params.page > 1
    )

    return users, meta
