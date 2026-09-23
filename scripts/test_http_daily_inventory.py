"""HTTP transport tests for daily inventory confirmation — Stage 18.

Tests daily confirmation get, 1-tap confirm, confirm with changes,
and tenant isolation. Real auth boundary, real database.
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


def _seed_vendor_with_inventory(cur, suffix):
    user_id = str(uuid4())
    org_id = str(uuid4())
    vendor_id = str(uuid4())
    brand_id = str(uuid4())
    category_id = str(uuid4())
    subcategory_id = str(uuid4())
    product_id = str(uuid4())
    vendor_product_id = str(uuid4())

    cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Vendor', 'VENDOR_OWNER')",
                (user_id, f"+9891{uuid4().int % 100000000:08d}"))
    cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Daily Org', 'VENDOR', 'ACTIVE')", (org_id,))
    cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')",
                (str(uuid4()), org_id, user_id))
    cur.execute("INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman, status) "
                "VALUES (%s, %s, %s, 'Daily Vendor', 'Ahvaz', 1000000, 'ACTIVE')",
                (vendor_id, user_id, org_id))
    cur.execute("INSERT INTO brands (id, name_fa, slug) VALUES (%s, %s, %s)", (brand_id, f"B{suffix}", f"b-{suffix}"))
    cur.execute("INSERT INTO categories (id, name_fa, slug) VALUES (%s, %s, %s)", (category_id, f"C{suffix}", f"c-{suffix}"))
    cur.execute("INSERT INTO subcategories (id, category_id, name_fa, slug) VALUES (%s, %s, %s, %s)",
                (subcategory_id, category_id, f"S{suffix}", f"s-{suffix}"))
    cur.execute("INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id, is_active) "
                "VALUES (%s, %s, %s, %s, %s, %s, TRUE)",
                (product_id, f"POL-{suffix}", f"P{suffix}", brand_id, category_id, subcategory_id))
    cur.execute("INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity, sales_unit, is_active, listing_status) "
                "VALUES (%s, %s, %s, %s, 'CARTON', 4, 'CARTON', TRUE, 'ACTIVE')",
                (vendor_product_id, vendor_id, product_id, f"VP-{suffix}"))
    cur.execute("INSERT INTO vendor_inventory (vendor_product_id, inventory_unit, physical_quantity, reserved_quantity, moq, freshness_status) "
                "VALUES (%s, 'CARTON', 50, 0, 1, 'FRESH')",
                (vendor_product_id,))

    session_id = _create_session(cur, user_id, org_id)
    token = encode_access_token(user_id, session_id, org_id, "VENDOR_OWNER")
    return {"token": token, "vendor_id": vendor_id, "vendor_product_id": vendor_product_id}


def test_daily_inventory_get_creates_pending(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor_with_inventory(cur, uuid4().hex[:8])
        response = TestClient(app).get(
            f"/api/v1/inventory/daily/2026-10-15",
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["status"] == "PENDING"
        assert body["data"]["confirmation_date"] == "2026-10-15"
    finally:
        conn.close()


def test_daily_inventory_confirm_no_changes(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor_with_inventory(cur, uuid4().hex[:8])
        response = TestClient(app).post(
            f"/api/v1/inventory/daily/2026-10-15/confirm",
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["status"] == "CONFIRMED_NO_CHANGES"
        assert body["data"]["changed_item_count"] == 0
    finally:
        conn.close()


def test_daily_inventory_confirm_with_changes(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor_with_inventory(cur, uuid4().hex[:8])
        response = TestClient(app).post(
            f"/api/v1/inventory/daily/2026-10-15/confirm-with-changes",
            headers={"Authorization": f"Bearer {data['token']}"},
            json={
                "confirmation_date": "2026-10-15",
                "changes": [
                    {"vendor_product_id": str(data["vendor_product_id"]), "declared_quantity": 75},
                ],
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["status"] == "CONFIRMED_WITH_CHANGES"
        assert body["data"]["changed_item_count"] == 1
    finally:
        conn.close()


def test_daily_inventory_confirm_updates_vendor_inventory(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor_with_inventory(cur, uuid4().hex[:8])
        TestClient(app).post(
            f"/api/v1/inventory/daily/2026-10-15/confirm-with-changes",
            headers={"Authorization": f"Bearer {data['token']}"},
            json={
                "confirmation_date": "2026-10-15",
                "changes": [
                    {"vendor_product_id": str(data["vendor_product_id"]), "declared_quantity": 25},
                ],
            },
        )
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT physical_quantity, inventory_confidence FROM vendor_inventory WHERE vendor_product_id = %s",
                            (data["vendor_product_id"],))
                inv = cur.fetchone()
                assert inv["physical_quantity"] == 25
                assert inv["inventory_confidence"] == "CONFIRMED_TODAY"
    finally:
        conn.close()


def test_daily_inventory_confirm_is_idempotent(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor_with_inventory(cur, uuid4().hex[:8])
        resp1 = TestClient(app).post(
            f"/api/v1/inventory/daily/2026-10-15/confirm",
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        resp2 = TestClient(app).post(
            f"/api/v1/inventory/daily/2026-10-15/confirm",
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert resp1.json()["data"]["status"] == resp2.json()["data"]["status"]
    finally:
        conn.close()


def test_daily_inventory_cross_tenant_gets_own_confirmation(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor_with_inventory(cur, uuid4().hex[:8])
                other_user = str(uuid4())
                other_org = str(uuid4())
                other_vendor_id = str(uuid4())
                cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Other', 'VENDOR_OWNER')",
                            (other_user, f"+9891{uuid4().int % 100000000:08d}"))
                cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Other', 'VENDOR', 'ACTIVE')", (other_org,))
                cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')",
                            (str(uuid4()), other_org, other_user))
                cur.execute("INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman, status) "
                            "VALUES (%s, %s, %s, 'Other Vendor', 'Tehran', 1000000, 'ACTIVE')",
                            (other_vendor_id, other_user, other_org))
                other_token = encode_access_token(other_user, _create_session(cur, other_user, other_org), other_org, "VENDOR_OWNER")
        client = TestClient(app)
        client.post(
            f"/api/v1/inventory/daily/2026-10-15/confirm",
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        response = client.post(
            f"/api/v1/inventory/daily/2026-10-15/confirm",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "CONFIRMED_NO_CHANGES"
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT status FROM daily_inventory_confirmations WHERE vendor_id = %s AND confirmation_date = '2026-10-15'",
                            (data["vendor_id"],))
                conf = cur.fetchone()
                assert conf["status"] == "CONFIRMED_NO_CHANGES"
                cur.execute("SELECT status FROM daily_inventory_confirmations WHERE vendor_id = %s AND confirmation_date = '2026-10-15'",
                            (other_vendor_id,))
                other_conf = cur.fetchone()
                assert other_conf["status"] == "CONFIRMED_NO_CHANGES"
    finally:
        conn.close()


def test_daily_inventory_routes_require_auth(api_env):
    assert TestClient(app).get("/api/v1/inventory/daily/2026-10-15").status_code == 401
    assert TestClient(app).post("/api/v1/inventory/daily/2026-10-15/confirm").status_code == 401
    assert TestClient(app).post(
        "/api/v1/inventory/daily/2026-10-15/confirm-with-changes",
        json={"confirmation_date": "2026-10-15", "changes": []},
    ).status_code == 401
