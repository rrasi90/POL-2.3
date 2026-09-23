"""HTTP tests for Field Tasks — Stage 35."""

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


def _seed(role="OPS_AGENT"):
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            uid = str(uuid4())
            org_id = str(uuid4())
            cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'F', %s)",
                        (uid, f"+9891{uuid4().hex[:8]}", role))
            org_type = "RETAILER" if role == "RETAILER_OWNER" else "OPERATOR"
            cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'FO', %s, 'ACTIVE')", (org_id, org_type))
            mem_role = role if role == "RETAILER_OWNER" else role
            cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, %s, 'ACTIVE')",
                        (str(uuid4()), org_id, uid, mem_role))
            ft_id = str(uuid4())
            cur.execute("INSERT INTO field_tasks (id, task_type, assigned_to_user_id, target_organization_id, status, notes) VALUES (%s, 'ONBOARD_RETAILER', %s, %s, 'ASSIGNED', 'Test task')",
                        (ft_id, uid, org_id))
            sid = _create_session(cur, uid, org_id)
        conn.commit()
        token = encode_access_token(uid, sid, org_id, role)
        return {"uid": uid, "org_id": org_id, "token": token, "ft_id": ft_id}
    finally:
        conn.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app, raise_server_exceptions=False)


class TestFieldTaskCRUD:
    def test_list_tasks(self, client):
        data = _seed()
        resp = client.get("/api/v1/field/tasks",
                          headers={"Authorization": f"Bearer {data['token']}"})
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1

    def test_get_task(self, client):
        data = _seed()
        resp = client.get(f"/api/v1/field/tasks/{data['ft_id']}",
                          headers={"Authorization": f"Bearer {data['token']}"})
        assert resp.status_code == 200
        assert resp.json()["data"]["task_type"] == "ONBOARD_RETAILER"

    def test_update_task(self, client):
        data = _seed()
        resp = client.patch(f"/api/v1/field/tasks/{data['ft_id']}",
                            headers={"Authorization": f"Bearer {data['token']}"},
                            json={"status": "IN_PROGRESS", "notes": "Updated notes"})
        assert resp.status_code == 200

    def test_create_task(self, client):
        data = _seed("ADMIN_SUPER")
        resp = client.post("/api/v1/field/tasks",
                           headers={"Authorization": f"Bearer {data['token']}"},
                           json={"task_type": "TRAIN_RETAILER", "assigned_to_user_id": data["uid"]})
        assert resp.status_code == 201
        assert resp.json()["data"]["task_type"] == "TRAIN_RETAILER"


class TestFieldTaskAccess:
    def test_retailer_cannot_create_task(self, client):
        data = _seed("RETAILER_OWNER")
        resp = client.post("/api/v1/field/tasks",
                           headers={"Authorization": f"Bearer {data['token']}"},
                           json={"task_type": "TRAIN_RETAILER", "assigned_to_user_id": data["uid"]})
        assert resp.status_code in (403, 422)

    def test_unauthenticated_rejected(self, client):
        resp = client.get("/api/v1/field/tasks")
        assert resp.status_code == 401
