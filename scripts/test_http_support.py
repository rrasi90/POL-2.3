"""HTTP tests for Support Cases -- Stage 31.

Tests case creation, listing, retrieval, messaging, transition, secure access.
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


def _seed_support(suffix, *, include_ops=False):
    """Seed retailer + vendor + org infrastructure for support tests."""
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            ru = str(uuid4()); ro = str(uuid4()); ri = str(uuid4())
            vu = str(uuid4()); vo = str(uuid4()); vi = str(uuid4())

            cur.execute(
                "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'R', 'RETAILER_OWNER')",
                (ru, f"+9891{uuid4().int % 100000000:08d}"),
            )
            cur.execute(
                "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'RO', 'RETAILER', 'ACTIVE')",
                (ro,),
            )
            cur.execute(
                "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'RETAILER_OWNER', 'ACTIVE')",
                (str(uuid4()), ro, ru),
            )
            cur.execute(
                "INSERT INTO retailers (id, user_id, organization_id, store_name, city, neighborhood, address) VALUES (%s, %s, %s, 'S', 'Ahvaz', 'N', 'A')",
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
                "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')",
                (str(uuid4()), vo, vu),
            )
            cur.execute(
                "INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman, status) "
                "VALUES (%s, %s, %s, 'V', 'Ahvaz', 1000000, 'ACTIVE')",
                (vi, vu, vo),
            )

            ou = str(uuid4()); oo = str(uuid4())
            if include_ops:
                cur.execute(
                    "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'OPS', 'OPS_AGENT')",
                    (ou, f"+9891{uuid4().int % 100000000:08d}"),
                )
                cur.execute(
                    "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'OO', 'OPERATOR', 'ACTIVE')",
                    (oo,),
                )
                cur.execute(
                    "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'OPS_AGENT', 'ACTIVE')",
                    (str(uuid4()), oo, ou),
                )

            rs = _create_session(cur, ru, ro)
            vs = _create_session(cur, vu, vo)
            os_s = _create_session(cur, ou, oo) if include_ops else None

        conn.commit()
        rt = encode_access_token(ru, rs, ro, "RETAILER_OWNER")
        vt = encode_access_token(vu, vs, vo, "VENDOR_OWNER")
        ot = encode_access_token(ou, os_s, oo, "OPS_AGENT") if include_ops else None
        return {"r_token": rt, "v_token": vt, "o_token": ot, "ru": ru, "ro": ro, "vu": vu, "vo": vo, "vi": vi, "ou": ou, "oo": oo}
    finally:
        conn.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app, raise_server_exceptions=False)


class TestCreateSupportCase:
    def test_create_case(self, client):
        data = _seed_support(uuid4().hex[:8])
        resp = client.post(
            "/api/v1/support/cases",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"case_type": "ORDER_INQUIRY", "subject": "Where is my delivery?"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["case_type"] == "ORDER_INQUIRY"
        assert body["data"]["status"] == "OPEN"
        assert "case_number" in body["data"]

    def test_create_case_with_high_priority(self, client):
        data = _seed_support(uuid4().hex[:8])
        resp = client.post(
            "/api/v1/support/cases",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"case_type": "PAYMENT_ASSISTANCE", "subject": "Payment issue",
                  "priority": "HIGH"},
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["priority"] == "HIGH"


    def test_related_order_must_belong_to_active_support_tenant(self, client):
        data = _seed_support(uuid4().hex[:8])
        conn = _db()
        other_user = str(uuid4())
        other_org = str(uuid4())
        other_retailer = str(uuid4())
        other_group = str(uuid4())
        other_order = str(uuid4())
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s,%s,'Other Retailer','RETAILER_OWNER')",
                    (other_user, f"+9891{uuid4().int % 100000000:08d}"),
                )
                cur.execute(
                    "INSERT INTO organizations (id,name,org_type,status) VALUES (%s,'Other Retailer Org','RETAILER','ACTIVE')",
                    (other_org,),
                )
                cur.execute(
                    """
                    INSERT INTO organization_memberships
                        (id,organization_id,user_id,role,status)
                    VALUES (%s,%s,%s,'RETAILER_OWNER','ACTIVE')
                    """,
                    (str(uuid4()), other_org, other_user),
                )
                cur.execute(
                    """
                    INSERT INTO retailers
                        (id,user_id,organization_id,store_name,city,neighborhood,address)
                    VALUES (%s,%s,%s,'Other Store','Ahvaz','Other','Other Address')
                    """,
                    (other_retailer, other_user, other_org),
                )
                cur.execute(
                    """
                    INSERT INTO order_groups
                        (id,retailer_id,total_amount_toman,group_status)
                    VALUES (%s,%s,1000000,'ACTIVE')
                    """,
                    (other_group, other_retailer),
                )
                cur.execute(
                    """
                    INSERT INTO orders
                        (id,order_number,order_group_id,retailer_id,vendor_id,
                         order_status,total_amount_toman)
                    VALUES (%s,%s,%s,%s,%s,'DELIVERED',1000000)
                    """,
                    (other_order, f"ORD-SUP-{uuid4().hex[:10]}", other_group, other_retailer, data["vi"]),
                )
            conn.commit()

            resp = client.post(
                "/api/v1/support/cases",
                headers={"Authorization": f"Bearer {data['r_token']}"},
                json={
                    "case_type": "ORDER_INQUIRY",
                    "subject": "Cross-tenant related order regression",
                    "related_order_id": other_order,
                },
            )
            assert resp.status_code == 403
            body = resp.json()
            assert body["success"] is False
        finally:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM orders WHERE id=%s", (other_order,))
                cur.execute("DELETE FROM order_groups WHERE id=%s", (other_group,))
                cur.execute("DELETE FROM retailers WHERE id=%s", (other_retailer,))
                cur.execute("DELETE FROM organization_memberships WHERE organization_id=%s", (other_org,))
                cur.execute("DELETE FROM organizations WHERE id=%s", (other_org,))
                cur.execute("DELETE FROM users WHERE id=%s", (other_user,))
            conn.commit()
            conn.close()


class TestListSupportCases:
    def test_list_cases(self, client):
        data = _seed_support(uuid4().hex[:8])
        client.post(
            "/api/v1/support/cases",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"case_type": "GENERAL", "subject": "First case"},
        )
        client.post(
            "/api/v1/support/cases",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"case_type": "ORDER_INQUIRY", "subject": "Second case"},
        )
        resp = client.get(
            "/api/v1/support/cases",
            headers={"Authorization": f"Bearer {data['r_token']}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert len(body["data"]) >= 2


class TestGetSupportCase:
    def test_get_case_by_id(self, client):
        data = _seed_support(uuid4().hex[:8])
        create_resp = client.post(
            "/api/v1/support/cases",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"case_type": "GENERAL", "subject": "Test get"},
        )
        case_id = create_resp.json()["data"]["id"]
        resp = client.get(
            f"/api/v1/support/cases/{case_id}",
            headers={"Authorization": f"Bearer {data['r_token']}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == case_id

    def test_get_case_not_found(self, client):
        data = _seed_support(uuid4().hex[:8])
        resp = client.get(
            f"/api/v1/support/cases/{uuid4()}",
            headers={"Authorization": f"Bearer {data['r_token']}"},
        )
        assert resp.status_code == 404


class TestAddMessage:
    def test_add_message_to_case(self, client):
        data = _seed_support(uuid4().hex[:8])
        create_resp = client.post(
            "/api/v1/support/cases",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"case_type": "GENERAL", "subject": "Msg test"},
        )
        case_id = create_resp.json()["data"]["id"]
        resp = client.post(
            f"/api/v1/support/cases/{case_id}/messages",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"message_text": "Hello support team!"},
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["message_text"] == "Hello support team!"
        assert resp.json()["data"]["sender_type"] == "USER"


class TestListSupportMessages:
    def test_list_messages_excludes_internal_notes_and_returns_public_thread(self, client):
        data = _seed_support(uuid4().hex[:8], include_ops=True)
        create_resp = client.post(
            "/api/v1/support/cases",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"case_type": "GENERAL", "subject": "History test"},
        )
        assert create_resp.status_code == 201
        case_id = create_resp.json()["data"]["id"]

        first = client.post(
            f"/api/v1/support/cases/{case_id}/messages",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"message_text": "پیام خرده‌فروش"},
        )
        assert first.status_code == 201

        reply = client.post(
            f"/api/v1/support/cases/{case_id}/messages",
            headers={"Authorization": f"Bearer {data['o_token']}"},
            json={"message_text": "پاسخ پشتیبانی"},
        )
        assert reply.status_code == 201

        conn = _db()
        try:
            with conn.cursor() as cur:
                # Stabilize chronology for the endpoint ordering assertion.
                cur.execute(
                    """
                    UPDATE support_case_messages
                    SET created_at = now() - interval '2 seconds'
                    WHERE support_case_id = %s AND message_text = %s
                    """,
                    (case_id, "پیام خرده‌فروش"),
                )
                cur.execute(
                    """
                    UPDATE support_case_messages
                    SET created_at = now() - interval '1 seconds'
                    WHERE support_case_id = %s AND message_text = %s
                    """,
                    (case_id, "پاسخ پشتیبانی"),
                )
                cur.execute(
                    """
                    INSERT INTO support_case_messages
                        (id, support_case_id, sender_user_id, sender_type, message_text, is_internal)
                    VALUES (%s, %s, %s, 'AGENT', %s, TRUE)
                    """,
                    (str(uuid4()), case_id, data["ou"], "یادداشت داخلی تیم پشتیبانی"),
                )
            conn.commit()
        finally:
            conn.close()

        resp = client.get(
            f"/api/v1/support/cases/{case_id}/messages",
            headers={"Authorization": f"Bearer {data['r_token']}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        messages = body["data"]
        assert [m["message_text"] for m in messages] == ["پیام خرده‌فروش", "پاسخ پشتیبانی"]
        assert "یادداشت داخلی تیم پشتیبانی" not in [m["message_text"] for m in messages]
        timestamps = [m["created_at"] for m in messages]
        assert timestamps == sorted(timestamps)

    def test_list_messages_rejects_another_tenant(self, client):
        owner = _seed_support(uuid4().hex[:8])
        other = _seed_support(uuid4().hex[:8])
        create_resp = client.post(
            "/api/v1/support/cases",
            headers={"Authorization": f"Bearer {owner['r_token']}"},
            json={"case_type": "GENERAL", "subject": "Private history"},
        )
        case_id = create_resp.json()["data"]["id"]
        resp = client.get(
            f"/api/v1/support/cases/{case_id}/messages",
            headers={"Authorization": f"Bearer {other['r_token']}"},
        )
        assert resp.status_code == 403
        assert resp.json()["success"] is False


    def test_list_messages_rejects_same_user_in_wrong_active_organization(self, client):
        owner = _seed_support(uuid4().hex[:8])
        create_resp = client.post(
            "/api/v1/support/cases",
            headers={"Authorization": f"Bearer {owner['r_token']}"},
            json={"case_type": "GENERAL", "subject": "Tenant-bound history"},
        )
        assert create_resp.status_code == 201
        case_id = create_resp.json()["data"]["id"]

        other_org = str(uuid4())
        other_session = None
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Other active org', 'RETAILER', 'ACTIVE')",
                    (other_org,),
                )
                cur.execute(
                    "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'RETAILER_OWNER', 'ACTIVE')",
                    (str(uuid4()), other_org, owner["ru"]),
                )
                other_session = _create_session(cur, owner["ru"], other_org)
            conn.commit()
            other_token = encode_access_token(
                owner["ru"], other_session, other_org, "RETAILER_OWNER"
            )
            resp = client.get(
                f"/api/v1/support/cases/{case_id}/messages",
                headers={"Authorization": f"Bearer {other_token}"},
            )
            assert resp.status_code == 403
            assert resp.json()["success"] is False
        finally:
            with conn.cursor() as cur:
                if other_session:
                    cur.execute("DELETE FROM user_sessions WHERE id = %s", (other_session,))
                cur.execute("DELETE FROM organization_memberships WHERE organization_id = %s", (other_org,))
                cur.execute("DELETE FROM organizations WHERE id = %s", (other_org,))
            conn.commit()
            conn.close()


class TestSupportAssignment:
    def test_assign_case_uses_canonical_route(self, client):
        data = _seed_support(uuid4().hex[:8], include_ops=True)
        create_resp = client.post(
            "/api/v1/support/cases",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"case_type": "GENERAL", "subject": "Assign test"},
        )
        case_id = create_resp.json()["data"]["id"]
        resp = client.post(
            f"/api/v1/support/cases/{case_id}/assign",
            headers={"Authorization": f"Bearer {data['o_token']}"},
            json={"assignee_user_id": data["ou"]},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["assigned_to_user_id"] == data["ou"]

    def test_status_alias_uses_canonical_route(self, client):
        data = _seed_support(uuid4().hex[:8], include_ops=True)
        create_resp = client.post(
            "/api/v1/support/cases",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"case_type": "GENERAL", "subject": "Status route test"},
        )
        case_id = create_resp.json()["data"]["id"]
        resp = client.patch(
            f"/api/v1/support/cases/{case_id}/status",
            headers={"Authorization": f"Bearer {data['o_token']}"},
            json={"target_status": "IN_PROGRESS"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "IN_PROGRESS"

class TestTransitionCase:
    def test_transition_to_in_progress(self, client):
        data = _seed_support(uuid4().hex[:8], include_ops=True)
        create_resp = client.post(
            "/api/v1/support/cases",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"case_type": "GENERAL", "subject": "Transition test"},
        )
        case_id = create_resp.json()["data"]["id"]
        resp = client.patch(
            f"/api/v1/support/cases/{case_id}",
            headers={"Authorization": f"Bearer {data['o_token']}"},
            json={"target_status": "IN_PROGRESS"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "IN_PROGRESS"

    def test_transition_user_rejected(self, client):
        data = _seed_support(uuid4().hex[:8])
        create_resp = client.post(
            "/api/v1/support/cases",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"case_type": "GENERAL", "subject": "User transition"},
        )
        case_id = create_resp.json()["data"]["id"]
        resp = client.patch(
            f"/api/v1/support/cases/{case_id}",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"target_status": "IN_PROGRESS"},
        )
        assert resp.status_code == 403


class TestSupportSecureAccess:
    def test_unauthenticated_rejected(self, client):
        resp = client.get("/api/v1/support/cases")
        assert resp.status_code == 401

    def test_wrong_tenant_rejected(self, client):
        data = _seed_support(uuid4().hex[:8])
        create_resp = client.post(
            "/api/v1/support/cases",
            headers={"Authorization": f"Bearer {data['r_token']}"},
            json={"case_type": "GENERAL", "subject": "Tenant isolation"},
        )
        case_id = create_resp.json()["data"]["id"]
        resp = client.get(
            f"/api/v1/support/cases/{case_id}",
            headers={"Authorization": f"Bearer {data['v_token']}"},
        )
        assert resp.status_code == 403
