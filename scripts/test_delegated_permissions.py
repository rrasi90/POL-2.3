"""Integration tests for D-026 / VD-15 delegated permissions."""

from __future__ import annotations

import os
from uuid import uuid4

import psycopg2
import pytest
from psycopg2.extras import RealDictCursor

from scripts.permissions import (
    effective_permissions,
    grant_permission,
    membership_permissions,
    require_permission,
    revoke_permission,
)


def _db():
    return psycopg2.connect(
        dbname=os.environ.get("POL_API_DB_NAME", "pol_test"),
        host=os.environ.get("POL_API_DB_HOST", os.environ.get("PGHOST", "127.0.0.1")),
        port=int(os.environ.get("POL_API_DB_PORT", os.environ.get("POL_PG_PORT", "5432"))),
        user=os.environ.get("POL_API_DB_USER", os.environ.get("PGUSER", "postgres")),
    )


@pytest.fixture
def permission_env():
    conn = _db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    owner_id = str(uuid4())
    staff_id = str(uuid4())
    vendor_org_id = str(uuid4())
    other_org_id = str(uuid4())
    owner_membership_id = str(uuid4())
    staff_membership_id = str(uuid4())
    other_membership_id = str(uuid4())

    try:
        cur.execute(
            "INSERT INTO users (id, phone_number, full_name, role, is_active) VALUES (%s,%s,%s,%s,TRUE)",
            (owner_id, f"+9891{uuid4().int % 100000000:08d}", "Permission Owner", "VENDOR_OWNER"),
        )
        cur.execute(
            "INSERT INTO users (id, phone_number, full_name, role, is_active) VALUES (%s,%s,%s,%s,TRUE)",
            (staff_id, f"+9891{uuid4().int % 100000000:08d}", "Permission Staff", "VENDOR_STAFF"),
        )
        other_user_id = str(uuid4())
        cur.execute(
            "INSERT INTO users (id, phone_number, full_name, role, is_active) VALUES (%s,%s,%s,%s,TRUE)",
            (other_user_id, f"+9891{uuid4().int % 100000000:08d}", "Other Org Owner", "VENDOR_OWNER"),
        )

        cur.execute(
            "INSERT INTO organizations (id,name,org_type,status) VALUES (%s,%s,'VENDOR','ACTIVE')",
            (vendor_org_id, "Permission Vendor"),
        )
        cur.execute(
            "INSERT INTO organizations (id,name,org_type,status) VALUES (%s,%s,'VENDOR','ACTIVE')",
            (other_org_id, "Other Vendor"),
        )
        cur.execute(
            "INSERT INTO organization_memberships (id,organization_id,user_id,role,status,is_primary) VALUES (%s,%s,%s,'VENDOR_OWNER','ACTIVE',TRUE)",
            (owner_membership_id, vendor_org_id, owner_id),
        )
        cur.execute(
            "INSERT INTO organization_memberships (id,organization_id,user_id,role,status,is_primary) VALUES (%s,%s,%s,'VENDOR_STAFF','ACTIVE',FALSE)",
            (staff_membership_id, vendor_org_id, staff_id),
        )
        cur.execute(
            "INSERT INTO organization_memberships (id,organization_id,user_id,role,status,is_primary) VALUES (%s,%s,%s,'VENDOR_OWNER','ACTIVE',TRUE)",
            (other_membership_id, other_org_id, other_user_id),
        )
        conn.commit()

        yield {
            "conn": conn,
            "cur": cur,
            "owner_id": owner_id,
            "staff_id": staff_id,
            "vendor_org_id": vendor_org_id,
            "other_org_id": other_org_id,
            "owner_membership_id": owner_membership_id,
            "staff_membership_id": staff_membership_id,
            "other_membership_id": other_membership_id,
            "other_user_id": other_user_id,
        }
    finally:
        conn.rollback()
        cur.execute("DELETE FROM delegated_permission_grants WHERE membership_id IN (%s,%s,%s)",
                    (owner_membership_id, staff_membership_id, other_membership_id))
        cur.execute("DELETE FROM permission_audit_events WHERE membership_id IN (%s,%s,%s)",
                    (owner_membership_id, staff_membership_id, other_membership_id))
        cur.execute("DELETE FROM organization_memberships WHERE id IN (%s,%s,%s)",
                    (owner_membership_id, staff_membership_id, other_membership_id))
        cur.execute("DELETE FROM organizations WHERE id IN (%s,%s)", (vendor_org_id, other_org_id))
        cur.execute("DELETE FROM users WHERE id IN (%s,%s,%s)", (owner_id, staff_id, other_user_id))
        conn.commit()
        cur.close()
        conn.close()


def test_delegated_permission_grant_effective_and_revoke(permission_env):
    env = permission_env

    with pytest.raises(PermissionError, match="not granted"):
        require_permission(
            env["cur"],
            env["staff_id"],
            env["vendor_org_id"],
            "inventory.adjust",
        )

    granted = grant_permission(
        env["cur"],
        env["owner_id"],
        env["vendor_org_id"],
        env["staff_membership_id"],
        "inventory.adjust",
        "warehouse lead needs stock correction authority",
        client="test",
    )
    assert granted["status"] == "GRANTED"

    effective = effective_permissions(
        env["cur"],
        env["staff_id"],
        env["vendor_org_id"],
    )
    assert "inventory.adjust" in effective["permissions"]

    details = membership_permissions(
        env["cur"],
        env["owner_id"],
        env["vendor_org_id"],
        env["staff_membership_id"],
    )
    assert details["role"] == "VENDOR_STAFF"
    assert "inventory.adjust" in details["effective_permissions"]

    revoked = revoke_permission(
        env["cur"],
        env["owner_id"],
        env["vendor_org_id"],
        env["staff_membership_id"],
        "inventory.adjust",
        "temporary duty ended",
        client="test",
    )
    assert revoked["status"] == "REVOKED"

    with pytest.raises(PermissionError, match="not granted"):
        require_permission(
            env["cur"],
            env["staff_id"],
            env["vendor_org_id"],
            "inventory.adjust",
        )


def test_privilege_ceiling_blocks_unsupported_owner_grant(permission_env):
    env = permission_env
    with pytest.raises(PermissionError, match="Privilege ceiling"):
        grant_permission(
            env["cur"],
            env["owner_id"],
            env["vendor_org_id"],
            env["staff_membership_id"],
            "payment.record",
            "invalid escalation test",
            client="test",
        )


def test_delegation_is_tenant_scoped(permission_env):
    env = permission_env
    with pytest.raises(KeyError, match="Target membership not found"):
        grant_permission(
            env["cur"],
            env["owner_id"],
            env["vendor_org_id"],
            env["other_membership_id"],
            "inventory.adjust",
            "cross tenant attempt",
            client="test",
        )


def test_permission_audit_is_append_only(permission_env):
    env = permission_env
    granted = grant_permission(
        env["cur"],
        env["owner_id"],
        env["vendor_org_id"],
        env["staff_membership_id"],
        "inventory.adjust",
        "audit mutation test",
        client="test",
    )
    conn = env["conn"]
    cur = env["cur"]
    cur.execute(
        "SELECT id FROM permission_audit_events WHERE membership_id=%s AND action='GRANT' ORDER BY created_at DESC LIMIT 1",
        (env["staff_membership_id"],),
    )
    audit_id = cur.fetchone()["id"]

    with pytest.raises(psycopg2.Error, match="append-only"):
        cur.execute(
            "UPDATE permission_audit_events SET reason='tampered' WHERE id=%s",
            (audit_id,),
        )
    conn.rollback()

    # The transaction is rolled back; verify the grant itself remains absent only
    # because the test transaction was intentionally aborted, not because audit
    # mutation succeeded.
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT id FROM permission_audit_events WHERE id=%s",
        (audit_id,),
    )
    assert cur.fetchone() is None
    cur.close()
    _ = granted


def test_vendor_editor_rejects_non_vendor_staff_target(permission_env):
    env = permission_env
    # The application-boundary vendor editor passes target_role=VENDOR_STAFF.
    # Exercise the underlying guard directly to prove a manager cannot retarget
    # a different membership/persona type through the vendor staff capability.
    with pytest.raises(ValueError, match="VENDOR_STAFF"):
        grant_permission(
            env["cur"],
            env["owner_id"],
            env["vendor_org_id"],
            env["owner_membership_id"],
            "inventory.adjust",
            "cross-role target test",
            client="test",
            target_role="VENDOR_STAFF",
        )

def test_vendor_staff_role_does_not_receive_order_accept_permission():
    from scripts.permissions import BASE_ROLE_PERMISSIONS

    assert "order.accept" not in BASE_ROLE_PERMISSIONS["VENDOR_STAFF"]
    assert "order.accept" in BASE_ROLE_PERMISSIONS["VENDOR_OWNER"]
\n

def test_owner_only_permissions_cannot_be_delegated_to_vendor_staff(permission_env):
    env = permission_env
    for permission_key in ("order.accept", "membership.manage"):
        with pytest.raises(PermissionError, match="cannot be delegated"):
            grant_permission(
                env["cur"],
                env["owner_id"],
                env["vendor_org_id"],
                env["staff_membership_id"],
                permission_key,
                "role ceiling regression",
                client="test",
            )
\n
def test_historical_owner_only_grant_cannot_become_effective(permission_env):
    env = permission_env
    env["cur"].execute(
        """
        INSERT INTO delegated_permission_grants
            (id, membership_id, permission_key, status, granted_by_user_id, reason)
        VALUES (%s, %s, 'order.accept', 'GRANTED', %s, 'legacy fixture')
        """,
        (str(uuid4()), env["staff_membership_id"], env["owner_id"]),
    )

    effective = effective_permissions(
        env["cur"],
        env["staff_id"],
        env["vendor_org_id"],
    )
    assert "order.accept" not in effective["permissions"]

    with pytest.raises(PermissionError, match="not granted"):
        require_permission(
            env["cur"],
            env["staff_id"],
            env["vendor_org_id"],
            "order.accept",
        )

    details = membership_permissions(
        env["cur"],
        env["owner_id"],
        env["vendor_org_id"],
        env["staff_membership_id"],
    )
    assert "order.accept" not in details["effective_permissions"]
    assert "order.accept" not in details["delegatable_permissions"]


def test_retailer_staff_order_accept_is_not_delegatable():
    from scripts.permissions import ROLE_DELEGATION_DENY

    assert "order.accept" in ROLE_DELEGATION_DENY["RETAILER_STAFF"]
