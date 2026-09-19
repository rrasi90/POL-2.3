"""Analytics Event Lineage — Stage 36.

Ensures every KPI is traceable to its source events and tables.
Pure module, no DB dependencies beyond schema checks.
"""

from __future__ import annotations


KPI_DEFINITIONS = {
    "gmv": {
        "description": "Gross Merchandise Value — total order value before deductions",
        "source_table": "orders",
        "source_event": "order_created",
        "calculation": "SUM(total_amount_toman) WHERE order_status IN ('DELIVERED', 'DISPATCHED')",
        "cohort": "none",
        "timezone": "Asia/Tehran",
    },
    "aov": {
        "description": "Average Order Value",
        "source_table": "orders",
        "source_event": "order_created",
        "calculation": "SUM(total_amount_toman) / COUNT(DISTINCT order_id)",
        "cohort": "none",
        "timezone": "Asia/Tehran",
    },
    "repeat_rate": {
        "description": "Repeat retailer rate — % of retailers with >1 order",
        "source_table": "orders",
        "source_event": "order_created",
        "calculation": "COUNT(DISTINCT retailer_id WHERE order_count>1) / COUNT(DISTINCT retailer_id)",
        "cohort": "retailer_signup_date",
        "timezone": "Asia/Tehran",
    },
    "otif": {
        "description": "On-Time In-Full delivery rate",
        "source_table": "orders",
        "source_event": "order_delivered",
        "calculation": "COUNT(orders delivered on time and complete) / COUNT(orders dispatched)",
        "cohort": "none",
        "timezone": "Asia/Tehran",
    },
    "self_service_rate": {
        "description": "Percentage of orders completed without field assistance",
        "source_table": "field_tasks",
        "source_event": "field_task_created",
        "calculation": "1 - (COUNT(FIRST_ORDER_ASSIST tasks) / COUNT(orders))",
        "cohort": "retailer_signup_date",
        "timezone": "Asia/Tehran",
    },
    "churn": {
        "description": "Retailer churn rate — % inactive in last 30 days",
        "source_table": "orders",
        "source_event": "order_created",
        "calculation": "COUNT(retailers with no order in 30d) / COUNT(active retailers)",
        "cohort": "retailer_signup_date",
        "timezone": "Asia/Tehran",
    },
    "cost_to_serve": {
        "description": "Average delivery cost per order",
        "source_table": "settlements",
        "source_event": "settlement_created",
        "calculation": "SUM(platform_fee_toman) / COUNT(orders)",
        "cohort": "none",
        "timezone": "Asia/Tehran",
    },
    "cac": {
        "description": "Customer Acquisition Cost",
        "source_table": "vendor_referrals",
        "source_event": "referral_qualified",
        "calculation": "SUM(reward_amount_toman) / COUNT(qualified retailers)",
        "cohort": "retailer_signup_date",
        "timezone": "Asia/Tehran",
    },
    "vendor_continuation": {
        "description": "Vendor retention rate after first order",
        "source_table": "vendors",
        "source_event": "vendor_activated",
        "calculation": "COUNT(vendors with >1 order in 60d) / COUNT(vendors with >0 orders)",
        "cohort": "vendor_activation_date",
        "timezone": "Asia/Tehran",
    },
    "catalog_coverage": {
        "description": "Percentage of basket items matched to vendor products",
        "source_table": "allocation_items",
        "source_event": "allocation_created",
        "calculation": "COUNT(allocated items) / COUNT(basket items)",
        "cohort": "none",
        "timezone": "Asia/Tehran",
    },
}


REQUIRED_TABLES = [
    "orders", "deliveries", "settlements", "vendors", "retailers",
    "allocation_items", "field_tasks", "vendor_referrals",
]


def validate_lineage(cur) -> list[str]:
    """Check all source tables exist in DB. Returns list of missing tables."""
    missing = []
    for table in REQUIRED_TABLES:
        cur.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_name = %s",
            (table,),
        )
        if not cur.fetchone():
            missing.append(table)
    return missing
