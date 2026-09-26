"""Stage-11 evidence tests for the Delivery/POD chain (G-440..G-451).

Covers the canonical operational state machine (ASSIGNED -> PICKED_UP ->
IN_TRANSIT -> ARRIVED -> DELIVERED, FAILED semantics), concurrent POD
idempotency, delivered_quantity invariants, proof validation, and
terminal-state evidence consistency.
"""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import psycopg2
import pytest
from fastapi.testclient import TestClient
from psycopg2.extras import RealDictCursor

from scripts.api.main import app
from scripts.auth_boundary import encode_access_token, hash_token


@pytest.fixture(scope="module", autouse=True)
def _api_test_environment():
    os.environ["POL_API_DB_NAME"] = "pol_test"
    os.environ.setdefault("POL_API_DB_HOST", os.environ.get("PGHOST", "127.0.0.1"))
    os.environ.setdefault(
        "POL_API_DB_PORT",
        os.environ.get("POL_API_DB_PORT") or os.environ.get("PGPORT") or "5432",
    )
    os.environ["ENVIRONMENT"] = "test"


def _db():
    port = int(os.environ.get("POL_API_DB_PORT") or os.environ.get("PGPORT", "5432"))
    return psycopg2.connect(
        dbname="pol_test",
        host=os.environ.get("POL_API_DB_HOST", os.environ.get("PGHOST", "127.0.0.1")),
        port=port,
        user=os.environ.get("PGUSER", "postgres"),
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


def _seed_dispatch(suffix, *, delivery_status="ASSIGNED", otp="1234",
                   ordered=10, accepted=10):
    """Dispatched order + item + delivery in the requested stage."""
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            ru, ro, ri = str(uuid4()), str(uuid4()), str(uuid4())
            vu, vo, vi = str(uuid4()), str(uuid4()), str(uuid4())
            bi, pi, ogi = str(uuid4()), str(uuid4()), str(uuid4())
            oi, oii, di = str(uuid4()), str(uuid4()), str(uuid4())
            brand_id, category_id, subcategory_id = str(uuid4()), str(uuid4()), str(uuid4())
            product_id, vendor_product_id = str(uuid4()), str(uuid4())
            cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s,%s,'R','RETAILER_OWNER')",
                        (ru, f"+9891{uuid4().hex[:8]}"))
            cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s,'RO','RETAILER','ACTIVE')", (ro,))
            cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s,%s,%s,'RETAILER_OWNER','ACTIVE')",
                        (str(uuid4()), ro, ru))
            cur.execute("INSERT INTO retailers (id, user_id, organization_id, store_name, city, neighborhood, address) VALUES (%s,%s,%s,'S','Ahvaz','N','A')",
                        (ri, ru, ro))
            cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s,%s,'V','VENDOR_OWNER')",
                        (vu, f"+9891{uuid4().hex[:8]}"))
            cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s,'VO','VENDOR','ACTIVE')", (vo,))
            cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s,%s,%s,'VENDOR_OWNER','ACTIVE')",
                        (str(uuid4()), vo, vu))
            cur.execute("INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman, status) "
                        "VALUES (%s,%s,%s,'V','Ahvaz',1000000,'ACTIVE')", (vi, vu, vo))
            cur.execute("INSERT INTO baskets (id, retailer_id, status, version) VALUES (%s,%s,'OPEN',1)", (bi, ri))
            cur.execute("INSERT INTO allocation_plans (id, basket_id, basket_version, status, strategy, vendor_count, total_estimated_toman, expires_at) "
                        "VALUES (%s,%s,1,'CONFIRMED','SINGLE_VENDOR',1,5000000, now() + interval '15 minutes')", (pi, bi))
            cur.execute("INSERT INTO order_groups (id, basket_id, retailer_id, checkout_idempotency_key, total_amount_toman, order_count, group_status) "
                        "VALUES (%s,%s,%s,%s,5000000,1,'ACTIVE')", (ogi, bi, ri, str(uuid4())))
            cur.execute("INSERT INTO brands (id, name_fa, slug) VALUES (%s,'Seed Brand',%s)", (brand_id, f"sb-{suffix}"))
            cur.execute("INSERT INTO categories (id, name_fa, slug) VALUES (%s,'Seed Cat',%s)", (category_id, f"sc-{suffix}"))
            cur.execute("INSERT INTO subcategories (id, category_id, name_fa, slug) VALUES (%s,%s,'Seed Sub',%s)",
                        (subcategory_id, category_id, f"ss-{suffix}"))
            cur.execute("INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id) "
                        "VALUES (%s,%s,'Seed Product',%s,%s,%s)",
                        (product_id, f"SEED-{suffix}", brand_id, category_id, subcategory_id))
            cur.execute("INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity, listing_status, is_active) "
                        "VALUES (%s,%s,%s,%s,'CARTON',1,'ACTIVE',TRUE)", (vendor_product_id, vi, product_id, f"SEED-VP-{suffix}"))
            cur.execute("INSERT INTO orders (id, order_number, order_group_id, allocation_plan_id, retailer_id, vendor_id, order_status, total_amount_toman) "
                        "VALUES (%s,%s,%s,%s,%s,%s,'DISPATCHED',5000000)", (oi, f"ORD-{suffix}", ogi, pi, ri, vi))
            cur.execute(
                """
                INSERT INTO order_items (
                    id, order_id, product_id, vendor_product_id,
                    product_name_snapshot, brand_name_snapshot, vendor_sku_snapshot,
                    packaging_unit_snapshot, pack_quantity_snapshot,
                    ordered_quantity, accepted_quantity,
                    delivered_quantity, unit_price_toman, total_line_amount_toman,
                    fulfillment_status
                ) VALUES (%s,%s,%s,%s,'Seed Product','Seed Brand',%s,'CARTON',1,%s,%s,0,500000,5000000,'PENDING')
                """,
                (oii, oi, product_id, vendor_product_id, f"SEED-VP-{suffix}", ordered, accepted),
            )
            cur.execute(
                "INSERT INTO deliveries (id, order_id, vendor_id, delivery_status, driver_name, vehicle_plate, delivery_otp, dispatched_at, created_at) "
                "VALUES (%s,%s,%s,%s,'Ali','12-A-345',%s, now(), now())",
                (di, oi, vi, delivery_status, otp),
            )
            rs = _create_session(cur, ru, ro)
            vs = _create_session(cur, vu, vo)
        conn.commit()
        return {
            "oi": oi, "oii": oii, "di": di,
            "ru": ru,
            "r_token": encode_access_token(ru, rs, ro, "RETAILER_OWNER"),
            "v_token": encode_access_token(vu, vs, vo, "VENDOR_OWNER"),
            "otp": otp, "ordered": ordered, "accepted": accepted,
        }
    finally:
        conn.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app, raise_server_exceptions=False)


def _h(token):
    return {"Authorization": f"Bearer {token}"}


def _stage(client, data, stage):
    return client.post(f"/api/v1/orders/{data['oi']}/delivery/{stage}", headers=_h(data["v_token"]))


class TestG440ArrivedRuntime:
    def test_full_stage_chain_persists_timestamps_and_timeline(self, client):
        data = _seed_dispatch(uuid4().hex[:8])
        for stage in ("picked-up", "in-transit", "arrived"):
            resp = _stage(client, data, stage)
            assert resp.status_code == 200, (stage, resp.text)
            assert resp.json()["data"]["delivery_status"] == stage.upper().replace("-", "_")
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT delivery_status, picked_up_at, in_transit_at, arrived_at FROM deliveries WHERE id=%s",
                    (data["di"],),
                )
                row = cur.fetchone()
                assert row["delivery_status"] == "ARRIVED"
                assert row["picked_up_at"] and row["in_transit_at"] and row["arrived_at"]
                cur.execute(
                    "SELECT to_status FROM delivery_timeline_events WHERE delivery_id=%s ORDER BY created_at",
                    (data["di"],),
                )
                assert [r["to_status"] for r in cur.fetchall()] == [
                    "PICKED_UP", "IN_TRANSIT", "ARRIVED",
                ]
        finally:
            conn.close()

    def test_illegal_jump_rejected(self, client):
        data = _seed_dispatch(uuid4().hex[:8], delivery_status="ASSIGNED")
        resp = _stage(client, data, "arrived")
        assert resp.status_code == 422

    def test_stage_replay_is_idempotent(self, client):
        data = _seed_dispatch(uuid4().hex[:8], delivery_status="ARRIVED")
        first = _stage(client, data, "arrived")
        assert first.status_code == 200
        assert first.json()["data"]["idempotent_replay"] is True

    def test_stage_requires_dispatched_order(self, client):
        data = _seed_dispatch(uuid4().hex[:8], delivery_status="ASSIGNED")
        conn = _db()
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE orders SET order_status='CANCELLED' WHERE id=%s", (data["oi"],))
            conn.commit()
        finally:
            conn.close()
        resp = _stage(client, data, "picked-up")
        assert resp.status_code == 422


class TestG441ConcurrentPod:
    def test_concurrent_confirmation_is_single_terminal_mutation(self, client):
        data = _seed_dispatch(uuid4().hex[:8], delivery_status="ARRIVED", otp="1234")

        def confirm(_):
            c = TestClient(app, raise_server_exceptions=False)
            return c.post(
                f"/api/v1/orders/{data['oi']}/deliver",
                headers=_h(data["r_token"]),
                json={"recipient_name": "Reza", "otp_code": "1234"},
            )

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(confirm, [0, 1]))

        statuses = sorted(r.status_code for r in results)
        assert statuses in ([200, 200], [200, 422]), [r.text for r in results]
        replays = [r.json()["data"].get("idempotent_replay") for r in results if r.status_code == 200]
        assert replays == [True] or sorted(replays) == [False, True]

        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT COUNT(*) AS c FROM proof_of_delivery WHERE delivery_id=%s", (data["di"],))
                assert cur.fetchone()["c"] == 1
                cur.execute("SELECT delivery_status, delivery_otp_used_at FROM deliveries WHERE id=%s", (data["di"],))
                row = cur.fetchone()
                assert row["delivery_status"] == "DELIVERED"
                assert row["delivery_otp_used_at"] is not None
                cur.execute("SELECT COUNT(*) AS c FROM deliveries WHERE order_id=%s AND delivery_status='DELIVERED'", (data["oi"],))
                assert cur.fetchone()["c"] == 1
        finally:
            conn.close()


class TestG442DeliveredQuantity:
    def test_full_delivery_fulfills_item(self, client):
        data = _seed_dispatch(uuid4().hex[:8], delivery_status="ARRIVED")
        resp = client.post(f"/api/v1/orders/{data['oi']}/deliver", headers=_h(data["r_token"]),
                           json={"recipient_name": "Reza", "otp_code": data["otp"]})
        assert resp.status_code == 200
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT delivered_quantity, fulfillment_status FROM order_items WHERE id=%s", (data["oii"],))
                row = cur.fetchone()
                assert row["delivered_quantity"] == 10
                assert row["fulfillment_status"] == "FULFILLED"
        finally:
            conn.close()

    def test_partial_delivery_derives_shortage(self, client):
        data = _seed_dispatch(uuid4().hex[:8], delivery_status="ARRIVED")
        resp = client.post(f"/api/v1/orders/{data['oi']}/deliver", headers=_h(data["r_token"]),
                           json={"recipient_name": "Reza", "otp_code": data["otp"],
                                 "delivered_items": [{"order_item_id": data["oii"], "delivered_quantity": 5}]})
        assert resp.status_code == 200
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT delivered_quantity, fulfillment_status FROM order_items WHERE id=%s", (data["oii"],))
                row = cur.fetchone()
                assert row["delivered_quantity"] == 5
                assert row["fulfillment_status"] == "SHORTAGE"
        finally:
            conn.close()

    def test_zero_delivery_derives_rejected(self, client):
        data = _seed_dispatch(uuid4().hex[:8], delivery_status="ARRIVED")
        resp = client.post(f"/api/v1/orders/{data['oi']}/deliver", headers=_h(data["r_token"]),
                           json={"recipient_name": "Reza", "otp_code": data["otp"],
                                 "delivered_items": [{"order_item_id": data["oii"], "delivered_quantity": 0}]})
        assert resp.status_code == 200
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT delivered_quantity, fulfillment_status FROM order_items WHERE id=%s", (data["oii"],))
                row = cur.fetchone()
                assert row["delivered_quantity"] == 0
                assert row["fulfillment_status"] == "REJECTED"
        finally:
            conn.close()

    def test_delivered_quantity_cannot_exceed_accepted(self, client):
        data = _seed_dispatch(uuid4().hex[:8], delivery_status="ARRIVED", ordered=10, accepted=5)
        resp = client.post(f"/api/v1/orders/{data['oi']}/deliver", headers=_h(data["r_token"]),
                           json={"recipient_name": "Reza", "otp_code": data["otp"],
                                 "delivered_items": [{"order_item_id": data["oii"], "delivered_quantity": 6}]})
        assert resp.status_code == 422

    def test_unknown_order_item_rejected(self, client):
        data = _seed_dispatch(uuid4().hex[:8], delivery_status="ARRIVED")
        resp = client.post(f"/api/v1/orders/{data['oi']}/deliver", headers=_h(data["r_token"]),
                           json={"recipient_name": "Reza", "otp_code": data["otp"],
                                 "delivered_items": [{"order_item_id": str(uuid4()), "delivered_quantity": 1}]})
        assert resp.status_code == 422

    def test_duplicate_order_item_rejected(self, client):
        data = _seed_dispatch(uuid4().hex[:8], delivery_status="ARRIVED")
        entry = {"order_item_id": data["oii"], "delivered_quantity": 5}
        resp = client.post(f"/api/v1/orders/{data['oi']}/deliver", headers=_h(data["r_token"]),
                           json={"recipient_name": "Reza", "otp_code": data["otp"],
                                 "delivered_items": [entry, dict(entry)]})
        assert resp.status_code == 422

    def test_missing_delivered_items_defaults_to_accepted(self, client):
        data = _seed_dispatch(uuid4().hex[:8], delivery_status="ARRIVED", ordered=10, accepted=7)
        resp = client.post(f"/api/v1/orders/{data['oi']}/deliver", headers=_h(data["r_token"]),
                           json={"recipient_name": "Reza", "otp_code": data["otp"]})
        assert resp.status_code == 200
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT delivered_quantity, fulfillment_status FROM order_items WHERE id=%s", (data["oii"],))
                row = cur.fetchone()
                assert row["delivered_quantity"] == 7
                assert row["fulfillment_status"] == "SHORTAGE"
        finally:
            conn.close()


class TestG447FailedSemantics:
    def test_failed_from_assigned_rejected(self, client):
        data = _seed_dispatch(uuid4().hex[:8], delivery_status="ASSIGNED")
        resp = client.post(f"/api/v1/orders/{data['oi']}/delivery/failed", headers=_h(data["v_token"]),
                           json={"reason": "truck breakdown"})
        assert resp.status_code == 422

    def test_failed_from_arrived_persists_reason_and_timeline(self, client):
        data = _seed_dispatch(uuid4().hex[:8], delivery_status="ARRIVED")
        resp = client.post(f"/api/v1/orders/{data['oi']}/delivery/failed", headers=_h(data["v_token"]),
                           json={"reason": "customer unavailable at ARRIVED handoff"})
        assert resp.status_code == 200
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT delivery_status, failed_at, failed_reason FROM deliveries WHERE id=%s", (data["di"],))
                row = cur.fetchone()
                assert row["delivery_status"] == "FAILED"
                assert row["failed_at"] is not None
                assert "customer unavailable" in row["failed_reason"]
                cur.execute(
                    "SELECT to_status FROM delivery_timeline_events WHERE delivery_id=%s ORDER BY created_at DESC LIMIT 1",
                    (data["di"],),
                )
                assert cur.fetchone()["to_status"] == "FAILED"
                cur.execute("SELECT order_status FROM orders WHERE id=%s", (data["oi"],))
                assert cur.fetchone()["order_status"] == "DISPATCHED"  # FAILED never implies DELIVERED
        finally:
            conn.close()

    def test_duplicate_failed_is_replay(self, client):
        data = _seed_dispatch(uuid4().hex[:8], delivery_status="ARRIVED")
        first = client.post(f"/api/v1/orders/{data['oi']}/delivery/failed", headers=_h(data["v_token"]),
                            json={"reason": "x"})
        assert first.status_code == 200
        second = client.post(f"/api/v1/orders/{data['oi']}/delivery/failed", headers=_h(data["v_token"]),
                             json={"reason": "x"})
        assert second.status_code == 200
        assert second.json()["data"]["idempotent_replay"] is True

    def test_deliver_rejected_after_failed(self, client):
        data = _seed_dispatch(uuid4().hex[:8], delivery_status="ARRIVED")
        client.post(f"/api/v1/orders/{data['oi']}/delivery/failed", headers=_h(data["v_token"]),
                    json={"reason": "x"})
        resp = client.post(f"/api/v1/orders/{data['oi']}/deliver", headers=_h(data["r_token"]),
                           json={"recipient_name": "Reza", "otp_code": data["otp"]})
        assert resp.status_code == 422


class TestG445G446ProofValidation:
    def test_photo_proof_requires_delivery_bound_media(self, client):
        data = _seed_dispatch(uuid4().hex[:8], delivery_status="ARRIVED")
        unbound = str(uuid4())
        conn = _db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO media_assets (id, storage_key, file_size_bytes, uploaded_by_user_id, status, provenance, checksum_sha256, upload_target_type, upload_target_id, created_at) "
                    "VALUES (%s,'x',1024,%s,'READY','POL_OWNED',%s,'ORDER',%s, now())",
                    (unbound, data["ru"], "b" * 64, data["oi"]),
                )
            conn.commit()
        finally:
            conn.close()
        resp = client.post(f"/api/v1/orders/{data['oi']}/deliver", headers=_h(data["r_token"]),
                           json={"recipient_name": "Reza", "otp_code": data["otp"],
                                 "proof_type": "PHOTO_PROOF", "proof_media_id": unbound})
        assert resp.status_code == 422

    def test_signature_proof_without_media_accepted(self, client):
        data = _seed_dispatch(uuid4().hex[:8], delivery_status="ARRIVED")
        resp = client.post(f"/api/v1/orders/{data['oi']}/deliver", headers=_h(data["r_token"]),
                           json={"recipient_name": "Reza", "otp_code": data["otp"],
                                 "proof_type": "PHYSICAL_SIGNATURE"})
        assert resp.status_code == 200
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT proof_type, otp_verified, proof_media_id FROM proof_of_delivery WHERE delivery_id=%s", (data["di"],))
                row = cur.fetchone()
                assert row["proof_type"] == "PHYSICAL_SIGNATURE"
                assert row["otp_verified"] is True
                assert row["proof_media_id"] is None
        finally:
            conn.close()


class TestG450G451PodPersistenceAndConsistency:
    def test_success_then_replay_single_pod_and_consistent_evidence(self, client):
        data = _seed_dispatch(uuid4().hex[:8], delivery_status="ARRIVED")
        first = client.post(f"/api/v1/orders/{data['oi']}/deliver", headers=_h(data["r_token"]),
                            json={"recipient_name": "Reza", "otp_code": data["otp"]})
        assert first.status_code == 200
        replay = client.post(f"/api/v1/orders/{data['oi']}/deliver", headers=_h(data["r_token"]),
                             json={"recipient_name": "Reza", "otp_code": data["otp"]})
        assert replay.status_code == 200
        assert replay.json()["data"]["idempotent_replay"] is True

        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT COUNT(*) AS c FROM proof_of_delivery WHERE delivery_id=%s", (data["di"],))
                assert cur.fetchone()["c"] == 1
                cur.execute("SELECT order_status FROM orders WHERE id=%s", (data["oi"],))
                assert cur.fetchone()["order_status"] == "DELIVERED"
                cur.execute("SELECT delivery_status FROM deliveries WHERE id=%s", (data["di"],))
                assert cur.fetchone()["delivery_status"] == "DELIVERED"
                cur.execute(
                    "SELECT event_name, COUNT(*) AS c FROM outbox_events "
                    "WHERE aggregate_id=%s AND event_name='ORDER_DELIVERED' GROUP BY event_name",
                    (data["oi"],),
                )
                events = cur.fetchall()
                assert len(events) == 1 and events[0]["c"] >= 1
                cur.execute(
                    "SELECT to_status FROM order_timeline_events WHERE order_id=%s AND to_status='DELIVERED'",
                    (data["oi"],),
                )
                assert cur.fetchall()  # one terminal timeline mutation exists
        finally:
            conn.close()
