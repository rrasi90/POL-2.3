"""HTTP tests for Payment Evidence contract -- Stage 27.

Tests evidence submission, listing, vendor verification, and access control.
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


def _seed_order(suffix):
    """Seed retailer, vendor, order with a PENDING payment, and return tokens."""
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            ru = str(uuid4()); ro = str(uuid4()); ri = str(uuid4())
            vu = str(uuid4()); vo = str(uuid4()); vi = str(uuid4())
            bi = str(uuid4()); pi = str(uuid4()); ogi = str(uuid4())
            oi = str(uuid4()); pay_id = str(uuid4())

            cur.execute(
                "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'R', 'RETAILER_OWNER')",
                (ru, f"+9891{uuid4().int % 100000000:08d}"),
            )
            cur.execute(
                "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'RO', 'RETAILER', 'ACTIVE')",
                (ro,),
            )
            cur.execute(
                "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) "
                "VALUES (%s, %s, %s, 'RETAILER_OWNER', 'ACTIVE')",
                (str(uuid4()), ro, ru),
            )
            cur.execute(
                "INSERT INTO retailers (id, user_id, organization_id, store_name, city, neighborhood, address) "
                "VALUES (%s, %s, %s, 'S', 'Ahvaz', 'N', 'A')",
                (ri, ru, ro),
            )
            cur.execute(
                "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'V', 'VENDOR_OWNER')",
                (vu, f"+9891{uuid4().int % 100000000:08d}"),
            )
            cur.execute(
                "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'VO', 'VENDOR', 'ACTIVE')",
                (vo,),
            )
            cur.execute(
                "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) "
                "VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')",
                (str(uuid4()), vo, vu),
            )
            cur.execute(
                "INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, "
                "min_order_value_toman, status) "
                "VALUES (%s, %s, %s, 'V', 'Ahvaz', 1000000, 'ACTIVE')",
                (vi, vu, vo),
            )
            cur.execute(
                "INSERT INTO baskets (id, retailer_id, status, version) VALUES (%s, %s, 'OPEN', 1)",
                (bi, ri),
            )
            cur.execute(
                "INSERT INTO allocation_plans (id, basket_id, basket_version, status, strategy, "
                "vendor_count, total_estimated_toman, expires_at) "
                "VALUES (%s, %s, 1, 'CONFIRMED', 'SINGLE_VENDOR', 1, 5000000, now() + interval '15 minutes')",
                (pi, bi),
            )
            cur.execute(
                "INSERT INTO order_groups (id, basket_id, retailer_id, checkout_idempotency_key, "
                "total_amount_toman, order_count, group_status) "
                "VALUES (%s, %s, %s, %s, 5000000, 1, 'ACTIVE')",
                (ogi, bi, ri, str(uuid4())),
            )
            cur.execute(
                "INSERT INTO orders (id, order_number, order_group_id, allocation_plan_id, retailer_id, "
                "vendor_id, order_status, total_amount_toman, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, 'DISPATCHED', 5000000, now(), now())",
                (oi, f"ORD-{suffix}", ogi, pi, ri, vi),
            )
            cur.execute(
                "INSERT INTO payments (id, order_id, retailer_id, vendor_id, amount_toman, "
                "payment_method, custody_model, payment_status) "
                "VALUES (%s, %s, %s, %s, 5000000, 'DIRECT_BANK_TRANSFER', 'NON_CUSTODIAL_DIRECT', 'PENDING')",
                (pay_id, oi, ri, vi),
            )

            rs = _create_session(cur, ru, ro)
            vs = _create_session(cur, vu, vo)

        conn.commit()
        r_token = encode_access_token(ru, rs, ro, "RETAILER_OWNER")
        v_token = encode_access_token(vu, vs, vo, "VENDOR_OWNER")
        return {"oi": oi, "pay_id": pay_id, "r_token": r_token, "v_token": v_token,
                "ru": ru, "vu": vu, "ro": ro, "vo": vo}
    finally:
        conn.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app, raise_server_exceptions=False)


class TestSubmitEvidence:
    def test_retailer_submits_bank_reference(self, client):
        data = _seed_order(uuid4().hex[:8])
        ref = f"TXN-{uuid4().hex[:12]}"
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/payments/evidence",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={
                "evidence_type": "BANK_REFERENCE",
                "reference_number": ref,
                "amount_toman": 5000000,
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["evidence_type"] == "BANK_REFERENCE"
        assert body["data"]["reference_number"] == ref
        assert body["data"]["amount_toman"] == 5000000

    def test_replay_of_same_external_reference_is_idempotent(self, client):
        data = _seed_order(uuid4().hex[:8])
        reference = f"TXN-REPLAY-{uuid4().hex[:10]}"
        payload = {
            "evidence_type": "BANK_REFERENCE",
            "reference_number": reference,
            "amount_toman": 5000000,
        }
        first = client.post(
            f"/api/v1/orders/{data['oi']}/payments/evidence",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json=payload,
        )
        second = client.post(
            f"/api/v1/orders/{data['oi']}/payments/evidence",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json=payload,
        )
        assert first.status_code == 201
        assert second.status_code == 201
        first_data = first.json()["data"]
        second_data = second.json()["data"]
        assert first_data["evidence_id"] == second_data["evidence_id"]
        assert second_data["idempotent_replay"] is True

    def test_vendor_submits_pos_reference(self, client):
        data = _seed_order(uuid4().hex[:8])
        ref = f"POS-{uuid4().hex[:12]}"
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/payments/evidence",
            headers={"Authorization": f"Bearer {data['v_token']}"},
            json={
                "evidence_type": "POS_REFERENCE",
                "reference_number": ref,
                "amount_toman": 5000000,
                "notes": "Terminal receipt attached",
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["evidence_type"] == "POS_REFERENCE"

    def test_invalid_evidence_type_rejected(self, client):
        data = _seed_order(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/payments/evidence",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={
                "evidence_type": "INVALID_TYPE",
                "reference_number": f"INV-{uuid4().hex[:8]}",
                "amount_toman": 100,
            },
        )
        assert resp.status_code == 422

    def test_list_evidence_for_order(self, client):
        data = _seed_order(uuid4().hex[:8])
        ref = f"TXN-LIST-{uuid4().hex[:8]}"
        client.post(
            f"/api/v1/orders/{data['oi']}/payments/evidence",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={
                "evidence_type": "BANK_REFERENCE",
                "reference_number": ref,
                "amount_toman": 5000000,
            },
        )
        resp = client.get(
            f"/api/v1/orders/{data['oi']}/payments/evidence",
            headers={"Authorization": f"Bearer {data['r_token']}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert len(body["data"]) >= 1
        assert body["data"][0]["reference_number"] == ref


class TestVerifyPayment:
    def test_vendor_verify_requires_matching_evidence(self, client):
        data = _seed_order(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/payments/verify",
            headers={"Authorization": f"Bearer {data['v_token']}"},
            json={"notes": "No evidence"},
        )
        assert resp.status_code == 422



    def test_canonical_direct_transfer_alias_and_payment_id_verify(self, client):
        data = _seed_order(uuid4().hex[:8])
        evidence = client.post(
            f"/api/v1/orders/{data['oi']}/payments/direct-transfer",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={
                "evidence_type": "BANK_REFERENCE",
                "reference_number": f"TXN-CANON-{uuid4().hex[:10]}",
                "amount_toman": 5000000,
            },
        )
        assert evidence.status_code == 201
        payment_id = evidence.json()["data"]["payment_id"]
        assert payment_id

        verified = client.post(
            f"/api/v1/orders/{data['oi']}/payments/{payment_id}/verify",
            headers={"Authorization": f"Bearer {data['v_token']}"},
            json={"notes": "Canonical payment id verification"},
        )
        assert verified.status_code == 200
        assert verified.json()["data"]["status"] == "SUCCESS"
        assert verified.json()["data"]["idempotent_replay"] is False

    def test_payment_id_verify_rejects_payment_from_other_order(self, client):
        first = _seed_order(uuid4().hex[:8])
        second = _seed_order(uuid4().hex[:8])
        evidence = client.post(
            f"/api/v1/orders/{first['oi']}/payments/direct-transfer",
            headers={"Authorization": f"Bearer {first['r_token']}"},
            json={
                "evidence_type": "BANK_REFERENCE",
                "reference_number": f"TXN-X-{uuid4().hex[:10]}",
                "amount_toman": 5000000,
            },
        )
        payment_id = evidence.json()["data"]["payment_id"]
        forged = client.post(
            f"/api/v1/orders/{second['oi']}/payments/{payment_id}/verify",
            headers={"Authorization": f"Bearer {second['v_token']}"},
            json={},
        )
        assert forged.status_code == 422

    def test_vendor_verifies_payment(self, client):
        data = _seed_order(uuid4().hex[:8])
        evidence = client.post(
            f"/api/v1/orders/{data['oi']}/payments/evidence",
            headers={"Authorization": f"Bearer {data['v_token']}"},
            json={
                "evidence_type": "BANK_REFERENCE",
                "reference_number": f"TXN-{uuid4().hex[:12]}",
                "amount_toman": 5000000,
                "notes": "Bank statement reference",
            },
        )
        assert evidence.status_code == 201

        resp = client.post(
            f"/api/v1/orders/{data['oi']}/payments/verify",
            headers={"Authorization": f"Bearer {data['v_token']}"},
            json={"notes": "Confirmed via bank statement"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["status"] == "SUCCESS"
        assert body["data"]["idempotent_replay"] is False

        replay = client.post(
            f"/api/v1/orders/{data['oi']}/payments/verify",
            headers={"Authorization": f"Bearer {data['v_token']}"},
            json={"notes": "Replay"},
        )
        assert replay.status_code == 200
        assert replay.json()["data"]["idempotent_replay"] is True

    def test_retailer_cannot_verify_payment(self, client):
        data = _seed_order(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/payments/verify",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={},
        )
        assert resp.status_code == 403


class TestAccessControl:
    def test_unauthenticated_cannot_submit(self, client):
        data = _seed_order(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/payments/evidence",
            json={
                "evidence_type": "BANK_REFERENCE",
                "reference_number": "X",
                "amount_toman": 100,
            },
        )
        assert resp.status_code == 401

    def test_wrong_tenant_rejected(self, client):
        data = _seed_order(uuid4().hex[:8])
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                other_u = str(uuid4()); other_o = str(uuid4())
                cur.execute(
                    "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'O', 'RETAILER_OWNER')",
                    (other_u, f"+9891{uuid4().int % 100000000:08d}"),
                )
                cur.execute(
                    "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'OTHER', 'RETAILER', 'ACTIVE')",
                    (other_o,),
                )
                cur.execute(
                    "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) "
                    "VALUES (%s, %s, %s, 'RETAILER_OWNER', 'ACTIVE')",
                    (str(uuid4()), other_o, other_u),
                )
                other_sess = _create_session(cur, other_u, other_o)
            conn.commit()
            other_token = encode_access_token(other_u, other_sess, other_o, "RETAILER_OWNER")
        finally:
            conn.close()

        resp = client.post(
            f"/api/v1/orders/{data['oi']}/payments/evidence",
            headers={"Authorization": f"Bearer {other_token}"},
            json={
                "evidence_type": "BANK_REFERENCE",
                "reference_number": f"WRONG-{uuid4().hex[:8]}",
                "amount_toman": 100,
            },
        )
        assert resp.status_code == 403


    def test_wrong_tenant_cannot_read_evidence(self, client):
        data = _seed_order(uuid4().hex[:8])
        conn = _db()
        other_token = None
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                other_u = str(uuid4()); other_o = str(uuid4())
                cur.execute(
                    "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s,%s,'OTHER','RETAILER_OWNER')",
                    (other_u, f"+9891{uuid4().int % 100000000:08d}"),
                )
                cur.execute(
                    "INSERT INTO organizations (id, name, org_type, status) VALUES (%s,'OTHER-READ','RETAILER','ACTIVE')",
                    (other_o,),
                )
                cur.execute(
                    "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) "
                    "VALUES (%s,%s,%s,'RETAILER_OWNER','ACTIVE')",
                    (str(uuid4()), other_o, other_u),
                )
                other_sess = _create_session(cur, other_u, other_o)
            conn.commit()
            other_token = encode_access_token(other_u, other_sess, other_o, "RETAILER_OWNER")
        finally:
            conn.close()

        resp = client.get(
            f"/api/v1/orders/{data['oi']}/payments/evidence",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        assert resp.status_code == 403

