"""FastAPI dependencies for authentication, application context, and RBAC."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, Request

from scripts.api.db import get_db_cursor
from scripts.application_boundary import ApplicationContext, POLApplicationBoundary
from scripts.auth_application import AuthApplicationService
from scripts.permissions import require_permission as check_permission
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


def require_permission(permission_key: str):
    """FastAPI dependency for effective server-side permissions.

    Baseline role permissions and delegated grants are evaluated against the
    active membership in the current organization.
    """

    def _check(
        cur=Depends(get_db_cursor),
        context: ApplicationContext = Depends(get_application_context),
    ) -> dict:
        if not context.organization_id:
            raise PermissionError("An active organization context is required.")
        return check_permission(
            cur,
            context.user_id,
            context.organization_id,
            permission_key,
        )

    return _check


def require_roles(*allowed_roles: str):
    """FastAPI dependency factory that enforces RBAC role checks.

    Usage:
        @router.get("/vendor/orders")
        async def list_vendor_orders(
            _auth: Annotated[dict, Depends(require_roles("VENDOR_OWNER", "VENDOR_STAFF"))],
        ):
            ...
    """

    def _check(
        cur=Depends(get_db_cursor),
        context: ApplicationContext = Depends(get_application_context),
    ) -> dict:
        return AuthApplicationService.authorize_action(
            cur, context.user_id, context.organization_id, list(allowed_roles)
        )

    return _check
