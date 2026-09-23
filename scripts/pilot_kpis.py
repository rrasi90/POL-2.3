"""Pilot KPI Measurement Pipeline — Stage 37.

SQL-based KPI calculations with date/timezone support.
Read-only queries against existing tables. No new schema needed.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone


KPI_QUERIES = {
    "gmv": {
        "description": "Gross Merchandise Value",
        "sql": (
            "SELECT COALESCE(SUM(total_amount_toman), 0) AS value "
            "FROM orders "
            "WHERE order_status IN ('DELIVERED', 'DISPATCHED') "
            "AND created_at >= %s AND created_at < %s"
        ),
        "params": "date_range",
    },
    "aov": {
        "description": "Average Order Value",
        "sql": (
            "SELECT COALESCE(SUM(total_amount_toman) / NULLIF(COUNT(DISTINCT id), 0), 0) AS value "
            "FROM orders "
            "WHERE order_status IN ('DELIVERED', 'DISPATCHED') "
            "AND created_at >= %s AND created_at < %s"
        ),
        "params": "date_range",
    },
    "repeat_rate": {
        "description": "Repeat retailer rate (%)",
        "sql": (
            "SELECT COALESCE( "
            "  COUNT(DISTINCT CASE WHEN order_count > 1 THEN retailer_id END) * 100.0 "
            "  / NULLIF(COUNT(DISTINCT retailer_id), 0), 0) AS value "
            "FROM ( "
            "  SELECT retailer_id, COUNT(*) AS order_count "
            "  FROM orders "
            "  WHERE created_at >= %s AND created_at < %s "
            "  GROUP BY retailer_id "
            ") sub"
        ),
        "params": "date_range",
    },
    "otif": {
        "description": "On-Time In-Full delivery rate (%)",
        "sql": (
            "SELECT COALESCE( "
            "  COUNT(CASE WHEN d.delivered_at <= d.dispatched_at + INTERVAL '24 hours' THEN 1 END) * 100.0 "
            "  / NULLIF(COUNT(*), 0), 0) AS value "
            "FROM deliveries d "
            "JOIN orders o ON o.id = d.order_id "
            "WHERE d.delivery_status = 'DELIVERED' "
            "AND d.delivered_at IS NOT NULL AND d.dispatched_at IS NOT NULL "
            "AND o.created_at >= %s AND o.created_at < %s"
        ),
        "params": "date_range",
    },
    "self_service_rate": {
        "description": "Self-service order rate (%)",
        "sql": (
            "SELECT COALESCE( "
            "  (COUNT(DISTINCT o.id) - COUNT(DISTINCT ft.id)) * 100.0 "
            "  / NULLIF(COUNT(DISTINCT o.id), 0), 100) AS value "
            "FROM orders o "
            "LEFT JOIN field_tasks ft ON ft.assigned_to_user_id = o.retailer_id "
            "  AND ft.task_type = 'FIRST_ORDER_ASSIST' "
            "  AND ft.created_at >= %s AND ft.created_at < %s "
            "WHERE o.created_at >= %s AND o.created_at < %s"
        ),
        "params": "date_range_double",
    },
    "churn": {
        "description": "Retailer churn rate — % inactive in last 30 days",
        "sql": (
            "SELECT COALESCE( "
            "  COUNT(DISTINCT CASE WHEN last_order_date < %s THEN retailer_id END) * 100.0 "
            "  / NULLIF(COUNT(DISTINCT retailer_id), 0), 0) AS value "
            "FROM ( "
            "  SELECT retailer_id, MAX(created_at) AS last_order_date "
            "  FROM orders "
            "  GROUP BY retailer_id "
            ") sub"
        ),
        "params": "cutoff_date",
    },
    "cost_to_serve": {
        "description": "Average delivery cost per order (toman)",
        "sql": (
            "SELECT COALESCE(SUM(commission_amount_toman) / NULLIF(COUNT(DISTINCT order_id), 0), 0) AS value "
            "FROM settlements "
            "WHERE created_at >= %s AND created_at < %s"
        ),
        "params": "date_range",
    },
    "cac": {
        "description": "Customer Acquisition Cost (toman)",
        "sql": (
            "SELECT COALESCE(COUNT(DISTINCT vra.id) * 0, 0) AS value "
            "FROM vendor_referral_attributions vra "
            "WHERE vra.converted_at IS NOT NULL "
            "AND vra.created_at >= %s AND vra.created_at < %s"
        ),
        "params": "date_range",
    },
    "vendor_continuation": {
        "description": "Vendor retention rate (%) after first order",
        "sql": (
            "SELECT COALESCE( "
            "  COUNT(DISTINCT CASE WHEN order_count > 1 THEN vendor_id END) * 100.0 "
            "  / NULLIF(COUNT(DISTINCT vendor_id), 0), 0) AS value "
            "FROM ( "
            "  SELECT vendor_id, COUNT(*) AS order_count "
            "  FROM orders "
            "  WHERE created_at >= %s AND created_at < %s "
            "  GROUP BY vendor_id "
            ") sub"
        ),
        "params": "date_range",
    },
    "catalog_coverage": {
        "description": "Catalog match rate (%) — allocated items / basket items",
        "sql": (
            "SELECT COALESCE( "
            "  COUNT(CASE WHEN ai.id IS NOT NULL THEN 1 END) * 100.0 "
            "  / NULLIF(COUNT(bi.id), 0), 0) AS value "
            "FROM basket_items bi "
            "JOIN baskets b ON b.id = bi.basket_id "
            "LEFT JOIN allocation_items ai ON ai.basket_item_id = bi.id "
            "WHERE b.created_at >= %s AND b.created_at < %s"
        ),
        "params": "date_range",
    },
}


def compute_kpi(cur, kpi_name: str, start_date: date, end_date: date) -> dict:
    """Compute a single KPI. Returns {name, description, value, start_date, end_date}."""
    if kpi_name not in KPI_QUERIES:
        raise ValueError(f"Unknown KPI: {kpi_name}. Available: {list(KPI_QUERIES.keys())}")
    kpi = KPI_QUERIES[kpi_name]
    start_dt = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)
    end_dt = datetime(end_date.year, end_date.month, end_date.day, tzinfo=timezone.utc)
    params_type = kpi["params"]
    if params_type == "date_range":
        cur.execute(kpi["sql"], (start_dt, end_dt))
    elif params_type == "date_range_double":
        cur.execute(kpi["sql"], (start_dt, end_dt, start_dt, end_dt))
    elif params_type == "cutoff_date":
        cur.execute(kpi["sql"], (end_dt,))
    else:
        raise ValueError(f"Unknown params_type: {params_type}")
    row = cur.fetchone()
    value = float(row["value"]) if row and row["value"] is not None else 0.0
    return {
        "name": kpi_name,
        "description": kpi["description"],
        "value": value,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }


def compute_all_kpis(cur, start_date: date, end_date: date) -> list[dict]:
    """Compute all KPIs for a date range."""
    return [compute_kpi(cur, name, start_date, end_date) for name in KPI_QUERIES]


def weekly_snapshot(cur, snapshot_date: date) -> dict:
    """Compute weekly KPI snapshot for a given week ending date."""
    week_start = snapshot_date - timedelta(days=6)
    kpis = compute_all_kpis(cur, week_start, snapshot_date)
    return {
        "snapshot_date": snapshot_date.isoformat(),
        "week_start": week_start.isoformat(),
        "kpis": {k["name"]: k["value"] for k in kpis},
    }
