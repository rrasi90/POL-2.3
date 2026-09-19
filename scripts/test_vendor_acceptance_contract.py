"""Contract verification tests for vendor acceptance UI contract -- Stage 21.

Verifies that the API surface matches the contract defined in
06_PRODUCT/vendor_acceptance_ui_contract.md.
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
        "VALUES (%s, %s, %s, %s, \'ACTIVE\', %s)",
        (session_id, user_id, org_id, hash_token(session_id),
         datetime.now(timezone.utc) + timedelta(hours=1)),
    )
    return session_id


def _seed_full(suffix):
    """Seed a complete order with timeline event and SLA deadline."""
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            retailer_user = str(uuid4())
            retailer_org = str(uuid4())
            retailer_id = str(uuid4())
            vendor_user = str(uuid4())
            vendor_org = str(uuid4())
            vendor_id = str(uuid4())
            brand_id = str(uuid4())
            category_id = str(uuid4())
            subcategory_id = str(uuid4())
            product_id = str(uuid4())
            vendor_product_id = str(uuid4())
            basket_id = str(uuid4())
            plan_id = str(uuid4())
            order_group_id = str(uuid4())
            order_id = str(uuid4())
            order_item_id = str(uuid4())
            deadline = datetime.now(timezone.utc) + timedelta(hours=2)

            cur.execute(
                "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, \'Retailer\', \'RETAILER_OWNER\')",
                (retailer_user, f"+9891{uuid4().int % 100000000:08d}"),
            )
            cur.execute(
                "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, \'R\', \'RETAILER\', \'ACTIVE\')",
                (retailer_org,),
            )
            cur.execute(
                "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, \'RETAILER_OWNER\', \'ACTIVE\')",
                (str(uuid4()), retailer_org, retailer_user),
            )
            cur.execute(
                "INSERT INTO retailers (id, user_id, organization_id, store_name, city, neighborhood, address) VALUES (%s, %s, %s, \'S\', \'Ahvaz\', \'N\', \'A\')",
                (retailer_id, retailer_user, retailer_org),
            )
            cur.execute(
                "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, \'Vendor\', \'VENDOR_OWNER\')",
                (vendor_user, f"+9891{uuid4().int % 100000000:08d}"),
            )
            cur.execute(
                "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, \'V\', \'VENDOR\', \'ACTIVE\')",
                (vendor_org,),
            )
            cur.execute(
                "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, \'VENDOR_OWNER\', \'ACTIVE\')",
                (str(uuid4()), vendor_org, vendor_user),
            )
            cur.execute(
                "INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman, status) "
                "VALUES (%s, %s, %s, \'V\', \'Ahvaz\', 1000000, \'ACTIVE\')",
                (vendor_id, vendor_user, vendor_org),
            )
            cur.execute(
                "INSERT INTO brands (id, name_fa, slug) VALUES (%s, %s, %s)",
                (brand_id, f"B{suffix}", f"b-{suffix}"),
            )
            cur.execute(
                "INSERT INTO categories (id, name_fa, slug) VALUES (%s, %s, %s)",
                (category_id, f"C{suffix}", f"c-{suffix}"),
            )
            cur.execute(
                "INSERT INTO subcategories (id, category_id, name_fa, slug) VALUES (%s, %s, %s, %s)",
                (subcategory_id, category_id, f"S{suffix}", f"s-{suffix}"),
            )
            cur.execute(
                "INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id, is_active) "
                "VALUES (%s, %s, %s, %s, %s, %s, TRUE)",
                (product_id, f"SKU-{suffix}", f"P{suffix}", brand_id, category_id, subcategory_id),
            )
            cur.execute(
                "INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity, sales_unit, is_active, listing_status) "
                "VALUES (%s, %s, %s, %s, \'CARTON\', 4, \'CARTON\', TRUE, \'ACTIVE\')",
                (vendor_product_id, vendor_id, product_id, f"VP-{suffix}"),
            )
            cur.execute(
                "INSERT INTO baskets (id, retailer_id, status, version) VALUES (%s, %s, \'OPEN\', 1)",
                (basket_id, retailer_id),
            )
            cur.execute(
                "INSERT INTO allocation_plans (id, basket_id, basket_version, status, strategy, vendor_count, total_estimated_toman, expires_at) "
                "VALUES (%s, %s, 1, \'CONFIRMED\', \'SINGLE_VENDOR\', 1, 5000000, now() + interval \'15 minutes\')",
                (plan_id, basket_id),
            )
            cur.execute(
                "INSERT INTO order_groups (id, basket_id, retailer_id, checkout_idempotency_key, "
                "total_amount_toman, order_count, group_status) "
                "VALUES (%s, %s, %s, %s, 5000000, 1, \'ACTIVE\')",
                (order_group_id, basket_id, retailer_id, str(uuid4())),
            )
            cur.execute(
                "INSERT INTO orders (id, order_number, order_group_id, allocation_plan_id, "
                "retailer_id, vendor_id, order_status, total_amount_toman, "
                "vendor_acceptance_deadline_at, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, \'SUBMITTED\', 5000000, %s, now(), now())",
                (order_id, f"ORD-{suffix}", order_group_id, plan_id, retailer_id, vendor_id, deadline),
            )
            cur.execute(
                "INSERT INTO order_items (id, order_id, product_id, vendor_product_id, "
                "product_name_snapshot, brand_name_snapshot, vendor_sku_snapshot, "
                "packaging_unit_snapshot, pack_quantity_snapshot, ordered_quantity, "
                "unit_price_toman, total_line_amount_toman, fulfillment_status) "
                "VALUES (%s, %s, %s, %s, \'P\', \'B\', \'VS\', \'CARTON\', 4, 10, 500000, 5000000, \'PENDING\')",
                (order_item_id, order_id, product_id, vendor_product_id),
            )
            cur.execute(
                "INSERT INTO order_timeline_events (order_id, event_type, from_status, to_status, actor_user_id, actor_organization_id) "
                "VALUES (%s, \'CREATED\', NULL, \'SUBMITTED\', %s, %s)",
                (order_id, retailer_user, retailer_org),
            )
            r_session = _create_session(cur, retailer_user, retailer_org)
            v_session = _create_session(cur, vendor_user, vendor_org)

        conn.commit()

        r_token = encode_access_token(retailer_user, r_session, retailer_org, "RETAILER_OWNER")
        v_token = encode_access_token(vendor_user, v_session, vendor_org, "VENDOR_OWNER")

        return {
            "retailer_user": retailer_user, "retailer_org": retailer_org,
            "vendor_user": vendor_user, "vendor_org": vendor_org,
            "retailer_id": retailer_id, "vendor_id": vendor_id,
            "order_id": order_id, "order_group_id": order_group_id,
            "order_item_id": order_item_id, "deadline": deadline,
            "r_token": r_token, "v_token": v_token,
        }
    finally:
        conn.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app, raise_server_exceptions=False)


class TestSLADeadlineContract:
    def test_order_detail_includes_sla_deadline(self, client):
        data = _seed_full(uuid4().hex[:8])
        resp = client.get(
            f"/api/v1/orders/{data['order_id']}",
            headers={"Authorization": f"Bearer {data['v_token']}"},
        )
        assert resp.status_code == 200
        order = resp.json()["data"]
        assert "vendor_acceptance_deadline_at" in order
        assert order["vendor_acceptance_deadline_at"] is not None

    def test_order_list_includes_status(self, client):
        data = _seed_full(uuid4().hex[:8])
        resp = client.get(
            "/api/v1/orders",
            headers={"Authorization": f"Bearer {data['v_token']}"},
        )
        assert resp.status_code == 200
        orders = resp.json()["data"]["orders"]
        statuses = {o["order_status"] for o in orders}
        assert "SUBMITTED" in statuses


class TestTimelineContract:
    def test_timeline_events_recorded(self, client):
        data = _seed_full(uuid4().hex[:8])
        resp = client.get(
            f"/api/v1/orders/{data['order_id']}/timeline",
            headers={"Authorization": f"Bearer {data['v_token']}"},
        )
        assert resp.status_code == 200
        events = resp.json()["data"]["events"]
        assert len(events) >= 1
        assert events[0]["event_type"] == "CREATED"
        assert events[0]["from_status"] is None
        assert events[0]["to_status"] == "SUBMITTED"

    def test_timeline_includes_actor_info(self, client):
        data = _seed_full(uuid4().hex[:8])
        resp = client.get(
            f"/api/v1/orders/{data['order_id']}/timeline",
            headers={"Authorization": f"Bearer {data['v_token']}"},
        )
        events = resp.json()["data"]["events"]
        assert events[0]["actor_user_id"] is not None
        assert events[0]["actor_organization_id"] is not None


class TestOrderItemsContract:
    def test_order_items_contain_fulfillment_status(self, client):
        data = _seed_full(uuid4().hex[:8])
        resp = client.get(
            f"/api/v1/orders/{data['order_id']}/items",
            headers={"Authorization": f"Bearer {data['v_token']}"},
        )
        assert resp.status_code == 200
        items = resp.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["fulfillment_status"] == "PENDING"
        assert items[0]["ordered_quantity"] == 10
        assert items[0]["unit_price_toman"] == 500000
        assert items[0]["total_line_amount_toman"] == 5000000


class TestOrderGroupContract:
    def test_order_group_shows_child_orders(self, client):
        data = _seed_full(uuid4().hex[:8])
        resp = client.get(
            f"/api/v1/orders/group/{data['order_group_id']}/orders",
            headers={"Authorization": f"Bearer {data['v_token']}"},
        )
        assert resp.status_code == 200
        body = resp.json()["data"]
        assert len(body["orders"]) == 1
        assert body["orders"][0]["order_status"] == "SUBMITTED"

    def test_order_group_detail_shows_status(self, client):
        data = _seed_full(uuid4().hex[:8])
        resp = client.get(
            f"/api/v1/orders/group/{data['order_group_id']}",
            headers={"Authorization": f"Bearer {data['v_token']}"},
        )
        assert resp.status_code == 200
        group = resp.json()["data"]
        assert group["group_status"] == "ACTIVE"
        assert group["total_amount_toman"] == 5000000
        assert group["order_count"] == 1


class TestTenantIsolationContract:
    def test_vendor_sees_only_own_orders(self, client):
        data = _seed_full(uuid4().hex[:8])
        resp = client.get(
            "/api/v1/orders",
            headers={"Authorization": f"Bearer {data['v_token']}"},
        )
        orders = resp.json()["data"]["orders"]
        for o in orders:
            assert o["vendor_id"] == data["vendor_id"]

    def test_retailer_sees_only_own_orders(self, client):
        data = _seed_full(uuid4().hex[:8])
        resp = client.get(
            "/api/v1/orders",
            headers={"Authorization": f"Bearer {data['r_token']}"},
        )
        orders = resp.json()["data"]["orders"]
        for o in orders:
            assert o["retailer_id"] == data["retailer_id"]
