"""HTTP tests for Delivery Exceptions -- Stage 25.

Tests exception reporting, resolution, escalation, secure access.
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


def _seed_delivered(suffix):
    """Seed a fully dispatched order with delivery and proof of delivery."""
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            ru = str(uuid4()); ro = str(uuid4()); ri = str(uuid4())
            vu = str(uuid4()); vo = str(uuid4()); vi = str(uuid4())
            ou = str(uuid4()); oo = str(uuid4())
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
            cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Ops', 'OPS_AGENT')",
                        (ou, f"+9891{uuid4().int % 100000000:08d}"))
            cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'OPS', 'OPERATOR', 'ACTIVE')", (oo,))
            cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'OPS_AGENT', 'ACTIVE')",
                        (str(uuid4()), oo, ou))
            cur.execute("INSERT INTO baskets (id, retailer_id, status, version) VALUES (%s, %s, \'OPEN\', 1)", (bi, ri))
            cur.execute("INSERT INTO allocation_plans (id, basket_id, basket_version, status, strategy, vendor_count, total_estimated_toman, expires_at) "
                        "VALUES (%s, %s, 1, \'CONFIRMED\', \'SINGLE_VENDOR\', 1, 5000000, now() + interval \'15 minutes\')", (pi, bi))
            cur.execute("INSERT INTO order_groups (id, basket_id, retailer_id, checkout_idempotency_key, total_amount_toman, order_count, group_status) "
                        "VALUES (%s, %s, %s, %s, 5000000, 1, \'ACTIVE\')", (ogi, bi, ri, str(uuid4())))
            cur.execute("INSERT INTO orders (id, order_number, order_group_id, allocation_plan_id, retailer_id, vendor_id, order_status, total_amount_toman, created_at, updated_at) "
                        "VALUES (%s, %s, %s, %s, %s, %s, \'DELIVERED\', 5000000, now(), now())",
                        (oi, f"ORD-{suffix}", ogi, pi, ri, vi))
            cur.execute(
                "INSERT INTO deliveries (id, order_id, vendor_id, delivery_status, driver_name, vehicle_plate, delivery_otp, dispatched_at, delivered_at, created_at) "
                "VALUES (%s, %s, %s, \'DELIVERED\', \'Ali\', \'12-A-345\', %s, now(), now(), now())",
                (di, oi, vi, "123456"),
            )
            media_id = str(uuid4())
            cur.execute("INSERT INTO media_assets (id, storage_key, file_size_bytes, uploaded_by_user_id, status, provenance, checksum_sha256, created_at) "
                        "VALUES (%s, %s, 1024, %s, 'READY', 'POL_OWNED', %s, now())",
                        (media_id, f"proof/{media_id}", ru, "d" * 64))
            cur.execute(
                "INSERT INTO proof_of_delivery (id, delivery_id, accepted_by_name, accepted_at, "
                "proof_type, otp_verified, proof_media_id, issue_reported_at_delivery) "
                "VALUES (%s, %s, 'Reza', now(), 'OTP_CODE', true, %s, false)",
                (str(uuid4()), di, media_id),
            )
            rs = _create_session(cur, ru, ro)
            vs = _create_session(cur, vu, vo)

        conn.commit()
        rt = encode_access_token(ru, rs, ro, "RETAILER_OWNER")
        vt = encode_access_token(vu, vs, vo, "VENDOR_OWNER")
        return {"oi": oi, "di": di, "r_token": rt, "v_token": vt, "ru": ru, "ro": ro,
                "vu": vu, "vi": vi, "vo": vo, "oo": oo}
    finally:
        conn.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app, raise_server_exceptions=False)


class TestExceptionReporting:
    def test_report_damaged_goods(self, client):
        data = _seed_delivered(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/delivery-exceptions",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"delivery_id": data["di"], "order_id": data["oi"],
                  "exception_type": "DAMAGED_GOODS", "description": "2 cartons crushed"},
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["exception_type"] == "DAMAGED_GOODS"
        assert resp.json()["data"]["status"] == "REPORTED"
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT target_user_id, target_organization_id, dedupe_key
                    FROM outbox_events
                    WHERE event_name='DELIVERY_EXCEPTION_REPORTED'
                      AND aggregate_id=%s
                    """,
                    (resp.json()["data"]["exception_id"],),
                )
                event = cur.fetchone()
                assert event is not None
                assert str(event["target_user_id"]) == data["vu"]
                assert str(event["target_organization_id"]) == data["vo"]
                assert event["dedupe_key"].startswith("DELIVERY_EXCEPTION_REPORTED:")
                cur.execute(
                    """
                    SELECT COUNT(*) AS c FROM notification_templates
                    WHERE event_name='DELIVERY_EXCEPTION_REPORTED'
                      AND channel='INBOX'
                      AND enabled=TRUE
                    """
                )
                assert int(cur.fetchone()["c"]) >= 1
        finally:
            conn.close()

    def test_report_doorstep_rejection(self, client):
        data = _seed_delivered(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/delivery-exceptions",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"delivery_id": data["di"], "order_id": data["oi"],
                  "exception_type": "DOORSTEP_REJECTION", "description": "Wrong items delivered"},
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["exception_type"] == "DOORSTEP_REJECTION"

    def test_report_item_discrepancy(self, client):
        data = _seed_delivered(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/delivery-exceptions",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"delivery_id": data["di"], "order_id": data["oi"],
                  "exception_type": "ITEM_DISCREPANCY", "description": "Short 3 units of SKU-123"},
        )
        assert resp.status_code == 201

    def test_report_invalid_type_rejected(self, client):
        data = _seed_delivered(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/delivery-exceptions",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"delivery_id": data["di"], "order_id": data["oi"],
                  "exception_type": "INVALID_TYPE"},
        )
        assert resp.status_code == 422


class TestExceptionResolution:
    def test_resolve_full_refund(self, client):
        data = _seed_delivered(uuid4().hex[:8])
        report_resp = client.post(
            f"/api/v1/orders/{data['oi']}/delivery-exceptions",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"delivery_id": data["di"], "order_id": data["oi"],
                  "exception_type": "DAMAGED_GOODS"},
        )
        exc_id = report_resp.json()["data"]["exception_id"]
        resp = client.patch(
            f"/api/v1/orders/delivery-exceptions/{exc_id}/resolve",
            headers={"Authorization": f"Bearer {data['v_token']}"},
            json={"resolution_type": "FULL_REFUND", "resolution_note": "Confirmed damage via photos"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["resolution_type"] == "FULL_REFUND"
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT target_user_id, target_organization_id
                    FROM outbox_events
                    WHERE event_name='DELIVERY_EXCEPTION_RESOLVED'
                      AND aggregate_id=%s
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (exc_id,),
                )
                event = cur.fetchone()
                assert event is not None
                assert str(event["target_user_id"]) == data["ru"]
                assert str(event["target_organization_id"]) == data["ro"]
        finally:
            conn.close()

    def test_resolve_replacement(self, client):
        data = _seed_delivered(uuid4().hex[:8])
        report_resp = client.post(
            f"/api/v1/orders/{data['oi']}/delivery-exceptions",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"delivery_id": data["di"], "order_id": data["oi"],
                  "exception_type": "ITEM_DISCREPANCY"},
        )
        exc_id = report_resp.json()["data"]["exception_id"]
        resp = client.patch(
            f"/api/v1/orders/delivery-exceptions/{exc_id}/resolve",
            headers={"Authorization": f"Bearer {data['v_token']}"},
            json={"resolution_type": "REPLACEMENT"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["resolution_type"] == "REPLACEMENT"

    def test_cannot_resolve_already_resolved(self, client):
        data = _seed_delivered(uuid4().hex[:8])
        report_resp = client.post(
            f"/api/v1/orders/{data['oi']}/delivery-exceptions",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"delivery_id": data["di"], "order_id": data["oi"],
                  "exception_type": "DAMAGED_GOODS"},
        )
        exc_id = report_resp.json()["data"]["exception_id"]
        client.patch(
            f"/api/v1/orders/delivery-exceptions/{exc_id}/resolve",
            headers={"Authorization": f"Bearer {data['v_token']}"},
            json={"resolution_type": "FULL_REFUND"},
        )
        resp = client.patch(
            f"/api/v1/orders/delivery-exceptions/{exc_id}/resolve",
            headers={"Authorization": f"Bearer {data['v_token']}"},
            json={"resolution_type": "NO_ACTION"},
        )
        assert resp.status_code in (409, 422)


class TestExceptionEscalation:
    def test_escalate_exception(self, client):
        data = _seed_delivered(uuid4().hex[:8])
        report_resp = client.post(
            f"/api/v1/orders/{data['oi']}/delivery-exceptions",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"delivery_id": data["di"], "order_id": data["oi"],
                  "exception_type": "VENDOR_NO_SHOW"},
        )
        exc_id = report_resp.json()["data"]["exception_id"]
        resp = client.patch(
            f"/api/v1/orders/delivery-exceptions/{exc_id}/escalate",
            headers={"Authorization": f"Bearer {data['v_token']}"},
            json={"reason": "Vendor unresponsive for 24h"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "ESCALATED"
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT target_user_id, target_organization_id
                    FROM outbox_events
                    WHERE event_name='DELIVERY_EXCEPTION_ESCALATED'
                      AND aggregate_id=%s
                      AND target_organization_id=%s
                    LIMIT 1
                    """,
                    (exc_id, data["oo"]),
                )
                event = cur.fetchone()
                assert event is not None
                assert str(event["target_organization_id"]) == data["oo"]
        finally:
            conn.close()


class TestExceptionQuery:
    def test_list_exceptions_for_order(self, client):
        data = _seed_delivered(uuid4().hex[:8])
        client.post(
            f"/api/v1/orders/{data['oi']}/delivery-exceptions",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"delivery_id": data["di"], "order_id": data["oi"],
                  "exception_type": "DAMAGED_GOODS"},
        )
        resp = client.get(
            f"/api/v1/orders/{data['oi']}/delivery-exceptions",
            headers={"Authorization": f"Bearer {data['r_token']}"},
        )
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1

    def test_get_single_exception(self, client):
        data = _seed_delivered(uuid4().hex[:8])
        report_resp = client.post(
            f"/api/v1/orders/{data['oi']}/delivery-exceptions",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"delivery_id": data["di"], "order_id": data["oi"],
                  "exception_type": "DAMAGED_GOODS"},
        )
        exc_id = report_resp.json()["data"]["exception_id"]
        resp = client.get(
            f"/api/v1/orders/delivery-exceptions/{exc_id}",
            headers={"Authorization": f"Bearer {data['r_token']}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["exception_type"] == "DAMAGED_GOODS"


class TestExceptionSecureAccess:
    def test_unauthenticated_cannot_report(self, client):
        data = _seed_delivered(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/delivery-exceptions",
            json={"delivery_id": data["di"], "order_id": data["oi"],
                  "exception_type": "DAMAGED_GOODS"},
        )
        assert resp.status_code == 401

    def test_vendor_cannot_report_exception(self, client):
        data = _seed_delivered(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/delivery-exceptions",
            headers={"Authorization": f"Bearer {data['v_token']}"},
            json={"delivery_id": data["di"], "order_id": data["oi"],
                  "exception_type": "DAMAGED_GOODS"},
        )
        assert resp.status_code in (403, 422)
