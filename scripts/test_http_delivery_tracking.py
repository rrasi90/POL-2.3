"""HTTP tests for delivery tracking routes -- Stage 23.

Tests GET /orders/{id}/delivery and GET /orders/{id}/delivery/proof.
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


def _seed_delivery(suffix, order_status="DISPATCHED", delivery_status="IN_TRANSIT"):
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            ru = str(uuid4()); ro = str(uuid4()); ri = str(uuid4())
            vu = str(uuid4()); vo = str(uuid4()); vi = str(uuid4())
            bi = str(uuid4()); pi = str(uuid4()); ogi = str(uuid4())
            oi = str(uuid4()); di = str(uuid4())

            cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, \'R\', \'RETAILER_OWNER\')",
                        (ru, f"+9891{uuid4().int % 100000000:08d}"))
            cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, \'RO\', \'RETAILER\', \'ACTIVE\')", (ro,))
            cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, \'RETAILER_OWNER\', \'ACTIVE\')",
                        (str(uuid4()), ro, ru))
            cur.execute("INSERT INTO retailers (id, user_id, organization_id, store_name, city, neighborhood, address) VALUES (%s, %s, %s, \'S\', \'Ahvaz\', \'N\', \'A\')",
                        (ri, ru, ro))
            cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, \'V\', \'VENDOR_OWNER\')",
                        (vu, f"+9891{uuid4().int % 100000000:08d}"))
            cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, \'VO\', \'VENDOR\', \'ACTIVE\')", (vo,))
            cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, \'VENDOR_OWNER\', \'ACTIVE\')",
                        (str(uuid4()), vo, vu))
            cur.execute("INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman, status) "
                        "VALUES (%s, %s, %s, \'V\', \'Ahvaz\', 1000000, \'ACTIVE\')", (vi, vu, vo))
            cur.execute("INSERT INTO baskets (id, retailer_id, status, version) VALUES (%s, %s, \'OPEN\', 1)", (bi, ri))
            cur.execute("INSERT INTO allocation_plans (id, basket_id, basket_version, status, strategy, vendor_count, total_estimated_toman, expires_at) "
                        "VALUES (%s, %s, 1, \'CONFIRMED\', \'SINGLE_VENDOR\', 1, 5000000, now() + interval \'15 minutes\')", (pi, bi))
            cur.execute("INSERT INTO order_groups (id, basket_id, retailer_id, checkout_idempotency_key, total_amount_toman, order_count, group_status) "
                        "VALUES (%s, %s, %s, %s, 5000000, 1, \'ACTIVE\')", (ogi, bi, ri, str(uuid4())))
            cur.execute("INSERT INTO orders (id, order_number, order_group_id, allocation_plan_id, retailer_id, vendor_id, order_status, total_amount_toman, created_at, updated_at) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, 5000000, now(), now())",
                        (oi, f"ORD-{suffix}", ogi, pi, ri, vi, order_status))

            if delivery_status or order_status == "DISPATCHED":
                cur.execute(
                    "INSERT INTO deliveries (id, order_id, vendor_id, delivery_status, driver_name, vehicle_plate, driver_phone, dispatched_at, created_at) "
                    "VALUES (%s, %s, %s, %s, \'Ali\', \'12-A-345\', \'09121234567\', now(), now())",
                    (di, oi, vi, delivery_status or "IN_TRANSIT"),
                )

            if delivery_status == "DELIVERED":
                cur.execute(
                    "INSERT INTO proof_of_delivery (id, delivery_id, accepted_by_name, accepted_at) VALUES (%s, %s, \'Reza\', now())",
                    (str(uuid4()), di),
                )

            rs = _create_session(cur, ru, ro)
            vs = _create_session(cur, vu, vo)

        conn.commit()
        rt = encode_access_token(ru, rs, ro, "RETAILER_OWNER")
        vt = encode_access_token(vu, vs, vo, "VENDOR_OWNER")
        return {"ru": ru, "ro": ro, "vu": vu, "vo": vo, "ri": ri, "vi": vi,
                "oi": oi, "ogi": ogi, "di": di, "r_token": rt, "v_token": vt}
    finally:
        conn.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app, raise_server_exceptions=False)


class TestDeliveryGet:
    def test_get_delivery_for_dispatched_order(self, client):
        data = _seed_delivery(uuid4().hex[:8], "DISPATCHED", "IN_TRANSIT")
        resp = client.get(f"/api/v1/orders/{data['oi']}/delivery",
                          headers={"Authorization": f"Bearer {data['r_token']}"})
        assert resp.status_code == 200
        d = resp.json()["data"]
        assert d["delivery_status"] == "IN_TRANSIT"
        assert d["driver_name"] == "Ali"
        assert d["vehicle_plate"] == "12-A-345"

    def test_get_delivery_for_vendor(self, client):
        data = _seed_delivery(uuid4().hex[:8], "DISPATCHED", "IN_TRANSIT")
        resp = client.get(f"/api/v1/orders/{data['oi']}/delivery",
                          headers={"Authorization": f"Bearer {data['v_token']}"})
        assert resp.status_code == 200

    def test_get_delivery_not_found(self, client):
        data = _seed_delivery(uuid4().hex[:8], "ACCEPTED", None)
        resp = client.get(f"/api/v1/orders/{data['oi']}/delivery",
                          headers={"Authorization": f"Bearer {data['r_token']}"})
        assert resp.status_code == 422


class TestDeliveryProof:
    def test_get_proof_for_delivered_order(self, client):
        data = _seed_delivery(uuid4().hex[:8], "DELIVERED", "DELIVERED")
        resp = client.get(f"/api/v1/orders/{data['oi']}/delivery/proof",
                          headers={"Authorization": f"Bearer {data['r_token']}"})
        assert resp.status_code == 200
        proof = resp.json()["data"]
        assert proof["accepted_by_name"] == "Reza"

    def test_get_proof_returns_none_for_undelivered(self, client):
        data = _seed_delivery(uuid4().hex[:8], "DISPATCHED", "IN_TRANSIT")
        resp = client.get(f"/api/v1/orders/{data['oi']}/delivery/proof",
                          headers={"Authorization": f"Bearer {data['r_token']}"})
        assert resp.status_code == 200
        assert resp.json()["data"]["message"] == "No proof of delivery found."
