from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request

from app.account.models import User
from app.account.repository import get_user_by_id
from app.account.request import UserUpdateRequest, UserListQuery
from app.account.response import UserBasicResponse, SuccessResponse, SuccessResponse, PaginatedResponse

from app.account.utils.dependencies import get_current_user
from app.account.views import update_user, delete_user, get_users_paginated
from app.core.audit_logs import log_action
from config.config import settings
from config.database import get_db

ACCESS_TOKEN_EXPIRY = settings.ACCESS_TOKEN_EXPIRE_MINUTES

user_router = APIRouter(prefix="/user", tags=["Users"])


@user_router.get("/", response_model=PaginatedResponse[UserBasicResponse])
def list_users(query_params: UserListQuery = Depends(), db: Session = Depends(get_db)):
    users, meta = get_users_paginated(db, query_params)

    # Convert SQLAlchemy Users to Pydantic UserBasicResponse
    user_responses = [UserBasicResponse.model_validate(user) for user in users]

    return PaginatedResponse(
        message="Users fetched successfully",
        data=user_responses,
        meta=meta
    )


@user_router.put("/{user_id}", response_model=SuccessResponse[UserBasicResponse])
def update_user_route(user_id: int, update_data: UserUpdateRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),):
    """API route to update a user"""
    updated_user = update_user(db, user_id, update_data, request, current_user)

    return SuccessResponse(
        message="User updated successfully",
        data=UserBasicResponse.model_validate(updated_user)
    )


@user_router.delete("/{user_id}", response_model=SuccessResponse)
def delete_user_route(user_id: int, request: Request, permanent: bool = Query(False, description="Perform hard delete if true"), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """API endpoint to delete a user (soft or hard)"""
    delete_user(db, user_id, request, current_user, permanent)

    return SuccessResponse(
        message="User deleted successfully"
    )
