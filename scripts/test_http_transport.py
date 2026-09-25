"""PostgreSQL-backed smoke tests for the first FastAPI transport slice."""

from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient
from psycopg2.extras import RealDictCursor

from scripts.api.main import app
from scripts.migration_runner import get_connection


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("POL_API_DB_NAME", "pol_test")
    monkeypatch.setenv("POL_PG_PORT", os.environ.get("POL_PG_PORT", "5432"))
    monkeypatch.setenv(
        "POL_JWT_SECRET",
        "test-secret-key-for-auth-contract-tests-only-32bytes!!",
    )
    monkeypatch.setenv("ENVIRONMENT", "test")
    return TestClient(app)


def _test_db_name():
    dbname = os.environ.get("POL_API_DB_NAME", "pol_test")
    if dbname not in {"pol_test", "postgres"}:
        raise RuntimeError("HTTP transport tests refuse non-isolated database names.")
    return dbname


def _conn():
    conn, _ = get_connection(_test_db_name())
    conn.autocommit = False
    return conn


def _seed_user():
    conn = _conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    user_id = str(uuid.uuid4())
    org_a = str(uuid.uuid4())
    org_b = str(uuid.uuid4())
    phone = f"+9891{uuid.uuid4().int % 100000000:08d}"

    cur.execute(
        """
        INSERT INTO organizations (id, name, org_type, status)
        VALUES (%s, 'HTTP Test Retailer A', 'RETAILER', 'ACTIVE'),
               (%s, 'HTTP Test Retailer B', 'RETAILER', 'ACTIVE');
        """,
        (org_a, org_b),
    )
    cur.execute(
        """
        INSERT INTO users (id, phone_number, full_name, role, is_active)
        VALUES (%s, %s, 'HTTP Test User', 'RETAILER_OWNER', TRUE);
        """,
        (user_id, phone),
    )
    cur.execute(
        """
        INSERT INTO organization_memberships
            (id, organization_id, user_id, role, status, is_primary)
        VALUES
            (%s, %s, %s, 'RETAILER_OWNER', 'ACTIVE', TRUE),
            (%s, %s, %s, 'RETAILER_OWNER', 'ACTIVE', FALSE);
        """,
        (str(uuid.uuid4()), org_a, user_id, str(uuid.uuid4()), org_b, user_id),
    )
    conn.commit()
    conn.close()
    return phone, org_a, org_b, user_id


def _cleanup(phone, user_id):
    conn = _conn()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM user_sessions WHERE user_id = %s;", (user_id,))
        cur.execute("DELETE FROM otp_challenges WHERE phone_number = %s;", (phone,))
        cur.execute("DELETE FROM organization_memberships WHERE user_id = %s;", (user_id,))
        cur.execute("DELETE FROM user_profiles WHERE user_id = %s;", (user_id,))
        cur.execute("DELETE FROM users WHERE id = %s;", (user_id,))
        conn.commit()
    finally:
        conn.close()


def test_cors_is_scoped_to_known_web_origins(client):
    response = client.options(
        "/api/v1/profile",
        headers={
            "Origin": "http://localhost:3001",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3001"
    assert response.headers.get("access-control-allow-methods")

    blocked = client.options(
        "/api/v1/profile",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        },
    )
    assert "access-control-allow-origin" not in blocked.headers


def test_security_headers_present(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "no-referrer"
    assert response.headers.get("Permissions-Policy") == "camera=(), microphone=(), geolocation=()"
    assert response.headers.get("X-Correlation-ID")


def test_health_and_readiness(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_auth_profile_switch_and_revocation_flow(client):
    phone, _, org_b, user_id = _seed_user()

    try:
        response = client.post(
            "/api/v1/auth/request-otp",
            json={"mobile_number": phone},
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["data"]["expires_in_seconds"] == 120
        assert response.json()["data"]["resend_interval_seconds"] == 60

        response = client.post(
            "/api/v1/auth/verify-otp",
            json={"mobile_number": phone, "otp_code": "1234", "client_platform": "web"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        access_a = body["data"]["access_token"]
        assert "refresh_token" not in body["data"]
        set_cookie = response.headers.get("set-cookie", "")
        assert "pol_refresh=" in set_cookie
        assert "HttpOnly" in set_cookie
        assert "SameSite=lax" in set_cookie


        response = client.get(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {access_a}"},
        )
        assert response.status_code == 200

        response = client.post(
            "/api/v1/auth/refresh",
        )
        assert response.status_code == 200
        access_refreshed = response.json()["data"]["access_token"]
        assert access_refreshed

        response = client.post(
            "/api/v1/auth/switch-organization",
            json={"target_organization_id": org_b},
            headers={"Authorization": f"Bearer {access_a}"},
        )
        assert response.status_code == 200
        access_b = response.json()["data"]["access_token"]

        stale = client.get(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {access_a}"},
        )
        assert stale.status_code == 401
        assert stale.json()["error"]["code"] == "INVALID_ACCESS_TOKEN"

        current = client.get(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {access_b}"},
        )
        assert current.status_code == 200

        revoked = client.delete(
            "/api/v1/auth/sessions/current",
            headers={"Authorization": f"Bearer {access_b}"},
        )
        assert revoked.status_code == 200

        rejected = client.get(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {access_b}"},
        )
        assert rejected.status_code == 401

        refresh_after_revoke = client.post(
            "/api/v1/auth/refresh",
        )
        assert refresh_after_revoke.status_code == 401
        assert refresh_after_revoke.json()["error"]["code"] == "SESSION_REVOKED"
    finally:
        _cleanup(phone, user_id)


def test_rate_limit_and_error_envelope(client):
    phone, _, _, user_id = _seed_user()

    try:
        for _ in range(3):
            response = client.post(
                "/api/v1/auth/request-otp",
                json={"mobile_number": phone},
            )
            assert response.status_code == 200

        response = client.post(
            "/api/v1/auth/request-otp",
            json={"mobile_number": phone},
        )
        assert response.status_code == 429
        assert response.json()["error"]["code"] == "OTP_RATE_LIMITED"
        assert response.headers.get("X-Correlation-ID")

        response = client.get("/api/v1/profile")
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_ACCESS_TOKEN"
    finally:
        _cleanup(phone, user_id)


def test_transport_validation_uses_canonical_error_envelope(client):
    response = client.post(
        "/api/v1/auth/verify-otp",
        json={"mobile_number": "bad", "otp_code": "12"},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "timestamp" in body["error"]
