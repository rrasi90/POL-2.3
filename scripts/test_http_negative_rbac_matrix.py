"""Negative / RBAC HTTP matrix (TODO-014).

Every case asserts the canonical transport contract:
    AuthError -> 401, PermissionError -> 403, KeyError -> 404,
    ConflictError -> 409, ValueError -> 422, RequestValidationError -> 422.

Fixtures reuse the real-PostgreSQL order seeder from the Delivery/POD suite so
the calls hit the authenticated HTTP path (JWT + DB session + membership), not
a stubbed boundary.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import psycopg2
import pytest
from fastapi.testclient import TestClient

from scripts.api.main import app
from scripts.auth_boundary import encode_access_token, hash_token
from scripts.test_http_delivery_pod_g440_451 import _seed_dispatch

API = "/api/v1"


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


def _session(cur, user_id, org_id, *, status="ACTIVE", expires_in_hours=1):
    session_id = str(uuid4())
    cur.execute(
        "INSERT INTO user_sessions (id, user_id, active_organization_id, token_hash, status, expires_at) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (
            session_id,
            user_id,
            org_id,
            hash_token(session_id),
            status,
            datetime.now(timezone.utc) + timedelta(hours=expires_in_hours),
        ),
    )
    return session_id


def _admin_token():
    """SUPER_ADMIN on an OPERATOR organization, backed by a real session."""
    conn = _db()
    try:
        with conn.cursor() as cur:
            user_id, org_id = str(uuid4()), str(uuid4())
            cur.execute(
                "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s,%s,'Admin','SUPER_ADMIN')",
                (user_id, f"+9893{uuid4().hex[:8]}"),
            )
            cur.execute(
                "INSERT INTO organizations (id, name, org_type, status) VALUES (%s,'OPS','OPERATOR','ACTIVE')",
                (org_id,),
            )
            cur.execute(
                "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) "
                "VALUES (%s,%s,%s,'SUPER_ADMIN','ACTIVE')",
                (str(uuid4()), org_id, user_id),
            )
            sid = _session(cur, user_id, org_id)
        conn.commit()
        return encode_access_token(user_id, sid, org_id, "SUPER_ADMIN")
    finally:
        conn.close()


def _h(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def client():
    return TestClient(app, raise_server_exceptions=False)


class TestAuthenticationRequired:
    """AuthError must surface as 401 with the canonical error envelope."""

    def test_order_read_without_header_is_401(self, client):
        data = _seed_dispatch(uuid4().hex[:8])
        resp = client.get(f"{API}/orders/{data['oi']}")
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "INVALID_ACCESS_TOKEN"

    def test_basket_read_without_header_is_401(self, client):
        resp = client.get(f"{API}/baskets/current")
        assert resp.status_code == 401

    def test_admin_audit_logs_without_header_is_401(self, client):
        resp = client.get(f"{API}/admin/audit-logs")
        assert resp.status_code == 401

    def test_malformed_bearer_token_is_401(self, client):
        data = _seed_dispatch(uuid4().hex[:8])
        resp = client.get(f"{API}/orders/{data['oi']}", headers={"Authorization": "Bearer not-a-jwt"})
        assert resp.status_code == 401

    def test_revoked_session_is_401(self, client):
        data = _seed_dispatch(uuid4().hex[:8])
        conn = _db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM user_sessions WHERE user_id = %s ORDER BY created_at DESC LIMIT 1",
                    (data["ru"],),
                )
                row = cur.fetchone()
                cur.execute("UPDATE user_sessions SET status = 'REVOKED' WHERE id = %s", (row[0],))
            conn.commit()
        finally:
            conn.close()
        resp = client.get(f"{API}/orders/{data['oi']}", headers=_h(data["r_token"]))
        assert resp.status_code == 401

    def test_expired_status_session_is_401(self, client):
        """Access tokens are JWT-expiry bound; an EXPIRED session row must still be rejected."""
        data = _seed_dispatch(uuid4().hex[:8])
        conn = _db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM user_sessions WHERE user_id = %s ORDER BY created_at DESC LIMIT 1",
                    (data["ru"],),
                )
                row = cur.fetchone()
                cur.execute("UPDATE user_sessions SET status = 'EXPIRED' WHERE id = %s", (row[0],))
            conn.commit()
        finally:
            conn.close()
        resp = client.get(f"{API}/orders/{data['oi']}", headers=_h(data["r_token"]))
        assert resp.status_code == 401


class TestRoleBoundaries:
    """A valid session with the wrong role must be 403, never 404-as-oracle."""

    def test_retailer_cannot_read_admin_audit_logs(self, client):
        data = _seed_dispatch(uuid4().hex[:8])
        resp = client.get(f"{API}/admin/audit-logs", headers=_h(data["r_token"]))
        assert resp.status_code == 403
        assert resp.json()["error"]["code"] == "FORBIDDEN"

    def test_retailer_cannot_accept_vendor_order(self, client):
        data = _seed_dispatch(uuid4().hex[:8])
        resp = client.post(f"{API}/orders/{data['oi']}/accept", headers=_h(data["r_token"]))
        assert resp.status_code == 403

    def test_retailer_cannot_dispatch(self, client):
        data = _seed_dispatch(uuid4().hex[:8])
        resp = client.post(
            f"{API}/orders/{data['oi']}/dispatch",
            headers=_h(data["r_token"]),
            json={"driver_name": "Ali", "vehicle_plate": "12-A-345"},
        )
        assert resp.status_code == 403

    def test_admin_token_reaches_admin_surface(self, client):
        resp = client.get(f"{API}/admin/audit-logs", headers=_h(_admin_token()))
        assert resp.status_code == 200


class TestTenantIsolation:
    """Cross-tenant access must not reveal another retailer's order."""

    def test_other_retailer_cannot_read_order(self, client):
        owner = _seed_dispatch(uuid4().hex[:8])
        stranger = _seed_dispatch(uuid4().hex[:8])
        resp = client.get(f"{API}/orders/{owner['oi']}", headers=_h(stranger["r_token"]))
        assert resp.status_code in (403, 404)

    def test_other_retailer_cannot_read_timeline(self, client):
        owner = _seed_dispatch(uuid4().hex[:8])
        stranger = _seed_dispatch(uuid4().hex[:8])
        resp = client.get(f"{API}/orders/{owner['oi']}/timeline", headers=_h(stranger["r_token"]))
        assert resp.status_code in (403, 404)


class TestMissingResources:
    def test_unknown_order_is_404(self, client):
        data = _seed_dispatch(uuid4().hex[:8])
        resp = client.get(f"{API}/orders/{uuid4()}", headers=_h(data["r_token"]))
        assert resp.status_code == 404

    def test_unknown_product_is_404(self, client):
        data = _seed_dispatch(uuid4().hex[:8])
        resp = client.get(f"{API}/catalog/products/{uuid4()}", headers=_h(data["r_token"]))
        assert resp.status_code == 404

    def test_unknown_order_group_is_404(self, client):
        data = _seed_dispatch(uuid4().hex[:8])
        resp = client.get(f"{API}/orders/group/{uuid4()}", headers=_h(data["r_token"]))
        assert resp.status_code == 404

    def test_unknown_delivery_exception_is_404(self, client):
        data = _seed_dispatch(uuid4().hex[:8])
        resp = client.get(f"{API}/orders/delivery-exceptions/{uuid4()}", headers=_h(data["r_token"]))
        assert resp.status_code == 404


class TestInvalidTransitionsAndPayloads:
    def test_stale_allocation_plan_checkout_is_409(self, client):
        """G-326: stale basket/plan must surface as 409 CONFLICT, not 422."""
        data = _seed_dispatch(uuid4().hex[:8])
        conn = _db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT ap.id, ap.basket_id FROM allocation_plans ap "
                    "JOIN baskets b ON b.id = ap.basket_id "
                    "JOIN retailers r ON r.id = b.retailer_id WHERE r.user_id = %s LIMIT 1",
                    (data["ru"],),
                )
                plan_id, basket_id = cur.fetchone()
                cur.execute("UPDATE baskets SET version = version + 1 WHERE id = %s", (basket_id,))
            conn.commit()
        finally:
            conn.close()
        resp = client.post(
            f"{API}/orders",
            headers={**_h(data["r_token"]), "Idempotency-Key": str(uuid4())},
            json={
                "allocation_plan_id": str(plan_id),
                "delivery_address": "Ahvaz, Test Street 1",
                "preferred_payment_method": "POS_DRIVER",
            },
        )
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "CONFLICT"

    def test_delivery_stage_out_of_order_is_conflict(self, client):
        """PICKED_UP on an already-DELIVERED delivery must be a state conflict, not a success."""
        data = _seed_dispatch(uuid4().hex[:8], delivery_status="DELIVERED")
        resp = client.post(f"{API}/orders/{data['oi']}/delivery/picked-up", headers=_h(data["v_token"]))
        assert resp.status_code in (409, 422)

    def test_basket_item_without_required_fields_is_422(self, client):
        data = _seed_dispatch(uuid4().hex[:8])
        conn = _db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT b.id FROM baskets b JOIN retailers r ON r.id = b.retailer_id WHERE r.user_id = %s LIMIT 1",
                    (data["ru"],),
                )
                basket_id = cur.fetchone()[0]
        finally:
            conn.close()
        resp = client.post(f"{API}/baskets/{basket_id}/items", headers=_h(data["r_token"]), json={})
        assert resp.status_code == 422
        assert resp.json()["error"]["code"] == "VALIDATION_ERROR"

    def test_negative_basket_quantity_is_422(self, client):
        data = _seed_dispatch(uuid4().hex[:8])
        conn = _db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT b.id FROM baskets b JOIN retailers r ON r.id = b.retailer_id WHERE r.user_id = %s LIMIT 1",
                    (data["ru"],),
                )
                basket_id = cur.fetchone()[0]
        finally:
            conn.close()
        resp = client.post(
            f"{API}/baskets/{basket_id}/items",
            headers=_h(data["r_token"]),
            json={"vendor_product_id": str(uuid4()), "quantity": -3},
        )
        assert resp.status_code == 422

    def test_media_presign_with_empty_body_is_422(self, client):
        data = _seed_dispatch(uuid4().hex[:8])
        resp = client.post(f"{API}/media/presigned-url", headers=_h(data["r_token"]), json={})
        assert resp.status_code == 422

    def test_invalid_delivery_stage_is_422(self, client):
        data = _seed_dispatch(uuid4().hex[:8], delivery_status="ARRIVED")
        resp = client.post(f"{API}/orders/{data['oi']}/deliver", headers=_h(data["r_token"]), json={})
        assert resp.status_code == 422
