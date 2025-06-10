# /app/middleware/error_handling.py

from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

from app.baselayer.baseview import FastResponder
from config.logging_utils import logger


async def error_handling_middleware(request: Request, call_next):
    """
    Middleware for handling errors that occur during request processing.
    """
    try:
        response = await call_next(request)
        return response

    except IntegrityError as exc:
        # Handle database integrity errors
        return await handle_integrity_error(request, exc)

    except HTTPException as exc:
        # Handle HTTP exceptions
        return await handle_http_exception(request, exc)

    except Exception as exc:
        # Handle all other unexpected errors
        return await handle_unexpected_error(request, exc)


async def handle_integrity_error(request: Request, exc):
    logger.error({
        "method": "handle_integrity_error",
        "message": "Database integrity error occurred",
        "path": request.url.path,
        "error": str(exc)
    })
    return FastResponder.send_bad_request_response(
        message="Database integrity error occurred."
    )


async def handle_http_exception(request: Request, exc: HTTPException):
    logger.error({
        "method": "handle_http_exception",
        "message": "Validation error occurred",
        "path": request.url.path,
        "error": exc.detail,
        "status_code": exc.status_code
    })
    return FastResponder.send_response(
        success=False,
        status_code=exc.status_code,
        message=exc.detail  # Directly send the error message
    )


async def handle_unexpected_error(request: Request, exc):
    logger.error({
        "method": "handle_unexpected_error",
        "message": "Validation error occurred",
        "path": request.url.path,
        "request_headers": request.headers,
        "error": str(exc)
    })
    return FastResponder.send_internal_server_error_response(
        message="Please try again in a while."
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

    return FastResponder.send_bad_request_response(message=errors[0]["msg"])
