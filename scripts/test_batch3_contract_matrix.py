from copy import deepcopy
import json
from pathlib import Path
import re

import pytest
from psycopg2.errors import CheckViolation

from scripts.application_boundary import ApplicationContext, POLApplicationBoundary
from scripts.returns_rma import ReturnStateError
from scripts.test_batch2_rma_and_outbox import rma_case, open_return
from scripts.test_e2e_mvp_platform import (
    postgres_database, checkout_catalog, checkout_request, snapshot, transaction,
)

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_ORDER_STATES = {
    "CREATED", "SUBMITTED", "ACCEPTED", "PARTIALLY_ACCEPTED", "REJECTED",
    "PREPARING", "READY", "DISPATCHED", "DELIVERED", "CANCELLED",
}


def read(path):
    return (ROOT / path).read_text(encoding="utf-8-sig")


def test_order_lifecycle_states_match_schema_vocabulary():
    lifecycle = read("06_PRODUCT/Order_Lifecycle.md")
    schema = read("migrations/001_initial_schema.sql")
    state_check = re.search(r"order_status IN\s*\((.*?)\)", schema, re.S).group(1)
    assert set(re.findall(r"'([A-Z_]+)'", state_check)) == CANONICAL_ORDER_STATES
    assert all(f"`{state}`" in lifecycle for state in CANONICAL_ORDER_STATES)


def test_api_contract_uses_submitted_not_pending_for_child_orders():
    api = read("06_PRODUCT/API_Contracts.md")
    section = api[api.index("### ۵.۱."):api.index("### ۵.۲.")]
    examples = [json.loads(block) for block in re.findall(r"```json\s*(.*?)```", section, re.S)]
    response = next(example for example in examples if "child_orders" in example)
    assert response["group_status"] == "ACTIVE"
    assert len(response["child_orders"]) == 2
    assert {order["order_status"] for order in response["child_orders"]} == {"SUBMITTED"}


@pytest.mark.parametrize("state", ["PENDING", "PROCESSING", "CONFIRMED", "COMPLETED"])
def test_database_rejects_non_canonical_order_states(
    postgres_database, checkout_catalog, checkout_request, state,
):
    with transaction(postgres_database) as cur:
        result = POLApplicationBoundary(cur, checkout_catalog["context"]).checkout(**deepcopy(checkout_request))
        order_id = result["orders"][0]["id"]
        before = snapshot(cur)
    with pytest.raises(CheckViolation) as failure:
        with transaction(postgres_database) as cur:
            cur.execute("UPDATE orders SET order_status=%s WHERE id=%s", (state, order_id))
    assert failure.value.diag.constraint_name == "orders_order_status_check"
    with transaction(postgres_database) as cur:
        assert snapshot(cur) == before


@pytest.mark.parametrize("context_kind", ["wrong_org", "inactive_membership", "missing_context"])
def test_checkout_rejects_invalid_tenant_context(
    postgres_database, checkout_catalog, checkout_request, context_kind,
):
    actor = checkout_catalog["context"]
    with transaction(postgres_database) as cur:
        if context_kind == "wrong_org":
            cur.execute("SELECT organization_id FROM vendors ORDER BY id LIMIT 1")
            actor = ApplicationContext(actor.user_id, str(cur.fetchone()["organization_id"]), actor.correlation_id)
        elif context_kind == "missing_context":
            actor = ApplicationContext(actor.user_id, None, actor.correlation_id)
        else:
            cur.execute(
                "UPDATE organization_memberships SET status='SUSPENDED' WHERE user_id=%s AND organization_id=%s",
                (actor.user_id, actor.organization_id),
            )
        before = snapshot(cur)
    with pytest.raises(PermissionError):
        with transaction(postgres_database) as cur:
            POLApplicationBoundary(cur, actor).checkout(**deepcopy(checkout_request))
    with transaction(postgres_database) as cur:
        assert snapshot(cur) == before


@pytest.mark.parametrize("change, message", [
    ("price", "Quoted price is not the current vendor price"),
    ("stock", "Available stock is insufficient"),
])
@pytest.mark.parametrize("mutation", ["inactive_user", "suspended_org"])
def test_boundary_role_resolution_rejects_inactive_security_context(
    postgres_database, checkout_catalog, mutation,
):
    actor = checkout_catalog["context"]
    with transaction(postgres_database) as cur:
        if mutation == "inactive_user":
            cur.execute("UPDATE users SET is_active=FALSE WHERE id=%s", (actor.user_id,))
        else:
            cur.execute("UPDATE organizations SET status='SUSPENDED' WHERE id=%s", (actor.organization_id,))
    with pytest.raises(PermissionError):
        with transaction(postgres_database) as cur:
            POLApplicationBoundary(cur, actor).order_list(limit=5)
    # The mutation above is intentional test state; fixture teardown owns restoration.

def test_checkout_revalidates_live_offer(
    postgres_database, checkout_catalog, checkout_request, change, message,
):
    offer_id = checkout_catalog["lines"][0]["vendor_product_id"]
    with transaction(postgres_database) as cur:
        if change == "price":
            cur.execute(
                "UPDATE vendor_prices SET price_toman=price_toman+1 WHERE vendor_product_id=%s AND is_current=TRUE",
                (offer_id,),
            )
        else:
            cur.execute("UPDATE vendor_inventory SET physical_quantity=0 WHERE vendor_product_id=%s", (offer_id,))
        before = snapshot(cur)
    with pytest.raises(ValueError, match=message):
        with transaction(postgres_database) as cur:
            POLApplicationBoundary(cur, checkout_catalog["context"]).checkout(**deepcopy(checkout_request))
    with transaction(postgres_database) as cur:
        assert snapshot(cur) == before


def test_rma_boundary_rejects_illegal_transition(postgres_database, rma_case):
    with transaction(postgres_database) as cur:
        ret = open_return(cur, rma_case)
    with pytest.raises(ReturnStateError, match="Invalid RMA transition"):
        with transaction(postgres_database) as cur:
            POLApplicationBoundary(cur, rma_case["vendor"]).return_transition(
                return_id=ret["id"], target_status="REFUNDED",
            )
    with transaction(postgres_database) as cur:
        cur.execute("SELECT status FROM returns WHERE id=%s", (ret["id"],))
        assert cur.fetchone()["status"] == "RETURN_REQUESTED"
        cur.execute("SELECT count(*) AS count FROM refunds WHERE return_id=%s", (ret["id"],))
        assert cur.fetchone()["count"] == 0
