"""HTTP tests for fulfillment state machine -- Stage 22.

Tests PREPARING, READY, DISPATCHED, DELIVERED transitions.
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




def _advance_delivery_to_arrived(client, data):
    v = {"Authorization": f"Bearer {data['v_token']}"}
    res = client.post(
        f"/api/v1/orders/{data['oi']}/preparing",
        headers=v,
    )
    assert res.status_code == 200, res.text
    res = client.post(
        f"/api/v1/orders/{data['oi']}/ready",
        headers=v,
    )
    assert res.status_code == 200, res.text
    res = client.post(
        f"/api/v1/orders/{data['oi']}/dispatch",
        headers=v,
        json={
            "driver_name": "Ali",
            "driver_phone": "+989121234567",
            "vehicle_plate": "12-A-345",
        },
    )
    assert res.status_code == 200
    result = res.json()["data"]
    assert "delivery_otp" not in result  # G-439: no OTP in vendor response
    otp = _recipient_delivery_otp(data["oi"])
    for path in ("picked-up", "in-transit", "arrived"):
        res = client.post(
            f"/api/v1/orders/{data['oi']}/delivery/{path}",
            headers=v,
        )
        assert res.status_code == 200, (path, res.text)
    return otp


def _recipient_delivery_otp(order_id):
    """G-438/G-439: the delivery OTP is a recipient secret.

    The vendor dispatch response must NOT contain it (G-439); the retailer
    receives it through the DELIVERY_OTP_GENERATED outbox event targeted at
    the retailer organization (canonical recipient channel, rendered into the
    retailer inbox by the integration worker).
    """
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT payload FROM outbox_events
                WHERE event_name = 'DELIVERY_OTP_GENERATED'
                  AND payload->>'order_id' = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (order_id,),
            )
            event = cur.fetchone()
            assert event is not None, "DELIVERY_OTP_GENERATED event missing"
            return event["payload"]["delivery_otp"]
    finally:
        conn.close()


def _create_session(cur, user_id, org_id):
    session_id = str(uuid4())
    cur.execute(
        "INSERT INTO user_sessions (id, user_id, active_organization_id, token_hash, status, expires_at) "
        "VALUES (%s, %s, %s, %s, \'ACTIVE\', %s)",
        (session_id, user_id, org_id, hash_token(session_id),
         datetime.now(timezone.utc) + timedelta(hours=1)),
    )
    return session_id


def _seed_order_with_status(suffix, order_status):
    """Seed order with given status and return tokens + ids."""
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            ru = str(uuid4())
            ro = str(uuid4())
            ri = str(uuid4())
            vu = str(uuid4())
            vo = str(uuid4())
            vi = str(uuid4())
            brand_id = str(uuid4())
            category_id = str(uuid4())
            subcategory_id = str(uuid4())
            product_id = str(uuid4())
            vendor_product_id = str(uuid4())
            bi = str(uuid4())
            pi = str(uuid4())
            ogi = str(uuid4())
            oi = str(uuid4())

            cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, \'R\', \'RETAILER_OWNER\')",
                        (ru, f"+9891{uuid4().int % 100000000:08d}"))
            cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, \'RO\', \'RETAILER\', \'ACTIVE\')",
                        (ro,))
            cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, \'RETAILER_OWNER\', \'ACTIVE\')",
                        (str(uuid4()), ro, ru))
            cur.execute("INSERT INTO retailers (id, user_id, organization_id, store_name, city, neighborhood, address) VALUES (%s, %s, %s, \'S\', \'Ahvaz\', \'N\', \'A\')",
                        (ri, ru, ro))
            cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, \'V\', \'VENDOR_OWNER\')",
                        (vu, f"+9891{uuid4().int % 100000000:08d}"))
            cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, \'VO\', \'VENDOR\', \'ACTIVE\')",
                        (vo,))
            cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, \'VENDOR_OWNER\', \'ACTIVE\')",
                        (str(uuid4()), vo, vu))
            cur.execute("INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman, status) "
                        "VALUES (%s, %s, %s, \'V\', \'Ahvaz\', 1000000, \'ACTIVE\')",
                        (vi, vu, vo))
            cur.execute("INSERT INTO brands (id, name_fa, slug) VALUES (%s, 'Fulfillment Brand', %s)",
                        (brand_id, f'fulfillment-brand-{suffix}'))
            cur.execute("INSERT INTO categories (id, name_fa, slug) VALUES (%s, 'Fulfillment Category', %s)",
                        (category_id, f'fulfillment-category-{suffix}'))
            cur.execute("INSERT INTO subcategories (id, category_id, name_fa, slug) VALUES (%s,%s,'Fulfillment Subcategory',%s)",
                        (subcategory_id, category_id, f'fulfillment-subcategory-{suffix}'))
            cur.execute(
                """
                INSERT INTO products
                    (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id, is_active)
                VALUES (%s,%s,'Fulfillment Product',%s,%s,%s,TRUE)
                """,
                (product_id, f'FULFILL-{suffix}', brand_id, category_id, subcategory_id),
            )
            cur.execute(
                """
                INSERT INTO vendor_products
                    (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity, listing_status, is_active)
                VALUES (%s,%s,%s,%s,'CARTON',1,'ACTIVE',TRUE)
                """,
                (vendor_product_id, vi, product_id, f'FULFILL-VP-{suffix}'),
            )

            cur.execute("INSERT INTO baskets (id, retailer_id, status, version) VALUES (%s, %s, \'OPEN\', 1)", (bi, ri))
            cur.execute("INSERT INTO allocation_plans (id, basket_id, basket_version, status, strategy, vendor_count, total_estimated_toman, expires_at) "
                        "VALUES (%s, %s, 1, \'CONFIRMED\', \'SINGLE_VENDOR\', 1, 5000000, now() + interval \'15 minutes\')",
                        (pi, bi))
            cur.execute("INSERT INTO order_groups (id, basket_id, retailer_id, checkout_idempotency_key, total_amount_toman, order_count, group_status) "
                        "VALUES (%s, %s, %s, %s, 5000000, 1, \'ACTIVE\')",
                        (ogi, bi, ri, str(uuid4())))
            cur.execute("INSERT INTO orders (id, order_number, order_group_id, allocation_plan_id, retailer_id, vendor_id, order_status, total_amount_toman, created_at, updated_at) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, 5000000, now(), now())",
                        (oi, f"ORD-{suffix}", ogi, pi, ri, vi, order_status))
            cur.execute(
                """
                INSERT INTO order_items (
                    id, order_id, product_id, vendor_product_id,
                    product_name_snapshot, brand_name_snapshot, vendor_sku_snapshot,
                    packaging_unit_snapshot, pack_quantity_snapshot,
                    ordered_quantity, accepted_quantity, delivered_quantity,
                    unit_price_toman, total_line_amount_toman, fulfillment_status
                )
                VALUES (%s,%s,%s,%s,'Fulfillment Product','Fulfillment Brand',%s,
                        'CARTON',1,10,NULL,0,500000,5000000,'PENDING')
                """,
                (str(uuid4()), oi, product_id, vendor_product_id, f'FULFILL-VP-{suffix}'),
            )

            rs = _create_session(cur, ru, ro)
            vs = _create_session(cur, vu, vo)

        conn.commit()
        rt = encode_access_token(ru, rs, ro, "RETAILER_OWNER")
        vt = encode_access_token(vu, vs, vo, "VENDOR_OWNER")
        return {"ru": ru, "ro": ro, "vu": vu, "vo": vo, "ri": ri, "vi": vi,
                "oi": oi, "ogi": ogi, "r_token": rt, "v_token": vt}
    finally:
        conn.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app, raise_server_exceptions=False)


class TestMarkPreparing:
    def test_preparing_from_accepted(self, client):
        data = _seed_order_with_status(uuid4().hex[:8], "ACCEPTED")
        resp = client.post(f"/api/v1/orders/{data['oi']}/preparing",
                           headers={"Authorization": f"Bearer {data['v_token']}"})
        assert resp.status_code == 200
        assert resp.json()["data"]["order_status"] == "PREPARING"

    def test_preparing_from_partially_accepted(self, client):
        data = _seed_order_with_status(uuid4().hex[:8], "PARTIALLY_ACCEPTED")
        resp = client.post(f"/api/v1/orders/{data['oi']}/preparing",
                           headers={"Authorization": f"Bearer {data['v_token']}"})
        assert resp.status_code == 200
        assert resp.json()["data"]["order_status"] == "PREPARING"

    def test_preparing_from_submitted_rejected(self, client):
        data = _seed_order_with_status(uuid4().hex[:8], "SUBMITTED")
        resp = client.post(f"/api/v1/orders/{data['oi']}/preparing",
                           headers={"Authorization": f"Bearer {data['v_token']}"})
        assert resp.status_code == 422

    def test_preparing_requires_vendor_auth(self, client):
        data = _seed_order_with_status(uuid4().hex[:8], "ACCEPTED")
        resp = client.post(f"/api/v1/orders/{data['oi']}/preparing",
                           headers={"Authorization": f"Bearer {data['r_token']}"})
        assert resp.status_code in (403, 422)


class TestMarkReady:
    def test_ready_from_preparing(self, client):
        data = _seed_order_with_status(uuid4().hex[:8], "ACCEPTED")
        client.post(f"/api/v1/orders/{data['oi']}/preparing",
                    headers={"Authorization": f"Bearer {data['v_token']}"})
        resp = client.post(f"/api/v1/orders/{data['oi']}/ready",
                           headers={"Authorization": f"Bearer {data['v_token']}"})
        assert resp.status_code == 200
        assert resp.json()["data"]["order_status"] == "READY"

    def test_ready_from_submitted_rejected(self, client):
        data = _seed_order_with_status(uuid4().hex[:8], "SUBMITTED")
        resp = client.post(f"/api/v1/orders/{data['oi']}/ready",
                           headers={"Authorization": f"Bearer {data['v_token']}"})
        assert resp.status_code == 422


class TestDispatch:
    def test_dispatch_from_ready(self, client):
        data = _seed_order_with_status(uuid4().hex[:8], "ACCEPTED")
        client.post(f"/api/v1/orders/{data['oi']}/preparing",
                    headers={"Authorization": f"Bearer {data['v_token']}"})
        client.post(f"/api/v1/orders/{data['oi']}/ready",
                    headers={"Authorization": f"Bearer {data['v_token']}"})
        resp = client.post(f"/api/v1/orders/{data['oi']}/dispatch",
                           headers={"Authorization": f"Bearer {data['v_token']}"},
                           json={"driver_name": "Ali", "driver_phone": "+989121234567", "vehicle_plate": "12-A-345"})
        assert resp.status_code == 200
        result = resp.json()["data"]
        assert result["order_status"] == "DISPATCHED"
        assert result["delivery_status"] == "ASSIGNED"
        assert "delivery_id" in result
        # G-439: the dispatch response is vendor-facing and must not carry the OTP.
        assert "delivery_otp" not in result
        # The OTP reaches the retailer through the targeted DELIVERY_OTP_GENERATED event.
        otp = _recipient_delivery_otp(data["oi"])
        assert isinstance(otp, str) and len(otp) == 4 and otp.isdigit()
        for path in ("picked-up", "in-transit", "arrived"):
            stage = client.post(
                f"/api/v1/orders/{data['oi']}/delivery/{path}",
                headers={"Authorization": f"Bearer {data['v_token']}"}
            )
            assert stage.status_code == 200
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/deliver",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"recipient_name": "Reza", "otp_code": otp},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["otp_verified"] is True

    def test_dispatch_from_preparing_rejected(self, client):
        data = _seed_order_with_status(uuid4().hex[:8], "ACCEPTED")
        client.post(f"/api/v1/orders/{data['oi']}/preparing",
                    headers={"Authorization": f"Bearer {data['v_token']}"})
        resp = client.post(f"/api/v1/orders/{data['oi']}/dispatch",
                           headers={"Authorization": f"Bearer {data['v_token']}"})
        assert resp.status_code == 422


class TestConfirmDelivery:
    def test_deliver_requires_arrived_and_otp(self, client):
        data = _seed_order_with_status(uuid4().hex[:8], "ACCEPTED")
        otp = _advance_delivery_to_arrived(client, data)
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/deliver",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"recipient_name": "Reza", "otp_code": otp},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["order_status"] == "DELIVERED"

    def test_deliver_from_dispatched_rejected(self, client):
        data = _seed_order_with_status(uuid4().hex[:8], "ACCEPTED")
        v = {"Authorization": f"Bearer {data['v_token']}"}
        client.post(f"/api/v1/orders/{data['oi']}/preparing", headers=v)
        client.post(f"/api/v1/orders/{data['oi']}/ready", headers=v)
        client.post(
            f"/api/v1/orders/{data['oi']}/dispatch",
            headers=v,
            json={"driver_name": "Ali", "driver_phone": "+989121234567", "vehicle_plate": "12-A-345"},
        )
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/deliver",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"recipient_name": "Reza", "otp_code": "1234"},
        )
        assert resp.status_code == 422

    def test_wrong_otp_rejected_without_delivery(self, client):
        data = _seed_order_with_status(uuid4().hex[:8], "ACCEPTED")
        _advance_delivery_to_arrived(client, data)
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/deliver",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"recipient_name": "Reza", "otp_code": "0000"},
        )
        assert resp.status_code == 422

    def test_repeated_delivery_confirmation_replays(self, client):
        data = _seed_order_with_status(uuid4().hex[:8], "ACCEPTED")
        otp = _advance_delivery_to_arrived(client, data)
        r = {"Authorization": f"Bearer {data['r_token']}"}
        first = client.post(
            f"/api/v1/orders/{data['oi']}/deliver",
            headers=r,
            json={"recipient_name": "Reza", "otp_code": otp},
        )
        second = client.post(
            f"/api/v1/orders/{data['oi']}/deliver",
            headers=r,
            json={"recipient_name": "Reza", "otp_code": otp},
        )
        assert first.status_code == 200
        assert second.status_code == 200
        assert second.json()["data"]["idempotent_replay"] is True

    def test_deliver_from_submitted_rejected(self, client):
        data = _seed_order_with_status(uuid4().hex[:8], "SUBMITTED")
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/deliver",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"recipient_name": "Reza", "otp_code": "1234"},
        )
        assert resp.status_code == 422


class TestFullLifecycle:
    def test_accepted_to_delivered(self, client):
        data = _seed_order_with_status(uuid4().hex[:8], "ACCEPTED")
        v = {"Authorization": f"Bearer {data['v_token']}"}
        r = {"Authorization": f"Bearer {data['r_token']}"}

        resp = client.post(f"/api/v1/orders/{data['oi']}/preparing", headers=v)
        assert resp.status_code == 200

        resp = client.post(f"/api/v1/orders/{data['oi']}/ready", headers=v)
        assert resp.status_code == 200

        resp = client.post(
            f"/api/v1/orders/{data['oi']}/dispatch",
            headers=v,
            json={"driver_name": "Ali", "driver_phone": "+989121234567", "vehicle_plate": "12-A-345"},
        )
        assert resp.status_code == 200
        assert "delivery_otp" not in resp.json()["data"]  # G-439: no OTP in vendor response
        otp = _recipient_delivery_otp(data["oi"])
        for path in ("picked-up", "in-transit", "arrived"):
            resp = client.post(f"/api/v1/orders/{data['oi']}/delivery/{path}", headers=v)
            assert resp.status_code == 200

        resp = client.post(f"/api/v1/orders/{data['oi']}/deliver", headers=r, json={"recipient_name": "Test", "otp_code": otp})
        assert resp.status_code == 200
        assert resp.json()["data"]["order_status"] == "DELIVERED"


class TestTimelineAfterFulfillment:
    def test_timeline_records_all_transitions(self, client):
        data = _seed_order_with_status(uuid4().hex[:8], "ACCEPTED")
        v = {"Authorization": f"Bearer {data['v_token']}"}
        r = {"Authorization": f"Bearer {data['r_token']}"}

        client.post(f"/api/v1/orders/{data['oi']}/preparing", headers=v)
        client.post(f"/api/v1/orders/{data['oi']}/ready", headers=v)
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/dispatch",
            headers=v,
            json={"driver_name": "Ali", "driver_phone": "+989121234567", "vehicle_plate": "12-A-345"},
        )
        assert resp.status_code == 200
        assert "delivery_otp" not in resp.json()["data"]  # G-439: no OTP in vendor response
        otp = _recipient_delivery_otp(data["oi"])
        for path in ("picked-up", "in-transit", "arrived"):
            resp = client.post(f"/api/v1/orders/{data['oi']}/delivery/{path}", headers=v)
            assert resp.status_code == 200
        client.post(f"/api/v1/orders/{data['oi']}/deliver", headers=r, json={"recipient_name": "Test", "otp_code": otp})

        resp = client.get(f"/api/v1/orders/{data['oi']}/timeline", headers=v)
        events = resp.json()["data"]["events"]
        event_types = [e["event_type"] for e in events]
        assert "PREPARING" in str(event_types) or "ACCEPTED_TO_PREPARING" in str(event_types)
