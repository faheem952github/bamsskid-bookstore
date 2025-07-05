from pydantic import BaseModel, EmailStr, Field, field_validator, constr
from typing import Optional, Dict, List, Any
from enum import Enum


# Auth Request Models
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None

    @field_validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v.lower()

    @field_validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLoginRequest(BaseModel):
    username_or_email: constr(strip_whitespace=True, min_length=3)
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator('new_password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class SortOrderEnum(str, Enum):
    asc = "asc"
    desc = "desc"


class UserListQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    search: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_staff: Optional[bool] = None
    is_superuser: Optional[bool] = None
    # sort_by: Optional[str] = Field(default="id", regex="^(id|username|email|created_at|last_login)$")
    # sort_order: Optional[str] = Field(default="asc", regex="^(asc|desc)$")
    # sort_by: str = Field(default="id")
    # sort_order: SortOrderEnum = SortOrderEnum.desc
    sort_by: Optional[str] = Field(
        default="id",
        pattern="^(id|username|email|created_at|last_login)$"
    )
    sort_order: Optional[str] = Field(
        default="asc",
        pattern="^(asc|desc)$"
    )


class UserUpdateRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None

    @field_validator('username')
    def validate_username(cls, v):
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v.lower() if v else v
