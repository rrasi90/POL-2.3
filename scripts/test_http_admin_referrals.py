"""HTTP tests for Admin & Referral endpoints — Stage 34.

Tests admin audit logs, exceptions dashboard, referral CRUD, and role-based access.
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


def _create_session(cur, user_id, org_id):
    session_id = str(uuid4())
    cur.execute(
        "INSERT INTO user_sessions (id, user_id, active_organization_id, token_hash, status, expires_at) "
        "VALUES (%s, %s, %s, %s, 'ACTIVE', %s)",
        (session_id, user_id, org_id, hash_token(session_id),
         datetime.now(timezone.utc) + timedelta(hours=1)),
    )
    return session_id


def _seed_admin_vendor_retailer():
    """Seed admin, vendor, retailer infrastructure for admin/referral tests."""
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            au = str(uuid4()); ao = str(uuid4())
            vu = str(uuid4()); vo = str(uuid4()); vi = str(uuid4())
            ru = str(uuid4()); ro = str(uuid4()); ri = str(uuid4())

            cur.execute(
                "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Admin User', 'ADMIN_SUPER')",
                (au, f"+9891{uuid4().int % 100000000:08d}"),
            )
            cur.execute(
                "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'POL Ops', 'OPERATOR', 'ACTIVE')",
                (ao,),
            )
            cur.execute(
                "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'ADMIN_SUPER', 'ACTIVE')",
                (str(uuid4()), ao, au),
            )

            cur.execute(
                "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Vendor User', 'VENDOR_OWNER')",
                (vu, f"+9891{uuid4().int % 100000000:08d}"),
            )
            cur.execute(
                "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Test Vendor', 'VENDOR', 'ACTIVE')",
                (vo,),
            )
            cur.execute(
                "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')",
                (str(uuid4()), vo, vu),
            )
            cur.execute(
                "INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman, status) "
                "VALUES (%s, %s, %s, 'Test Vendor Co', 'Ahvaz', 1000000, 'ACTIVE')",
                (vi, vu, vo),
            )

            cur.execute(
                "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Retailer User', 'RETAILER_OWNER')",
                (ru, f"+9891{uuid4().int % 100000000:08d}"),
            )
            cur.execute(
                "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Test Retailer', 'RETAILER', 'ACTIVE')",
                (ro,),
            )
            cur.execute(
                "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'RETAILER_OWNER', 'ACTIVE')",
                (str(uuid4()), ro, ru),
            )
            cur.execute(
                "INSERT INTO retailers (id, user_id, organization_id, store_name, city, neighborhood, address) "
                "VALUES (%s, %s, %s, 'Test Store', 'Ahvaz', 'N', 'A')",
                (ri, ru, ro),
            )

            as_ = _create_session(cur, au, ao)
            vs_ = _create_session(cur, vu, vo)
            rs_ = _create_session(cur, ru, ro)

        conn.commit()
        at = encode_access_token(au, as_, ao, "ADMIN_SUPER")
        vt = encode_access_token(vu, vs_, vo, "VENDOR_OWNER")
        rt = encode_access_token(ru, rs_, ro, "RETAILER_OWNER")
        return {
            "a_token": at, "v_token": vt, "r_token": rt,
            "au": au, "ao": ao, "vu": vu, "vo": vo, "vi": vi,
            "ru": ru, "ro": ro, "ri": ri,
        }
    finally:
        conn.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app, raise_server_exceptions=False)


class TestAdminAuditLogs:
    def test_admin_can_list_audit_logs(self, client):
        data = _seed_admin_vendor_retailer()
        resp = client.get(
            "/api/v1/admin/audit-logs",
            headers={"Authorization": f"Bearer {data['a_token']}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)

    def test_retailer_cannot_list_audit_logs(self, client):
        data = _seed_admin_vendor_retailer()
        resp = client.get(
            "/api/v1/admin/audit-logs",
            headers={"Authorization": f"Bearer {data['r_token']}"},
        )
        assert resp.status_code == 403


class TestAdminExceptionsDashboard:
    def test_admin_can_view_exceptions_dashboard(self, client):
        data = _seed_admin_vendor_retailer()
        resp = client.get(
            "/api/v1/admin/exceptions/dashboard",
            headers={"Authorization": f"Bearer {data['a_token']}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert "delivery_exceptions" in body["data"]
        assert "disputes" in body["data"]
        assert "support_cases" in body["data"]


class TestReferralCreate:
    def test_vendor_can_create_referral(self, client):
        data = _seed_admin_vendor_retailer()
        resp = client.post(
            "/api/v1/referrals",
            headers={"Authorization": f"Bearer {data['v_token']}"},
            json={},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["status"] == "ACTIVE"
        assert body["data"]["referral_code"].startswith("POLV-")

    def test_retailer_cannot_create_referral(self, client):
        data = _seed_admin_vendor_retailer()
        resp = client.post(
            "/api/v1/referrals",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"referral_code": f"POLV-{uuid4().hex[:8].upper()}"},
        )
        assert resp.status_code == 403


class TestReferralList:
    def test_vendor_can_list_own_referrals(self, client):
        data = _seed_admin_vendor_retailer()
        code = f"POLV-{uuid4().hex[:8].upper()}"
        client.post(
            "/api/v1/referrals",
            headers={"Authorization": f"Bearer {data['v_token']}"},
            json={"referral_code": code},
        )
        resp = client.get(
            "/api/v1/referrals",
            headers={"Authorization": f"Bearer {data['v_token']}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert isinstance(body["data"]["referrals"], list)
        assert any(r["referral_code"] == code for r in body["data"]["referrals"])


class TestReferralRedeem:
    def test_referral_redeem(self, client):
        data = _seed_admin_vendor_retailer()
        code = f"POLV-{uuid4().hex[:8].upper()}"
        create_resp = client.post(
            "/api/v1/referrals",
            headers={"Authorization": f"Bearer {data['v_token']}"},
            json={"referral_code": code},
        )
        assert create_resp.status_code == 201
        referral_id = create_resp.json()["data"]["id"]
        resp = client.post(
            f"/api/v1/referrals/{referral_id}/redeem",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["status"] == "ATTRIBUTED"

        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT redemption_count FROM vendor_referrals WHERE id=%s",
                    (referral_id,),
                )
                assert int(cur.fetchone()["redemption_count"]) == 1
        finally:
            conn.close()


class TestUnauthenticated:
    def test_unauthenticated_rejected(self, client):
        resp = client.get("/api/v1/admin/audit-logs")
        assert resp.status_code == 401

    def test_unauthenticated_referral_rejected(self, client):
        resp = client.get("/api/v1/referrals")
        assert resp.status_code == 401
