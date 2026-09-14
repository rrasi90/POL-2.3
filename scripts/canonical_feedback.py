"""Canonical tenant-safe feedback application boundary.

Legacy FeedbackService remains for existing isolated tests, but application code
must use these functions. User reads are scoped to the actor; admin reads are
explicitly authorized against organization membership.
"""


class FeedbackAccessError(PermissionError):
    pass


class CanonicalFeedbackService:
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

    @staticmethod
    def list_for_admin(cur, admin_user_id: str, organization_id: str,
                       status: str = None, priority: str = None):
        cur.execute(
            """
            SELECT role
            FROM organization_memberships
            WHERE user_id = %s
              AND organization_id = %s
              AND status = 'ACTIVE'
              AND role IN ('ADMIN_SUPER', 'OPS_AGENT', 'SUPER_ADMIN', 'OPS_ADMIN');
            """,
            (admin_user_id, organization_id),
        )
        membership = cur.fetchone()
        if not membership:
            raise FeedbackAccessError("Only active admin/ops members can access the feedback inbox.")

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
