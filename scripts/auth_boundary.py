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
