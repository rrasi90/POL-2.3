"""Canonical asynchronous integration worker for POL.

This module owns domain-outbox -> logical notification -> physical channel
materialization. Provider side effects remain in provider_delivery_worker.
"""

from psycopg2.extras import Json
import uuid


class IntegrationWorkerError(RuntimeError):
    pass


class CanonicalIntegrationWorker:
    PASSTHROUGH_EVENTS = {"VENDOR_REFERRAL_REDEEMED"}

    @staticmethod
    def _preference_category(event_name: str) -> str:
        name = event_name.upper()
        if any(k in name for k in ("PAYMENT", "SETTLEMENT", "INVOICE")):
            return "PAYMENTS"
        if any(k in name for k in ("DELIVERY", "RETURN", "DISPATCH", "ARRIVED", "PICKED_UP")):
            return "DELIVERY"
        if any(k in name for k in ("DISPUTE", "DAMAGE", "SHORTAGE")):
            return "DISPUTES"
        if "SUPPORT" in name or "FEEDBACK" in name:
            return "SUPPORT"
        if "SECURITY" in name or "OTP" in name:
            return "SECURITY"
        if "PROMO" in name or "BROADCAST" in name:
            return "MARKETING"
        return "ORDERS"

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
                retry_count=retry_count + 1,
                payload=%s,
                last_error=%s,
                published_at=COALESCE(published_at, now())
            WHERE id=%s AND status='PENDING';
            """,
            (Json(payload), reason, event["id"]),
        )

    @classmethod
    def _process_event(cls, cur, event: dict) -> None:
        event_name = event["event_name"]
        payload = event["payload"] or {}

        if event_name in cls.PASSTHROUGH_EVENTS:
            cur.execute(
                """
                UPDATE outbox_events
                SET status='PUBLISHED', published_at=now()
                WHERE id=%s AND status='PENDING';
                """,
                (event["id"],),
            )
            return

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
            JOIN users u ON u.id = om.user_id
            WHERE om.user_id = %s AND om.organization_id = %s
              AND om.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
              AND u.is_active = TRUE
            FOR SHARE OF om, o, u;
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
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
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

        channel_upper = str(channel).upper()
        if channel_upper != "INBOX":
            category = cls._preference_category(event_name)
            critical = str(priority).upper() == "CRITICAL"
            if channel_upper == "PUSH":
                pref_column = "push_enabled"
            elif channel_upper == "SMS":
                pref_column = "sms_enabled"
            else:
                raise IntegrationWorkerError(f"Unsupported notification channel: {channel}")

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
            if pref is None:
                enabled = True
            else:
                enabled = bool(
                    pref[pref_column]
                    if isinstance(pref, dict)
                    else pref[0]
                )

            delivery_status = "PENDING" if (enabled or critical) else "SKIPPED"
            failure_reason = (
                None
                if (enabled or critical)
                else "User preference disabled this transactional channel."
            )
            cur.execute(
                """
                INSERT INTO notification_deliveries
                    (id, notification_id, channel, status, scheduled_at, failure_reason)
                VALUES (%s,%s,%s,%s,now(),%s)
                ON CONFLICT (notification_id, channel) DO NOTHING;
                """,
                (
                    str(uuid.uuid4()),
                    notification_id,
                    channel_upper,
                    delivery_status,
                    failure_reason,
                ),
            )
        else:
            # Inbox is the canonical durable in-app channel.
            cur.execute(
                """
                INSERT INTO user_inbox_items
                    (id, user_id, organization_id, notification_id,
                     title, body, category, deep_link, is_read)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,FALSE)
                ON CONFLICT DO NOTHING;
                """,
                (
                    str(uuid.uuid4()),
                    str(target_user_id),
                    str(target_org_id),
                    notification_id,
                    title,
                    body,
                    cls._preference_category(event_name),
                    payload.get("deep_link") or payload.get("href") or None,
                ),
            )

        cur.execute(
            """
            UPDATE outbox_events
            SET status='PUBLISHED', published_at=now()
            WHERE id=%s AND status='PENDING';
            """,
            (event["id"],),
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
            try:
                cls._process_event(cur, event)
            except IntegrationWorkerError as exc:
                # A deterministic integration/configuration error must not poison
                # the whole polling transaction. Quarantine it and continue.
                cls._quarantine_unsupported(cur, event, str(exc))
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
            SET status='FAILED',
                attempt_count=attempt_count + 1,
                failure_reason=%s,
                last_error=%s,
                next_retry_at=%s,
                updated_at=now()
            WHERE id=%s;
            """,
            (error, error, retry_at, str(delivery_id)),
        )

    @staticmethod
    def mark_sent(cur, delivery_id: str, provider_message_id: str = None):
        cur.execute(
            """
            UPDATE notification_deliveries
            SET status='SENT',
                attempt_count=attempt_count + 1,
                provider_message_id=%s,
                sent_at=now(),
                updated_at=now()
            WHERE id=%s;
            """,
            (provider_message_id, str(delivery_id)),
        )
