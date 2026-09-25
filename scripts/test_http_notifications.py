"""HTTP tests for Notification Logical Layer — Stage 32."""

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


def _db():
    port = int(os.environ.get("POL_API_DB_PORT") or os.environ.get("PGPORT", "5432"))
    return psycopg2.connect(
        dbname="pol_test",
        host=os.environ.get("PGHOST", "127.0.0.1"),
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


def _seed():
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            uid = str(uuid4())
            org_id = str(uuid4())
            cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'U', 'RETAILER_OWNER')",
                        (uid, f"+9891{uuid4().hex[:8]}"))
            cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'O', 'RETAILER', 'ACTIVE')", (org_id,))
            cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'RETAILER_OWNER', 'ACTIVE')",
                        (str(uuid4()), org_id, uid))
            notif_id = str(uuid4())
            cur.execute("INSERT INTO notifications (id, user_id, organization_id, event_name, title, body, priority) VALUES (%s, %s, %s, 'ORDER_ACCEPTED', 'Test', 'Body', 'NORMAL')",
                        (notif_id, uid, org_id))
            inbox_id = str(uuid4())
            cur.execute(
                """
                INSERT INTO user_inbox_items
                    (id, user_id, organization_id, notification_id, title, body, category, deep_link, is_read)
                VALUES (%s,%s,%s,%s,'Test','Body','ORDERS','/orders/test',FALSE)
                """,
                (inbox_id, uid, org_id, notif_id),
            )
            sid = _create_session(cur, uid, org_id)
        conn.commit()
        token = encode_access_token(uid, sid, org_id, "RETAILER_OWNER")
        return {"uid": uid, "org_id": org_id, "token": token, "notif_id": notif_id}
    finally:
        conn.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app, raise_server_exceptions=False)


class TestNotificationsList:
    def test_list_notifications(self, client):
        data = _seed()
        resp = client.get("/api/v1/notifications",
                          headers={"Authorization": f"Bearer {data['token']}"})
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1


class TestNotificationPreferences:
    def test_get_preferences(self, client):
        data = _seed()
        resp = client.get("/api/v1/notifications/preferences",
                          headers={"Authorization": f"Bearer {data['token']}"})
        assert resp.status_code == 200

    def test_update_preference(self, client):
        data = _seed()
        resp = client.put("/api/v1/notifications/preferences",
                          headers={"Authorization": f"Bearer {data['token']}"},
                          json={"event_name": "ORDER_ACCEPTED", "channel": "PUSH", "is_enabled": False})
        assert resp.status_code == 200
        assert resp.json()["data"]["is_enabled"] is False

    def test_invalid_channel_rejected(self, client):
        data = _seed()
        resp = client.put("/api/v1/notifications/preferences",
                          headers={"Authorization": f"Bearer {data['token']}"},
                          json={"event_name": "ORDER_ACCEPTED", "channel": "INVALID", "is_enabled": True})
        assert resp.status_code == 422


class TestNotificationAccess:
    def test_unauthenticated_rejected(self, client):
        resp = client.get("/api/v1/notifications")
        assert resp.status_code == 401

class TestDurableInbox:
    def test_list_and_unread_count(self, client):
        data = _seed()
        resp = client.get("/api/v1/inbox/items", headers={"Authorization": f"Bearer {data['token']}"})
        assert resp.status_code == 200
        payload = resp.json()["data"]
        assert payload["unread_count"] >= 1
        assert any(item["deep_link"] == "/orders/test" and item["is_read"] is False for item in payload["items"])

    def test_mark_one_read_is_tenant_scoped(self, client):
        data = _seed()
        listed = client.get("/api/v1/inbox/items", headers={"Authorization": f"Bearer {data['token']}"}).json()["data"]["items"]
        item_id = listed[0]["id"]
        resp = client.patch(f"/api/v1/inbox/items/{item_id}/read", headers={"Authorization": f"Bearer {data['token']}"})
        assert resp.status_code == 200
        assert resp.json()["data"]["is_read"] is True
        assert resp.json()["data"]["unread_count"] == 0

    def test_mark_all_read_is_idempotent(self, client):
        data = _seed()
        first = client.patch("/api/v1/inbox/items/read-all", headers={"Authorization": f"Bearer {data['token']}"})
        assert first.status_code == 200
        assert first.json()["data"]["unread_count"] == 0
        second = client.patch("/api/v1/inbox/items/read-all", headers={"Authorization": f"Bearer {data['token']}"})
        assert second.status_code == 200
        assert second.json()["data"]["marked_count"] == 0

    def test_notification_projection_contains_read_state(self, client):
        data = _seed()
        resp = client.get("/api/v1/notifications", headers={"Authorization": f"Bearer {data['token']}"})
        assert resp.status_code == 200
        item = next(row for row in resp.json()["data"] if row["id"] == data["notif_id"])
        assert item["is_read"] is False
        assert item["deep_link"] == "/orders/test"