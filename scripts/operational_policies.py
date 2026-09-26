"""POL operational policies for checkout integrity and operational realism."""

from datetime import datetime, timezone, time, timedelta
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


def _local_day_bounds(now_utc: datetime, tz_name: str):
    """Return vendor-local now, local weekday, and UTC instants for local day bounds."""
    try:
        tz = ZoneInfo(tz_name or "Asia/Tehran")
    except Exception as exc:
        raise AllocationIntegrityError(f"Invalid vendor timezone: {tz_name}") from exc

    local_now = now_utc.astimezone(tz)
    local_midnight = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    next_midnight = local_midnight.replace(day=local_midnight.day) + __import__("datetime").timedelta(days=1)
    # PostgreSQL weekday convention: Sunday=0 ... Saturday=6.
    postgres_weekday = (local_now.weekday() + 1) % 7
    return local_now, postgres_weekday, local_midnight.astimezone(timezone.utc), next_midnight.astimezone(timezone.utc)


def _resolve_operating_window(cur, vendor_id: str, now_utc: datetime, fallback_tz_name: str):
    """Resolve the active operating window in the window row's own timezone."""
    cur.execute(
        """
        SELECT id, timezone, weekday, opens_at, closes_at, order_cutoff_at, effective_from
        FROM vendor_operating_windows
        WHERE vendor_id = %s
          AND is_active = TRUE
          AND effective_from <= now()
          AND (effective_until IS NULL OR effective_until > now())
        ORDER BY effective_from DESC, id ASC;
        """,
        (vendor_id,),
    )
    windows = cur.fetchall()
    if not windows:
        return None

    matches = []
    for window in windows:
        tz_name = window["timezone"] or fallback_tz_name or "Asia/Tehran"
        try:
            tz = ZoneInfo(tz_name)
        except Exception as exc:
            raise AllocationIntegrityError(f"Invalid vendor timezone: {tz_name}") from exc

        local_now = now_utc.astimezone(tz)
        current_time = local_now.timetz().replace(tzinfo=None)
        current_weekday = (local_now.weekday() + 1) % 7
        opens_at = window["opens_at"]
        closes_at = window["closes_at"]
        overnight = opens_at > closes_at
        business_weekday = (
            (current_weekday - 1) % 7
            if overnight and current_time <= closes_at
            else current_weekday
        )
        if int(window["weekday"]) != business_weekday:
            continue
        matches.append((window, local_now, current_time, overnight))

    if not matches:
        return None
    return matches[0]


def validate_vendor_operational_capacity(cur, vendor_allocations: list) -> None:
    """Apply configured vendor hours/capacity using the vendor's own timezone/day boundary."""
    _, vendor_units = _vendor_allocated_totals(vendor_allocations)
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
        tz_name = (capacity["timezone"] if capacity and capacity["timezone"] else "Asia/Tehran")
        local_now, local_weekday, day_start_utc, next_day_start_utc = _local_day_bounds(now_utc, tz_name)

        window_match = _resolve_operating_window(cur, vendor_id, now_utc, tz_name)

        if capacity:
            if capacity["max_orders_per_day"] is not None:
                cur.execute(
                    """
                    SELECT COUNT(*) AS order_count
                    FROM orders
                    WHERE vendor_id = %s
                      AND created_at >= %s
                      AND created_at < %s
                      AND order_status NOT IN ('CANCELLED', 'REJECTED');
                    """,
                    (vendor_id, day_start_utc, next_day_start_utc),
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
                    SELECT COALESCE(SUM(oi.ordered_quantity), 0) AS picked_units
                    FROM order_items oi
                    JOIN orders o ON o.id = oi.order_id
                    WHERE o.vendor_id = %s
                      AND o.created_at >= %s - interval '1 hour'
                      AND o.order_status NOT IN ('CANCELLED', 'REJECTED');
                    """,
                    (vendor_id, now_utc),
                )
                recent_units = int(cur.fetchone()["picked_units"])
                if recent_units + requested_units > int(capacity["max_pick_units_per_hour"]):
                    raise AllocationIntegrityError(
                        f"Vendor {vendor_id} hourly pick capacity exhausted: "
                        f"{recent_units + requested_units} > {capacity['max_pick_units_per_hour']}"
                    )

        if window_match:
            window, window_local_now, current_time, overnight = window_match
            opens_at = window["opens_at"]
            closes_at = window["closes_at"]
            cutoff = window["order_cutoff_at"]

            if opens_at <= closes_at:
                in_window = opens_at <= current_time <= closes_at
            else:
                in_window = current_time >= opens_at or current_time <= closes_at

            if not in_window:
                raise AllocationIntegrityError(f"Vendor {vendor_id} is outside its operating window.")
            if cutoff and current_time > cutoff:
                raise AllocationIntegrityError(f"Vendor {vendor_id} order cutoff has passed.")


def validate_allocation_against_basket(cur, basket_id: str, plan_id: str, retailer_id: str,
                                       vendor_allocations: list) -> None:
    """Reject forged/stale allocation input before transactional checkout.

    An allocation plan may legally contain UNFULFILLED basket lines. Checkout
    commits only ALLOCATED/PARTIALLY_ALLOCATED lines and leaves the unfulfilled
    demand represented in the consumed allocation plan.
    """
    allocated_statuses = {"ALLOCATED", "PARTIALLY_ALLOCATED"}

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
        SELECT bi.product_id, ai.vendor_product_id, ai.status,
               ai.allocated_quantity, ai.unit_price_snapshot_toman,
               ai.line_total_toman
        FROM allocation_items ai
        JOIN basket_items bi ON bi.id = ai.basket_item_id
        WHERE ai.allocation_plan_id = %s
          AND bi.basket_id = %s
        ORDER BY ai.id;
        """,
        (plan_id, basket_id),
    )
    plan_items = cur.fetchall()
    if not plan_items:
        raise AllocationIntegrityError("Allocation plan has no basket lines.")

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

    expected_requested = {
        str(row["product_id"]): int(row["requested_quantity"])
        for row in basket_items
    }
    plan_by_product = {}
    for row in plan_items:
        product_id = str(row["product_id"])
        if product_id in plan_by_product:
            raise AllocationIntegrityError("Allocation plan contains duplicate basket products.")
        plan_by_product[product_id] = row

    if set(plan_by_product) != set(expected_requested):
        raise AllocationIntegrityError("Allocation plan does not cover the current basket lines.")

    invalid_statuses = {
        row["status"]
        for row in plan_items
        if row["status"] not in allocated_statuses and row["status"] != "UNFULFILLED"
    }
    if invalid_statuses:
        raise AllocationIntegrityError(
            f"Allocation plan contains invalid line statuses: {sorted(invalid_statuses)}"
        )

    allocated_plan = [
        row for row in plan_items if row["status"] in allocated_statuses
    ]
    if not allocated_plan:
        raise AllocationIntegrityError("Cannot checkout an allocation plan with no fulfilled lines.")

    if len(vendor_allocations) != len(allocated_plan):
        raise AllocationIntegrityError(
            "Checkout allocations must exactly match the fulfilled allocation-plan lines."
        )

    expected_allocations = {
        (
            str(row["product_id"]),
            str(row["vendor_product_id"]),
            int(row["allocated_quantity"]),
            int(row["unit_price_snapshot_toman"]),
            int(row["line_total_toman"]),
        )
        for row in allocated_plan
    }
    if len(expected_allocations) != len(allocated_plan):
        raise AllocationIntegrityError("Allocation plan contains duplicate fulfilled allocation lines.")

    seen = set()
    supplied_allocations = set()
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
        if product_id in seen or product_id not in expected_requested:
            raise AllocationIntegrityError("Allocation does not map one-to-one to basket products.")
        seen.add(product_id)

        persisted = plan_by_product.get(product_id)
        if not persisted or persisted["status"] not in allocated_statuses:
            raise AllocationIntegrityError(
                f"Allocation for product {product_id} is not present as a fulfilled plan line."
            )

        qty = int(alloc["quantity"])
        unit_price = int(alloc["unit_price_toman"])
        amount = int(alloc["amount_toman"])
        expected_tuple = (
            product_id,
            str(persisted["vendor_product_id"]),
            int(persisted["allocated_quantity"]),
            int(persisted["unit_price_snapshot_toman"]),
            int(persisted["line_total_toman"]),
        )
        supplied_tuple = (product_id, str(vp_id), qty, unit_price, amount)
        if supplied_tuple != expected_tuple:
            raise AllocationIntegrityError(
                f"Checkout allocation does not match the persisted plan for product {product_id}."
            )
        supplied_allocations.add(supplied_tuple)

        if qty <= 0:
            raise AllocationIntegrityError(f"Allocated quantity must be positive for {vp_id}.")
        if qty < int(row["moq"]):
            raise AllocationIntegrityError(f"Requested quantity is below vendor MOQ for {vp_id}.")

        available = int(row["physical_quantity"]) - int(row["reserved_quantity"])
        if available < qty:
            raise AllocationIntegrityError(
                f"Available stock is insufficient for {vp_id}: {available} < requested {qty}."
            )

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

    expected_products = {
        str(row["product_id"]) for row in allocated_plan
    }
    if seen != expected_products or supplied_allocations != expected_allocations:
        raise AllocationIntegrityError(
            "Checkout allocations do not exactly match the fulfilled allocation plan."
        )

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
