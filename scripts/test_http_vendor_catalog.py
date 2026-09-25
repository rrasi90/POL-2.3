"""HTTP transport tests for vendor catalog management — Stage 15.

Tests vendor-scoped product listing, creation, update with real auth boundary
and real database. Validates tenant isolation (vendor A cannot manage B's products).
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


def _seed_vendor(cur, suffix):
    user_id = str(uuid4())
    org_id = str(uuid4())
    vendor_id = str(uuid4())
    brand_id = str(uuid4())
    category_id = str(uuid4())
    subcategory_id = str(uuid4())
    product_id = str(uuid4())

    cur.execute(
        "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Vendor User', 'VENDOR_OWNER')",
        (user_id, f"+9891{uuid4().int % 100000000:08d}"),
    )
    cur.execute(
        "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Vendor Org', 'VENDOR', 'ACTIVE')",
        (org_id,),
    )
    cur.execute(
        "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')",
        (str(uuid4()), org_id, user_id),
    )
    cur.execute(
        """
        INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman, status)
        VALUES (%s, %s, %s, 'Test Vendor', 'Ahvaz Hub', 1000000, 'ACTIVE')
        """,
        (vendor_id, user_id, org_id),
    )

    cur.execute(
        "INSERT INTO brands (id, name_fa, slug) VALUES (%s, %s, %s)",
        (brand_id, f"Brand {suffix}", f"brand-{suffix}"),
    )
    cur.execute(
        "INSERT INTO categories (id, name_fa, slug) VALUES (%s, %s, %s)",
        (category_id, f"Category {suffix}", f"cat-{suffix}"),
    )
    cur.execute(
        "INSERT INTO subcategories (id, category_id, name_fa, slug) VALUES (%s, %s, %s, %s)",
        (subcategory_id, category_id, f"Sub {suffix}", f"sub-{suffix}"),
    )
    cur.execute(
        """
        INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        """,
        (product_id, f"POL-PRD-{suffix}", f"Product {suffix}", brand_id, category_id, subcategory_id),
    )

    session_id = _create_session(cur, user_id, org_id)
    token = encode_access_token(user_id, session_id, org_id, "VENDOR_OWNER")

    return {
        "token": token,
        "user_id": user_id,
        "org_id": org_id,
        "vendor_id": vendor_id,
        "product_id": product_id,
    }


def _seed_second_vendor(cur, suffix):
    user_id = str(uuid4())
    org_id = str(uuid4())
    vendor_id = str(uuid4())
    cur.execute(
        "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Other Vendor', 'VENDOR_OWNER')",
        (user_id, f"+9891{uuid4().int % 100000000:08d}"),
    )
    cur.execute(
        "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Other Vendor Org', 'VENDOR', 'ACTIVE')",
        (org_id,),
    )
    cur.execute(
        "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')",
        (str(uuid4()), org_id, user_id),
    )
    cur.execute(
        """
        INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman, status)
        VALUES (%s, %s, %s, 'Other Vendor', 'Tehran Hub', 1000000, 'ACTIVE')
        """,
        (vendor_id, user_id, org_id),
    )
    session_id = _create_session(cur, user_id, org_id)
    token = encode_access_token(user_id, session_id, org_id, "VENDOR_OWNER")
    return {"token": token, "vendor_id": vendor_id, "org_id": org_id}


def test_vendor_list_products_returns_own_products(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor(cur, uuid4().hex[:8])
                cur.execute(
                    """
                    INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity, sales_unit, is_active, listing_status)
                    VALUES (gen_random_uuid(), %s, %s, %s, 'CARTON', 4, 'CARTON', TRUE, 'ACTIVE')
                    RETURNING id
                    """,
                    (data["vendor_id"], data["product_id"], f"VP-{uuid4().hex[:6]}"),
                )
                vp_id = cur.fetchone()["id"]
                cur.execute(
                    "INSERT INTO vendor_inventory (vendor_product_id, inventory_unit, physical_quantity, reserved_quantity, moq, freshness_status) VALUES (%s, 'CARTON', 50, 0, 1, 'FRESH')",
                    (vp_id,),
                )
        response = TestClient(app).get(
            "/api/v1/catalog/vendors/products",
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert len(body["data"]) >= 1
    finally:
        conn.close()


def test_vendor_create_product_with_existing_canonical(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor(cur, uuid4().hex[:8])
        response = TestClient(app).post(
            "/api/v1/catalog/vendors/products",
            headers={"Authorization": f"Bearer {data['token']}"},
            json={
                "vendor_sku": f"NEW-VP-{uuid4().hex[:6]}",
                "product_id": str(data["product_id"]),
                "packaging_unit": "CARTON",
                "pack_quantity": 6,
                "sales_unit": "CARTON",
                "initial_price_toman": 750000,
                "moq": 2,
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["listing_status"] == "ACTIVE"
        assert body["data"]["pack_quantity"] == 6
    finally:
        conn.close()


def test_vendor_create_product_draft_pending_catalog(api_env):
    conn = _db()
    try:
        candidate_id = str(uuid4())
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor(cur, uuid4().hex[:8])
                cur.execute(
                    """
                    INSERT INTO product_candidates (id, vendor_id, proposed_title, status)
                    VALUES (%s, %s, 'Draft Candidate', 'PENDING_REVIEW')
                    """,
                    (candidate_id, data["vendor_id"]),
                )
        response = TestClient(app).post(
            "/api/v1/catalog/vendors/products",
            headers={"Authorization": f"Bearer {data['token']}"},
            json={
                "vendor_sku": f"DRAFT-VP-{uuid4().hex[:6]}",
                "candidate_id": candidate_id,
                "packaging_unit": "CARTON",
                "pack_quantity": 12,
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["listing_status"] == "DRAFT_PENDING_CATALOG"
    finally:
        conn.close()


def test_vendor_create_product_duplicate_sku_rejected(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor(cur, uuid4().hex[:8])
                sku = f"DUP-{uuid4().hex[:6]}"
                cur.execute(
                    """
                    INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity, sales_unit, is_active, listing_status)
                    VALUES (gen_random_uuid(), %s, %s, %s, 'CARTON', 4, 'CARTON', TRUE, 'ACTIVE')
                    """,
                    (data["vendor_id"], data["product_id"], sku),
                )
        response = TestClient(app).post(
            "/api/v1/catalog/vendors/products",
            headers={"Authorization": f"Bearer {data['token']}"},
            json={"vendor_sku": sku, "product_id": str(data["product_id"])},
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "INVALID_REQUEST"
    finally:
        conn.close()


def test_vendor_create_product_requires_product_or_candidate(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor(cur, uuid4().hex[:8])
        response = TestClient(app).post(
            "/api/v1/catalog/vendors/products",
            headers={"Authorization": f"Bearer {data['token']}"},
            json={"vendor_sku": f"NO-TARGET-{uuid4().hex[:6]}"},
        )
        assert response.status_code == 422
    finally:
        conn.close()


def test_vendor_update_product_packaging_and_moq(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor(cur, uuid4().hex[:8])
                cur.execute(
                    """
                    INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity, sales_unit, is_active, listing_status)
                    VALUES (gen_random_uuid(), %s, %s, %s, 'CARTON', 12, 'CARTON', TRUE, 'ACTIVE')
                    RETURNING id
                    """,
                    (data["vendor_id"], data["product_id"], f"UP-{uuid4().hex[:6]}"),
                )
                vp_id = cur.fetchone()["id"]
                cur.execute(
                    "INSERT INTO vendor_inventory (vendor_product_id, inventory_unit, physical_quantity, reserved_quantity, moq, freshness_status) VALUES (%s, 'CARTON', 100, 0, 1, 'FRESH')",
                    (vp_id,),
                )
        response = TestClient(app).patch(
            f"/api/v1/catalog/vendors/products/{vp_id}",
            headers={"Authorization": f"Bearer {data['token']}"},
            json={"pack_quantity": 6, "moq": 3},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
    finally:
        conn.close()


def test_vendor_update_other_vendors_product_is_forbidden(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor(cur, uuid4().hex[:8])
                other = _seed_second_vendor(cur, uuid4().hex[:8])
                cur.execute(
                    """
                    INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity, sales_unit, is_active, listing_status)
                    VALUES (gen_random_uuid(), %s, %s, %s, 'CARTON', 12, 'CARTON', TRUE, 'ACTIVE')
                    RETURNING id
                    """,
                    (data["vendor_id"], data["product_id"], f"OWNER-{uuid4().hex[:6]}"),
                )
                vp_id = cur.fetchone()["id"]
                cur.execute(
                    "INSERT INTO vendor_inventory (vendor_product_id, inventory_unit, physical_quantity, reserved_quantity, moq, freshness_status) VALUES (%s, 'CARTON', 100, 0, 1, 'FRESH')",
                    (vp_id,),
                )
        response = TestClient(app).patch(
            f"/api/v1/catalog/vendors/products/{vp_id}",
            headers={"Authorization": f"Bearer {other['token']}"},
            json={"pack_quantity": 99},
        )
        assert response.status_code == 403
    finally:
        conn.close()


def test_vendor_catalog_routes_require_auth(api_env):
    response = TestClient(app).get("/api/v1/catalog/vendors/products")
    assert response.status_code == 401

    response = TestClient(app).post(
        "/api/v1/catalog/vendors/products",
        json={"vendor_sku": "test"},
    )
    assert response.status_code == 401

    response = TestClient(app).patch(
        f"/api/v1/catalog/vendors/products/{uuid4()}",
        json={"pack_quantity": 1},
    )
    assert response.status_code == 401

def test_public_products_search_contract(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor(cur, uuid4().hex[:8])
                cur.execute(
                    "INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity, sales_unit, is_active, listing_status) VALUES (gen_random_uuid(), %s, %s, %s, 'CARTON', 4, 'CARTON', TRUE, 'ACTIVE') RETURNING id",
                    (data['vendor_id'], data['product_id'], f"SEARCH-{uuid4().hex[:6]}"),
                )
                vp_id = cur.fetchone()['id']
                cur.execute("INSERT INTO vendor_inventory (vendor_product_id, inventory_unit, physical_quantity, reserved_quantity, moq, freshness_status) VALUES (%s, 'CARTON', 50, 0, 1, 'FRESH')", (vp_id,))
                cur.execute("INSERT INTO vendor_prices (vendor_product_id, price_toman, is_current) VALUES (%s, 380000, TRUE)", (vp_id,))
        response = TestClient(app).get('/api/v1/products/search?q=Product&limit=20')
        assert response.status_code == 200
        body = response.json()
        assert body['success'] is True
        assert body['data']['pagination']['page'] == 1
        assert body['data']['products']
        item = body['data']['products'][0]
        assert {'id','master_sku','canonical_name_fa','brand_name','pack_unit','pack_quantity','lowest_unit_price_toman','available_vendors_count'} <= set(item)
    finally:
        conn.close()

def test_vendor_barcode_match_and_unknown_candidate_flow(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor(cur, uuid4().hex[:8])
                cur.execute("INSERT INTO product_identifiers (product_id, identifier_type, identifier_value, identifier_scope, packaging_scope) VALUES (%s, 'EAN13', '6260123456789', 'GLOBAL', 'UNIT')", (data['product_id'],))
                cur.execute("INSERT INTO product_identifiers (product_id, identifier_type, identifier_value, identifier_scope, packaging_scope) VALUES (%s, 'EAN13', '6260123456790', 'GLOBAL', 'UNIT')", (data['product_id'],))
        client = TestClient(app)
        response = client.post('/api/v1/products/match-barcode', headers={'Authorization': f"Bearer {data['token']}"}, json={'raw_barcode': '6260123456789', 'scan_source': 'CAMERA_CONTINUOUS_SCAN'})
        assert response.status_code == 200
        assert response.json()['data']['match_status'] == 'EXACT'
        assert response.json()['data']['product']['master_sku'] == f"POL-PRD-{data['product_id'][:0]}" or response.json()['data']['product']['id'] == data['product_id']
        response = client.post('/api/v1/products/match-barcode', headers={'Authorization': f"Bearer {data['token']}"}, json={'raw_barcode': '6299999999999', 'scan_source': 'CAMERA_CONTINUOUS_SCAN'})
        assert response.status_code == 200
        assert response.json()['data']['match_status'] == 'NO_MATCH'
        candidate = client.post('/api/v1/product-candidates', headers={'Authorization': f"Bearer {data['token']}"}, json={'proposed_title':'Unknown Product','barcode':'6299999999999','vendor_sku':f"CAND-{uuid4().hex[:6]}"})
        assert candidate.status_code == 201
        assert candidate.json()['data']['status'] == 'PENDING_REVIEW'
    finally:
        conn.close()