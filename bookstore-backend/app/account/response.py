from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List, Any, Union
from datetime import datetime

from app.baselayer.ResonpseBase import SuccessResponse, PaginatedResponse, ErrorResponse, SuccessEnum


class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    website: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None
    preferences: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# User Response Models
class UserBasicResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_verified: bool
    is_staff: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    profile: UserProfileResponse

    class Config:
        from_attributes = True


# class PaginatedResponse(BaseModel):
#     success: SuccessEnum = SuccessEnum.SUCCESS
#     message: str
#     data: List[UserBasicResponse]
#     meta: PaginationMeta


# class UserProfileResponse(BaseModel):
#     id: int
#     user_id: int
#     bio: Optional[str] = None
#     avatar_url: Optional[str] = None
#     date_of_birth: Optional[datetime] = None
#     gender: Optional[str] = None
#     country: Optional[str] = None
#     city: Optional[str] = None
#     address: Optional[str] = None
#     postal_code: Optional[str] = None
#     website: Optional[str] = None
#     social_links: Optional[Dict[str, str]] = None
#     preferences: Optional[Dict[str, Any]] = None
#     created_at: datetime
#     updated_at: datetime
#
#     class Config:
#         from_attributes = True


class UserDetailResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_staff: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    profile: Optional[UserProfileResponse] = None

    class Config:
        from_attributes = True


class UserSessionResponse(BaseModel):
    id: int
    session_token: str
    device_info: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool
    expires_at: datetime
    last_accessed: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Auth Response Models
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserBasicResponse


class LoginResponse(SuccessResponse):
    data: TokenResponse


class RegisterResponse(SuccessResponse):
    data: Dict[str, Union[str, UserBasicResponse]]


class LogoutResponse(SuccessResponse):
    pass


# Admin Response Models
class AdminUserListResponse(PaginatedResponse):
    data: List[UserDetailResponse]


class AdminUserDetailResponse(SuccessResponse):
    data: UserDetailResponse


class AdminStatsResponse(BaseModel):
    total_users: int
    active_users: int
    verified_users: int
    staff_users: int
    superusers: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    user_growth_rate: float


class AdminStatsDashboard(SuccessResponse):
    data: AdminStatsResponse


# Audit Log Response Models
class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str
    resource: str
    resource_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(PaginatedResponse):
    data: List[AuditLogResponse]


# Bulk Operation Response Models
class BulkOperationResult(BaseModel):
    success_count: int
    failed_count: int
    # failed_items: List[Dict[str, Any]] = []


class BulkOperationResponse(SuccessResponse):
    data: BulkOperationResult


# Profile Response Models
class ProfileUpdateResponse(SuccessResponse):
    data: UserProfileResponse


class ProfileResponse(SuccessResponse):
    data: UserDetailResponse


# Password Response Models
class PasswordChangeResponse(SuccessResponse):
    pass


class PasswordResetResponse(SuccessResponse):
    pass


# Session Management Response Models
class SessionListResponse(BaseModel):
    success: SuccessEnum = SuccessEnum.SUCCESS
    message: str
    data: List[UserSessionResponse]
    timestamp: datetime = datetime.utcnow()


class SessionResponse(SuccessResponse):
    data: UserSessionResponse


# Health Check Response
class HealthCheckResponse(BaseModel):
    success: str = "healthy"
    timestamp: datetime = datetime.utcnow()
    version: str = "1.0.0"
    database: str = "connected"
    redis: Optional[str] = "connected"


# API Info Response
class APIInfoResponse(BaseModel):
    name: str = "User Management API"
    version: str = "1.0.0"
    description: str = "FastAPI based User Management System"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    timestamp: datetime = datetime.utcnow()


# File Upload Response
class FileUploadResponse(SuccessResponse):
    data: Dict[str, str]  # Contains file_url, file_name, file_size


