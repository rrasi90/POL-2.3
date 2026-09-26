"""Canonical privacy export and account-de-identification lifecycle."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone

from psycopg2.extras import Json


class PrivacyLifecycleError(ValueError):
    """Raised when a privacy request cannot be completed."""


class PrivacyLifecycleService:
    """User-owned privacy workflow preserving required business/audit history."""

    @staticmethod
    def _load_user(cur, user_id: str) -> dict:
        cur.execute(
            """
            SELECT id, phone_number, full_name, role, is_active,
                   last_login_at, created_at, updated_at
            FROM users
            WHERE id = %s
            FOR UPDATE;
            """,
            (user_id,),
        )
        row = cur.fetchone()
        if not row:
            raise PrivacyLifecycleError("User does not exist.")
        return row

    @staticmethod
    def _load_export(cur, user_id: str) -> dict:
        user = PrivacyLifecycleService._load_user(cur, user_id)

        cur.execute(
            """
            SELECT id, display_name, avatar_media_asset_id, email,
                   preferred_language, timezone, bio, profile_status,
                   onboarding_completed_at, last_seen_at, created_at, updated_at
            FROM user_profiles
            WHERE user_id = %s;
            """,
            (user_id,),
        )
        profile = cur.fetchone()

        cur.execute(
            """
            SELECT m.id, m.organization_id, o.name AS organization_name,
                   o.org_type, m.role, m.status, m.is_primary,
                   m.created_at, m.updated_at
            FROM organization_memberships m
            JOIN organizations o ON o.id = m.organization_id
            WHERE m.user_id = %s
            ORDER BY m.created_at, m.id;
            """,
            (user_id,),
        )
        memberships = cur.fetchall()

        cur.execute(
            """
            SELECT id, device_type, is_active, created_at, updated_at
            FROM user_devices
            WHERE user_id = %s
            ORDER BY created_at, id;
            """,
            (user_id,),
        )
        devices = cur.fetchall()

        cur.execute(
            """
            SELECT id, organization_id, consent_type, status, source, version,
                   granted_at, revoked_at, created_at
            FROM data_consents
            WHERE user_id = %s
            ORDER BY created_at, id;
            """,
            (user_id,),
        )
        consents = cur.fetchall()

        cur.execute(
            """
            SELECT COUNT(*) AS notification_count
            FROM notifications
            WHERE user_id = %s;
            """,
            (user_id,),
        )
        notification_count = int(cur.fetchone()["notification_count"])

        cur.execute(
            """
            SELECT COUNT(*) AS inbox_count
            FROM user_inbox_items
            WHERE user_id = %s;
            """,
            (user_id,),
        )
        inbox_count = int(cur.fetchone()["inbox_count"])

        cur.execute(
            """
            SELECT COUNT(*) AS session_count
            FROM user_sessions
            WHERE user_id = %s;
            """,
            (user_id,),
        )
        session_count = int(cur.fetchone()["session_count"])

        def clean(value):
            if hasattr(value, "isoformat"):
                return value.isoformat()
            if isinstance(value, dict):
                return {k: clean(v) for k, v in value.items()}
            if isinstance(value, list):
                return [clean(v) for v in value]
            return value

        return clean({
            "export_version": "1.0",
            "exported_at": datetime.now(timezone.utc),
            "user": dict(user),
            "profile": dict(profile) if profile else None,
            "memberships": [dict(row) for row in memberships],
            "devices": [dict(row) for row in devices],
            "consents": [dict(row) for row in consents],
            "activity_counts": {
                "notifications": notification_count,
                "inbox_items": inbox_count,
                "sessions": session_count,
            },
        })

    @classmethod
    def request_export(cls, cur, user_id: str) -> dict:
        snapshot = cls._load_export(cur, user_id)
        serialized = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

        cur.execute(
            """
            INSERT INTO privacy_requests (
                user_id, request_type, status, started_at, completed_at,
                export_sha256, result_summary
            )
            VALUES (%s, 'EXPORT', 'COMPLETED', now(), now(), %s, %s)
            RETURNING id, request_type, status, requested_at, started_at, completed_at,
                      export_sha256, result_summary;
            """,
            (
                user_id,
                digest,
                Json({"export_version": "1.0", "record_count": len(snapshot["memberships"]) + len(snapshot["devices"]) + len(snapshot["consents"])}),
            ),
        )
        request = dict(cur.fetchone())
        return {"request": request, "data": snapshot}

    @classmethod
    def request_deletion(cls, cur, user_id: str) -> dict:
        user = cls._load_user(cur, user_id)
        cur.execute(
            """
            SELECT id
            FROM privacy_requests
            WHERE user_id = %s
              AND request_type = 'DELETION'
              AND status IN ('REQUESTED', 'PROCESSING')
            LIMIT 1;
            """,
            (user_id,),
        )
        if cur.fetchone():
            raise PrivacyLifecycleError("A deletion request is already in progress.")

        cur.execute(
            """
            INSERT INTO privacy_requests (user_id, request_type, status, started_at)
            VALUES (%s, 'DELETION', 'PROCESSING', now())
            RETURNING id, requested_at, started_at;
            """,
            (user_id,),
        )
        request = dict(cur.fetchone())

        # Preserve business, financial and immutable audit history. Remove or
        # revoke direct personal/security data that is not needed for history.
        tombstone = f"Deleted User {str(user['id'])[:8]}"
        digits = re.sub(r"\D", "", str(user["id"]))
        tombstone_phone = "+000" + digits[:11]
        cur.execute(
            """
            UPDATE user_profiles
            SET display_name = %s,
                email = NULL,
                bio = NULL,
                avatar_media_asset_id = NULL,
                profile_status = 'SUSPENDED',
                updated_at = now()
            WHERE user_id = %s;
            """,
            (tombstone, user_id),
        )
        cur.execute(
            """
            UPDATE users
            SET phone_number = %s,
                full_name = %s,
                is_active = FALSE,
                updated_at = now()
            WHERE id = %s;
            """,
            (tombstone_phone, tombstone, user_id),
        )
        cur.execute(
            """
            UPDATE user_sessions
            SET status = 'REVOKED',
                revoked_at = COALESCE(revoked_at, now()),
                refresh_token_hash = NULL
            WHERE user_id = %s
              AND status = 'ACTIVE';
            """,
            (user_id,),
        )
        cur.execute(
            """
            UPDATE user_devices
            SET is_active = FALSE, push_token = NULL, updated_at = now()
            WHERE user_id = %s;
            """,
            (user_id,),
        )
        cur.execute(
            """
            UPDATE data_consents
            SET status = 'REVOKED',
                revoked_at = COALESCE(revoked_at, now())
            WHERE user_id = %s
              AND status = 'GRANTED';
            """,
            (user_id,),
        )
        cur.execute(
            """
            UPDATE membership_profiles
            SET display_name_override = NULL,
                preferences = '{}'::jsonb,
                updated_at = now()
            WHERE membership_id IN (
                SELECT id FROM organization_memberships WHERE user_id = %s
            );
            """,
            (user_id,),
        )

        # Remove PII from notification delivery text that is explicitly owned
        # by the user while retaining the durable notification/event reference.
        cur.execute(
            """
            UPDATE notifications
            SET title = CASE WHEN title <> '' THEN 'Notification' ELSE title END,
                body = CASE WHEN body <> '' THEN 'Notification retained for audit' ELSE body END,
                data_payload = NULL
            WHERE user_id = %s;
            """,
            (user_id,),
        )
        cur.execute(
            """
            UPDATE user_inbox_items
            SET title = CASE WHEN title <> '' THEN 'Notification' ELSE title END,
                body = CASE WHEN body <> '' THEN 'Notification retained for audit' ELSE body END,
                deep_link = NULL
            WHERE user_id = %s;
            """,
            (user_id,),
        )

        cur.execute(
            """
            UPDATE privacy_requests
            SET status = 'COMPLETED',
                completed_at = now(),
                result_summary = %s
            WHERE id = %s
            RETURNING id, request_type, status, requested_at, started_at, completed_at, result_summary;
            """,
            (Json({"deidentified_user": True, "sessions_revoked": True, "financial_history_preserved": True}), request["id"]),
        )
        return {"request": dict(cur.fetchone())}
