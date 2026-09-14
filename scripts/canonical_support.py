"""Canonical support application boundary.

Support is not Dispute and is not Feedback. User access is restricted to the
user's own tenant/cases; operational agents must belong to an ACTIVE OPERATOR
organization. Assignment and internal notes are operator-only actions.
"""

from __future__ import annotations

import uuid


class SupportAccessError(PermissionError):
    pass


class SupportStateError(ValueError):
    pass


OPS_ROLES = {"ADMIN_SUPER", "OPS_AGENT", "SUPER_ADMIN", "OPS_ADMIN"}
USER_ROLES = {"RETAILER_OWNER", "RETAILER_STAFF", "VENDOR_OWNER", "VENDOR_STAFF"}


class CanonicalSupportService:
    @staticmethod
    def _actor(cur, user_id: str, organization_id: str | None = None):
        sql = """
            SELECT om.organization_id, om.role, o.org_type, om.status, o.status AS organization_status
            FROM organization_memberships om
            JOIN organizations o ON o.id = om.organization_id
            WHERE om.user_id = %s
              AND om.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
        """
        params = [user_id]
        if organization_id:
            sql += " AND om.organization_id = %s"
            params.append(organization_id)
        sql += " ORDER BY om.is_primary DESC"
        cur.execute(sql, tuple(params))
        return cur.fetchall()

    @classmethod
    def _is_ops_actor(cls, cur, user_id: str) -> bool:
        return any(r["org_type"] == "OPERATOR" and r["role"] in OPS_ROLES for r in cls._actor(cur, user_id))

    @staticmethod
    def _audit(cur, case_id: str, actor_user_id: str, action: str, allowed: bool, reason: str = None):
        cur.execute(
            """
            INSERT INTO support_case_access_audit
                (id, support_case_id, actor_user_id, action, allowed, reason)
            VALUES (%s,%s,%s,%s,%s,%s)
            """,
            (str(uuid.uuid4()), case_id, actor_user_id, action, allowed, reason),
        )

    @classmethod
    def create_case(cls, cur, actor_user_id: str, organization_id: str, case_type: str,
                    subject: str, related_order_id: str | None = None, priority: str = "NORMAL"):
        memberships = cls._actor(cur, actor_user_id, organization_id)
        if not memberships or not any(r["org_type"] in ("RETAILER", "VENDOR") and r["role"] in USER_ROLES for r in memberships):
            raise SupportAccessError("Case creation requires active membership in the target tenant.")
        case_id = str(uuid.uuid4())
        case_number = "SUP-" + case_id.replace("-", "")[:12].upper()
        cur.execute(
            """
            INSERT INTO support_cases
                (id, user_id, organization_id, case_number, case_type, priority, status,
                 related_order_id, subject, created_by_user_id)
            VALUES (%s,%s,%s,%s,%s,%s,'OPEN',%s,%s,%s)
            RETURNING *;
            """,
            (case_id, actor_user_id, organization_id, case_number, case_type, priority,
             related_order_id, subject, actor_user_id),
        )
        row = cur.fetchone()
        cls._audit(cur, case_id, actor_user_id, "CREATE", True)
        return row

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
        cls._audit(cur, case_id, actor_user_id, "INTERNAL_NOTE" if internal else "MESSAGE", True)
        return cur.fetchone()

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
        assignment = cur.fetchone()
        cur.execute(
            "UPDATE support_cases SET assigned_at = now(), updated_at = now(), status = CASE WHEN status = 'OPEN' THEN 'IN_PROGRESS' ELSE status END WHERE id = %s",
            (case_id,),
        )
        cls._audit(cur, case_id, actor_user_id, "ASSIGN", True)
        return assignment

    @classmethod
    def transition(cls, cur, actor_user_id: str, case_id: str, target_status: str,
                   resolution_code: str | None = None, resolution_note: str | None = None):
        allowed = {
            "OPEN": {"IN_PROGRESS", "CLOSED"},
            "IN_PROGRESS": {"WAITING_ON_USER", "RESOLVED", "CLOSED"},
            "WAITING_ON_USER": {"IN_PROGRESS", "RESOLVED", "CLOSED"},
            "RESOLVED": {"CLOSED", "IN_PROGRESS"},
            "CLOSED": set(),
        }
        if not cls._is_ops_actor(cur, actor_user_id):
            cls._audit(cur, case_id, actor_user_id, "UPDATE", False, "state transition is ops-only")
            raise SupportAccessError("Only operator staff may transition support case state.")
        cur.execute("SELECT status FROM support_cases WHERE id = %s FOR UPDATE", (case_id,))
        case = cur.fetchone()
        if not case:
            raise KeyError("Support case not found")
        if target_status not in allowed.get(case["status"], set()):
            raise SupportStateError(f"Invalid support transition: {case['status']} -> {target_status}")
        cur.execute(
            """
            UPDATE support_cases
            SET status = %s,
                updated_at = now(),
                resolved_at = CASE WHEN %s IN ('RESOLVED','CLOSED') THEN COALESCE(resolved_at, now()) ELSE resolved_at END,
                closed_by_user_id = CASE WHEN %s = 'CLOSED' THEN %s ELSE closed_by_user_id END,
                resolution_code = COALESCE(%s, resolution_code),
                resolution_note = COALESCE(%s, resolution_note)
            WHERE id = %s
            RETURNING *;
            """,
            (target_status, target_status, target_status, actor_user_id, resolution_code, resolution_note, case_id),
        )
        cls._audit(cur, case_id, actor_user_id, "UPDATE", True)
        return cur.fetchone()
