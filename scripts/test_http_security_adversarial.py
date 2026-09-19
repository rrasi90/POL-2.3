"""HTTP-level adversarial security tests for tenant isolation — Stage 12.

Adversarial scenarios (real auth boundary, real database, no overrides):
- Cross-tenant vendor order accept (IDOR) → 403 FORBIDDEN
- Cross-tenant vendor order reject (IDOR) → 403 FORBIDDEN
- Positive control: owning vendor accepts its own order → 200 ACCEPTED
- Malformed JWT → 401 INVALID_ACCESS_TOKEN
- Order state must remain unchanged after every rejected adversarial attempt
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import psycopg2
import pytest
from fastapi.testclient import TestClient
from psycopg2.extras import RealDictCursor

from scripts.api.main import app
from scripts.auth_boundary import encode_access_token, hash_token
from scripts.test_vendor_order_acceptance import _setup_order


JWT_SECRET = "test-secret-key-for-auth-contract-tests-only-32bytes!!"


@pytest.fixture
def api_env(monkeypatch):
    pg_port = (
        os.environ.get("POL_API_DB_PORT")
        or os.environ.get("POL_PG_PORT")
        or os.environ.get("PGPORT")
        or "5432"
    )
    monkeypatch.setenv("POL_API_DB_NAME", "pol_test")
    monkeypatch.setenv("POL_API_DB_HOST", os.environ.get("PGHOST", "127.0.0.1"))
    monkeypatch.setenv("POL_API_DB_PORT", pg_port)
    monkeypatch.setenv("POL_JWT_SECRET", JWT_SECRET)
    monkeypatch.setenv("ENVIRONMENT", "test")


def _db():
    port = int(
        os.environ.get("POL_API_DB_PORT")
        or os.environ.get("POL_PG_PORT")
        or os.environ.get("PGPORT", "5432")
    )
    return psycopg2.connect(
        dbname="pol_test",
        host=os.environ.get("POL_API_DB_HOST", os.environ.get("PGHOST", "127.0.0.1")),
        port=port,
        user=os.environ.get("POL_API_DB_USER", os.environ.get("PGUSER", "postgres")),
    )


def _create_session(cur, user_id: str, org_id: str) -> str:
    """Create a user_sessions row and return the session_id."""
    session_id = str(uuid4())
    token_hash = hash_token(session_id)
    cur.execute(
        """
        INSERT INTO user_sessions (
            id, user_id, active_organization_id, token_hash,
            status, expires_at
        ) VALUES (%s, %s, %s, %s, 'ACTIVE', %s)
        """,
        (session_id, user_id, org_id, token_hash,
         datetime.now(timezone.utc) + timedelta(hours=1)),
    )
    return session_id


def _second_vendor(cur):
    """Create an unrelated vendor org for adversarial cross-tenant attempts."""
    other_user = str(uuid4())
    other_org = str(uuid4())
    other_vendor = str(uuid4())
    cur.execute(
        "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Adversary Vendor', 'VENDOR_OWNER')",
        (other_user, f"+9891{uuid4().int % 100000000:08d}"),
    )
    cur.execute(
        "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Adversary Vendor Org', 'VENDOR', 'ACTIVE')",
        (other_org,),
    )
    cur.execute(
        "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')",
        (str(uuid4()), other_org, other_user),
    )
    cur.execute(
        """
        INSERT INTO vendors (
            id, user_id, organization_id, business_name,
            warehouse_address, min_order_value_toman, status
        ) VALUES (%s, %s, %s, 'Adversary Vendor', 'Elsewhere', 1000000, 'ACTIVE')
        """,
        (other_vendor, other_user, other_org),
    )
    return other_user, other_org, other_vendor


def _token_for(cur, user_id, org_id):
    """Create a session row and mint a JWT referencing that session."""
    session_id = _create_session(cur, user_id, org_id)
    return encode_access_token(user_id, session_id, org_id, "VENDOR_OWNER")


def _order_status(order_id):
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT order_status FROM orders WHERE id = %s", (order_id,))
            return cur.fetchone()["order_status"]
    finally:
        conn.close()


def test_cross_tenant_vendor_accept_is_forbidden(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _setup_order(cur, uuid4().hex[:10])
                other_user, other_org, _vendor = _second_vendor(cur)
                adversarial_token = _token_for(cur, other_user, other_org)
        response = TestClient(app).post(
            f"/api/v1/orders/{data['order_id']}/accept",
            headers={"Authorization": f"Bearer {adversarial_token}"},
        )
        assert response.status_code == 403
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "FORBIDDEN"
        assert _order_status(data["order_id"]) == "SUBMITTED"
    finally:
        conn.close()


def test_cross_tenant_vendor_reject_is_forbidden(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _setup_order(cur, uuid4().hex[:10])
                other_user, other_org, _vendor = _second_vendor(cur)
                adversarial_token = _token_for(cur, other_user, other_org)
        response = TestClient(app).post(
            f"/api/v1/orders/{data['order_id']}/reject",
            headers={"Authorization": f"Bearer {adversarial_token}"},
            json={"reason": "ADVERSARY ATTEMPT"},
        )
        assert response.status_code == 403
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "FORBIDDEN"
        assert _order_status(data["order_id"]) == "SUBMITTED"
    finally:
        conn.close()


def test_owner_vendor_accept_succeeds_positive_control(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _setup_order(cur, uuid4().hex[:10])
                owner_token = _token_for(cur, data["vendor_user"], data["vendor_org"])
        response = TestClient(app).post(
            f"/api/v1/orders/{data['order_id']}/accept",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["order_status"] == "ACCEPTED"
    finally:
        conn.close()


def test_malformed_jwt_is_rejected(api_env):
    response = TestClient(app).post(
        f"/api/v1/orders/{uuid4()}/accept",
        headers={"Authorization": "Bearer not-a-real-jwt"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_ACCESS_TOKEN"


def test_cross_tenant_reject_extra_fields_rejected_by_schema(api_env):
    """Reject body with unknown vendor_id field is rejected at schema validation layer."""
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _setup_order(cur, uuid4().hex[:10])
                other_user, other_org, _vendor = _second_vendor(cur)
                adversarial_token = _token_for(cur, other_user, other_org)
        response = TestClient(app).post(
            f"/api/v1/orders/{data['order_id']}/reject",
            headers={"Authorization": f"Bearer {adversarial_token}"},
            json={"reason": "X", "vendor_id": str(uuid4())},
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    finally:
        conn.close()


def test_revoked_session_token_is_rejected(api_env):
    """Token referencing a revoked session returns 401."""
    conn = _db()
    try:
        vendor_user = str(uuid4())
        vendor_org = str(uuid4())
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Revoked Vendor', 'VENDOR_OWNER')",
                    (vendor_user, f"+9891{uuid4().int % 100000000:08d}"),
                )
                cur.execute(
                    "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Revoked Org', 'VENDOR', 'ACTIVE')",
                    (vendor_org,),
                )
                cur.execute(
                    "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')",
                    (str(uuid4()), vendor_org, vendor_user),
                )
                session_id = _create_session(cur, vendor_user, vendor_org)
                token = encode_access_token(vendor_user, session_id, vendor_org, "VENDOR_OWNER")
                cur.execute("UPDATE user_sessions SET status = 'REVOKED' WHERE id = %s", (session_id,))
        response = TestClient(app).post(
            f"/api/v1/orders/{uuid4()}/accept",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_ACCESS_TOKEN"
    finally:
        conn.close()
