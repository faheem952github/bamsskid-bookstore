from pydantic import BaseModel
from typing import Optional, Dict, List, Any, TypeVar, Generic
from enum import Enum

T = TypeVar("T")  # Generic Type for Data


class SuccessEnum(str, Enum):
    SUCCESS = True
    ERROR = False


# Generic Base Response
class BaseResponse(BaseModel):
    success: SuccessEnum
    message: str


class ErrorResponse(BaseResponse):
    success: SuccessEnum = SuccessEnum.ERROR
    status_code: int
    details: Optional[Dict[str, Any]] = None


# Generic Success Response
class SuccessResponse(BaseResponse, Generic[T]):
    success: SuccessEnum = SuccessEnum.SUCCESS
    data: Optional[T] = None
    meta: Optional[Dict[str, Any]] = None


class PaginationMeta(BaseModel):
    current_page: int
    per_page: int
    total_pages: int
    total_items: int
    has_next: bool
    has_prev: bool


# Paginated Success Response
class PaginatedResponse(BaseResponse, Generic[T]):
    success: SuccessEnum = SuccessEnum.SUCCESS
    data: List[T]
    meta: PaginationMeta


# Generic API Responses
class ValidationErrorResponse(ErrorResponse):
    success: SuccessEnum = SuccessEnum.ERROR
    error_code: str = "VALIDATION_ERROR"


class NotFoundResponse(ErrorResponse):
    success: SuccessEnum = SuccessEnum.ERROR
    error_code: str = "NOT_FOUND"


class UnauthorizedResponse(ErrorResponse):
    success: SuccessEnum = SuccessEnum.ERROR
    error_code: str = "UNAUTHORIZED"


class ForbiddenResponse(ErrorResponse):
    success: SuccessEnum = SuccessEnum.ERROR
    error_code: str = "FORBIDDEN"


class ConflictResponse(ErrorResponse):
    success: SuccessEnum = SuccessEnum.ERROR
    error_code: str = "CONFLICT"


class InternalServerErrorResponse(ErrorResponse):
    success: SuccessEnum = SuccessEnum.ERROR
    error_code: str = "INTERNAL_SERVER_ERROR"
