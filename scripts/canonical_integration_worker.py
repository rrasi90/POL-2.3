"""Canonical asynchronous integration worker for POL.

This module is intentionally provider-neutral. It consumes domain outbox events,
resolves explicit recipients, materializes logical notifications, and lets the
notification_deliveries worker handle physical channels.
"""

from psycopg2.extras import Json, RealDictCursor


class IntegrationWorkerError(RuntimeError):
    pass


class CanonicalIntegrationWorker:
    ALLOWED_DIRECT_NOTIFICATION_EVENTS = {
        "ORDER_SUBMITTED",
        "ORDER_ACCEPTED",
        "ORDER_REJECTED",
        "DISPUTE_OPENED",
        "FEEDBACK_REPLIED",
        "DAILY_INVENTORY_REMINDER",
    }

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
    def process_pending(cls, cur, limit: int = 100) -> int:
        """Process explicit, routable domain events exactly once per transaction."""
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
            target_user_id = event.get("target_user_id")
            target_org_id = event.get("target_organization_id")

            if event_name not in cls.ALLOWED_DIRECT_NOTIFICATION_EVENTS:
                # Non-notification domain events are acknowledged by their own
                # domain worker. This worker must never steal them.
                continue

            if not target_user_id or not target_org_id:
                raise IntegrationWorkerError(
                    f"Event {event['event_id']} lacks explicit notification routing."
                )

            title, body, priority, channel_hint = cls._render_message(cur, event_name, payload)
            cur.execute(
                """
                INSERT INTO notifications (
                    id, user_id, organization_id, event_name, title, body, data_payload, priority
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (
                    __import__("uuid").uuid4(),
                    target_user_id,
                    target_org_id,
                    event_name,
                    title,
                    body,
                    Json(payload),
                    priority,
                ),
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
    """Persist/retry physical delivery state without provider-specific side effects."""

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
            (error, retry_at, delivery_id),
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
                delivered_at = now(),
                updated_at = now()
            WHERE id = %s;
            """,
            (provider_message_id, delivery_id),
        )
