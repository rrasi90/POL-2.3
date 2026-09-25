"""Canonical asynchronous integration worker for POL.

This module owns domain-outbox -> logical notification -> physical channel
materialization. Provider side effects remain in provider_delivery_worker.
"""

from psycopg2.extras import Json
import uuid


class IntegrationWorkerError(RuntimeError):
    pass


class CanonicalIntegrationWorker:
    @staticmethod
    def _preference_category(event_name: str) -> str:
        name = event_name.upper()
        if any(k in name for k in ("PAYMENT", "SETTLEMENT", "INVOICE")):
            return "PAYMENTS"
        if any(k in name for k in ("DELIVERY", "RETURN", "DISPATCH", "ARRIVED", "PICKED_UP")):
            return "DELIVERY"
        if any(k in name for k in ("DISPUTE", "DAMAGE", "SHORTAGE")):
            return "DISPUTES"
        if "SUPPORT" in name:
            return "SUPPORT"
        if "SECURITY" in name or "OTP" in name:
            return "SECURITY"
        if "FEEDBACK" in name:
            return "SUPPORT"
        if "PROMO" in name or "BROADCAST" in name:
            return "MARKETING"
        return "ORDERS"

PASSTHROUGH_EVENTS = {"VENDOR_REFERRAL_REDEEMED"}

    @staticmethod
    def _render_message(cur, event_name: str, payload: dict):
        cur.execute(
            """
            SELECT title_template, body_template, priority, channel
            FROM notification_templates
            WHERE event_name = %s
              AND enabled = TRUE
              AND effective_from <= now()
              AND (effective_until IS NULL OR effective_until > now())
            ORDER BY effective_from DESC
            LIMIT 1;
            """,
            (event_name,),
        )
        template = cur.fetchone()
        if not template:
            raise IntegrationWorkerError(f"No active notification template for {event_name}")

        body = template["body_template"]
        title = template["title_template"] or "POL"
        for key, value in (payload or {}).items():
            token = "{{" + str(key) + "}}"
            body = body.replace(token, str(value))
            title = title.replace(token, str(value))
        return title, body, template["priority"], template["channel"]

    @classmethod
    def _quarantine_unsupported(cls, cur, event: dict, reason: str):
        payload = dict(event.get("payload") or {})
        payload["_integration_quarantine"] = {
            "reason": reason,
            "handler": "CanonicalIntegrationWorker",
        }
        cur.execute(
            """
            UPDATE outbox_events
            SET status='FAILED',
                payload=%s,
                last_error=%s,
                published_at=COALESCE(published_at, now())
            WHERE id=%s;
            """,
            (Json(payload), reason, event["id"]),
        )

    @classmethod
    def process_pending(cls, cur, limit: int = 100) -> int:
        cur.execute(
            """
            SELECT *
            FROM outbox_events
            WHERE status = 'PENDING'
              AND event_name <> 'NOTIFICATION_DELIVERY_REQUESTED'
            ORDER BY created_at
            FOR UPDATE SKIP LOCKED
            LIMIT %s;
            """,
            (limit,),
        )
        events = cur.fetchall()
        processed = 0

        for event in events:
            event_name = event["event_name"]
            payload = event["payload"] or {}

            if event_name in cls.PASSTHROUGH_EVENTS:
                cur.execute(
                    """
                    UPDATE outbox_events
                    SET status='PUBLISHED', published_at=now()
                    WHERE id=%s;
                    """,
                    (event["id"],),
                )
                processed += 1
                continue

            if event_name not in cls.PASSTHROUGH_EVENTS:
                cur.execute(
                    """
                    SELECT 1
                    FROM notification_templates
                    WHERE event_name = %s
                      AND enabled = TRUE
                      AND effective_from <= now()
                      AND (effective_until IS NULL OR effective_until > now())
                    LIMIT 1
                    """,
                    (event_name,),
                )
                if not cur.fetchone():
                    cls._quarantine_unsupported(
                        cur,
                        event,
                        f"No active notification template for canonical event: {event_name}",
                    )
                    processed += 1
                    continue

            target_user_id = event.get("target_user_id")
            target_org_id = event.get("target_organization_id")
            if not target_user_id or not target_org_id:
                raise IntegrationWorkerError(
                    f"Event {event['event_id']} lacks explicit notification routing."
                )

            cur.execute(
                """
                SELECT 1
                FROM organization_memberships om
                JOIN organizations o ON o.id = om.organization_id
                WHERE om.user_id = %s AND om.organization_id = %s
                  AND om.status = 'ACTIVE' AND o.status = 'ACTIVE'
                FOR SHARE OF om, o;
                """,
                (target_user_id, target_org_id),
            )
            if not cur.fetchone():
                raise IntegrationWorkerError(
                    "Notification recipient requires an active membership in the target organization."
                )

            title, body, priority, channel = cls._render_message(cur, event_name, payload)
            notification_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO notifications (
                    id, user_id, organization_id, event_name, title, body, data_payload, priority
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (
                    notification_id,
                    str(target_user_id),
                    str(target_org_id),
                    event_name,
                    title,
                    body,
                    Json(payload),
                    priority,
                ),
            )
            if channel != "INBOX":
                category = cls._preference_category(event_name)
                critical = str(priority).upper() == "CRITICAL"
                pref_column = "push_enabled" if str(channel).upper() == "PUSH" else "sms_enabled"
                cur.execute(
                    f"""
                    SELECT {pref_column}
                    FROM notification_preferences
                    WHERE user_id=%s AND category=%s
                    ORDER BY id DESC
                    LIMIT 1
                    """,
                    (str(target_user_id), category),
                )
                pref = cur.fetchone()
                enabled = True if pref is None else bool(pref[0] if not isinstance(pref, dict) else pref[pref_column])
                delivery_status = "PENDING" if (enabled or critical) else "SKIPPED"
                failure_reason = None if (enabled or critical) else "User preference disabled this transactional channel."
                cur.execute(
                    """
                    INSERT INTO notification_deliveries
                        (id, notification_id, channel, status, scheduled_at, failure_reason)
                    VALUES (%s,%s,%s,%s,now(),%s)
                    ON CONFLICT (notification_id, channel) DO NOTHING;
                    """,
                    (str(uuid.uuid4()), notification_id, channel, delivery_status, failure_reason),
                )
            cur.execute(
                """
                UPDATE outbox_events
                SET status = 'PUBLISHED', published_at = now()
                WHERE id = %s;
                """,
                (event["id"],),
            )
            processed += 1

        return processed


class NotificationDeliveryWorker:
    """Legacy-compatible persistence worker; provider calls live in provider_delivery_worker."""

    @staticmethod
    def claim_pending(cur, limit: int = 100):
        cur.execute(
            """
            SELECT nd.*, n.user_id, n.organization_id, n.event_name, n.title, n.body
            FROM notification_deliveries nd
            JOIN notifications n ON n.id = nd.notification_id
            WHERE nd.status = 'PENDING'
              AND nd.scheduled_at <= now()
            ORDER BY nd.created_at
            FOR UPDATE SKIP LOCKED
            LIMIT %s;
            """,
            (limit,),
        )
        return cur.fetchall()

    @staticmethod
    def mark_failed(cur, delivery_id: str, error: str, retry_at):
        cur.execute(
            """
            UPDATE notification_deliveries
            SET status = 'FAILED',
                attempt_count = attempt_count + 1,
                last_error = %s,
                next_retry_at = %s,
                updated_at = now()
            WHERE id = %s;
            """,
            (error, retry_at, str(delivery_id)),
        )

    @staticmethod
    def mark_sent(cur, delivery_id: str, provider_message_id: str = None):
        cur.execute(
            """
            UPDATE notification_deliveries
            SET status = 'SENT',
                attempt_count = attempt_count + 1,
                provider_message_id = %s,
                sent_at = now(),
                updated_at = now()
            WHERE id = %s;
            """,
            (provider_message_id, str(delivery_id)),
        )
