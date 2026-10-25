"""Canonical Support case service with tenant-safe access and lifecycle controls."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone


class SupportAccessError(PermissionError):
    pass


class SupportStateError(ValueError):
    pass


OPS_ROLES = {"ADMIN_SUPER", "OPS_AGENT", "SUPER_ADMIN", "OPS_ADMIN"}


class CanonicalSupportService:
    @staticmethod
    def _is_ops_actor(cur, actor_user_id: str) -> bool:
        cur.execute(
            """
            SELECT 1
            FROM organization_memberships om
            JOIN organizations o ON o.id = om.organization_id
            WHERE om.user_id = %s
              AND om.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
              AND o.org_type = 'OPERATOR'
              AND om.role = ANY(%s)
            LIMIT 1;
            """,
            (actor_user_id, list(OPS_ROLES)),
        )
        return cur.fetchone() is not None

    @staticmethod
    def _audit(cur, case_id, actor_user_id, action, allowed, reason=None):
        cur.execute(
            """
            INSERT INTO support_case_access_audit
                (id,support_case_id,actor_user_id,action,allowed,reason)
            VALUES (%s,%s,%s,%s,%s,%s);
            """,
            (str(uuid.uuid4()), case_id, actor_user_id, action, allowed, reason),
        )

    @staticmethod
    def _new_case_number() -> str:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        return f"POL-SUP-{stamp}-{uuid.uuid4().hex[:8].upper()}"

    @classmethod
    def create_case(cls, cur, actor_user_id, organization_id, case_type, subject,
                    related_order_id=None, priority="NORMAL"):
        # The support case tenant and the optional related order tenant must
        # resolve to the same commercial organization. Never allow a caller to
        # plant a cross-tenant order reference into a support case.
        cur.execute(
            """
            SELECT 1
            FROM organization_memberships om
            JOIN organizations o ON o.id = om.organization_id
            WHERE om.user_id=%s
              AND om.organization_id=%s
              AND om.status='ACTIVE'
              AND o.status='ACTIVE'
            LIMIT 1
            """,
            (actor_user_id, organization_id),
        )
        if not cur.fetchone():
            raise SupportAccessError("Actor is not an active member of the support organization.")

        if related_order_id:
            cur.execute(
                """
                SELECT 1
                FROM orders o
                JOIN retailers r ON r.id=o.retailer_id
                JOIN vendors v ON v.id=o.vendor_id
                WHERE o.id=%s
                  AND (%s = r.organization_id OR %s = v.organization_id)
                LIMIT 1
                """,
                (related_order_id, organization_id, organization_id),
            )
            if not cur.fetchone():
                raise SupportAccessError(
                    "Related order does not belong to the active support organization."
                )

        for _ in range(3):
            case_id = str(uuid.uuid4())
            case_number = cls._new_case_number()
            try:
                cur.execute(
                    """
                    INSERT INTO support_cases
                        (id,user_id,organization_id,case_number,case_type,subject,
                         related_order_id,priority,status,created_by_user_id)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'OPEN',%s)
                    RETURNING *;
                    """,
                    (case_id, actor_user_id, organization_id, case_number, case_type,
                     subject, related_order_id, priority, actor_user_id),
                )
                return cur.fetchone()
            except Exception as exc:
                if getattr(exc, "pgcode", None) != "23505":
                    raise
        raise SupportStateError("Unable to allocate a unique support case number.")

    @classmethod
    def get_case(cls, cur, actor_user_id: str, case_id: str):
        cur.execute("SELECT * FROM support_cases WHERE id = %s", (case_id,))
        case = cur.fetchone()
        if not case:
            raise KeyError("Support case not found")
        allowed = str(case["user_id"]) == str(actor_user_id)
        if not allowed:
            allowed = cls._is_ops_actor(cur, actor_user_id)
        cls._audit(cur, case_id, actor_user_id, "READ", bool(allowed), None if allowed else "tenant/ops authorization failed")
        if not allowed:
            raise SupportAccessError("Actor is not authorized to read this support case.")
        return case

    @classmethod
    def list_messages(cls, cur, actor_user_id: str, case_id: str,
                     organization_id: str | None = None):
        # Reuse the case authorization and audit trail before reading any messages.
        case = cls.get_case(cur, actor_user_id, case_id)
        is_ops = cls._is_ops_actor(cur, actor_user_id)
        # A user can belong to several organizations. Do not let an otherwise
        # valid user token read a conversation while acting in another tenant.
        if (
            not is_ops
            and (
                organization_id is None
                or str(case["organization_id"]) != str(organization_id)
            )
        ):
            # Reuse the schema-approved READ action; the access-audit table
            # constrains action values and deliberately has no READ_MESSAGES enum.
            cls._audit(cur, case_id, actor_user_id, "READ", False,
                       "active tenant does not own this support case")
            raise SupportAccessError(
                "Support messages are not available in the active organization."
            )
        # Return only the minimum public message fields; never expose internal notes
        # or sender user IDs through the customer-facing history endpoint.
        cur.execute(
            """
            SELECT id, sender_type, message_text, created_at
            FROM support_case_messages
            WHERE support_case_id = %s AND is_internal = FALSE
            ORDER BY created_at ASC, id ASC;
            """,
            (case_id,),
        )
        return cur.fetchall()

    @classmethod
    def add_message(cls, cur, actor_user_id: str, case_id: str, message_text: str,
                    internal: bool = False, sender_type: str | None = None):
        if not message_text.strip():
            raise ValueError("Support message cannot be empty.")
        case = cls.get_case(cur, actor_user_id, case_id)
        is_ops = cls._is_ops_actor(cur, actor_user_id)
        if internal and not is_ops:
            cls._audit(cur, case_id, actor_user_id, "INTERNAL_NOTE", False, "internal notes are ops-only")
            raise SupportAccessError("Internal support notes are operator-only.")
        if sender_type is None:
            sender_type = "AGENT" if is_ops else "USER"
        if sender_type == "AGENT" and not is_ops:
            raise SupportAccessError("Agent messages require operator authorization.")
        cur.execute(
            """
            INSERT INTO support_case_messages
                (id, support_case_id, sender_user_id, sender_type, message_text, is_internal)
            VALUES (%s,%s,%s,%s,%s,%s)
            RETURNING *;
            """,
            (str(uuid.uuid4()), case["id"], actor_user_id, sender_type, message_text, internal),
        )
        message = cur.fetchone()
        cls._audit(cur, case_id, actor_user_id, "INTERNAL_NOTE" if internal else "MESSAGE", True)
        return message

    @classmethod
    def assign(cls, cur, actor_user_id: str, case_id: str, assignee_user_id: str):
        if not cls._is_ops_actor(cur, actor_user_id):
            cls._audit(cur, case_id, actor_user_id, "ASSIGN", False, "assignments are ops-only")
            raise SupportAccessError("Only operator staff may assign cases.")
        if not cls._is_ops_actor(cur, assignee_user_id):
            raise SupportAccessError("Support cases can only be assigned to active operator staff.")
        cur.execute("SELECT status FROM support_cases WHERE id = %s FOR UPDATE", (case_id,))
        case = cur.fetchone()
        if not case:
            raise KeyError("Support case not found")
        cur.execute(
            "UPDATE support_case_assignments SET is_active = FALSE WHERE support_case_id = %s AND is_active = TRUE",
            (case_id,),
        )
        cur.execute(
            """
            INSERT INTO support_case_assignments
                (id, support_case_id, assigned_to_user_id, assigned_by_user_id, is_active)
            VALUES (%s,%s,%s,%s,TRUE)
            RETURNING *;
            """,
            (str(uuid.uuid4()), case_id, assignee_user_id, actor_user_id),
        )
        row = cur.fetchone()
        cls._audit(cur, case_id, actor_user_id, "ASSIGN", True)
        return row

    @classmethod
    def list_cases(cls, cur, actor_user_id: str, organization_id: str):
        cur.execute(
            """
            SELECT id, user_id, organization_id, case_number, case_type, subject,
                   related_order_id, priority, status, created_by_user_id,
                   created_at, updated_at
            FROM support_cases
            WHERE organization_id = %s
            ORDER BY created_at DESC;
            """,
            (organization_id,),
        )
        cases = cur.fetchall()
        for case in cases:
            allowed = str(case["user_id"]) == str(actor_user_id)
            if not allowed:
                allowed = cls._is_ops_actor(cur, actor_user_id)
            if not allowed:
                raise SupportAccessError("Actor is not authorized to list support cases for this organization.")
        return cases

    @classmethod
    def transition(cls, cur, actor_user_id, case_id, target_status,
                   resolution_code=None, resolution_note=None):
        case = cls.get_case(cur, actor_user_id, case_id)
        is_ops = cls._is_ops_actor(cur, actor_user_id)
        if not is_ops:
            raise SupportAccessError("Only operator staff may transition support cases.")
        allowed = {
            "OPEN": {"IN_PROGRESS", "WAITING_ON_USER", "RESOLVED", "CLOSED"},
            "IN_PROGRESS": {"WAITING_ON_USER", "RESOLVED", "CLOSED"},
            "WAITING_ON_USER": {"IN_PROGRESS", "RESOLVED", "CLOSED"},
            "RESOLVED": {"CLOSED", "IN_PROGRESS"},
            "CLOSED": set(),
        }
        current = case["status"]
        if target_status not in allowed.get(current, set()):
            raise SupportStateError(f"Illegal support transition {current} -> {target_status}")
        cur.execute(
            """
            UPDATE support_cases
            SET status=%s,
                resolution_code=%s,
                resolution_note=%s,
                closed_by_user_id=CASE WHEN %s='CLOSED' THEN %s ELSE closed_by_user_id END,
                updated_at=now()
            WHERE id=%s
            RETURNING *;
            """,
            (target_status, resolution_code, resolution_note,
             target_status, actor_user_id, case_id),
        )
        updated = cur.fetchone()
        cls._audit(cur, case_id, actor_user_id, "CLOSE" if target_status == "CLOSED" else "UPDATE", True)
        return updated
