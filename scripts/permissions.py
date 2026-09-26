"""Canonical delegated-permission evaluation and management.

D-026 / VD-15:
Organization -> Membership -> Role -> Delegated Permissions -> Effective Access.

The permission keys below are the canonical examples defined by the Master Tree.
Base role permissions are the role ceiling; a delegated grant can only add a
permission already possessed by the granting actor. This implements least
privilege, tenant scope, deny-by-default, and privilege ceiling.
"""

from __future__ import annotations

from typing import Iterable

CANONICAL_PERMISSIONS = (
    "catalog.view",
    "catalog.manage",
    "inventory.view",
    "inventory.scan",
    "inventory.adjust",
    "price.view",
    "price.manage",
    "order.view",
    "order.accept",
    "order.fulfillment",
    "delivery.dispatch",
    "delivery.handoff",
    "payment.view",
    "payment.record",
    "settlement.view",
    "membership.manage",
    "reports.view",
)

# Baseline capabilities derived from the current Roles & Permissions matrix.
# Legacy aliases are normalized to their canonical current names.
BASE_ROLE_PERMISSIONS = {
    "ADMIN_SUPER": frozenset(CANONICAL_PERMISSIONS),
    "SUPER_ADMIN": frozenset(CANONICAL_PERMISSIONS),
    "OPS_AGENT": frozenset({
        "catalog.view",
        "catalog.manage",
        "inventory.view",
        "price.view",
        "price.manage",
        "order.view",
        "order.accept",
        "order.fulfillment",
        "delivery.dispatch",
        "delivery.handoff",
        "payment.view",
        "settlement.view",
        "reports.view",
    }),
    "OPS_ADMIN": frozenset({
        "catalog.view",
        "catalog.manage",
        "inventory.view",
        "price.view",
        "price.manage",
        "order.view",
        "order.accept",
        "order.fulfillment",
        "delivery.dispatch",
        "delivery.handoff",
        "payment.view",
        "settlement.view",
        "reports.view",
    }),
    "VENDOR_OWNER": frozenset({
        "catalog.view",
        "catalog.manage",
        "inventory.view",
        "inventory.scan",
        "inventory.adjust",
        "price.view",
        "price.manage",
        "order.view",
        "order.accept",
        "order.fulfillment",
        "delivery.dispatch",
        "payment.view",
        "settlement.view",
        "membership.manage",
        "reports.view",
    }),
    "VENDOR_STAFF": frozenset({
        "catalog.view",
        "inventory.view",
        "inventory.scan",
        "price.view",
        "order.view",
        "order.fulfillment",
        "delivery.dispatch",
    }),
    "RETAILER_OWNER": frozenset({
        "catalog.view",
        "order.view",
        "delivery.handoff",
        "payment.view",
        "payment.record",
        "settlement.view",
        "membership.manage",
        "reports.view",
    }),
    "RETAILER_STAFF": frozenset({
        "catalog.view",
        "order.view",
        "delivery.handoff",
    }),
    "FIELD_ACTIVATOR": frozenset({
        "catalog.view",
        "order.view",
        "delivery.handoff",
    }),
}

MANAGER_ROLES = frozenset({
    "ADMIN_SUPER",
    "SUPER_ADMIN",
    "VENDOR_OWNER",
    "RETAILER_OWNER",
})


def canonical_role(role: str) -> str:
    return {
        "SUPER_ADMIN": "ADMIN_SUPER",
        "OPS_ADMIN": "OPS_AGENT",
    }.get(role, role)


def _active_membership(cur, user_id: str, organization_id: str):
    cur.execute(
        """
        SELECT m.id AS membership_id,
               m.role,
               m.status AS membership_status,
               o.org_type,
               o.status AS organization_status,
               u.is_active AS user_is_active
        FROM organization_memberships m
        JOIN organizations o ON o.id = m.organization_id
        JOIN users u ON u.id = m.user_id
        WHERE m.user_id = %s
          AND m.organization_id = %s
        LIMIT 1
        """,
        (user_id, organization_id),
    )
    membership = cur.fetchone()
    if not membership or membership["membership_status"] != "ACTIVE":
        raise PermissionError("No active organization membership found.")
    if not membership["user_is_active"]:
        raise PermissionError("User is inactive.")
    if membership["organization_status"] != "ACTIVE":
        raise PermissionError("Organization is not active.")
    return membership


def effective_permissions(cur, user_id: str, organization_id: str) -> dict:
    membership = _active_membership(cur, user_id, organization_id)
    role = canonical_role(membership["role"])
    permissions = set(BASE_ROLE_PERMISSIONS.get(role, frozenset()))

    cur.execute(
        """
        SELECT permission_key
        FROM delegated_permission_grants
        WHERE membership_id = %s
          AND status = 'GRANTED'
        ORDER BY permission_key
        """,
        (membership["membership_id"],),
    )
    permissions.update(row["permission_key"] for row in cur.fetchall())

    return {
        "membership_id": str(membership["membership_id"]),
        "role": membership["role"],
        "permissions": sorted(permissions),
    }


def require_permission(cur, user_id: str, organization_id: str, permission_key: str) -> dict:
    if permission_key not in CANONICAL_PERMISSIONS:
        raise PermissionError("Unknown permission.")
    result = effective_permissions(cur, user_id, organization_id)
    if permission_key not in result["permissions"]:
        raise PermissionError(f"Permission '{permission_key}' is not granted.")
    return result


def grant_permission(
    cur,
    actor_user_id: str,
    organization_id: str,
    target_membership_id: str,
    permission_key: str,
    reason: str,
    client: str | None = None,
) -> dict:
    if permission_key not in CANONICAL_PERMISSIONS:
        raise ValueError("Unknown permission.")
    if not reason or not reason.strip():
        raise ValueError("A reason is required for a permission grant.")

    actor = effective_permissions(cur, actor_user_id, organization_id)
    if "membership.manage" not in actor["permissions"]:
        raise PermissionError("membership.manage is required to grant permissions.")
    if permission_key not in actor["permissions"]:
        raise PermissionError("Privilege ceiling prevents granting a permission the actor does not hold.")

    cur.execute(
        """
        SELECT m.id, m.user_id, m.role, m.status, o.status AS organization_status
        FROM organization_memberships m
        JOIN organizations o ON o.id = m.organization_id
        WHERE m.id = %s
          AND m.organization_id = %s
        FOR UPDATE
        """,
        (target_membership_id, organization_id),
    )
    target = cur.fetchone()
    if not target:
        raise KeyError("Target membership not found.")
    if target["status"] != "ACTIVE" or target["organization_status"] != "ACTIVE":
        raise ValueError("Target membership must be active.")

    cur.execute(
        """
        SELECT id, status
        FROM delegated_permission_grants
        WHERE membership_id = %s AND permission_key = %s
        FOR UPDATE
        """,
        (target_membership_id, permission_key),
    )
    current = cur.fetchone()

    if current and current["status"] == "GRANTED":
        return {
            "grant_id": str(current["id"]),
            "membership_id": str(target_membership_id),
            "permission_key": permission_key,
            "status": "GRANTED",
            "idempotent_replay": True,
        }

    if current:
        cur.execute(
            """
            UPDATE delegated_permission_grants
            SET status='GRANTED',
                granted_by_user_id=%s,
                granted_at=now(),
                revoked_by_user_id=NULL,
                revoked_at=NULL,
                reason=%s
            WHERE id=%s
            RETURNING id, status, granted_at
            """,
            (actor_user_id, reason.strip(), current["id"]),
        )
    else:
        cur.execute(
            """
            INSERT INTO delegated_permission_grants
                (membership_id, permission_key, status, granted_by_user_id, reason)
            VALUES (%s, %s, 'GRANTED', %s, %s)
            RETURNING id, status, granted_at
            """,
            (target_membership_id, permission_key, actor_user_id, reason.strip()),
        )
    grant = cur.fetchone()

    cur.execute(
        """
        INSERT INTO permission_audit_events
            (membership_id, permission_key, action, actor_user_id, reason, client)
        VALUES (%s, %s, 'GRANT', %s, %s, %s)
        """,
        (target_membership_id, permission_key, actor_user_id, reason.strip(), client),
    )

    return {
        "grant_id": str(grant["id"]),
        "membership_id": str(target_membership_id),
        "permission_key": permission_key,
        "status": grant["status"],
        "granted_at": grant["granted_at"].isoformat(),
        "idempotent_replay": False,
    }


def revoke_permission(
    cur,
    actor_user_id: str,
    organization_id: str,
    target_membership_id: str,
    permission_key: str,
    reason: str,
    client: str | None = None,
) -> dict:
    if permission_key not in CANONICAL_PERMISSIONS:
        raise ValueError("Unknown permission.")
    if not reason or not reason.strip():
        raise ValueError("A reason is required for a permission revoke.")

    actor = effective_permissions(cur, actor_user_id, organization_id)
    if "membership.manage" not in actor["permissions"]:
        raise PermissionError("membership.manage is required to revoke permissions.")

    cur.execute(
        """
        SELECT id, user_id, role, status
        FROM organization_memberships
        WHERE id=%s AND organization_id=%s
        FOR UPDATE
        """,
        (target_membership_id, organization_id),
    )
    target = cur.fetchone()
    if not target:
        raise KeyError("Target membership not found.")

    cur.execute(
        """
        SELECT id, status
        FROM delegated_permission_grants
        WHERE membership_id=%s AND permission_key=%s
        FOR UPDATE
        """,
        (target_membership_id, permission_key),
    )
    grant = cur.fetchone()
    if not grant:
        raise KeyError("Delegated permission grant not found.")
    if grant["status"] == "REVOKED":
        return {
            "grant_id": str(grant["id"]),
            "membership_id": str(target_membership_id),
            "permission_key": permission_key,
            "status": "REVOKED",
            "idempotent_replay": True,
        }

    cur.execute(
        """
        UPDATE delegated_permission_grants
        SET status='REVOKED',
            revoked_by_user_id=%s,
            revoked_at=now(),
            reason=%s
        WHERE id=%s
        RETURNING id, status, revoked_at
        """,
        (actor_user_id, reason.strip(), grant["id"]),
    )
    updated = cur.fetchone()

    cur.execute(
        """
        INSERT INTO permission_audit_events
            (membership_id, permission_key, action, actor_user_id, reason, client)
        VALUES (%s, %s, 'REVOKE', %s, %s, %s)
        """,
        (target_membership_id, permission_key, actor_user_id, reason.strip(), client),
    )

    return {
        "grant_id": str(updated["id"]),
        "membership_id": str(target_membership_id),
        "permission_key": permission_key,
        "status": updated["status"],
        "revoked_at": updated["revoked_at"].isoformat(),
        "idempotent_replay": False,
    }


def membership_permissions(cur, actor_user_id: str, organization_id: str, target_membership_id: str) -> dict:
    actor = effective_permissions(cur, actor_user_id, organization_id)
    if "membership.manage" not in actor["permissions"]:
        raise PermissionError("membership.manage is required to inspect delegated permissions.")

    cur.execute(
        """
        SELECT m.id, m.user_id, m.role, m.status, u.full_name, u.phone_number
        FROM organization_memberships m
        JOIN users u ON u.id=m.user_id
        WHERE m.id=%s AND m.organization_id=%s
        """,
        (target_membership_id, organization_id),
    )
    target = cur.fetchone()
    if not target:
        raise KeyError("Target membership not found.")

    base = sorted(BASE_ROLE_PERMISSIONS.get(canonical_role(target["role"]), frozenset()))
    cur.execute(
        """
        SELECT id, permission_key, status, granted_at, revoked_at,
               granted_by_user_id, revoked_by_user_id, reason
        FROM delegated_permission_grants
        WHERE membership_id=%s
        ORDER BY permission_key
        """,
        (target_membership_id,),
    )
    grants = []
    granted = set(base)
    for row in cur.fetchall():
        item = dict(row)
        item["id"] = str(item["id"])
        item["granted_by_user_id"] = str(item["granted_by_user_id"])
        if item["revoked_by_user_id"]:
            item["revoked_by_user_id"] = str(item["revoked_by_user_id"])
        if item["granted_at"]:
            item["granted_at"] = item["granted_at"].isoformat()
        if item["revoked_at"]:
            item["revoked_at"] = item["revoked_at"].isoformat()
        grants.append(item)
        if item["status"] == "GRANTED":
            granted.add(item["permission_key"])

    return {
        "membership_id": str(target["id"]),
        "user_id": str(target["user_id"]),
        "full_name": target["full_name"],
        "phone_number": target["phone_number"],
        "role": target["role"],
        "base_permissions": base,
        "delegated_grants": grants,
        "effective_permissions": sorted(granted),
    }


def permission_audit(cur, actor_user_id: str, organization_id: str, target_membership_id: str | None = None, limit: int = 100) -> list[dict]:
    actor = effective_permissions(cur, actor_user_id, organization_id)
    if "membership.manage" not in actor["permissions"]:
        raise PermissionError("membership.manage is required to inspect permission audit.")

    params = [organization_id]
    clause = "AND m.organization_id=%s"
    if target_membership_id:
        clause += " AND e.membership_id=%s"
        params.append(target_membership_id)
    params.append(limit)

    cur.execute(
        f"""
        SELECT e.id, e.membership_id, e.permission_key, e.action,
               e.actor_user_id, e.reason, e.client, e.created_at,
               u.full_name AS actor_name
        FROM permission_audit_events e
        JOIN organization_memberships m ON m.id=e.membership_id
        LEFT JOIN users u ON u.id=e.actor_user_id
        WHERE 1=1 {clause}
        ORDER BY e.created_at DESC, e.id DESC
        LIMIT %s
        """,
        tuple(params),
    )
    rows = []
    for row in cur.fetchall():
        item = dict(row)
        item["id"] = str(item["id"])
        item["membership_id"] = str(item["membership_id"])
        item["actor_user_id"] = str(item["actor_user_id"])
        item["created_at"] = item["created_at"].isoformat()
        rows.append(item)
    return rows
