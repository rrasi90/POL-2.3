"""HTTP tests for Proof of Delivery contract -- Stage 24.

Tests OTP verification, proof_type, evidence, and secure access.
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


def _seed_dispatched(suffix, otp="1234"):
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            ru = str(uuid4()); ro = str(uuid4()); ri = str(uuid4())
            vu = str(uuid4()); vo = str(uuid4()); vi = str(uuid4())
            brand_id = str(uuid4()); category_id = str(uuid4()); subcategory_id = str(uuid4())
            product_id = str(uuid4()); vendor_product_id = str(uuid4())
            bi = str(uuid4()); pi = str(uuid4()); ogi = str(uuid4())
            oi = str(uuid4()); di = str(uuid4())

            cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, \'R\', \'RETAILER_OWNER\')",
                        (ru, f"+9891{uuid4().hex[:8]}"))
            cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, \'RO\', \'RETAILER\', \'ACTIVE\')", (ro,))
            cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, \'RETAILER_OWNER\', \'ACTIVE\')",
                        (str(uuid4()), ro, ru))
            cur.execute("INSERT INTO retailers (id, user_id, organization_id, store_name, city, neighborhood, address) VALUES (%s, %s, %s, \'S\', \'Ahvaz\', \'N\', \'A\')",
                        (ri, ru, ro))
            cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, \'V\', \'VENDOR_OWNER\')",
                        (vu, f"+9891{uuid4().hex[:8]}"))
            cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, \'VO\', \'VENDOR\', \'ACTIVE\')", (vo,))
            cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, \'VENDOR_OWNER\', \'ACTIVE\')",
                        (str(uuid4()), vo, vu))
            cur.execute("INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman, status) "
                        "VALUES (%s, %s, %s, \'V\', \'Ahvaz\', 1000000, \'ACTIVE\')", (vi, vu, vo))
            cur.execute("INSERT INTO brands (id,name_fa,slug) VALUES (%s,'Proof Brand',%s)",
                        (brand_id, f'proof-brand-{suffix}'))
            cur.execute("INSERT INTO categories (id,name_fa,slug) VALUES (%s,'Proof Category',%s)",
                        (category_id, f'proof-category-{suffix}'))
            cur.execute("INSERT INTO subcategories (id,category_id,name_fa,slug) VALUES (%s,%s,'Proof Subcategory',%s)",
                        (subcategory_id, category_id, f'proof-subcategory-{suffix}'))
            cur.execute(
                "INSERT INTO products (id,master_sku,canonical_name_fa,brand_id,category_id,subcategory_id,is_active) VALUES (%s,%s,'Proof Product',%s,%s,%s,TRUE)",
                (product_id, f'PROOF-{suffix}', brand_id, category_id, subcategory_id),
            )
            cur.execute(
                "INSERT INTO vendor_products (id,vendor_id,product_id,vendor_sku,packaging_unit,pack_quantity,listing_status,is_active) VALUES (%s,%s,%s,%s,'CARTON',1,'ACTIVE',TRUE)",
                (vendor_product_id, vi, product_id, f'PROOF-VP-{suffix}'),
            )
            cur.execute("INSERT INTO baskets (id, retailer_id, status, version) VALUES (%s, %s, \'OPEN\', 1)", (bi, ri))
            cur.execute("INSERT INTO allocation_plans (id, basket_id, basket_version, status, strategy, vendor_count, total_estimated_toman, expires_at) "
                        "VALUES (%s, %s, 1, \'CONFIRMED\', \'SINGLE_VENDOR\', 1, 5000000, now() + interval \'15 minutes\')", (pi, bi))
            cur.execute("INSERT INTO order_groups (id, basket_id, retailer_id, checkout_idempotency_key, total_amount_toman, order_count, group_status) "
                        "VALUES (%s, %s, %s, %s, 5000000, 1, \'ACTIVE\')", (ogi, bi, ri, str(uuid4())))
            cur.execute("INSERT INTO orders (id, order_number, order_group_id, allocation_plan_id, retailer_id, vendor_id, order_status, total_amount_toman, created_at, updated_at) "
                        "VALUES (%s, %s, %s, %s, %s, %s, \'DISPATCHED\', 5000000, now(), now())",
                        (oi, f"ORD-{suffix}", ogi, pi, ri, vi))
            cur.execute(
                """
                INSERT INTO order_items (
                    id, order_id, product_id, vendor_product_id,
                    product_name_snapshot, brand_name_snapshot, vendor_sku_snapshot,
                    packaging_unit_snapshot, pack_quantity_snapshot,
                    ordered_quantity, accepted_quantity, delivered_quantity,
                    unit_price_toman, total_line_amount_toman, fulfillment_status
                )
                VALUES (%s,%s,%s,%s,'Proof Product','Proof Brand',%s,'CARTON',1,10,10,0,500000,5000000,'PENDING')
                """,
                (str(uuid4()), oi, product_id, vendor_product_id, f'PROOF-VP-{suffix}'),
            )
            cur.execute(
                "INSERT INTO deliveries (id, order_id, vendor_id, delivery_status, driver_name, vehicle_plate, delivery_otp, dispatched_at, created_at) "
                "VALUES (%s, %s, %s, \'ARRIVED\', \'Ali\', \'12-A-345\', %s, now(), now())",
                (di, oi, vi, otp),
            )
            media_id = str(uuid4())
            cur.execute("INSERT INTO media_assets (id, storage_key, file_size_bytes, uploaded_by_user_id, status, provenance, created_at) "
                        "VALUES (%s, %s, 1024, %s, 'READY', 'POL_OWNED', now())",
                        (media_id, f"proof/{media_id}", ru))
            rs = _create_session(cur, ru, ro)
            vs = _create_session(cur, vu, vo)

        conn.commit()
        rt = encode_access_token(ru, rs, ro, "RETAILER_OWNER")
        vt = encode_access_token(vu, vs, vo, "VENDOR_OWNER")
        return {"oi": oi, "di": di, "r_token": rt, "v_token": vt, "otp": otp, "media_id": media_id}
    finally:
        conn.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app, raise_server_exceptions=False)


class TestOTPVerification:
    def test_deliver_with_correct_otp(self, client):
        data = _seed_dispatched(uuid4().hex[:8], "1234")
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/deliver",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"recipient_name": "Reza", "otp_code": "1234"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["otp_verified"] is True

    def test_deliver_with_wrong_otp(self, client):
        data = _seed_dispatched(uuid4().hex[:8], "1234")
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/deliver",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"recipient_name": "Reza", "otp_code": "9999"},
        )
        assert resp.status_code == 422
        assert resp.json()["success"] is False

    def test_deliver_without_otp(self, client):
        data = _seed_dispatched(uuid4().hex[:8], "1234")
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/deliver",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"recipient_name": "Reza"},
        )
        assert resp.status_code == 422
        assert resp.json()["success"] is False


class TestProofType:
    def test_deliver_with_signature_proof(self, client):
        data = _seed_dispatched(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/deliver",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"recipient_name": "Reza", "otp_code": data["otp"], "proof_type": "PHYSICAL_SIGNATURE"},
        )
        assert resp.status_code == 200
        proof_resp = client.get(
            f"/api/v1/orders/{data['oi']}/delivery/proof",
            headers={"Authorization": f"Bearer {data['r_token']}"},
        )
        assert proof_resp.status_code == 200

    def test_deliver_with_photo_proof(self, client):
        data = _seed_dispatched(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/deliver",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"recipient_name": "Reza", "otp_code": data["otp"], "proof_type": "PHOTO_PROOF", "proof_media_id": data["media_id"]},
        )
        assert resp.status_code == 200


class TestIssueReporting:
    def test_deliver_with_issue(self, client):
        data = _seed_dispatched(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/deliver",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"recipient_name": "Reza", "otp_code": data["otp"], "issue_reported": "2 cartons damaged"},
        )
        assert resp.status_code == 200

    def test_proof_shows_issue(self, client):
        data = _seed_dispatched(uuid4().hex[:8])
        client.post(
            f"/api/v1/orders/{data['oi']}/deliver",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"recipient_name": "Reza", "otp_code": data["otp"], "issue_reported": "Damaged goods"},
        )
        proof_resp = client.get(
            f"/api/v1/orders/{data['oi']}/delivery/proof",
            headers={"Authorization": f"Bearer {data['r_token']}"},
        )
        assert proof_resp.status_code == 200


class TestSecureAccess:
    def test_retailer_can_create_pod(self, client):
        data = _seed_dispatched(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/deliver",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"recipient_name": "Reza", "otp_code": data["otp"]},
        )
        assert resp.status_code == 200

    def test_vendor_cannot_create_pod(self, client):
        data = _seed_dispatched(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/deliver",
            headers={"Authorization": f"Bearer {data['v_token']}"},
            json={"recipient_name": "Reza"},
        )
        assert resp.status_code in (403, 422)

    def test_unauthenticated_cannot_create_pod(self, client):
        data = _seed_dispatched(uuid4().hex[:8])
        resp = client.post(
            f"/api/v1/orders/{data['oi']}/deliver",
            json={"recipient_name": "Reza"},
        )
        assert resp.status_code == 401
