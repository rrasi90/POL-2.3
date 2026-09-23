"""Authentication and session HTTP routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request

from scripts.api.db import get_db_cursor
from scripts.api.dependencies import get_bearer_token, get_current_auth
from scripts.api.errors import success_payload
from scripts.api.schemas import (
    RefreshTokenRequest,
    RequestOTPRequest,
    SwitchOrganizationRequest,
    VerifyOTPRequest,
)
from scripts.auth_application import AuthApplicationService
from scripts.operational_config import OTP_RESEND_INTERVAL_SECONDS, OTP_TTL_SECONDS

router = APIRouter(prefix="/auth", tags=["auth"])


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
def verify_otp(payload: VerifyOTPRequest, cur=Depends(get_db_cursor)):
    result = AuthApplicationService.verify_otp(
        cur,
        payload.mobile_number,
        payload.otp_code,
    )
    return success_payload(result)


@router.post("/refresh")
def refresh(payload: RefreshTokenRequest, cur=Depends(get_db_cursor)):
    return success_payload(AuthApplicationService.refresh(cur, payload.refresh_token))


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
    token: str = Depends(get_bearer_token),
    claims: dict = Depends(get_current_auth),
    cur=Depends(get_db_cursor),
):
    session_id = claims["sid"]
    AuthApplicationService.revoke_session(cur, token, str(session_id))
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
    token: str = Depends(get_bearer_token),
    cur=Depends(get_db_cursor),
):
    revoked_count = AuthApplicationService.logout_all(cur, token)
    return success_payload({"revoked_sessions": revoked_count, "status": "ALL_REVOKED"})
