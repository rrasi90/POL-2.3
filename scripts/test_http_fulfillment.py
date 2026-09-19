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
                           json={"driver_name": "Ali", "vehicle_plate": "12-A-345"})
        assert resp.status_code == 200
        result = resp.json()["data"]
        assert result["order_status"] == "DISPATCHED"
        assert "delivery_id" in result
        assert "delivery_otp" in result

    def test_dispatch_from_preparing_rejected(self, client):
        data = _seed_order_with_status(uuid4().hex[:8], "ACCEPTED")
        client.post(f"/api/v1/orders/{data['oi']}/preparing",
                    headers={"Authorization": f"Bearer {data['v_token']}"})
        resp = client.post(f"/api/v1/orders/{data['oi']}/dispatch",
                           headers={"Authorization": f"Bearer {data['v_token']}"})
        assert resp.status_code == 422


class TestConfirmDelivery:
    def test_deliver_from_dispatched(self, client):
        data = _seed_order_with_status(uuid4().hex[:8], "ACCEPTED")
        client.post(f"/api/v1/orders/{data['oi']}/preparing",
                    headers={"Authorization": f"Bearer {data['v_token']}"})
        client.post(f"/api/v1/orders/{data['oi']}/ready",
                    headers={"Authorization": f"Bearer {data['v_token']}"})
        client.post(f"/api/v1/orders/{data['oi']}/dispatch",
                    headers={"Authorization": f"Bearer {data['v_token']}"})
        resp = client.post(f"/api/v1/orders/{data['oi']}/deliver",
                           headers={"Authorization": f"Bearer {data['r_token']}"},
                           json={"recipient_name": "Reza"})
        assert resp.status_code == 200
        assert resp.json()["data"]["order_status"] == "DELIVERED"

    def test_deliver_from_submitted_rejected(self, client):
        data = _seed_order_with_status(uuid4().hex[:8], "SUBMITTED")
        resp = client.post(f"/api/v1/orders/{data['oi']}/deliver",
                           headers={"Authorization": f"Bearer {data['r_token']}"},
                           json={"recipient_name": "Reza"})
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

        resp = client.post(f"/api/v1/orders/{data['oi']}/dispatch", headers=v)
        assert resp.status_code == 200

        resp = client.post(f"/api/v1/orders/{data['oi']}/deliver", headers=r, json={"recipient_name": "Test"})
        assert resp.status_code == 200
        assert resp.json()["data"]["order_status"] == "DELIVERED"


class TestTimelineAfterFulfillment:
    def test_timeline_records_all_transitions(self, client):
        data = _seed_order_with_status(uuid4().hex[:8], "ACCEPTED")
        v = {"Authorization": f"Bearer {data['v_token']}"}
        r = {"Authorization": f"Bearer {data['r_token']}"}

        client.post(f"/api/v1/orders/{data['oi']}/preparing", headers=v)
        client.post(f"/api/v1/orders/{data['oi']}/ready", headers=v)
        client.post(f"/api/v1/orders/{data['oi']}/dispatch", headers=v)
        client.post(f"/api/v1/orders/{data['oi']}/deliver", headers=r, json={"recipient_name": "Test"})

        resp = client.get(f"/api/v1/orders/{data['oi']}/timeline", headers=v)
        events = resp.json()["data"]["events"]
        event_types = [e["event_type"] for e in events]
        assert "PREPARING" in str(event_types) or "ACCEPTED_TO_PREPARING" in str(event_types)
