"""Authentication and session HTTP routes."""

from __future__ import annotations

import os
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response

from scripts.api.db import get_db_cursor
from scripts.api.dependencies import get_bearer_token, get_current_auth
from scripts.api.errors import success_payload
from scripts.auth_boundary import InvalidRefreshTokenError
from scripts.api.schemas import (
    RefreshTokenRequest,
    RequestOTPRequest,
    SwitchOrganizationRequest,
    VerifyOTPRequest,
)
from scripts.auth_application import AuthApplicationService
from scripts.auth_boundary import InvalidOTPError, InvalidRefreshTokenError, OTPLockoutError
from scripts.operational_config import OTP_RESEND_INTERVAL_SECONDS, OTP_TTL_SECONDS

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        "pol_refresh",
        refresh_token,
        max_age=30 * 24 * 60 * 60,
        httponly=True,
        secure=not (os.environ.get("ENVIRONMENT", "").lower() == "test"),
        samesite="lax",
        path="/api/v1/auth",
    )


@router.post("/request-otp")
def request_otp(payload: RequestOTPRequest, request: Request, cur=Depends(get_db_cursor)):
    client_ip = request.client.host if request.client else "127.0.0.1"
    result = AuthApplicationService.request_otp(
        cur,
        payload.mobile_number,
        client_ip,
        "LOGIN",
    )
    return success_payload(
        {
            "otp_request_id": str(result["id"]),
            "expires_in_seconds": OTP_TTL_SECONDS,
            "resend_interval_seconds": OTP_RESEND_INTERVAL_SECONDS,
        }
    )


@router.post("/verify-otp")
def verify_otp(payload: VerifyOTPRequest, response: Response, cur=Depends(get_db_cursor)):
    try:
        result = AuthApplicationService.verify_otp(
            cur,
            payload.mobile_number,
            payload.otp_code,
        )
    except (InvalidOTPError, OTPLockoutError):
        # Failed-attempt accounting must survive the request-level rollback that
        # the error handler triggers; otherwise brute-force lockout never engages.
        cur.connection.commit()
        raise
    refresh_token = result.get("refresh_token")
    if refresh_token and payload.client_platform == "web":
        _set_refresh_cookie(response, refresh_token)
    if payload.client_platform == "web":
        result = {key: value for key, value in result.items() if key != "refresh_token"}
    return success_payload(result)


@router.post("/refresh")
def refresh(request: Request, response: Response, payload: RefreshTokenRequest | None = None, cur=Depends(get_db_cursor)):
    cookie_refresh = request.cookies.get("pol_refresh")
    refresh_token = cookie_refresh or (payload.refresh_token if payload else None)
    if not refresh_token:
        raise InvalidRefreshTokenError("Refresh token is required.")
    result = AuthApplicationService.refresh(cur, refresh_token)
    next_refresh = result.get("refresh_token")
    if next_refresh and cookie_refresh:
        _set_refresh_cookie(response, next_refresh)
    if cookie_refresh:
        result = {key: value for key, value in result.items() if key != "refresh_token"}
    return success_payload(result)


@router.post("/switch-organization")
def switch_organization(
    payload: SwitchOrganizationRequest,
    token: str = Depends(get_bearer_token),
    cur=Depends(get_db_cursor),
):
    result = AuthApplicationService.switch_organization(
        cur,
        token,
        str(payload.target_organization_id),
    )
    return success_payload(result)


@router.delete("/sessions/current")
def revoke_current_session(
    response: Response,
    token: str = Depends(get_bearer_token),
    claims: dict = Depends(get_current_auth),
    cur=Depends(get_db_cursor),
):
    session_id = claims["sid"]
    AuthApplicationService.revoke_session(cur, token, str(session_id))
    response.delete_cookie("pol_refresh", path="/api/v1/auth")
    return success_payload({"session_id": str(session_id), "status": "REVOKED"})


@router.delete("/sessions/{session_id}")
def revoke_session(
    session_id: UUID,
    token: str = Depends(get_bearer_token),
    cur=Depends(get_db_cursor),
):
    AuthApplicationService.revoke_session(cur, token, str(session_id))
    return success_payload({"session_id": str(session_id), "status": "REVOKED"})


@router.post("/logout-all")
def logout_all(
    response: Response,
    token: str = Depends(get_bearer_token),
    cur=Depends(get_db_cursor),
):
    revoked_count = AuthApplicationService.logout_all(cur, token)
    response.delete_cookie("pol_refresh", path="/api/v1/auth")
    return success_payload({"revoked_sessions": revoked_count, "status": "ALL_REVOKED"})
