"""Canonical inventory reservation expiry worker.

Releases stale ACTIVE reservations atomically and records an immutable inventory
audit entry plus a durable domain outbox event for each release.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from psycopg2.extras import Json


class ReservationExpiryWorker:
    EVENT_NAME = "INVENTORY_RESERVATION_EXPIRED"

    @classmethod
    def process_expired(cls, cur, *, now: datetime | None = None, limit: int = 100) -> dict:
        if limit <= 0:
            raise ValueError("Reservation expiry worker limit must be positive.")

        effective_now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        cur.execute(
            """
            SELECT ir.id, ir.order_id, ir.vendor_product_id, ir.quantity,
                   vp.vendor_id, v.organization_id AS vendor_organization_id
            FROM inventory_reservations ir
            JOIN vendor_products vp ON vp.id=ir.vendor_product_id
            JOIN vendors v ON v.id=vp.vendor_id
            WHERE ir.status='ACTIVE'
              AND ir.expires_at IS NOT NULL
              AND ir.expires_at <= %s
            ORDER BY ir.expires_at, ir.id
            FOR UPDATE OF ir SKIP LOCKED
            LIMIT %s
            """,
            (effective_now, limit),
        )
        reservations = cur.fetchall()

        expired_count = 0
        released_quantity = 0

        for reservation in reservations:
            cur.execute(
                """
                SELECT physical_quantity, reserved_quantity
                FROM vendor_inventory
                WHERE vendor_product_id=%s
                FOR UPDATE
                """,
                (reservation["vendor_product_id"],),
            )
            inventory = cur.fetchone()
            if not inventory:
                raise ValueError(
                    f"Inventory record missing for reservation {reservation['id']}."
                )

            quantity = int(reservation["quantity"])
            reserved_before = int(inventory["reserved_quantity"])
            if reserved_before < quantity:
                raise ValueError(
                    f"Reserved quantity underflow for reservation {reservation['id']}."
                )

            physical = int(inventory["physical_quantity"])
            cur.execute(
                """
                UPDATE vendor_inventory
                SET reserved_quantity=reserved_quantity-%s,
                    updated_at=now()
                WHERE vendor_product_id=%s
                RETURNING physical_quantity, reserved_quantity
                """,
                (quantity, reservation["vendor_product_id"]),
            )
            inventory_after = cur.fetchone()

            cur.execute(
                """
                UPDATE inventory_reservations
                SET status='EXPIRED',
                    consumed_quantity=0,
                    released_at=COALESCE(released_at,now())
                WHERE id=%s AND status='ACTIVE'
                RETURNING id
                """,
                (reservation["id"],),
            )
            if cur.rowcount != 1:
                continue

            cur.execute(
                """
                INSERT INTO inventory_audit_log (
                    vendor_id, vendor_product_id, old_quantity, new_quantity,
                    old_price_toman, new_price_toman,
                    source_trigger, reference_id, actor_user_id
                )
                VALUES (%s,%s,%s,%s,NULL,NULL,%s,%s,%s)
                """,
                (
                    reservation["vendor_id"],
                    reservation["vendor_product_id"],
                    physical,
                    physical,
                    "RESERVATION_EXPIRY",
                    str(reservation["id"]),
                    uuid.UUID(int=0),
                ),
            )

            cur.execute(
                """
                INSERT INTO outbox_events (
                    id, event_id, event_name, aggregate_type, aggregate_id,
                    payload, status, target_user_id, target_organization_id,
                    dedupe_key, channel_hint
                )
                SELECT
                    gen_random_uuid(), gen_random_uuid(), %s, 'INVENTORY_RESERVATION', %s,
                    jsonb_build_object(
                        'reservation_id', %s,
                        'order_id', %s,
                        'vendor_product_id', %s,
                        'quantity', %s
                    ),
                    'PENDING', om.user_id, om.organization_id,
                    %s, 'INBOX'
                FROM organization_memberships om
                JOIN organizations org ON org.id=om.organization_id
                WHERE om.organization_id=%s
                  AND om.status='ACTIVE'
                  AND org.status='ACTIVE'
                  AND om.role IN ('VENDOR_OWNER','VENDOR_STAFF')
                ON CONFLICT (event_name, dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING
                """,
                (
                    cls.EVENT_NAME,
                    str(reservation["id"]),
                    str(reservation["id"]),
                    str(reservation["order_id"]) if reservation["order_id"] else None,
                    str(reservation["vendor_product_id"]),
                    quantity,
                    f"inventory_reservation_expired:{reservation['id']}",
                    reservation["vendor_organization_id"],
                ),
            )

            expired_count += 1
            released_quantity += quantity

        return {
            "expired_reservation_count": expired_count,
            "released_quantity": released_quantity,
        }
