"""Canonical inventory reservation commands."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4


class ReservationServiceError(ValueError):
    pass


class ReservationConflictError(ReservationServiceError):
    pass


class ReservationService:
    TTL = timedelta(minutes=15)

    @classmethod
    def reserve(
        cls,
        cur,
        *,
        vendor_product_id: str,
        quantity: int,
        idempotency_key: str,
        expires_at: datetime | None = None,
        order_id: str | None = None,
        order_item_id: str | None = None,
    ) -> dict:
        if quantity <= 0:
            raise ReservationServiceError("Reservation quantity must be positive.")
        key = (idempotency_key or "").strip()
        if not key:
            raise ReservationServiceError("Reservation idempotency key is required.")

        cur.execute(
            """
            SELECT id, vendor_product_id, quantity, status, expires_at, order_id, order_item_id
            FROM inventory_reservations
            WHERE idempotency_key=%s
            FOR UPDATE
            """,
            (key,),
        )
        existing = cur.fetchone()
        if existing:
            same = (
                str(existing["vendor_product_id"]) == str(vendor_product_id)
                and int(existing["quantity"]) == int(quantity)
                and str(existing["order_id"] or "") == str(order_id or "")
                and str(existing["order_item_id"] or "") == str(order_item_id or "")
            )
            if not same:
                raise ReservationConflictError(
                    "Reservation idempotency key was already used with different reservation parameters."
                )
            return {**dict(existing), "id": str(existing["id"]), "idempotent_replay": True}

        cur.execute(
            """
            SELECT vendor_product_id, physical_quantity, reserved_quantity,
                   (physical_quantity - reserved_quantity) AS available_quantity
            FROM vendor_inventory
            WHERE vendor_product_id=%s
            FOR UPDATE
            """,
            (vendor_product_id,),
        )
        inventory = cur.fetchone()
        if not inventory:
            raise ReservationServiceError("Vendor inventory row not found.")
        if int(inventory["available_quantity"]) < quantity:
            raise ReservationServiceError(
                f"Insufficient available inventory: requested={quantity}, available={inventory['available_quantity']}."
            )

        expiry = expires_at or (datetime.now(timezone.utc) + cls.TTL)
        reservation_id = str(uuid4())

        # A concurrent transaction may have committed the same key while this
        # request waited for the inventory row. Re-check before INSERT so a
        # legitimate replay is returned instead of surfacing a unique violation.
        cur.execute(
            """
            SELECT id, vendor_product_id, quantity, status, expires_at, order_id, order_item_id
            FROM inventory_reservations
            WHERE idempotency_key=%s
            FOR UPDATE
            """,
            (key,),
        )
        existing = cur.fetchone()
        if existing:
            same = (
                str(existing["vendor_product_id"]) == str(vendor_product_id)
                and int(existing["quantity"]) == int(quantity)
                and str(existing["order_id"] or "") == str(order_id or "")
                and str(existing["order_item_id"] or "") == str(order_item_id or "")
            )
            if not same:
                raise ReservationConflictError(
                    "Reservation idempotency key was already used with different reservation parameters."
                )
            return {**dict(existing), "id": str(existing["id"]), "idempotent_replay": True}

        cur.execute(
            """
            INSERT INTO inventory_reservations (
                id, vendor_product_id, order_id, order_item_id, quantity,
                status, idempotency_key, expires_at, consumed_quantity
            )
            VALUES (%s,%s,%s,%s,%s,'ACTIVE',%s,%s,0)
            RETURNING id, vendor_product_id, order_id, order_item_id,
                      quantity, status, idempotency_key, expires_at
            """,
            (reservation_id, vendor_product_id, order_id, order_item_id, quantity, key, expiry),
        )

        cur.execute(
            """
            UPDATE vendor_inventory
            SET reserved_quantity = reserved_quantity + %s,
                updated_at = now()
            WHERE vendor_product_id=%s
              AND physical_quantity - reserved_quantity >= %s
            RETURNING reserved_quantity
            """,
            (quantity, vendor_product_id, quantity),
        )
        updated = cur.fetchone()
        if not updated:
            raise ReservationServiceError("Inventory became unavailable while reserving.")

        cur.execute(
            """
            INSERT INTO outbox_events (
                id,event_id,event_name,aggregate_type,aggregate_id,payload,
                status,target_user_id,target_organization_id,dedupe_key,channel_hint
            )
            VALUES (
                gen_random_uuid(),gen_random_uuid(),'INVENTORY_RESERVATION_CREATED',
                'INVENTORY_RESERVATION',%s,
                jsonb_build_object(
                    'reservation_id',%s,'vendor_product_id',%s,'order_id',%s,
                    'order_item_id',%s,'quantity',%s,'expires_at',%s,'idempotency_key',%s
                ),
                'PENDING',NULL,NULL,%s,'INBOX'
            )
            ON CONFLICT (event_name,dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING
            """,
            (
                reservation_id, reservation_id, vendor_product_id, order_id,
                order_item_id, quantity, expiry, key,
                f"reservation-created:{reservation_id}"
            ),
        )

        return {
            "id": reservation_id,
            "vendor_product_id": vendor_product_id,
            "order_id": order_id,
            "order_item_id": order_item_id,
            "quantity": quantity,
            "status": "ACTIVE",
            "idempotency_key": key,
            "expires_at": expiry,
            "idempotent_replay": False,
        }
