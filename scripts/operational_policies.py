"""POL operational policies for checkout integrity and operational realism."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo


class AllocationIntegrityError(ValueError):
    pass


def _vendor_allocated_totals(vendor_allocations: list) -> dict:
    totals = {}
    units = {}
    for alloc in vendor_allocations:
        vendor_id = str(alloc["vendor_id"])
        totals[vendor_id] = totals.get(vendor_id, 0) + int(alloc["amount_toman"])
        units[vendor_id] = units.get(vendor_id, 0) + int(alloc["quantity"])
    return totals, units


def validate_vendor_operational_capacity(cur, vendor_allocations: list) -> None:
    """Apply optional vendor hours/capacity constraints only when configured.

    Absence of a configured operational profile means "no additional restriction";
    this keeps the Ahvaz pilot backwards-compatible while making configured
    constraints authoritative for vendors that opt into them.
    """
    vendor_totals, vendor_units = _vendor_allocated_totals(vendor_allocations)
    now_utc = datetime.now(timezone.utc)

    for vendor_id, requested_units in vendor_units.items():
        cur.execute(
            """
            SELECT timezone, max_orders_per_day, max_pick_units_per_hour
            FROM vendor_capacity_profiles
            WHERE vendor_id = %s
              AND is_active = TRUE
              AND effective_from <= now()
              AND (effective_until IS NULL OR effective_until > now())
            ORDER BY effective_from DESC
            LIMIT 1;
            """,
            (vendor_id,),
        )
        capacity = cur.fetchone()

        cur.execute(
            """
            SELECT timezone, opens_at, closes_at, order_cutoff_at
            FROM vendor_operating_windows
            WHERE vendor_id = %s
              AND weekday = EXTRACT(DOW FROM CURRENT_DATE)
              AND is_active = TRUE
              AND effective_from <= now()
              AND (effective_until IS NULL OR effective_until > now())
            ORDER BY effective_from DESC
            LIMIT 1;
            """,
            (vendor_id,),
        )
        window = cur.fetchone()

        if capacity:
            tz_name = capacity["timezone"] or "Asia/Tehran"
            try:
                local_now = now_utc.astimezone(ZoneInfo(tz_name))
            except Exception as exc:
                raise AllocationIntegrityError(f"Invalid vendor timezone for {vendor_id}: {tz_name}") from exc

            if capacity["max_orders_per_day"] is not None:
                cur.execute(
                    """
                    SELECT COUNT(*) AS order_count
                    FROM orders
                    WHERE vendor_id = %s
                      AND created_at >= date_trunc('day', %s::timestamptz)
                      AND created_at < date_trunc('day', %s::timestamptz) + interval '1 day'
                      AND order_status NOT IN ('CANCELLED', 'REJECTED');
                    """,
                    (vendor_id, local_now, local_now),
                )
                current_orders = int(cur.fetchone()["order_count"])
                if current_orders + 1 > int(capacity["max_orders_per_day"]):
                    raise AllocationIntegrityError(
                        f"Vendor {vendor_id} daily order capacity exhausted: "
                        f"{current_orders + 1} > {capacity['max_orders_per_day']}"
                    )

            if capacity["max_pick_units_per_hour"] is not None:
                cur.execute(
                    """
                    SELECT COALESCE(SUM(oi.quantity), 0) AS picked_units
                    FROM order_items oi
                    JOIN orders o ON o.id = oi.order_id
                    WHERE o.vendor_id = %s
                      AND o.created_at >= now() - interval '1 hour'
                      AND o.order_status NOT IN ('CANCELLED', 'REJECTED');
                    """,
                    (vendor_id,),
                )
                recent_units = int(cur.fetchone()["picked_units"])
                if recent_units + requested_units > int(capacity["max_pick_units_per_hour"]):
                    raise AllocationIntegrityError(
                        f"Vendor {vendor_id} hourly pick capacity exhausted: "
                        f"{recent_units + requested_units} > {capacity['max_pick_units_per_hour']}"
                    )

        if window:
            try:
                local_now = now_utc.astimezone(ZoneInfo(window["timezone"] or "Asia/Tehran"))
            except Exception as exc:
                raise AllocationIntegrityError(
                    f"Invalid vendor operating-window timezone for {vendor_id}: {window['timezone']}"
                ) from exc

            current_time = local_now.timetz().replace(tzinfo=None)
            if not (window["opens_at"] <= current_time <= window["closes_at"]):
                raise AllocationIntegrityError(f"Vendor {vendor_id} is outside its operating window.")
            if window["order_cutoff_at"] and current_time > window["order_cutoff_at"]:
                raise AllocationIntegrityError(f"Vendor {vendor_id} order cutoff has passed.")


def validate_allocation_against_basket(cur, basket_id: str, plan_id: str, retailer_id: str,
                                       vendor_allocations: list) -> None:
    """Reject forged/stale allocation input before transactional checkout."""
    cur.execute(
        """
        SELECT b.retailer_id, b.status, b.version,
               p.basket_version, p.status AS plan_status, p.expires_at
        FROM baskets b
        JOIN allocation_plans p ON p.id = %s
        WHERE b.id = %s;
        """,
        (plan_id, basket_id),
    )
    plan = cur.fetchone()
    if not plan:
        raise AllocationIntegrityError("Basket or allocation plan not found.")
    if str(plan["retailer_id"]) != str(retailer_id):
        raise AllocationIntegrityError("Checkout retailer does not own the basket.")
    if plan["status"] not in ("OPEN", "SUBMITTED"):
        raise AllocationIntegrityError(f"Basket status {plan['status']} cannot be checked out.")
    if plan["plan_status"] != "CONFIRMED":
        raise AllocationIntegrityError("Allocation plan is not confirmed.")
    if plan["version"] != plan["basket_version"]:
        raise AllocationIntegrityError("Allocation plan is stale for the current basket version.")
    if plan["expires_at"] < datetime.now(timezone.utc):
        raise AllocationIntegrityError("Allocation plan has expired.")

    cur.execute(
        """
        SELECT product_id, requested_quantity
        FROM basket_items
        WHERE basket_id = %s
        ORDER BY product_id;
        """,
        (basket_id,),
    )
    basket_items = cur.fetchall()
    if not basket_items:
        raise AllocationIntegrityError("Cannot checkout an empty basket.")

    if len(vendor_allocations) != len(basket_items):
        raise AllocationIntegrityError(
            "MVP allocation must assign exactly one vendor offer to each basket line."
        )

    expected = {str(r["product_id"]): int(r["requested_quantity"]) for r in basket_items}
    seen = set()
    vendor_totals = {}

    for alloc in vendor_allocations:
        vp_id = alloc["vendor_product_id"]
        cur.execute(
            """
            SELECT vp.vendor_id, vp.product_id, vp.is_active, vp.listing_status,
                   v.status AS vendor_status, v.min_order_value_toman,
                   vi.moq, vi.physical_quantity, vi.reserved_quantity
            FROM vendor_products vp
            JOIN vendors v ON v.id = vp.vendor_id
            LEFT JOIN vendor_inventory vi ON vi.vendor_product_id = vp.id
            WHERE vp.id = %s;
            """,
            (vp_id,),
        )
        row = cur.fetchone()
        if not row:
            raise AllocationIntegrityError(f"Vendor product {vp_id} does not exist.")
        if not row["is_active"] or row["listing_status"] != "ACTIVE":
            raise AllocationIntegrityError(f"Vendor product {vp_id} is not active.")
        if row["vendor_status"] != "ACTIVE":
            raise AllocationIntegrityError(f"Vendor {row['vendor_id']} is not active.")
        if row["physical_quantity"] is None or row["reserved_quantity"] is None:
            raise AllocationIntegrityError(f"Vendor product {vp_id} has incomplete inventory data.")

        product_id = str(row["product_id"])
        if product_id in seen or product_id not in expected:
            raise AllocationIntegrityError("Allocation does not map one-to-one to basket products.")
        seen.add(product_id)

        qty = int(alloc["quantity"])
        if qty != expected[product_id]:
            raise AllocationIntegrityError(
                f"Quantity mismatch for product {product_id}: allocation={qty}, basket={expected[product_id]}"
            )
        if qty < int(row["moq"]):
            raise AllocationIntegrityError(f"Requested quantity is below vendor MOQ for {vp_id}.")

        available = int(row["physical_quantity"]) - int(row["reserved_quantity"])
        if available < qty:
            raise AllocationIntegrityError(
                f"Available stock is insufficient for {vp_id}: {available} < requested {qty}."
            )

        unit_price = int(alloc["unit_price_toman"])
        amount = int(alloc["amount_toman"])
        if amount != unit_price * qty:
            raise AllocationIntegrityError(f"Line amount mismatch for vendor product {vp_id}.")

        cur.execute(
            """
            SELECT price_toman
            FROM vendor_prices
            WHERE vendor_product_id = %s AND is_current = TRUE;
            """,
            (vp_id,),
        )
        price = cur.fetchone()
        if not price or int(price["price_toman"]) != unit_price:
            raise AllocationIntegrityError(f"Quoted price is not the current vendor price for {vp_id}.")

        vendor_key = str(row["vendor_id"])
        vendor_totals[vendor_key] = vendor_totals.get(vendor_key, 0) + amount

    if seen != set(expected):
        raise AllocationIntegrityError("Allocation is missing one or more basket products.")

    for vendor_id, total in vendor_totals.items():
        cur.execute("SELECT min_order_value_toman FROM vendors WHERE id = %s;", (vendor_id,))
        vendor = cur.fetchone()
        if vendor and total < int(vendor["min_order_value_toman"]):
            raise AllocationIntegrityError(
                f"Vendor minimum order value not met for {vendor_id}: {total} < {vendor['min_order_value_toman']}"
            )

    validate_vendor_operational_capacity(cur, vendor_allocations)


class NotificationRoutingPolicy:
    """Never infer an arbitrary recipient for a domain/integration event."""

    @staticmethod
    def require_explicit_recipient(target_user_id=None, target_org_id=None):
        if not target_user_id or not target_org_id:
            raise ValueError("Notification routing requires an explicit user and organization recipient.")
        return target_user_id, target_org_id


class PaymentReconciliationPolicy:
    """Non-custodial payment remains a claim/evidence/reconciliation workflow."""

    @staticmethod
    def status_for(expected_amount: int, observed_amount: int | None) -> str:
        if observed_amount is None:
            return "OPEN"
        if observed_amount == expected_amount:
            return "MATCHED"
        if observed_amount == 0:
            return "MISMATCH"
        if 0 < observed_amount < expected_amount:
            return "PARTIALLY_MATCHED"
        return "MISMATCH"
