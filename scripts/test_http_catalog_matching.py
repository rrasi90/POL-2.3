"""HTTP regression coverage for canonical barcode matching."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import psycopg2
from fastapi.testclient import TestClient
from psycopg2.extras import RealDictCursor

from scripts.api.main import app
from scripts.auth_boundary import encode_access_token, hash_token


def _db():
    return psycopg2.connect(
        dbname="pol_test",
        host=os.environ.get("PGHOST", "127.0.0.1"),
        port=int(os.environ.get("POL_PG_PORT") or os.environ.get("PGPORT", "5432")),
        user=os.environ.get("PGUSER", "postgres"),
    )


def _seed_vendor_catalog(cur, suffix: str):
    user_id, org_id, vendor_id = str(uuid4()), str(uuid4()), str(uuid4())
    brand_id, category_id, subcategory_id, product_id = [str(uuid4()) for _ in range(4)]
    session_id = str(uuid4())

    cur.execute(
        "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s,%s,%s,'VENDOR_OWNER')",
        (user_id, f"+9891{uuid4().int % 100000000:08d}", "Barcode Vendor"),
    )
    cur.execute(
        "INSERT INTO organizations (id,name,org_type,status) VALUES (%s,%s,'VENDOR','ACTIVE')",
        (org_id, "Barcode Vendor Org " + suffix),
    )
    cur.execute(
        """
        INSERT INTO organization_memberships
            (id,organization_id,user_id,role,status,is_primary)
        VALUES (%s,%s,%s,'VENDOR_OWNER','ACTIVE',TRUE)
        """,
        (str(uuid4()), org_id, user_id),
    )
    cur.execute(
        """
        INSERT INTO vendors
            (id,user_id,organization_id,business_name,warehouse_address,min_order_value_toman,status)
        VALUES (%s,%s,%s,%s,'Ahvaz',1000000,'ACTIVE')
        """,
        (vendor_id, user_id, org_id, "Barcode Vendor " + suffix),
    )
    cur.execute(
        "INSERT INTO brands (id,name_fa,slug) VALUES (%s,%s,%s)",
        (brand_id, "Barcode Brand " + suffix, "barcode-brand-" + suffix),
    )
    cur.execute(
        "INSERT INTO categories (id,name_fa,slug) VALUES (%s,%s,%s)",
        (category_id, "Barcode Category " + suffix, "barcode-cat-" + suffix),
    )
    cur.execute(
        "INSERT INTO subcategories (id,category_id,name_fa,slug) VALUES (%s,%s,%s,%s)",
        (subcategory_id, category_id, "Barcode Sub " + suffix, "barcode-sub-" + suffix),
    )
    cur.execute(
        """
        INSERT INTO products
            (id,master_sku,canonical_name_fa,brand_id,category_id,subcategory_id,is_active,is_verified)
        VALUES (%s,%s,%s,%s,%s,%s,TRUE,TRUE)
        """,
        (product_id, "BAR-" + suffix, "محصول بارکدی " + suffix, brand_id, category_id, subcategory_id),
    )
    barcode = "626000" + suffix[:6].replace("a", "1").replace("b", "2").replace("c", "3").replace("d", "4").replace("e", "5").replace("f", "6")
    barcode = "".join(ch if ch.isdigit() else "7" for ch in barcode)[:13].ljust(13, "0")
    cur.execute(
        """
        INSERT INTO product_identifiers
            (product_id,vendor_id,identifier_scope,identifier_type,identifier_value,
             packaging_scope,source,confidence_score,is_primary)
        VALUES (%s,NULL,'GLOBAL','EAN13',%s,'UNIT','OPS_VERIFIED',1.00,TRUE)
        """,
        (product_id, barcode),
    )
    access = encode_access_token(user_id, session_id, org_id, "VENDOR_OWNER")
    cur.execute(
        """
        INSERT INTO user_sessions
            (id,user_id,active_organization_id,token_hash,status,expires_at)
        VALUES (%s,%s,%s,%s,'ACTIVE',%s)
        """,
        (
            session_id,
            user_id,
            org_id,
            hash_token(access),
            datetime.now(timezone.utc) + timedelta(hours=1),
        ),
    )
    return {
        "user_id": user_id,
        "org_id": org_id,
        "vendor_id": vendor_id,
        "product_id": product_id,
        "brand_id": brand_id,
        "category_id": category_id,
        "subcategory_id": subcategory_id,
        "session_id": session_id,
        "token": access,
        "barcode": barcode,
    }


def test_exact_barcode_match_uses_canonical_identifier():
    conn = _db()
    client = TestClient(app)
    data = None
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor_catalog(cur, uuid4().hex[:8])
        response = client.get(
            "/api/v1/catalog/barcode/lookup",
            params={"barcode": data["barcode"]},
            headers={"Authorization": "Bearer " + data["token"]},
        )
        assert response.status_code == 200
        body = response.json()["data"]
        assert body["match_type"] == "EXACT"
        assert body["confidence_score"] == 1.0
        assert body["product"]["id"] == data["product_id"]
        assert body["identifier"]["identifier_type"] == "EAN13"
    finally:
        with conn:
            with conn.cursor() as cur:
                if data:
                    cur.execute("DELETE FROM product_identifiers WHERE product_id=%s", (data["product_id"],))
                    cur.execute("DELETE FROM products WHERE id=%s", (data["product_id"],))
                    cur.execute("DELETE FROM subcategories WHERE id=%s", (data["subcategory_id"],))
                    cur.execute("DELETE FROM categories WHERE id=%s", (data["category_id"],))
                    cur.execute("DELETE FROM brands WHERE id=%s", (data["brand_id"],))
                    cur.execute("DELETE FROM user_sessions WHERE user_id=%s", (data["user_id"],))
                    cur.execute("DELETE FROM organization_memberships WHERE user_id=%s", (data["user_id"],))
                    cur.execute("DELETE FROM vendors WHERE id=%s", (data["vendor_id"],))
                    cur.execute("DELETE FROM users WHERE id=%s", (data["user_id"],))
                    cur.execute("DELETE FROM organizations WHERE id=%s", (data["org_id"],))
        conn.close()



def test_unknown_barcode_creates_quarantined_candidate_idempotently():
    conn = _db()
    client = TestClient(app)
    suffix = uuid4().hex[:8]
    data = None
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                data = _seed_vendor_catalog(cur, suffix)
                unknown = "626999" + str(uuid4().int % 1000000000).zfill(9)
                if len(unknown) > 13:
                    unknown = unknown[:13]

        payload = {
            "barcode": unknown,
            "proposed_title": "کالای ناشناخته " + suffix,
            "vendor_sku": "UNKNOWN-" + suffix,
            "packaging_unit": "CARTON",
            "pack_quantity": 12,
            "create_candidate": True,
        }
        first = client.post(
            "/api/v1/products/match-barcode",
            headers={"Authorization": "Bearer " + data["token"]},
            json=payload,
        )
        second = client.post(
            "/api/v1/products/match-barcode",
            headers={"Authorization": "Bearer " + data["token"]},
            json=payload,
        )
        assert first.status_code == 200
        assert second.status_code == 200
        a = first.json()["data"]
        b = second.json()["data"]
        assert a["match_type"] == "NO_MATCH"
        assert a["listing_status"] == "DRAFT_PENDING_CATALOG"
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT target_user_id, target_organization_id, dedupe_key
                FROM outbox_events
                WHERE event_name='product_candidate_created' AND aggregate_id=%s
                """,
                (a["candidate_id"],),
            )
            event = cur.fetchone()
            assert event is not None
            assert str(event["target_user_id"]) == data["user_id"]
            assert str(event["target_organization_id"]) == data["org_id"]
            assert event["dedupe_key"] == "PRODUCT_CANDIDATE_CREATED:" + a["candidate_id"]
        assert b["candidate_id"] == a["candidate_id"]
        assert b["vendor_product_id"] == a["vendor_product_id"]
        assert b["idempotent_replay"] is True

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT status, vendor_id, barcode FROM product_candidates WHERE id=%s",
                (a["candidate_id"],),
            )
            candidate = cur.fetchone()
            assert candidate["status"] == "PENDING_REVIEW"
            assert str(candidate["vendor_id"]) == data["vendor_id"]
            assert candidate["barcode"] == unknown

            cur.execute(
                """
                SELECT product_id, candidate_id, listing_status
                FROM vendor_products
                WHERE id=%s
                """,
                (a["vendor_product_id"],),
            )
            vp = cur.fetchone()
            assert vp["product_id"] is None
            assert str(vp["candidate_id"]) == a["candidate_id"]
            assert vp["listing_status"] == "DRAFT_PENDING_CATALOG"
    finally:
        if data:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM product_candidates WHERE vendor_id=%s", (data["vendor_id"],))
                    cur.execute("DELETE FROM vendor_inventory WHERE vendor_product_id IN (SELECT id FROM vendor_products WHERE vendor_id=%s)", (data["vendor_id"],))
                    cur.execute("DELETE FROM vendor_prices WHERE vendor_product_id IN (SELECT id FROM vendor_products WHERE vendor_id=%s)", (data["vendor_id"],))
                    cur.execute("DELETE FROM vendor_products WHERE vendor_id=%s", (data["vendor_id"],))
                    cur.execute("DELETE FROM product_identifiers WHERE product_id=%s", (data["product_id"],))
                    cur.execute("DELETE FROM products WHERE id=%s", (data["product_id"],))
                    cur.execute("DELETE FROM subcategories WHERE id=%s", (data["subcategory_id"],))
                    cur.execute("DELETE FROM categories WHERE id=%s", (data["category_id"],))
                    cur.execute("DELETE FROM brands WHERE id=%s", (data["brand_id"],))
                    cur.execute("DELETE FROM user_sessions WHERE user_id=%s", (data["user_id"],))
                    cur.execute("DELETE FROM organization_memberships WHERE user_id=%s", (data["user_id"],))
                    cur.execute("DELETE FROM vendors WHERE id=%s", (data["vendor_id"],))
                    cur.execute("DELETE FROM users WHERE id=%s", (data["user_id"],))
                    cur.execute("DELETE FROM organizations WHERE id=%s", (data["org_id"],))
        conn.close()
