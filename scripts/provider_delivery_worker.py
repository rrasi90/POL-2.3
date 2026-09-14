"""External provider delivery worker with leases, retries and idempotency."""

from __future__ import annotations

import uuid

from psycopg2.extras import Json

from scripts.provider_adapters import (
    ProviderConfigurationError,
    ProviderPermanentError,
    ProviderTransientError,
    build_adapter,
)


class ProviderDeliveryWorker:
    RETRY_DELAYS_MINUTES = (1, 5, 15, 60)
    MAX_ATTEMPTS = 8

    @staticmethod
    def claim_pending(cur, limit: int = 100, lease_minutes: int = 5):
        lease_id = str(uuid.uuid4())
        cur.execute(
            """
            WITH candidates AS (
                SELECT id
                FROM notification_deliveries
                WHERE channel IN ('PUSH','SMS')
                  AND status IN ('PENDING','FAILED')
                  AND attempt_count < %s
                  AND scheduled_at <= now()
                  AND (next_retry_at IS NULL OR next_retry_at <= now())
                  AND (lease_until IS NULL OR lease_until <= now())
                ORDER BY created_at
                FOR UPDATE SKIP LOCKED
                LIMIT %s
            )
            UPDATE notification_deliveries d
            SET lease_id = %s,
                lease_until = now() + (%s || ' minutes')::interval,
                updated_at = now()
            FROM candidates x
            WHERE d.id = x.id
            RETURNING d.*;
            """,
            (ProviderDeliveryWorker.MAX_ATTEMPTS, limit, lease_id, lease_minutes),
        )
        return lease_id, cur.fetchall()

    @staticmethod
    def _identity(cur, delivery):
        cur.execute(
            """
            SELECT n.user_id, n.organization_id, n.event_name, n.title, n.body,
                   n.data_payload, u.phone_number
            FROM notifications n
            JOIN users u ON u.id = n.user_id
            WHERE n.id = %s;
            """,
            (delivery["notification_id"],),
        )
        return cur.fetchone()

    @staticmethod
    def _device_token(cur, user_id: str):
        cur.execute(
            """
            SELECT push_token
            FROM user_devices
            WHERE user_id = %s AND is_active = TRUE AND push_token IS NOT NULL
            ORDER BY updated_at DESC
            LIMIT 1;
            """,
            (user_id,),
        )
        row = cur.fetchone()
        return row["push_token"] if row else None

    @staticmethod
    def _finish_attempt(cur, attempt_id, outcome, error_message=None, provider_message_id=None, provider_code=None, metadata=None):
        cur.execute(
            """
            UPDATE notification_provider_attempts
            SET outcome=%s,
                error_message=%s,
                provider_message_id=%s,
                provider_code=%s,
                response_metadata=%s,
                completed_at=now()
            WHERE id=%s;
            """,
            (outcome, error_message, provider_message_id, provider_code,
             Json(metadata or {}), attempt_id),
        )

    @classmethod
    def process_delivery(cls, cur, delivery, lease_id: str):
        delivery_id = str(delivery["id"])
        attempt_number = int(delivery["attempt_count"]) + 1
        provider_attempt_key = f"notification:{delivery_id}:attempt:{attempt_number}"
        identity = cls._identity(cur, delivery)
        if not identity:
            raise ValueError("Notification referenced by delivery does not exist.")

        attempt_row = None
        try:
            adapter = build_adapter(delivery["channel"])
            cur.execute(
                """
                INSERT INTO notification_provider_attempts
                    (id,delivery_id,attempt_number,channel,provider,idempotency_key,started_at,outcome)
                VALUES (%s,%s,%s,%s,%s,%s,now(),'RETRYABLE_FAILURE')
                ON CONFLICT (delivery_id, attempt_number) DO NOTHING
                RETURNING id;
                """,
                (str(uuid.uuid4()), delivery_id, attempt_number, delivery["channel"], adapter.provider_name, provider_attempt_key),
            )
            attempt_row = cur.fetchone()
            if attempt_row is None:
                return "DUPLICATE_ATTEMPT"

            if delivery["channel"] == "SMS":
                result = adapter.send(
                    phone_number=identity["phone_number"], title=identity["title"], body=identity["body"],
                    idempotency_key=provider_attempt_key,
                )
            else:
                token = cls._device_token(cur, str(identity["user_id"]))
                if not token:
                    raise ProviderPermanentError("No active push token for notification recipient")
                result = adapter.send(
                    push_token=token, title=identity["title"], body=identity["body"],
                    data=identity["data_payload"] or {}, idempotency_key=provider_attempt_key,
                )

            cls._finish_attempt(
                cur, attempt_row["id"], "SENT",
                provider_message_id=result.provider_message_id,
                provider_code=result.provider_code,
                metadata=result.metadata,
            )
            cur.execute(
                """
                UPDATE notification_deliveries
                SET status='SENT', attempt_count=%s, provider=%s,
                    provider_message_id=%s, sent_at=now(),
                    lease_id=NULL, lease_until=NULL, next_retry_at=NULL,
                    last_error=NULL, last_provider_code=%s,
                    provider_attempt_key=%s, updated_at=now()
                WHERE id=%s AND lease_id=%s;
                """,
                (attempt_number, result.provider, result.provider_message_id,
                 result.provider_code, provider_attempt_key, delivery_id, lease_id),
            )
            return "SENT"

        except ProviderTransientError as exc:
            if attempt_row:
                cls._finish_attempt(cur, attempt_row["id"], "RETRYABLE_FAILURE", error_message=str(exc))
            if attempt_number >= cls.MAX_ATTEMPTS:
                cur.execute(
                    """
                    UPDATE notification_deliveries
                    SET status='FAILED', attempt_count=%s, last_error=%s,
                        next_retry_at=NULL, lease_id=NULL, lease_until=NULL, updated_at=now()
                    WHERE id=%s AND lease_id=%s;
                    """,
                    (attempt_number, f"max attempts exceeded: {exc}", delivery_id, lease_id),
                )
                return "MAX_RETRIES_EXCEEDED"
            delay = cls.RETRY_DELAYS_MINUTES[min(attempt_number - 1, len(cls.RETRY_DELAYS_MINUTES) - 1)]
            cur.execute(
                """
                UPDATE notification_deliveries
                SET status='FAILED', attempt_count=%s, last_error=%s,
                    next_retry_at=now() + (%s || ' minutes')::interval,
                    lease_id=NULL, lease_until=NULL, updated_at=now()
                WHERE id=%s AND lease_id=%s;
                """,
                (attempt_number, str(exc), delay, delivery_id, lease_id),
            )
            return "RETRYABLE_FAILURE"

        except (ProviderPermanentError, ProviderConfigurationError) as exc:
            if attempt_row:
                cls._finish_attempt(cur, attempt_row["id"], "PERMANENT_FAILURE", error_message=str(exc))
            cur.execute(
                """
                UPDATE notification_deliveries
                SET status='FAILED', attempt_count=%s, last_error=%s,
                    next_retry_at=NULL, lease_id=NULL, lease_until=NULL, updated_at=now()
                WHERE id=%s AND lease_id=%s;
                """,
                (attempt_number, str(exc), delivery_id, lease_id),
            )
            return "PERMANENT_FAILURE"

    @classmethod
    def process_pending(cls, cur, limit: int = 100):
        lease_id, deliveries = cls.claim_pending(cur, limit=limit)
        return [cls.process_delivery(cur, delivery, lease_id) for delivery in deliveries]
