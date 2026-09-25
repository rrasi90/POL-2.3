"""HTTP tests for Returns/RMA and Disputes -- Stage 30.

Tests return requests, transitions, dispute open, access control.
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


def _seed_delivered_order(suffix):
    """Seed a delivered order with retailer, vendor, products, order items, settlement."""
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            ru = str(uuid4()); ro = str(uuid4()); ri = str(uuid4())
            vu = str(uuid4()); vo = str(uuid4()); vi = str(uuid4())
            bi = str(uuid4()); pi = str(uuid4()); ogi = str(uuid4())
            oi = str(uuid4()); oii = str(uuid4()); si = str(uuid4())
            brand_id = str(uuid4()); cat_id = str(uuid4()); subcat_id = str(uuid4())
            prod_id = str(uuid4()); vpid = str(uuid4())

            cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'R', 'RETAILER_OWNER')",
                        (ru, f"+9891{uuid4().int % 100000000:08d}"))
            cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'RO', 'RETAILER', 'ACTIVE')", (ro,))
            cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'RETAILER_OWNER', 'ACTIVE')",
                        (str(uuid4()), ro, ru))
            cur.execute("INSERT INTO retailers (id, user_id, organization_id, store_name, city, neighborhood, address) VALUES (%s, %s, %s, 'S', 'Ahvaz', 'N', 'A')",
                        (ri, ru, ro))
            cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'V', 'VENDOR_OWNER')",
                        (vu, f"+9891{uuid4().int % 100000000:08d}"))
            cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'VO', 'VENDOR', 'ACTIVE')", (vo,))
            cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')",
                        (str(uuid4()), vo, vu))
            cur.execute("INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman, status) "
                        "VALUES (%s, %s, %s, 'V', 'Ahvaz', 1000000, 'ACTIVE')", (vi, vu, vo))

            cur.execute("INSERT INTO brands (id, name_fa, slug) VALUES (%s, %s, %s)",
                        (brand_id, f"B{suffix}", f"b-{suffix}"))
            cur.execute("INSERT INTO categories (id, name_fa, slug) VALUES (%s, %s, %s)",
                        (cat_id, f"C{suffix}", f"c-{suffix}"))
            cur.execute("INSERT INTO subcategories (id, category_id, name_fa, slug) VALUES (%s, %s, %s, %s)",
                        (subcat_id, cat_id, f"S{suffix}", f"s-{suffix}"))
            cur.execute(
                "INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id, is_active) "
                "VALUES (%s, %s, %s, %s, %s, %s, TRUE)",
                (prod_id, f"SKU-{suffix}", f"P{suffix}", brand_id, cat_id, subcat_id),
            )
            cur.execute(
                "INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity, sales_unit, is_active, listing_status) "
                "VALUES (%s, %s, %s, %s, 'CARTON', 4, 'CARTON', TRUE, 'ACTIVE')",
                (vpid, vi, prod_id, f"VP-{suffix}"),
            )

            cur.execute("INSERT INTO baskets (id, retailer_id, status, version) VALUES (%s, %s, 'OPEN', 1)", (bi, ri))
            cur.execute("INSERT INTO allocation_plans (id, basket_id, basket_version, status, strategy, vendor_count, total_estimated_toman, expires_at) "
                        "VALUES (%s, %s, 1, 'CONFIRMED', 'SINGLE_VENDOR', 1, 5000000, now() + interval '15 minutes')", (pi, bi))
            cur.execute("INSERT INTO order_groups (id, basket_id, retailer_id, checkout_idempotency_key, total_amount_toman, order_count, group_status) "
                        "VALUES (%s, %s, %s, %s, 5000000, 1, 'ACTIVE')", (ogi, bi, ri, str(uuid4())))
            cur.execute("INSERT INTO orders (id, order_number, order_group_id, allocation_plan_id, retailer_id, vendor_id, order_status, total_amount_toman, created_at, updated_at) "
                        "VALUES (%s, %s, %s, %s, %s, %s, 'DELIVERED', 5000000, now(), now())",
                        (oi, f"ORD-{suffix}", ogi, pi, ri, vi))
            cur.execute(
                "INSERT INTO order_items (id, order_id, product_id, vendor_product_id, "
                "product_name_snapshot, brand_name_snapshot, vendor_sku_snapshot, "
                "packaging_unit_snapshot, pack_quantity_snapshot, ordered_quantity, delivered_quantity, "
                "unit_price_toman, total_line_amount_toman, fulfillment_status) "
                "VALUES (%s, %s, %s, %s, 'Product', 'Brand', 'VS', 'CARTON', 4, 10, 10, 500000, 5000000, 'PENDING')",
                (oii, oi, prod_id, vpid),
            )
            cur.execute(
                "INSERT INTO deliveries (id, order_id, vendor_id, carrier_type, carrier_name, delivery_status, delivered_at) VALUES (%s, %s, %s, 'CLUSTER_LOGISTICS', 'Test Carrier', 'DELIVERED', now())",
                (str(uuid4()), oi, vi),
            )
            cur.execute(
                "INSERT INTO settlements (id, order_id, vendor_id, gross_amount_toman, commission_rate, commission_amount_toman, net_vendor_amount_toman, status) "
                "VALUES (%s, %s, %s, 5000000, 0, 0, 5000000, 'CALCULATED')",
                (si, oi, vi),
            )

            rs = _create_session(cur, ru, ro)
            vs = _create_session(cur, vu, vo)

        conn.commit()
        rt = encode_access_token(ru, rs, ro, "RETAILER_OWNER")
        vt = encode_access_token(vu, vs, vo, "VENDOR_OWNER")
        return {"oi": oi, "oii": oii, "si": si, "r_token": rt, "v_token": vt,
                "ru": ru, "ro": ro, "vi": vi, "vo": vo, "ri": ri}
    finally:
        conn.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app, raise_server_exceptions=False)


class TestReturnRequest:
    def test_retailer_can_create_return(self, client):
        data = _seed_delivered_order(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/returns",
            headers={
                "Authorization": f"Bearer {data['r_token']}",
                "Idempotency-Key": str(uuid4()),
            },
            json={
                "items": [{"order_item_id": data["oii"], "quantity": 2, "reason_code": "DAMAGED"}],
                "reason": "2 cartons arrived crushed",
                "idempotency_key": str(uuid4()),
                "claimed_refund_amount_toman": 1000000,
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["status"] == "RETURN_REQUESTED"
        assert body["data"]["reason"] == "2 cartons arrived crushed"

    def test_vendor_cannot_create_return(self, client):
        data = _seed_delivered_order(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/returns",
            headers={
                "Authorization": f"Bearer {data['v_token']}",
                "Idempotency-Key": str(uuid4()),
            },
            json={
                "items": [{"order_item_id": data["oii"], "quantity": 1, "reason_code": "OTHER"}],
                "reason": "Test",
                "idempotency_key": str(uuid4()),
                "claimed_refund_amount_toman": 100000,
            },
        )
        assert resp.status_code in (403, 422)

    def test_unauthenticated_cannot_create_return(self, client):
        data = _seed_delivered_order(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/returns",
            json={
                "items": [{"order_item_id": data["oii"], "quantity": 1, "reason_code": "OTHER"}],
                "reason": "Test",
                "idempotency_key": str(uuid4()),
                "claimed_refund_amount_toman": 100000,
            },
        )
        assert resp.status_code == 401


class TestReturnTransition:
    def test_vendor_can_approve_return(self, client):
        data = _seed_delivered_order(uuid4().hex[:8])
        create_resp = client.post(
            f"/api/v1/orders/{data['oi']}/returns",
            headers={
                "Authorization": f"Bearer {data['r_token']}",
                "Idempotency-Key": str(uuid4()),
            },
            json={
                "items": [{"order_item_id": data["oii"], "quantity": 2, "reason_code": "DAMAGED"}],
                "reason": "Damaged goods",
                "idempotency_key": str(uuid4()),
                "claimed_refund_amount_toman": 1000000,
            },
        )
        return_id = create_resp.json()["data"]["id"]
        resp = client.patch(
            f"/api/v1/returns/{return_id}",
            headers={"Authorization": f"Bearer {data['v_token']}"},
            json={"target_status": "APPROVED"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "APPROVED"

    def test_unauthenticated_cannot_transition_return(self, client):
        data = _seed_delivered_order(uuid4().hex[:8])
        create_resp = client.post(
            f"/api/v1/orders/{data['oi']}/returns",
            headers={
                "Authorization": f"Bearer {data['r_token']}",
                "Idempotency-Key": str(uuid4()),
            },
            json={
                "items": [{"order_item_id": data["oii"], "quantity": 1, "reason_code": "OTHER"}],
                "reason": "Test",
                "idempotency_key": str(uuid4()),
                "claimed_refund_amount_toman": 100000,
            },
        )
        return_id = create_resp.json()["data"]["id"]
        resp = client.patch(
            f"/api/v1/returns/{return_id}",
            json={"target_status": "APPROVED"},
        )
        assert resp.status_code == 401


class TestReturnQuery:
    def test_list_returns_for_order(self, client):
        data = _seed_delivered_order(uuid4().hex[:8])
        client.post(
            f"/api/v1/orders/{data['oi']}/returns",
            headers={
                "Authorization": f"Bearer {data['r_token']}",
                "Idempotency-Key": str(uuid4()),
            },
            json={
                "items": [{"order_item_id": data["oii"], "quantity": 1, "reason_code": "SHORTAGE"}],
                "reason": "Short delivery",
                "idempotency_key": str(uuid4()),
                "claimed_refund_amount_toman": 500000,
            },
        )
        resp = client.get(
            f"/api/v1/orders/{data['oi']}/returns",
            headers={"Authorization": f"Bearer {data['r_token']}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["count"] >= 1

    def test_get_single_return(self, client):
        data = _seed_delivered_order(uuid4().hex[:8])
        create_resp = client.post(
            f"/api/v1/orders/{data['oi']}/returns",
            headers={
                "Authorization": f"Bearer {data['r_token']}",
                "Idempotency-Key": str(uuid4()),
            },
            json={
                "items": [{"order_item_id": data["oii"], "quantity": 1, "reason_code": "QUALITY"}],
                "reason": "Quality issue",
                "idempotency_key": str(uuid4()),
                "claimed_refund_amount_toman": 500000,
            },
        )
        return_id = create_resp.json()["data"]["id"]
        resp = client.get(
            f"/api/v1/returns/{return_id}",
            headers={"Authorization": f"Bearer {data['r_token']}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == return_id


class TestDisputeOpen:
    def test_retailer_can_open_dispute(self, client):
        data = _seed_delivered_order(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/disputes",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"claimed_amount_toman": 1000000, "description": "Wrong items delivered, vendor unresponsive"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["dispute_status"] == "OPEN"
        assert body["data"]["description"] == "Wrong items delivered, vendor unresponsive"
        assert body["data"]["claimed_amount_toman"] == 1000000

        with _db() as verify_conn:
            with verify_conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT event_name, target_user_id, target_organization_id FROM outbox_events WHERE event_name = %s AND aggregate_id = %s",
                    ("DISPUTE_OPENED", data["oi"]),
                )
                events = cur.fetchall()
                assert events and all(e["target_user_id"] and e["target_organization_id"] for e in events)

    def test_vendor_cannot_open_dispute(self, client):
        data = _seed_delivered_order(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/disputes",
            headers={"Authorization": f"Bearer {data['v_token']}"},
            json={"claimed_amount_toman": 100000, "description": "Test dispute from vendor"},
        )
        assert resp.status_code in (403, 422)

    def test_unauthenticated_cannot_open_dispute(self, client):
        data = _seed_delivered_order(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/disputes",
            json={"claimed_amount_toman": 100000, "description": "Test"},
        )
        assert resp.status_code == 401


class TestDisputeFilingWindow:
    def test_expired_dispute_window_is_rejected(self, client):
        data = _seed_delivered_order(uuid4().hex[:8])
        conn = _db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE deliveries SET delivered_at = now() - interval '5 hours' WHERE order_id = %s",
                    (data["oi"],),
                )
            conn.commit()
        finally:
            conn.close()

        resp = client.post(
            f"/api/v1/orders/{data['oi']}/disputes",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"claimed_amount_toman": 1000000, "description": "Expired dispute window"},
        )
        assert resp.status_code == 422

class TestDisputeQuery:
    def test_get_dispute_by_tenant(self, client):
        data = _seed_delivered_order(uuid4().hex[:8])
        create_resp = client.post(
            f"/api/v1/orders/{data['oi']}/disputes",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"claimed_amount_toman": 100000, "description": "Dispute for testing get"},
        )
        dispute_id = create_resp.json()["data"]["id"]
        resp = client.get(
            f"/api/v1/disputes/{dispute_id}",
            headers={"Authorization": f"Bearer {data['r_token']}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == dispute_id

    def test_list_disputes_for_order(self, client):
        data = _seed_delivered_order(uuid4().hex[:8])
        client.post(
            f"/api/v1/orders/{data['oi']}/disputes",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"claimed_amount_toman": 100000, "description": "Dispute for listing"},
        )
        resp = client.get(
            f"/api/v1/orders/{data['oi']}/disputes",
            headers={"Authorization": f"Bearer {data['r_token']}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["count"] >= 1
