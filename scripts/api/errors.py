"""Canonical HTTP error mapping for the POL transport layer."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

class ConflictError(ValueError):
    """Client supplied a stale/competing state; HTTP transport maps this to 409."""


from scripts.auth_boundary import (
    AuthError,
    InvalidRefreshTokenError,
    OTPRateLimitError,
    OTPLockoutError,
    SessionExpiredError,
    SessionRevokedError,
)


def _timestamp() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def error_payload(code: str, message: str, details=None) -> dict:
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "timestamp": _timestamp(),
        },
    }


def success_payload(data) -> dict:
    return {"success": True, "data": data}


def _response(request: Request, code: str, message: str, status_code: int, details=None):
    response = JSONResponse(
        status_code=status_code,
        content=error_payload(code, message, details),
    )
    correlation_id = getattr(request.state, "correlation_id", None)
    if correlation_id:
        response.headers["X-Correlation-ID"] = correlation_id
    return response


async def request_validation_handler(request: Request, exc: RequestValidationError):
    details = {
        "fields": [
            {
                "loc": list(error.get("loc", [])),
                "type": error.get("type"),
                "message": error.get("msg"),
            }
            for error in exc.errors()
        ]
    }
    return _response(request, "VALIDATION_ERROR", "Request validation failed.", 422, details)


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    code = {
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
    }.get(exc.status_code, "HTTP_ERROR")
    message = exc.detail if isinstance(exc.detail, str) else "HTTP request failed."
    return _response(request, code, message, exc.status_code, {})


async def auth_error_handler(request: Request, exc: AuthError):
    if isinstance(exc, SessionExpiredError):
        return _response(
            request,
            "SESSION_EXPIRED",
            "Session has expired. Please re-authenticate.",
            401,
        )
    if isinstance(exc, SessionRevokedError):
        return _response(
            request,
            "SESSION_REVOKED",
            "Session has been revoked.",
            401,
        )
    if isinstance(exc, InvalidRefreshTokenError):
        return _response(
            request,
            "INVALID_REFRESH_TOKEN",
            "Refresh token is invalid or expired.",
            401,
        )
    return _response(request, "INVALID_ACCESS_TOKEN", "Invalid or expired access token.", 401)


async def otp_rate_limit_handler(request: Request, exc: OTPRateLimitError):
    return _response(request, "OTP_RATE_LIMITED", str(exc), 429)


async def otp_lockout_handler(request: Request, exc: OTPLockoutError):
    return _response(request, "OTP_LOCKED", str(exc), 429)


async def permission_handler(request: Request, exc: PermissionError):
    return _response(request, "FORBIDDEN", str(exc), 403)


async def value_error_handler(request: Request, exc: ValueError):
    if isinstance(exc, ConflictError):
        return _response(request, "CONFLICT", str(exc), 409)
    return _response(request, "INVALID_REQUEST", str(exc), 422)


async def key_error_handler(request: Request, exc: KeyError):
    return _response(request, "NOT_FOUND", str(exc), 404)


async def data_integrity_handler(request: Request, exc: Exception):
    """A client-supplied reference or value violated a database constraint.

    Schema-level validation should catch these first; this handler is the last
    line of defence so an unknown enum value or a dangling foreign key can never
    surface as a 500 with an internal detail leak (TODO-131).
    """
    return _response(
        request,
        "INVALID_REQUEST",
        "The request references data that does not exist or is not allowed.",
        422,
    )


async def generic_error_handler(request: Request, exc: Exception):
    # Deliberately do not expose exception details or request bodies.
    return _response(
        request,
        "INTERNAL_SERVER_ERROR",
        "An unexpected server error occurred.",
        500,
    )
