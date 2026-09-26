"""HTTP transport tests for catalog read routes — Stage 14.

Tests catalog search, categories, product detail, and vendor offers
with real database and real auth boundary (no dependency overrides).
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


def _seed_catalog(cur, suffix):
    user_id = str(uuid4())
    org_id = str(uuid4())
    brand_id = str(uuid4())
    category_id = str(uuid4())
    subcategory_id = str(uuid4())
    product_id = str(uuid4())
    vendor_id = str(uuid4())
    vendor_user = str(uuid4())
    vendor_product_id = str(uuid4())

    cur.execute(
        "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Catalog User', 'RETAILER_OWNER')",
        (user_id, f"+9891{uuid4().int % 100000000:08d}"),
    )
    cur.execute(
        "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Catalog Org', 'RETAILER', 'ACTIVE')",
        (org_id,),
    )
    cur.execute(
        "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'RETAILER_OWNER', 'ACTIVE')",
        (str(uuid4()), org_id, user_id),
    )

    cur.execute(
        "INSERT INTO brands (id, name_fa, slug) VALUES (%s, %s, %s)",
        (brand_id, f"Test Brand {suffix}", f"test-brand-{suffix}"),
    )
    cur.execute(
        "INSERT INTO categories (id, name_fa, slug) VALUES (%s, %s, %s)",
        (category_id, f"Test Category {suffix}", f"test-cat-{suffix}"),
    )
    cur.execute(
        "INSERT INTO subcategories (id, category_id, name_fa, slug) VALUES (%s, %s, %s, %s)",
        (subcategory_id, category_id, f"Test Sub {suffix}", f"test-sub-{suffix}"),
    )
    cur.execute(
        """
        INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        """,
        (product_id, f"POL-PRD-{suffix}", f"Test Product {suffix}", brand_id, category_id, subcategory_id),
    )

    cur.execute(
        "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Vendor User', 'VENDOR_OWNER')",
        (vendor_user, f"+9891{uuid4().int % 100000000:08d}"),
    )
    vendor_org = str(uuid4())
    cur.execute(
        "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Vendor Org', 'VENDOR', 'ACTIVE')",
        (vendor_org,),
    )
    cur.execute(
        "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')",
        (str(uuid4()), vendor_org, vendor_user),
    )
    cur.execute(
        """
        INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman, status)
        VALUES (%s, %s, %s, 'Test Vendor', 'Ahvaz Hub', 1000000, 'ACTIVE')
        """,
        (vendor_id, vendor_user, vendor_org),
    )
    cur.execute(
        """
        INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity, sales_unit, is_active, listing_status)
        VALUES (%s, %s, %s, %s, 'CARTON', 4, 'CARTON', TRUE, 'ACTIVE')
        """,
        (vendor_product_id, vendor_id, product_id, f"VP-{suffix}"),
    )
    cur.execute(
        """
        INSERT INTO vendor_inventory (vendor_product_id, inventory_unit, physical_quantity, reserved_quantity, moq, freshness_status)
        VALUES (%s, 'CARTON', 100, 0, 1, 'FRESH')
        """,
        (vendor_product_id,),
    )
    cur.execute(
        "INSERT INTO vendor_prices (vendor_product_id, price_toman, is_current) VALUES (%s, 500000, TRUE)",
        (vendor_product_id,),
    )

    session_id = _create_session(cur, user_id, org_id)
    token = encode_access_token(user_id, session_id, org_id, "RETAILER_OWNER")

    return {
        "token": token,
        "product_id": product_id,
        "brand_id": brand_id,
        "category_id": category_id,
        "subcategory_id": subcategory_id,
        "vendor_product_id": vendor_product_id,
    }


def test_catalog_search_returns_results(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_catalog(cur, uuid4().hex[:8])
        response = TestClient(app).get(
            "/api/v1/catalog/search",
            params={"q": "Test Product"},
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert len(body["data"]["items"]) >= 1
        assert body["data"]["query"] == "Test Product"
    finally:
        conn.close()


def test_catalog_search_filters_by_category(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_catalog(cur, uuid4().hex[:8])
        other_cat = str(uuid4())
        response = TestClient(app).get(
            "/api/v1/catalog/search",
            params={"q": "Test Product", "category_id": other_cat},
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert response.status_code == 200
        assert len(response.json()["data"]["items"]) == 0
    finally:
        conn.close()


def test_catalog_search_empty_query_rejected(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_catalog(cur, uuid4().hex[:8])
        response = TestClient(app).get(
            "/api/v1/catalog/search",
            params={"q": ""},
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert response.status_code == 422
    finally:
        conn.close()


def test_catalog_categories_returns_tree(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_catalog(cur, uuid4().hex[:8])
        response = TestClient(app).get(
            "/api/v1/catalog/categories",
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        cats = body["data"]
        assert len(cats) >= 1
        cat = next(c for c in cats if str(c["id"]) == data["category_id"])
        assert cat["name_fa"] is not None
        assert isinstance(cat["subcategories"], list)
    finally:
        conn.close()


def test_catalog_product_detail_returns_identifiers_and_media(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_catalog(cur, uuid4().hex[:8])
        response = TestClient(app).get(
            f"/api/v1/catalog/products/{data['product_id']}",
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        product = body["data"]
        assert product["master_sku"] is not None
        assert product["brand_name"] is not None
        assert product["category_name"] is not None
        assert "identifiers" in product
        assert "media" in product
    finally:
        conn.close()


def test_catalog_product_media_requires_ready_and_approved_public_governance(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_catalog(cur, uuid4().hex[:8])
                approved_media = str(uuid4())
                pending_media = str(uuid4())
                private_media = str(uuid4())
                for media_id, status, approval in (
                    (approved_media, "READY", "APPROVED"),
                    (pending_media, "READY", "PENDING"),
                    (private_media, "READY", "PRIVATE_REFERENCE"),
                ):
                    cur.execute(
                        """INSERT INTO media_assets
                           (id, storage_bucket, storage_key, bucket_name, object_key, mime_type, file_size_bytes, checksum_sha256, status, provenance, uploaded_by_user_id)
                           VALUES (%s, 'pol-media', %s, 'pol-media', %s, 'image/webp', 1024, %s, %s, 'POL_OWNED', NULL)""",
                        (media_id, f"g317/{media_id}", f"g317/{media_id}", "a" * 64, status),
                    )
                    cur.execute(
                        """INSERT INTO product_media
                           (id, product_id, media_asset_id, media_type, source_provenance, approval_status, approved_at)
                           VALUES (%s, %s, %s, 'PRIMARY_IMAGE', 'POL_OWNED', %s, CASE WHEN %s = 'APPROVED' THEN now() ELSE NULL END)""",
                        (str(uuid4()), data["product_id"], media_id, approval, approval),
                    )
        response = TestClient(app).get(
            f"/api/v1/catalog/products/{data['product_id']}",
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert response.status_code == 200
        media_ids = {item["id"] for item in response.json()["data"]["media"]}
        assert approved_media in media_ids
        assert pending_media not in media_ids
        assert private_media not in media_ids
    finally:
        conn.close()

def test_catalog_product_detail_not_found(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_catalog(cur, uuid4().hex[:8])
        response = TestClient(app).get(
            f"/api/v1/catalog/products/{uuid4()}",
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert response.status_code == 404
    finally:
        conn.close()


def test_catalog_product_vendors_returns_offers(api_env):
    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_catalog(cur, uuid4().hex[:8])
        response = TestClient(app).get(
            f"/api/v1/catalog/products/{data['product_id']}/vendors",
            headers={"Authorization": f"Bearer {data['token']}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        vendors = body["data"]
        assert len(vendors) >= 1
        assert vendors[0]["business_name"] is not None
        assert vendors[0]["price_toman"] is not None
    finally:
        conn.close()


def test_catalog_search_requires_auth(api_env):
    response = TestClient(app).get("/api/v1/catalog/search", params={"q": "test"})
    assert response.status_code == 401


def test_catalog_categories_requires_auth(api_env):
    response = TestClient(app).get("/api/v1/catalog/categories")
    assert response.status_code == 401


def test_catalog_product_detail_requires_auth(api_env):
    response = TestClient(app).get(f"/api/v1/catalog/products/{uuid4()}")
    assert response.status_code == 401


def test_catalog_product_vendors_requires_auth(api_env):
    response = TestClient(app).get(f"/api/v1/catalog/products/{uuid4()}/vendors")
    assert response.status_code == 401


def test_public_categories_route_contract(api_env):
    response = TestClient(app).get("/api/v1/categories")
    assert response.status_code == 200
    assert response.json()["success"] is True

