"""Internal authentication boundary — JWT encode/decode, session validation, token issuance.

This is an internal authentication component, NOT a client-facing facade.
The canonical transport chain is:

    FastAPI → authentication/session → ApplicationContext → POLApplicationBoundary → domain services

auth_boundary.py sits inside the authentication step, providing helpers that
AuthService and FastAPI middleware call internally.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from scripts.operational_config import (
    JWT_ALGORITHM,
    JWT_ISSUER,
    JWT_AUDIENCE,
    JWT_ACCESS_TTL_SECONDS,
    OTP_SALT_BYTES,
    OTP_PBKDF2_ITERATIONS,
    REFRESH_TOKEN_BYTES,
)


class AuthError(Exception):
    """Canonical authentication/authorization failure."""
    pass


def get_jwt_secret() -> str:
    """Return the JWT signing secret from environment. Fails fast if missing."""
    secret = os.environ.get("POL_JWT_SECRET")
    if not secret:
        raise RuntimeError("POL_JWT_SECRET environment variable is not set.")
    return secret


def encode_access_token(
    user_id: str,
    session_id: str,
    org_id: str,
    role: str,
) -> str:
    """Issue a signed HS256 JWT access token with D-018 claims."""
    now = datetime.now(timezone.utc)
    claims = {
        "sub": user_id,
        "sid": session_id,
        "org_id": org_id,
        "role": role,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "exp": now + timedelta(seconds=JWT_ACCESS_TTL_SECONDS),
    }
    return jwt.encode(claims, get_jwt_secret(), algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token. Raises jwt.InvalidTokenError on failure."""
    return jwt.decode(
        token,
        get_jwt_secret(),
        algorithms=[JWT_ALGORITHM],
        issuer=JWT_ISSUER,
        audience=JWT_AUDIENCE,
        options={"require": ["exp", "iss", "aud", "sub", "sid", "org_id", "role"]},
    )


def validate_access_token(cur, token: str) -> dict:
    """Canonical access-token validation path.

    Validates JWT signature, claims, session existence, session status,
    org_id match, and active membership. Returns the validated claims dict.

    This is the SINGLE source-of-truth validation for all access tokens.
    JWT claims are cached authorization context, NOT the authorization SSoT.
    The database is the SSoT for session status, org context, and membership.
    """
    # 1. Decode + validate JWT signature, iss, aud, exp, required claims
    try:
        claims = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired.")
    except jwt.InvalidTokenError as e:
        raise AuthError(f"Invalid token: {e}")

    user_id = claims["sub"]
    session_id = claims["sid"]
    jwt_org_id = claims["org_id"]

    # 2. Session exists + status == ACTIVE
    cur.execute("""
        SELECT id, user_id, active_organization_id, status
        FROM user_sessions
        WHERE id = %s;
    """, (session_id,))
    session = cur.fetchone()
    if not session:
        raise AuthError("Session not found.")
    if session["status"] != "ACTIVE":
        raise AuthError("Session is not active.")

    # 3. JWT.sub == session.user_id
    if str(session["user_id"]) != user_id:
        raise AuthError("Token user does not match session user.")

    # 4. JWT.org_id == session.active_organization_id
    if str(session["active_organization_id"]) != jwt_org_id:
        raise AuthError("Token organization does not match session organization.")

    # 5. Active membership exists for JWT.org_id
    cur.execute("""
        SELECT role, status FROM organization_memberships
        WHERE user_id = %s AND organization_id = %s;
    """, (user_id, jwt_org_id))
    membership = cur.fetchone()
    if not membership or membership["status"] != "ACTIVE":
        raise AuthError("No active membership for token organization.")

    return claims


def generate_refresh_token() -> str:
    """Generate a cryptographically random opaque refresh token."""
    return secrets.token_urlsafe(REFRESH_TOKEN_BYTES)


def hash_token(token: str) -> str:
    """SHA-256 hash a token for storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def store_otp_hash(code: str) -> str:
    """Store OTP using PBKDF2-HMAC-SHA256 with random salt.

    Format: iterations$hex(salt)$hex(derived_key)
    Total length: 6 + 1 + 32 + 1 + 64 = 104 chars (fits VARCHAR(128)).
    """
    salt = secrets.token_bytes(OTP_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac(
        "sha256", code.encode("utf-8"), salt, OTP_PBKDF2_ITERATIONS, dklen=32
    )
    return f"{OTP_PBKDF2_ITERATIONS}${salt.hex()}${dk.hex()}"


def verify_otp_hash(code: str, stored: str) -> bool:
    """Verify a PBKDF2-HMAC-SHA256 OTP hash using timing-safe comparison."""
    try:
        iterations_str, salt_hex, dk_hex = stored.split("$")
        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
    except (ValueError, AttributeError):
        return False
    dk = hashlib.pbkdf2_hmac(
        "sha256", code.encode("utf-8"), salt, iterations, dklen=32
    )
    return hmac.compare_digest(dk.hex(), dk_hex)
