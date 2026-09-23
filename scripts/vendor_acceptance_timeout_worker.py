"""Canonical automated vendor-acceptance timeout worker."""

from __future__ import annotations

from datetime import datetime, timezone

from scripts.sla_calendar import (
    VENDOR_ACCEPTANCE_SLA_HOURS,
    calculate_sla_deadline,
    load_operational_holidays,
)


class VendorAcceptanceTimeoutWorker:
    EVENT_NAME = "ORDER_CANCELLED"
    CANCELLATION_REASON = "VENDOR_TIMEOUT"
    PENALTY_SCORE = -0.25

    @classmethod
    def process_expired(cls, cur, *, now: datetime | None = None, limit: int = 100) -> dict:
        if limit <= 0:
            raise ValueError("Timeout worker limit must be positive.")

        effective_now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        holidays = load_operational_holidays(cur)

        cur.execute(
            """
            SELECT id, created_at, vendor_acceptance_deadline_at
            FROM orders
            WHERE order_status = 'SUBMITTED'
            ORDER BY created_at, id
            FOR UPDATE SKIP LOCKED
            LIMIT %s
            """,
            (limit,),
        )
        candidates = cur.fetchall()

        cancelled_orders = 0
        released_reservations = 0
        notification_events = 0
        reliability_events = 0
        operational_tasks = 0

        for candidate in candidates:
            deadline = candidate["vendor_acceptance_deadline_at"]
            if deadline is None:
                deadline = calculate_sla_deadline(
                    candidate["created_at"], VENDOR_ACCEPTANCE_SLA_HOURS, holidays
                )
                cur.execute(
                    "UPDATE orders SET vendor_acceptance_deadline_at = %s WHERE id = %s",
                    (deadline, candidate["id"]),
                )

            if deadline.astimezone(timezone.utc) > effective_now:
                continue

            order_id = str(candidate["id"])

            cur.execute(
                """
                SELECT id, vendor_product_id, quantity, status
                FROM inventory_reservations
                WHERE order_id = %s
                ORDER BY id
                FOR UPDATE
                """,
                (order_id,),
            )
            reservations = cur.fetchall()

            for reservation in reservations:
                if reservation["status"] != "ACTIVE":
                    continue

                cur.execute(
                    """
                    SELECT reserved_quantity
                    FROM vendor_inventory
                    WHERE vendor_product_id = %s
                    FOR UPDATE
                    """,
                    (reservation["vendor_product_id"],),
                )
                inventory = cur.fetchone()
                if not inventory:
                    raise ValueError("Inventory record missing for reservation.")

                quantity = int(reservation["quantity"])
                if int(inventory["reserved_quantity"]) < quantity:
                    raise ValueError("Reserved inventory is insufficient for timeout release.")

                cur.execute(
                    """
                    UPDATE vendor_inventory
                    SET reserved_quantity = reserved_quantity - %s,
                        updated_at = now()
                    WHERE vendor_product_id = %s
                    """,
                    (quantity, reservation["vendor_product_id"]),
                )
                cur.execute(
                    """
                    UPDATE inventory_reservations
                    SET status = 'RELEASED',
                        consumed_quantity = 0,
                        released_at = now()
                    WHERE id = %s
                    """,
                    (reservation["id"],),
                )
                released_reservations += 1

            cur.execute(
                """
                SELECT o.order_number, o.order_group_id, o.retailer_id, o.vendor_id,
                       r.organization_id AS retailer_organization_id
                FROM orders o
                JOIN retailers r ON r.id = o.retailer_id
                WHERE o.id = %s
                """,
                (order_id,),
            )
            order = cur.fetchone()

            cur.execute(
                """
                UPDATE orders
                SET order_status = 'CANCELLED',
                    cancellation_reason = %s,
                    updated_at = now()
                WHERE id = %s
                  AND order_status = 'SUBMITTED'
                RETURNING id
                """,
                (cls.CANCELLATION_REASON, order_id),
            )
            if cur.rowcount != 1:
                continue

            cancelled_orders += 1

            cur.execute(
                """
                UPDATE order_partial_acceptance_proposals
                SET status = 'DECLINED',
                    decision_reason = %s,
                    decided_at = now(),
                    updated_at = now()
                WHERE order_id = %s
                  AND status = 'PENDING'
                """,
                (cls.CANCELLATION_REASON, order_id),
            )

            cur.execute(
                """
                INSERT INTO vendor_reliability_events (
                    vendor_id, event_type, order_id, impact_score, metadata
                )
                VALUES (
                    %s, 'ACCEPTANCE_LATE', %s, %s,
                    jsonb_build_object(
                        'reason', %s,
                        'deadline_at', %s
                    )
                )
                """,
                (
                    order["vendor_id"],
                    order_id,
                    cls.PENALTY_SCORE,
                    cls.CANCELLATION_REASON,
                    deadline,
                ),
            )
            reliability_events += 1

            cur.execute(
                """
                SELECT om.user_id, om.organization_id
                FROM organization_memberships om
                JOIN organizations org ON org.id = om.organization_id
                WHERE om.organization_id = %s
                  AND om.status = 'ACTIVE'
                  AND org.status = 'ACTIVE'
                  AND om.role IN ('RETAILER_OWNER', 'RETAILER_STAFF')
                ORDER BY om.user_id
                """,
                (order["retailer_organization_id"],),
            )
            recipients = cur.fetchall()

            for recipient in recipients:
                dedupe_key = (
                    f"ORDER_CANCELLED:{order_id}:"
                    f"{recipient['organization_id']}:{recipient['user_id']}"
                )
                cur.execute(
                    """
                    INSERT INTO outbox_events (
                        id, event_id, event_name, aggregate_type, aggregate_id,
                        payload, status, target_user_id, target_organization_id,
                        dedupe_key, channel_hint
                    )
                    VALUES (
                        gen_random_uuid(),
                        gen_random_uuid(),
                        'ORDER_CANCELLED', 'ORDER', %s,
                        jsonb_build_object(
                            'order_id', %s,
                            'order_number', %s,
                            'order_group_id', %s,
                            'order_status', 'CANCELLED',
                            'cancellation_reason', %s
                        ),
                        'PENDING', %s, %s, %s, 'INBOX'
                    )
                    ON CONFLICT (event_name, dedupe_key)
                    WHERE dedupe_key IS NOT NULL
                    DO NOTHING
                    """,
                    (
                        order_id,
                        order_id,
                        order["order_number"],
                        str(order["order_group_id"]),
                        cls.CANCELLATION_REASON,
                        recipient["user_id"],
                        recipient["organization_id"],
                        dedupe_key,
                    ),
                )
                notification_events += 1

            cur.execute(
                """
                SELECT
                (
                    SELECT m.user_id
                    FROM organization_memberships m
                    JOIN organizations org ON org.id = m.organization_id
                    WHERE m.status = 'ACTIVE'
                      AND org.status = 'ACTIVE'
                      AND m.role = 'FIELD_ACTIVATOR'
                    ORDER BY m.user_id
                    LIMIT 1
                ) AS field_activator_user_id,
                (
                    SELECT m.user_id
                    FROM organization_memberships m
                    JOIN organizations org ON org.id = m.organization_id
                    WHERE m.status = 'ACTIVE'
                      AND org.status = 'ACTIVE'
                      AND m.role IN ('OPS_ADMIN', 'SUPER_ADMIN')
                    ORDER BY m.user_id
                    LIMIT 1
                ) AS ops_user_id
                """,
            )
            operational_assignees = cur.fetchone()

            for assignee_id in (
                operational_assignees["field_activator_user_id"],
                operational_assignees["ops_user_id"],
            ):
                if assignee_id is None:
                    continue

                cur.execute(
                    """
                    INSERT INTO field_tasks (
                        task_type,
                        target_organization_id,
                        assigned_to_user_id,
                        status,
                        due_date,
                        notes
                    )
                    VALUES (
                        'VENDOR_TIMEOUT',
                        (SELECT v.organization_id FROM vendors v WHERE v.id = %s),
                        %s,
                        'ASSIGNED',
                        now(),
                        %s
                    )
                    """,
                    (
                        order["vendor_id"],
                        assignee_id,
                        f"Critical vendor acceptance timeout for order {order['order_number']}.",
                    ),
                )
                operational_tasks += 1

        return {
            "cancelled_order_count": cancelled_orders,
            "released_reservation_count": released_reservations,
            "notification_event_count": notification_events,
            "reliability_event_count": reliability_events,
            "operational_task_count": operational_tasks,
        }
