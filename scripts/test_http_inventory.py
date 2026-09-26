"""HTTP transport tests for inventory runtime — Stage 17.

Tests inventory read, adjustment with audit logging, freshness/confidence
updates, and cross-vendor inventory comparison. Real auth boundary, real DB.
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


def _seed_inventory(cur, suffix, qty=100, reserved=10):
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
    cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Inv Org', 'VENDOR', 'ACTIVE')", (org_id,))
    cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')",
                (str(uuid4()), org_id, user_id))
    cur.execute("INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman, status) "
                "VALUES (%s, %s, %s, 'Inv Vendor', 'Ahvaz', 1000000, 'ACTIVE')",
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
                "VALUES (%s, 'CARTON', %s, %s, 1, 'FRESH')",
                (vendor_product_id, qty, reserved))
    if reserved:
        # Migration 057 reconciliation invariant: reserved_quantity must equal
        # the sum of ACTIVE inventory_reservations for this vendor product.
        cur.execute("INSERT INTO inventory_reservations (vendor_product_id, quantity, status, expires_at) "
                    "VALUES (%s, %s, 'ACTIVE', now() + interval '1 day')",
                    (vendor_product_id, reserved))

    session_id = _create_session(cur, user_id, org_id)
    token = encode_access_token(user_id, session_id, org_id, "VENDOR_OWNER")
    return {"token": token, "vendor_product_id": vendor_product_id, "product_id": product_id}


def test_inventory_get_returns_details(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_inventory(cur, uuid4().hex[:8])
        response = TestClient(app).get(
            f"/api/v1/catalog/vendors/products/{data['vendor_product_id']}/inventory",
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        inv = body["data"]
        assert inv["physical_quantity"] == 100
        assert inv["reserved_quantity"] == 10
        assert inv["available_quantity"] == 90
        assert inv["freshness_status"] == "FRESH"
    finally:
        conn.close()


def test_inventory_adjust_updates_quantity_and_creates_audit_log(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_inventory(cur, uuid4().hex[:8])
        response = TestClient(app).patch(
            f"/api/v1/catalog/vendors/products/{data['vendor_product_id']}/inventory",
            headers={"Authorization": f"Bearer {data['token']}"},
            json={"new_physical_quantity": 150, "reason": "BARCODE_SCAN"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["old_quantity"] == 100
        assert body["data"]["new_quantity"] == 150
        assert body["data"]["delta"] == 50

        get_resp = TestClient(app).get(
            f"/api/v1/catalog/vendors/products/{data['vendor_product_id']}/inventory",
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert get_resp.json()["data"]["physical_quantity"] == 150

        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM inventory_audit_log WHERE vendor_product_id = %s ORDER BY created_at DESC LIMIT 1",
                    (data["vendor_product_id"],),
                )
                log = cur.fetchone()
                assert log is not None
                assert log["old_quantity"] == 100
                assert log["new_quantity"] == 150
                assert log["source_trigger"] == "BARCODE_SCAN"
    finally:
        conn.close()


def test_inventory_adjust_sets_freshness_to_fresh(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_inventory(cur, uuid4().hex[:8], qty=0, reserved=0)
                cur.execute(
                    "UPDATE vendor_inventory SET freshness_status = 'STALE', inventory_confidence = 'STALE' WHERE vendor_product_id = %s",
                    (data["vendor_product_id"],),
                )
        response = TestClient(app).patch(
            f"/api/v1/catalog/vendors/products/{data['vendor_product_id']}/inventory",
            headers={"Authorization": f"Bearer {data['token']}"},
            json={"new_physical_quantity": 50, "reason": "DAILY_CONFIRMATION"},
        )
        assert response.status_code == 200
        get_resp = TestClient(app).get(
            f"/api/v1/catalog/vendors/products/{data['vendor_product_id']}/inventory",
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        inv = get_resp.json()["data"]
        assert inv["freshness_status"] == "FRESH"
        assert inv["inventory_confidence"] == "CONFIRMED_TODAY"
        assert inv["verification_source"] == "MANUAL"
    finally:
        conn.close()


def test_inventory_adjust_rejects_negative_quantity(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_inventory(cur, uuid4().hex[:8])
        response = TestClient(app).patch(
            f"/api/v1/catalog/vendors/products/{data['vendor_product_id']}/inventory",
            headers={"Authorization": f"Bearer {data['token']}"},
            json={"new_physical_quantity": -1},
        )
        assert response.status_code == 422
    finally:
        conn.close()


def test_inventory_cross_tenant_forbidden(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_inventory(cur, uuid4().hex[:8])
                other_user = str(uuid4())
                other_org = str(uuid4())
                cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Other', 'VENDOR_OWNER')",
                            (other_user, f"+9891{uuid4().int % 100000000:08d}"))
                cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Other', 'VENDOR', 'ACTIVE')", (other_org,))
                cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')",
                            (str(uuid4()), other_org, other_user))
                other_token = encode_access_token(other_user, _create_session(cur, other_user, other_org), other_org, "VENDOR_OWNER")
        response = TestClient(app).get(
            f"/api/v1/catalog/vendors/products/{data['vendor_product_id']}/inventory",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        assert response.status_code == 403
    finally:
        conn.close()


def test_compare_inventory_returns_vendors(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_inventory(cur, uuid4().hex[:8])
        response = TestClient(app).get(
            f"/api/v1/catalog/products/{data['product_id']}/compare-inventory",
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert len(body["data"]) >= 1
        assert body["data"][0]["physical_quantity"] == 100
        assert body["data"][0]["available_quantity"] == 90
    finally:
        conn.close()


def test_inventory_routes_require_auth(api_env):
    vid = uuid4()
    pid = uuid4()
    assert TestClient(app).get(f"/api/v1/catalog/vendors/products/{vid}/inventory").status_code == 401
    assert TestClient(app).patch(
        f"/api/v1/catalog/vendors/products/{vid}/inventory",
        json={"new_physical_quantity": 0},
    ).status_code == 401
    assert TestClient(app).get(f"/api/v1/catalog/products/{pid}/compare-inventory").status_code == 401
