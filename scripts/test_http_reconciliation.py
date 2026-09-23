"""HTTP tests for Reconciliation Exception Management -- Stage 29.

Tests listing, retrieval, resolution of reconciliation cases, and access control.
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


def _seed_reconciliation(suffix, *, include_ops=False, case_status="OPEN"):
    """Seed retailer + vendor + order + payment + reconciliation case infrastructure."""
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            ru = str(uuid4()); ro = str(uuid4()); ri = str(uuid4())
            vu = str(uuid4()); vo = str(uuid4()); vi = str(uuid4())
            bi = str(uuid4()); pi = str(uuid4()); ogi = str(uuid4())
            oi = str(uuid4()); pay_id = str(uuid4()); case_id = str(uuid4())

            cur.execute(
                "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'R', 'RETAILER_OWNER')",
                (ru, f"+9891{uuid4().int % 100000000:08d}"),
            )
            cur.execute(
                "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'RO', 'RETAILER', 'ACTIVE')",
                (ro,),
            )
            cur.execute(
                "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) "
                "VALUES (%s, %s, %s, 'RETAILER_OWNER', 'ACTIVE')",
                (str(uuid4()), ro, ru),
            )
            cur.execute(
                "INSERT INTO retailers (id, user_id, organization_id, store_name, city, neighborhood, address) "
                "VALUES (%s, %s, %s, 'S', 'Ahvaz', 'N', 'A')",
                (ri, ru, ro),
            )
            cur.execute(
                "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'V', 'VENDOR_OWNER')",
                (vu, f"+9891{uuid4().int % 100000000:08d}"),
            )
            cur.execute(
                "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'VO', 'VENDOR', 'ACTIVE')",
                (vo,),
            )
            cur.execute(
                "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) "
                "VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')",
                (str(uuid4()), vo, vu),
            )
            cur.execute(
                "INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, "
                "min_order_value_toman, status) "
                "VALUES (%s, %s, %s, 'V', 'Ahvaz', 1000000, 'ACTIVE')",
                (vi, vu, vo),
            )
            cur.execute(
                "INSERT INTO baskets (id, retailer_id, status, version) VALUES (%s, %s, 'OPEN', 1)",
                (bi, ri),
            )
            cur.execute(
                "INSERT INTO allocation_plans (id, basket_id, basket_version, status, strategy, "
                "vendor_count, total_estimated_toman, expires_at) "
                "VALUES (%s, %s, 1, 'CONFIRMED', 'SINGLE_VENDOR', 1, 5000000, now() + interval '15 minutes')",
                (pi, bi),
            )
            cur.execute(
                "INSERT INTO order_groups (id, basket_id, retailer_id, checkout_idempotency_key, "
                "total_amount_toman, order_count, group_status) "
                "VALUES (%s, %s, %s, %s, 5000000, 1, 'ACTIVE')",
                (ogi, bi, ri, str(uuid4())),
            )
            cur.execute(
                "INSERT INTO orders (id, order_number, order_group_id, allocation_plan_id, retailer_id, "
                "vendor_id, order_status, total_amount_toman, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, 'DISPATCHED', 5000000, now(), now())",
                (oi, f"ORD-{suffix}", ogi, pi, ri, vi),
            )
            cur.execute(
                "INSERT INTO payments (id, order_id, retailer_id, vendor_id, amount_toman, "
                "payment_method, custody_model, payment_status) "
                "VALUES (%s, %s, %s, %s, 5000000, 'DIRECT_BANK_TRANSFER', 'NON_CUSTODIAL_DIRECT', 'PENDING')",
                (pay_id, oi, ri, vi),
            )
            cur.execute(
                "INSERT INTO payment_reconciliation_cases "
                "(id, payment_id, status, expected_amount_toman) "
                "VALUES (%s, %s, %s, 5000000)",
                (case_id, pay_id, case_status),
            )

            ou = str(uuid4()); oo = str(uuid4())
            if include_ops:
                cur.execute(
                    "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'OPS', 'ADMIN_SUPER')",
                    (ou, f"+9891{uuid4().int % 100000000:08d}"),
                )
                cur.execute(
                    "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'OO', 'OPERATOR', 'ACTIVE')",
                    (oo,),
                )
                cur.execute(
                    "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) "
                    "VALUES (%s, %s, %s, 'ADMIN_SUPER', 'ACTIVE')",
                    (str(uuid4()), oo, ou),
                )

            rs = _create_session(cur, ru, ro)
            vs = _create_session(cur, vu, vo)
            os_s = _create_session(cur, ou, oo) if include_ops else None

        conn.commit()
        r_token = encode_access_token(ru, rs, ro, "RETAILER_OWNER")
        v_token = encode_access_token(vu, vs, vo, "VENDOR_OWNER")
        o_token = encode_access_token(ou, os_s, oo, "ADMIN_SUPER") if include_ops else None
        return {
            "case_id": case_id, "pay_id": pay_id, "oi": oi,
            "r_token": r_token, "v_token": v_token, "o_token": o_token,
            "ru": ru, "ro": ro, "vu": vu, "vo": vo, "ou": ou, "oo": oo,
        }
    finally:
        conn.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app, raise_server_exceptions=False)


class TestListReconciliationCases:
    def test_ops_lists_cases(self, client):
        data = _seed_reconciliation(uuid4().hex[:8], include_ops=True)
        resp = client.get(
            "/api/v1/finance/reconciliation",
            headers={"Authorization": f"Bearer {data['o_token']}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        assert any(c["id"] == data["case_id"] for c in body["data"])

    def test_ops_filter_by_status(self, client):
        data = _seed_reconciliation(uuid4().hex[:8], include_ops=True, case_status="MISMATCH")
        resp = client.get(
            "/api/v1/finance/reconciliation?status=MISMATCH",
            headers={"Authorization": f"Bearer {data['o_token']}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert any(c["id"] == data["case_id"] for c in body["data"])


class TestGetReconciliationCase:
    def test_ops_get_case(self, client):
        data = _seed_reconciliation(uuid4().hex[:8], include_ops=True)
        resp = client.get(
            f"/api/v1/finance/reconciliation/{data['case_id']}",
            headers={"Authorization": f"Bearer {data['o_token']}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["id"] == data["case_id"]
        assert body["data"]["expected_amount_toman"] == 5000000

    def test_get_case_not_found(self, client):
        data = _seed_reconciliation(uuid4().hex[:8], include_ops=True)
        resp = client.get(
            f"/api/v1/finance/reconciliation/{uuid4()}",
            headers={"Authorization": f"Bearer {data['o_token']}"},
        )
        assert resp.status_code == 404


class TestResolveReconciliationCase:
    def test_ops_resolves_case(self, client):
        data = _seed_reconciliation(uuid4().hex[:8], include_ops=True)
        resp = client.patch(
            f"/api/v1/finance/reconciliation/{data['case_id']}/resolve",
            headers={"Authorization": f"Bearer {data['o_token']}"},
            json={"resolution_note": "Verified via bank statement."},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["status"] == "MATCHED"
        assert body["data"]["resolution_reason"] == "Verified via bank statement."
        assert body["data"]["resolved_by_user_id"] == data["ou"]

    def test_resolve_already_resolved_rejected(self, client):
        data = _seed_reconciliation(uuid4().hex[:8], include_ops=True, case_status="RESOLVED")
        resp = client.patch(
            f"/api/v1/finance/reconciliation/{data['case_id']}/resolve",
            headers={"Authorization": f"Bearer {data['o_token']}"},
            json={},
        )
        assert resp.status_code == 422

    def test_resolve_not_found(self, client):
        data = _seed_reconciliation(uuid4().hex[:8], include_ops=True)
        resp = client.patch(
            f"/api/v1/finance/reconciliation/{uuid4()}/resolve",
            headers={"Authorization": f"Bearer {data['o_token']}"},
            json={},
        )
        assert resp.status_code == 404


class TestReconciliationAccessControl:
    def test_retailer_cannot_list(self, client):
        data = _seed_reconciliation(uuid4().hex[:8], include_ops=True)
        resp = client.get(
            "/api/v1/finance/reconciliation",
            headers={"Authorization": f"Bearer {data['r_token']}"},
        )
        assert resp.status_code == 403

    def test_unauthenticated_rejected(self, client):
        resp = client.get("/api/v1/finance/reconciliation")
        assert resp.status_code == 401
