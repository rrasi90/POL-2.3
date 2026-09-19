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
