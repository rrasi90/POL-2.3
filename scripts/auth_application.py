"""Application-level authentication orchestration.

This module sits between FastAPI transport and the internal auth/domain helpers.
It owns identity-to-membership resolution for public auth flows and keeps
transport code free of direct domain-service imports.
"""

from __future__ import annotations

from scripts.auth_boundary import AuthError, validate_access_token
from scripts.domain_services import AuthService


class AuthApplicationService:
    """Canonical application service for HTTP authentication/session flows."""

    @staticmethod
    def request_otp(cur, phone_number: str, ip_address: str, purpose: str = "LOGIN") -> dict:
        return AuthService.request_otp(cur, phone_number, ip_address, purpose)

    @staticmethod
    def verify_otp(cur, phone_number: str, code: str) -> dict:
        cur.execute(
            """
            SELECT id, phone_number, full_name
            FROM users
            WHERE phone_number = %s
              AND is_active = TRUE
            LIMIT 1;
            """,
            (phone_number,),
        )
        user = cur.fetchone()
        if not user:
            raise ValueError("No active user exists for this phone number.")

        cur.execute(
            """
            SELECT
                m.id,
                m.organization_id,
                m.role,
                o.name,
                o.org_type,
                o.status
            FROM organization_memberships m
            JOIN organizations o ON o.id = m.organization_id
            WHERE m.user_id = %s
              AND m.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
            ORDER BY m.is_primary DESC, m.created_at ASC
            LIMIT 1;
            """,
            (user["id"],),
        )
        membership = cur.fetchone()
        if not membership:
            raise PermissionError("User has no active organization membership.")

        result = AuthService.verify_otp(
            cur,
            phone_number,
            code,
            str(user["id"]),
            str(membership["organization_id"]),
        )

        cur.execute(
            """
            SELECT
                m.organization_id AS id,
                o.name,
                o.org_type AS type,
                m.role,
                m.is_primary
            FROM organization_memberships m
            JOIN organizations o ON o.id = m.organization_id
            WHERE m.user_id = %s
              AND m.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
            ORDER BY m.is_primary DESC, m.created_at ASC;
            """,
            (user["id"],),
        )
        available = cur.fetchall()

        current = next(
            (item for item in available
             if str(item["id"]) == str(membership["organization_id"])),
            None,
        )

        return {
            **result,
            "user": {
                "id": user["id"],
                "mobile_number": user["phone_number"],
                "full_name": user["full_name"],
            },
            "current_organization": current,
            "available_organizations": available,
        }

    @staticmethod
    def refresh(cur, refresh_token: str) -> dict:
        return AuthService.refresh_access_token(cur, refresh_token)

    @staticmethod
    def authenticate(cur, access_token: str) -> dict:
        return validate_access_token(cur, access_token)

    @staticmethod
    def authorize_action(cur, user_id: str, organization_id: str, allowed_roles: list[str]) -> dict:
        return AuthService.authorize_action(cur, user_id, organization_id, allowed_roles)

    @staticmethod
    def switch_organization(cur, access_token: str, target_organization_id: str) -> dict:
        claims = validate_access_token(cur, access_token)
        return AuthService.switch_organization(
            cur,
            claims["sub"],
            target_organization_id,
            claims["sid"],
        )

    @staticmethod
    def revoke_session(cur, access_token: str, target_session_id: str) -> None:
        claims = validate_access_token(cur, access_token)
        if claims["sid"] != str(target_session_id):
            cur.execute(
                """
                SELECT 1
                FROM user_sessions
                WHERE id = %s AND user_id = %s;
                """,
                (target_session_id, claims["sub"]),
            )
            if not cur.fetchone():
                raise PermissionError("Session not found or not owned by authenticated user.")
        AuthService.revoke_session(cur, target_session_id)

    @staticmethod
    def logout_all(cur, access_token: str) -> int:
        claims = validate_access_token(cur, access_token)
        return AuthService.revoke_all_sessions(cur, claims["sub"])
