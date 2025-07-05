from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR
)

from app.baselayer.ResonpseBase import (
    ValidationErrorResponse,
    UnauthorizedResponse,
    ForbiddenResponse,
    NotFoundResponse,
    ConflictResponse,
    InternalServerErrorResponse,
)

from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from starlette.responses import JSONResponse

from app.account.response import ErrorResponse
from config.logging_utils import logger


# MIDDLEWARE
async def error_handling_middleware(request: Request, call_next):
    """
    Global error-handling middleware.
    """
    try:
        response = await call_next(request)
        return response

    except IntegrityError as exc:
        return await handle_integrity_error(request, exc)

    except HTTPException as exc:
        return await handle_http_exception(request, exc)

    except Exception as exc:
        return await handle_unexpected_error(request, exc)


# HANDLERS

async def handle_integrity_error(request: Request, exc: IntegrityError):
    logger.error({
        "method": "handle_integrity_error",
        "message": "Database integrity error occurred",
        "path": request.url.path,
        "error": str(exc)
    })
    return JSONResponse(
        status_code=HTTP_409_CONFLICT,
        content=ConflictResponse(
            message="A database integrity error occurred.",
            status_code=HTTP_409_CONFLICT,
            details={"error": str(exc)}
        ).dict()
    )


async def handle_http_exception(request: Request, exc: HTTPException):
    logger.error({
        "method": "handle_http_exception",
        "message": "Validation error occurred",
        "path": request.url.path,
        "error": exc.detail,
        "status_code": exc.status_code
    })

    error_class_map = {
        HTTP_400_BAD_REQUEST: ValidationErrorResponse,
        HTTP_401_UNAUTHORIZED: UnauthorizedResponse,
        HTTP_403_FORBIDDEN: ForbiddenResponse,
        HTTP_404_NOT_FOUND: NotFoundResponse,
        HTTP_409_CONFLICT: ConflictResponse,
    }

    response_class = error_class_map.get(exc.status_code, ErrorResponse)

    return JSONResponse(
        status_code=exc.status_code,
        content=response_class(
            message=exc.detail,
            status_code=exc.status_code,
            details={"error": exc.detail}
        ).dict()
    )


async def handle_unexpected_error(request: Request, exc: Exception):
    logger.error({
        "method": "handle_unexpected_error",
        "message": "Validation error occurred",
        "path": request.url.path,
        "request_headers": request.headers,
        "error": str(exc)
    })

    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=InternalServerErrorResponse(
            message="Something went wrong. Please try again later.",
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(exc)}
        ).dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handles validation errors and logs the error details.
    """
    errors = exc.errors()
    logger.error({
        "method": "validation_exception_handler",
        "message": "Validation error occurred",
        "path": request.url.path,
        "request_headers": request.headers,
        "error": exc.errors()
    })

    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content=ValidationErrorResponse(
            message=errors[0]["msg"],
            status_code=HTTP_400_BAD_REQUEST,
            details=errors
        ).dict()
    )
