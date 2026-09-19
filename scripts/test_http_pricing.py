"""HTTP transport tests for pricing runtime — Stage 16.

Tests price history, current price, price setting with temporal rotation,
and cross-vendor price comparison. Real auth boundary, real database.
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


def _seed_vendor_with_product(cur, suffix):
    user_id = str(uuid4())
    org_id = str(uuid4())
    vendor_id = str(uuid4())
    brand_id = str(uuid4())
    category_id = str(uuid4())
    subcategory_id = str(uuid4())
    product_id = str(uuid4())
    vendor_product_id = str(uuid4())

    cur.execute(
        "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Vendor', 'VENDOR_OWNER')",
        (user_id, f"+9891{uuid4().int % 100000000:08d}"),
    )
    cur.execute(
        "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Price Org', 'VENDOR', 'ACTIVE')",
        (org_id,),
    )
    cur.execute(
        "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')",
        (str(uuid4()), org_id, user_id),
    )
    cur.execute(
        "INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman, status) "
        "VALUES (%s, %s, %s, 'Price Vendor', 'Ahvaz', 1000000, 'ACTIVE')",
        (vendor_id, user_id, org_id),
    )
    cur.execute("INSERT INTO brands (id, name_fa, slug) VALUES (%s, %s, %s)", (brand_id, f"B{suffix}", f"b-{suffix}"))
    cur.execute("INSERT INTO categories (id, name_fa, slug) VALUES (%s, %s, %s)", (category_id, f"C{suffix}", f"c-{suffix}"))
    cur.execute("INSERT INTO subcategories (id, category_id, name_fa, slug) VALUES (%s, %s, %s, %s)",
                (subcategory_id, category_id, f"S{suffix}", f"s-{suffix}"))
    cur.execute(
        "INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id, is_active) "
        "VALUES (%s, %s, %s, %s, %s, %s, TRUE)",
        (product_id, f"POL-{suffix}", f"P{suffix}", brand_id, category_id, subcategory_id),
    )
    cur.execute(
        "INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity, sales_unit, is_active, listing_status) "
        "VALUES (%s, %s, %s, %s, 'CARTON', 4, 'CARTON', TRUE, 'ACTIVE')",
        (vendor_product_id, vendor_id, product_id, f"VP-{suffix}"),
    )
    cur.execute(
        "INSERT INTO vendor_inventory (vendor_product_id, inventory_unit, physical_quantity, reserved_quantity, moq, freshness_status) "
        "VALUES (%s, 'CARTON', 100, 0, 1, 'FRESH')",
        (vendor_product_id,),
    )
    cur.execute(
        "INSERT INTO vendor_prices (vendor_product_id, price_toman, is_current) VALUES (%s, 500000, TRUE)",
        (vendor_product_id,),
    )

    session_id = _create_session(cur, user_id, org_id)
    token = encode_access_token(user_id, session_id, org_id, "VENDOR_OWNER")
    return {
        "token": token, "vendor_product_id": vendor_product_id,
        "product_id": product_id, "org_id": org_id,
    }


def test_price_history_returns_records(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor_with_product(cur, uuid4().hex[:8])
        response = TestClient(app).get(
            f"/api/v1/catalog/vendors/products/{data['vendor_product_id']}/prices",
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert len(body["data"]) >= 1
        assert body["data"][0]["is_current"] is True
    finally:
        conn.close()


def test_price_current_returns_active_price(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor_with_product(cur, uuid4().hex[:8])
        response = TestClient(app).get(
            f"/api/v1/catalog/vendors/products/{data['vendor_product_id']}/prices/current",
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["price_toman"] == 500000
        assert body["data"]["is_current"] is True
    finally:
        conn.close()


def test_price_set_rotates_old_price(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor_with_product(cur, uuid4().hex[:8])
        response = TestClient(app).post(
            f"/api/v1/catalog/vendors/products/{data['vendor_product_id']}/prices",
            headers={"Authorization": f"Bearer {data['token']}"},
            json={"price_toman": 750000},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["price_toman"] == 750000
        assert body["data"]["is_current"] is True

        history_resp = TestClient(app).get(
            f"/api/v1/catalog/vendors/products/{data['vendor_product_id']}/prices",
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        prices = history_resp.json()["data"]
        assert len(prices) >= 2
        assert prices[0]["price_toman"] == 750000
        assert prices[0]["is_current"] is True
        assert prices[1]["is_current"] is False
    finally:
        conn.close()


def test_price_set_rejects_zero_price(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor_with_product(cur, uuid4().hex[:8])
        response = TestClient(app).post(
            f"/api/v1/catalog/vendors/products/{data['vendor_product_id']}/prices",
            headers={"Authorization": f"Bearer {data['token']}"},
            json={"price_toman": 0},
        )
        assert response.status_code == 422
    finally:
        conn.close()


def test_price_set_rejects_negative_price(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor_with_product(cur, uuid4().hex[:8])
        response = TestClient(app).post(
            f"/api/v1/catalog/vendors/products/{data['vendor_product_id']}/prices",
            headers={"Authorization": f"Bearer {data['token']}"},
            json={"price_toman": -100},
        )
        assert response.status_code == 422
    finally:
        conn.close()


def test_price_cross_tenant_access_forbidden(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor_with_product(cur, uuid4().hex[:8])
                other_user = str(uuid4())
                other_org = str(uuid4())
                cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Other', 'VENDOR_OWNER')",
                            (other_user, f"+9891{uuid4().int % 100000000:08d}"))
                cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Other', 'VENDOR', 'ACTIVE')", (other_org,))
                cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')",
                            (str(uuid4()), other_org, other_user))
                other_token = encode_access_token(other_user, _create_session(cur, other_user, other_org), other_org, "VENDOR_OWNER")
        response = TestClient(app).get(
            f"/api/v1/catalog/vendors/products/{data['vendor_product_id']}/prices",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        assert response.status_code == 403
    finally:
        conn.close()


def test_price_set_cross_tenant_forbidden(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor_with_product(cur, uuid4().hex[:8])
                other_user = str(uuid4())
                other_org = str(uuid4())
                cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Other', 'VENDOR_OWNER')",
                            (other_user, f"+9891{uuid4().int % 100000000:08d}"))
                cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Other', 'VENDOR', 'ACTIVE')", (other_org,))
                cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')",
                            (str(uuid4()), other_org, other_user))
                other_token = encode_access_token(other_user, _create_session(cur, other_user, other_org), other_org, "VENDOR_OWNER")
        response = TestClient(app).post(
            f"/api/v1/catalog/vendors/products/{data['vendor_product_id']}/prices",
            headers={"Authorization": f"Bearer {other_token}"},
            json={"price_toman": 999},
        )
        assert response.status_code == 403
    finally:
        conn.close()


def test_compare_prices_returns_vendors_sorted(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor_with_product(cur, uuid4().hex[:8])
        response = TestClient(app).get(
            f"/api/v1/catalog/products/{data['product_id']}/compare-prices",
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert len(body["data"]) >= 1
        assert body["data"][0]["price_toman"] == 500000
    finally:
        conn.close()


def test_pricing_routes_require_auth(api_env):
    vid = uuid4()
    pid = uuid4()
    for path in [
        f"/api/v1/catalog/vendors/products/{vid}/prices",
        f"/api/v1/catalog/vendors/products/{vid}/prices/current",
        f"/api/v1/catalog/products/{pid}/compare-prices",
    ]:
        assert TestClient(app).get(path).status_code == 401
    assert TestClient(app).post(
        f"/api/v1/catalog/vendors/products/{vid}/prices",
        json={"price_toman": 100},
    ).status_code == 401
