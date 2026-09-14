"""Canonical tenant-safe feedback application boundary.

Legacy FeedbackService remains for existing isolated tests, but application code
must use these functions. User reads are scoped to the actor; admin reads and
replies are authorized through an ACTIVE OPERATOR membership.
"""

from __future__ import annotations

import uuid


class FeedbackAccessError(PermissionError):
    pass


class CanonicalFeedbackService:
    @staticmethod
    def _require_admin(cur, admin_user_id: str):
        cur.execute(
            """
            SELECT om.organization_id, om.role
            FROM organization_memberships om
            JOIN organizations o ON o.id = om.organization_id
            WHERE om.user_id = %s
              AND om.status = 'ACTIVE'
              AND o.org_type = 'OPERATOR'
              AND o.status = 'ACTIVE'
              AND om.role IN ('SUPER_ADMIN', 'OPS_ADMIN')
            LIMIT 1;
            """,
            (admin_user_id,),
        )
        if not cur.fetchone():
            raise FeedbackAccessError("Only active operator admins can access the feedback inbox.")

    @staticmethod
    def list_for_user(cur, user_id: str, organization_id: str):
        cur.execute(
            """
            SELECT *
            FROM feedback_submissions
            WHERE user_id = %s
              AND organization_id = %s
            ORDER BY created_at DESC;
            """,
            (user_id, organization_id),
        )
        return cur.fetchall()

    @classmethod
    def list_for_admin(cls, cur, admin_user_id: str, organization_id: str,
                       status: str = None, priority: str = None):
        cls._require_admin(cur, admin_user_id)
        query = """
            SELECT * FROM feedback_submissions
            WHERE organization_id = %s
        """
        params = [organization_id]
        if status:
            query += " AND status = %s"
            params.append(status)
        if priority:
            query += " AND priority = %s"
            params.append(priority)
        query += " ORDER BY created_at DESC"
        cur.execute(query, tuple(params))
        return cur.fetchall()

    @classmethod
    def reply(cls, cur, admin_user_id: str, feedback_id: str, reply_text: str,
              next_status: str = "IN_REVIEW"):
        cls._require_admin(cur, admin_user_id)
        if not reply_text.strip():
            raise ValueError("Feedback reply cannot be empty.")
        cur.execute(
            """
            SELECT id, user_id, organization_id, status
            FROM feedback_submissions
            WHERE id = %s
            FOR UPDATE;
            """,
            (feedback_id,),
        )
        feedback = cur.fetchone()
        if not feedback:
            raise KeyError("Feedback submission not found.")
        cur.execute(
            """
            UPDATE feedback_submissions
            SET admin_reply = %s,
                status = %s,
                assigned_to_user_id = COALESCE(assigned_to_user_id, %s),
                triaged_at = COALESCE(triaged_at, now()),
                updated_at = now()
            WHERE id = %s
            RETURNING *;
            """,
            (reply_text, next_status, admin_user_id, feedback_id),
        )
        updated = cur.fetchone()
        cur.execute(
            """
            INSERT INTO outbox_events
                (id,event_id,event_name,aggregate_type,aggregate_id,payload,status,
                 target_user_id,target_organization_id,dedupe_key)
            VALUES
                (%s,%s,'FEEDBACK_REPLIED','FEEDBACK',%s,%s,'PENDING',%s,%s,%s)
            ON CONFLICT (event_name, dedupe_key) WHERE dedupe_key IS NOT NULL DO UPDATE
            SET payload = EXCLUDED.payload;
            """,
            (
                str(uuid.uuid4()),
                "feedback_replied:" + str(feedback_id),
                str(feedback_id),
                {"feedback_id": str(feedback_id), "body": reply_text},
                str(feedback["user_id"]),
                str(feedback["organization_id"]) if feedback["organization_id"] else None,
                "feedback_replied:" + str(feedback_id),
            ),
        )
        return updated
