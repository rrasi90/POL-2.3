"""FastAPI dependencies for authentication and application context."""

from __future__ import annotations

from fastapi import Depends, Header, Request

from scripts.api.db import get_db_cursor
from scripts.application_boundary import ApplicationContext, POLApplicationBoundary
from scripts.auth_application import AuthApplicationService
from scripts.auth_boundary import AuthError


def get_bearer_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization:
        raise AuthError("Missing Authorization header.")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise AuthError("Invalid Bearer authorization header.")
    return token.strip()


def get_current_auth(
    token: str = Depends(get_bearer_token),
    cur=Depends(get_db_cursor),
) -> dict:
    return AuthApplicationService.authenticate(cur, token)


def get_application_context(
    request: Request,
    claims: dict = Depends(get_current_auth),
) -> ApplicationContext:
    return ApplicationContext(
        user_id=str(claims["sub"]),
        organization_id=str(claims["org_id"]),
        correlation_id=request.state.correlation_id,
    )


def get_application_boundary(
    cur=Depends(get_db_cursor),
    context: ApplicationContext = Depends(get_application_context),
) -> POLApplicationBoundary:
    return POLApplicationBoundary(cur, context)
