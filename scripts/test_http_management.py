"""HTTP regression tests for the remediation management surface."""

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


def _session(cur, user_id, org_id):
    sid = str(uuid4())
    token = encode_access_token(user_id, sid, org_id, "SUPER_ADMIN")
    cur.execute(
        """
        INSERT INTO user_sessions
            (id, user_id, active_organization_id, token_hash, status, expires_at)
        VALUES (%s,%s,%s,%s,'ACTIVE',%s)
        """,
        (sid, user_id, org_id, hash_token(token), datetime.now(timezone.utc) + timedelta(hours=1)),
    )
    return sid, token


@pytest.fixture(scope="module")
def management_env():
    conn = _db()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        admin_user = str(uuid4())
        admin_org = str(uuid4())
        vendor_user = str(uuid4())
        vendor_org = str(uuid4())
        cur.execute(
            "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s,%s,'Management Admin','SUPER_ADMIN')",
            (admin_user, f"+9891{uuid4().hex[:8]}"),
        )
        cur.execute(
            "INSERT INTO organizations (id,name,org_type,status) VALUES (%s,'Ops Test','OPERATOR','ACTIVE')",
            (admin_org,),
        )
        cur.execute(
            """
            INSERT INTO organization_memberships
                (id,organization_id,user_id,role,status,is_primary)
            VALUES (%s,%s,%s,'SUPER_ADMIN','ACTIVE',TRUE)
            """,
            (str(uuid4()), admin_org, admin_user),
        )
        cur.execute(
            "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s,%s,'Management Vendor','VENDOR_OWNER')",
            (vendor_user, f"+9891{uuid4().hex[:8]}"),
        )
        cur.execute(
            "INSERT INTO organizations (id,name,org_type,status) VALUES (%s,'Vendor Test','VENDOR','ACTIVE')",
            (vendor_org,),
        )
        cur.execute(
            """
            INSERT INTO organization_memberships
                (id,organization_id,user_id,role,status,is_primary)
            VALUES (%s,%s,%s,'VENDOR_OWNER','ACTIVE',TRUE)
            """,
            (str(uuid4()), vendor_org, vendor_user),
        )
        sid_a, token_a = _session(cur, admin_user, admin_org)
        sid_v = str(uuid4())
        token_v = encode_access_token(vendor_user, sid_v, vendor_org, "VENDOR_OWNER")
        cur.execute(
            """
            INSERT INTO user_sessions
                (id,user_id,active_organization_id,token_hash,status,expires_at)
            VALUES (%s,%s,%s,%s,'ACTIVE',%s)
            """,
            (sid_v, vendor_user, vendor_org, hash_token(token_v), datetime.now(timezone.utc) + timedelta(hours=1)),
        )
    conn.commit()
    yield {
        "conn": conn,
        "admin": token_a,
        "vendor": token_v,
        "admin_user": admin_user,
        "admin_org": admin_org,
        "vendor_user": vendor_user,
        "vendor_org": vendor_org,
        "session_ids": [sid_a, sid_v],
    }
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM organization_memberships WHERE user_id IN (%s,%s)", (admin_user, vendor_user))
            cur.execute("DELETE FROM user_sessions WHERE user_id IN (%s,%s)", (admin_user, vendor_user))
            cur.execute("DELETE FROM users WHERE id IN (%s,%s)", (admin_user, vendor_user))
            cur.execute("DELETE FROM organizations WHERE id IN (%s,%s)", (admin_org, vendor_org))
        conn.commit()
    finally:
        conn.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app, raise_server_exceptions=False)


def test_vendor_customers_and_staff_are_tenant_scoped(client, management_env):
    resp = client.get(
        "/api/v1/vendors/customers",
        headers={"Authorization": f"Bearer {management_env['vendor']}"},
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert resp.json()["data"]["customers"] == []

    phone = f"+9891{uuid4().hex[:8]}"
    invite = client.post(
        "/api/v1/vendors/staff/invite",
        headers={"Authorization": f"Bearer {management_env['vendor']}"},
        json={"phone_number": phone, "full_name": "Invited Staff"},
    )
    assert invite.status_code == 201
    data = invite.json()["data"]
    assert data["role"] == "VENDOR_STAFF"
    assert data["status"] == "INVITED"

    conn = management_env["conn"]
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM organization_memberships
                WHERE organization_id=%s AND user_id=%s
                """,
                (management_env["vendor_org"], data["user_id"]),
            )
            cur.execute("DELETE FROM users WHERE id=%s", (data["user_id"],))
        conn.commit()
    finally:
        conn.rollback()


def test_only_vendor_owner_can_invite_staff(client, management_env):
    resp = client.post(
        "/api/v1/vendors/staff/invite",
        headers={"Authorization": f"Bearer {management_env['admin']}"},
        json={"phone_number": f"+9891{uuid4().hex[:8]}", "full_name": "Denied Staff"},
    )
    assert resp.status_code == 403


def test_admin_user_org_permission_and_global_returns_routes(client, management_env):
    headers = {"Authorization": f"Bearer {management_env['admin']}"}
    users = client.get("/api/v1/admin/users", headers=headers)
    orgs = client.get("/api/v1/admin/organizations", headers=headers)
    permissions = client.get("/api/v1/ops/permissions", headers=headers)
    returns = client.get("/api/v1/ops/returns", headers=headers)

    assert users.status_code == 200
    assert orgs.status_code == 200
    assert permissions.status_code == 200
    assert returns.status_code == 200
    assert "SUPER_ADMIN" in permissions.json()["data"]["roles"]


def test_management_routes_reject_unauthenticated(client):
    assert client.get("/api/v1/vendors/customers").status_code == 401
    assert client.get("/api/v1/admin/users").status_code == 401
    assert client.get("/api/v1/ops/permissions").status_code == 401
