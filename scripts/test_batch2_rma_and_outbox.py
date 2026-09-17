from copy import deepcopy
from uuid import uuid4

import psycopg2
import pytest
from psycopg2.errors import CheckViolation

from scripts.application_boundary import ApplicationContext, POLApplicationBoundary
from scripts.returns_rma import ReturnAccessError, ReturnStateError
from scripts.test_e2e_mvp_platform import (
    postgres_database, checkout_catalog, checkout_request,
    insert_row, snapshot, transaction,
)


def context(user_id, organization_id):
    return ApplicationContext(str(user_id), str(organization_id) if organization_id else None, uuid4().hex)


def add_member(cur, organization_id, role, user_id=None):
    if user_id is None:
        user_id = insert_row(
            cur, "users", phone_number=f"+989{uuid4().int % 1000000000:09d}",
            role="OPS_AGENT", full_name="Batch2 test actor",
        )["id"]
    insert_row(
        cur, "organization_memberships", organization_id=organization_id,
        user_id=user_id, role=role, status="ACTIVE", is_primary=False,
    )
    return context(user_id, organization_id)


@pytest.fixture
def rma_case(postgres_database, checkout_catalog, checkout_request):
    with transaction(postgres_database) as cur:
        result = POLApplicationBoundary(cur, checkout_catalog["context"]).checkout(**deepcopy(checkout_request))
        order = result["orders"][0]
        cur.execute("UPDATE orders SET order_status='DELIVERED' WHERE id=%s", (order["id"],))
        cur.execute("SELECT id FROM order_items WHERE order_id=%s ORDER BY id", (order["id"],))
        item_id = cur.fetchone()["id"]
        cur.execute("SELECT organization_id, user_id FROM vendors WHERE id=%s", (order["vendor_id"],))
        vendor = cur.fetchone()
        payload = dict(
            order_id=str(order["id"]), order_items=[{"order_item_id": str(item_id), "quantity": 1}],
            reason="DAMAGED", idempotency_key=uuid4().hex, claimed_refund_amount_toman=1000,
        )
    return dict(
        payload=payload, retailer=checkout_catalog["context"],
        vendor=context(vendor["user_id"], vendor["organization_id"]), order=order,
    )


def open_return(cur, case):
    return POLApplicationBoundary(cur, case["retailer"]).return_request(**deepcopy(case["payload"]))


def accept_return(cur, case):
    ret = open_return(cur, case)
    boundary = POLApplicationBoundary(cur, case["vendor"])
    for status in ("APPROVED", "PICKUP_REQUIRED", "RETURN_IN_TRANSIT", "RECEIVED", "VENDOR_INSPECTION", "ACCEPTED"):
        ret = boundary.return_transition(return_id=ret["id"], target_status=status)
    return ret


@pytest.mark.parametrize("replay", [False, True])
def test_rma_retailer_context_and_replay(postgres_database, rma_case, replay):
    with transaction(postgres_database) as cur:
        other_org = insert_row(cur, "organizations", name="Other retailer", org_type="RETAILER", status="ACTIVE")
        other_context = add_member(cur, other_org["id"], "RETAILER_OWNER")
        intruder_org = insert_row(cur, "organizations", name="Intruder retailer", org_type="RETAILER", status="ACTIVE")
        intruder_context = add_member(cur, intruder_org["id"], "RETAILER_OWNER")
        if replay:
            open_return(cur, rma_case)
    for denied in (other_context, intruder_context, context(rma_case["retailer"].user_id, None)):
        with pytest.raises(ReturnAccessError):
            with transaction(postgres_database) as cur:
                POLApplicationBoundary(cur, denied).return_request(**deepcopy(rma_case["payload"]))
    with transaction(postgres_database) as cur:
        ret = open_return(cur, rma_case)
        again = open_return(cur, rma_case)
        assert ret["id"] == again["id"]
        cur.execute("SELECT count(*) AS c FROM returns")
        assert cur.fetchone()["c"] == 1
    with pytest.raises(ReturnAccessError):
        with transaction(postgres_database) as cur:
            POLApplicationBoundary(cur, other_context).return_transition(return_id=ret["id"], target_status="CANCELLED")
    with transaction(postgres_database) as cur:
        cancelled = POLApplicationBoundary(cur, rma_case["retailer"]).return_transition(return_id=ret["id"], target_status="CANCELLED")
        assert cancelled["status"] == "CANCELLED"


def test_rma_vendor_context(postgres_database, rma_case):
    with transaction(postgres_database) as cur:
        ret = open_return(cur, rma_case)
        cur.execute("SELECT organization_id FROM vendors WHERE id<>%s", (rma_case["order"]["vendor_id"],))
        other_org = cur.fetchone()["organization_id"]
        other_context = add_member(cur, other_org, "VENDOR_STAFF", rma_case["vendor"].user_id)
    for status in ("APPROVED", "PICKUP_REQUIRED", "RETURN_IN_TRANSIT", "RECEIVED", "VENDOR_INSPECTION", "ACCEPTED"):
        for denied in (other_context, context(rma_case["vendor"].user_id, None)):
            with pytest.raises(ReturnAccessError):
                with transaction(postgres_database) as cur:
                    POLApplicationBoundary(cur, denied).return_transition(return_id=ret["id"], target_status=status)
        with transaction(postgres_database) as cur:
            updated = POLApplicationBoundary(cur, rma_case["vendor"]).return_transition(return_id=ret["id"], target_status=status)
            assert updated["status"] == status


@pytest.mark.parametrize("role", ["ADMIN_SUPER", "OPS_AGENT", "SUPER_ADMIN", "OPS_ADMIN"])
def test_rma_ops_context_and_separation_of_duties(postgres_database, rma_case, role):
    with transaction(postgres_database) as cur:
        ret = accept_return(cur, rma_case)
        org = insert_row(cur, "organizations", name="Batch2 operator", org_type="OPERATOR", status="ACTIVE")
        approver = add_member(cur, org["id"], role)
        completer = add_member(cur, org["id"], role)
        initiator_ops = add_member(cur, org["id"], role, rma_case["retailer"].user_id)
        other_org = insert_row(cur, "organizations", name="Other operator", org_type="OPERATOR", status="ACTIVE")
        other_context = context(approver.user_id, other_org["id"])
    for denied in (other_context, rma_case["vendor"], rma_case["retailer"], context(approver.user_id, None), initiator_ops):
        with pytest.raises(ReturnAccessError):
            with transaction(postgres_database) as cur:
                POLApplicationBoundary(cur, denied).return_transition(
                    return_id=ret["id"], target_status="REFUND_PENDING", approved_refund_amount_toman=1000,
                )
    with transaction(postgres_database) as cur:
        cur.execute("SELECT status FROM returns WHERE id=%s", (ret["id"],))
        assert cur.fetchone()["status"] == "ACCEPTED"
        pending = POLApplicationBoundary(cur, approver).return_transition(
            return_id=ret["id"], target_status="REFUND_PENDING", approved_refund_amount_toman=1000,
        )
        assert pending["status"] == "REFUND_PENDING"
    with pytest.raises(ReturnAccessError, match="different actor than the approver"):
        with transaction(postgres_database) as cur:
            POLApplicationBoundary(cur, approver).return_transition(return_id=ret["id"], target_status="REFUNDED")
    with transaction(postgres_database) as cur:
        done = POLApplicationBoundary(cur, completer).return_transition(return_id=ret["id"], target_status="REFUNDED")
        assert done["status"] == "REFUNDED"
        cur.execute("SELECT * FROM refunds WHERE return_id=%s", (ret["id"],))
        refund = cur.fetchone()
        assert str(refund["approved_by_user_id"]) == approver.user_id
        assert str(refund["completed_by_user_id"]) == completer.user_id
        assert refund["status"] == "COMPLETED"
        assert refund["refund_method"] == "VENDOR_CASH_DIRECT"
        assert refund["amount_toman"] == 1000


@pytest.mark.parametrize("status", ["REFUND_PENDING", "REFUNDED"])
@pytest.mark.parametrize("amount", [None, 0, -1])
def test_refund_invalid_amount_rejected_by_database(postgres_database, rma_case, status, amount):
    with transaction(postgres_database) as cur:
        ret = open_return(cur, rma_case)
    with pytest.raises(CheckViolation) as failure:
        with transaction(postgres_database) as cur:
            cur.execute(
                "UPDATE returns SET status=%s, approved_refund_amount_toman=%s WHERE id=%s",
                (status, amount, ret["id"]),
            )
    assert failure.value.diag.constraint_name == "chk_returns_refund_pending_amount"
    with transaction(postgres_database) as cur:
        cur.execute("SELECT status, approved_refund_amount_toman FROM returns WHERE id=%s", (ret["id"],))
        row = cur.fetchone()
        assert row["status"] == "RETURN_REQUESTED"
        assert row["approved_refund_amount_toman"] is None


def submission_events(cur):
    cur.execute(
        """
        SELECT event_name, aggregate_id, target_user_id, target_organization_id, dedupe_key, status
        FROM outbox_events
        WHERE event_name IN ('ORDER_GROUP_SUBMITTED', 'ORDER_SUBMITTED')
        ORDER BY event_name, aggregate_id, target_organization_id, target_user_id
        """
    )
    return cur.fetchall()


def test_checkout_enqueues_submission_events_with_explicit_routing(
    postgres_database, checkout_catalog, checkout_request,
):
    with transaction(postgres_database) as cur:
        add_member(cur, checkout_catalog["context"].organization_id, "RETAILER_STAFF")
        cur.execute("SELECT organization_id FROM vendors ORDER BY id")
        vendor_orgs = [row["organization_id"] for row in cur.fetchall()]
        for org_id in vendor_orgs:
            add_member(cur, org_id, "VENDOR_STAFF")
        result = POLApplicationBoundary(cur, checkout_catalog["context"]).checkout(**deepcopy(checkout_request))
        events = submission_events(cur)
        assert [row["event_name"] for row in events].count("ORDER_GROUP_SUBMITTED") == 2
        assert [row["event_name"] for row in events].count("ORDER_SUBMITTED") == 4
        cur.execute(
            "SELECT organization_id, user_id FROM organization_memberships WHERE status='ACTIVE'"
        )
        members = {(str(r["organization_id"]), str(r["user_id"])) for r in cur.fetchall()}
        for row in events:
            assert row["status"] == "PENDING"
            assert (str(row["target_organization_id"]), str(row["target_user_id"])) in members
            assert row["dedupe_key"].startswith(row["event_name"] + ":")
            assert row["dedupe_key"] == ":".join((
                row["event_name"], str(row["aggregate_id"]),
                str(row["target_organization_id"]), str(row["target_user_id"]),
            ))
    with transaction(postgres_database) as cur:
        replay = POLApplicationBoundary(cur, checkout_catalog["context"]).checkout(**deepcopy(checkout_request))
        assert replay["idempotent_replay"] is True
        assert len(submission_events(cur)) == len(events)
    with transaction(postgres_database) as cur:
        from scripts.canonical_integration_worker import CanonicalIntegrationWorker

        processed_first = CanonicalIntegrationWorker.process_pending(cur, limit=100)
        notifications_first = cur.execute("SELECT count(*) AS c FROM notifications") or cur
        cur.execute("SELECT count(*) AS c FROM notifications")
        count_first = cur.fetchone()["c"]
        assert count_first == len(events)
        processed_second = CanonicalIntegrationWorker.process_pending(cur, limit=100)
        cur.execute("SELECT count(*) AS c FROM notifications")
        assert cur.fetchone()["c"] == count_first
        cur.execute(
            "SELECT count(*) AS c FROM outbox_events WHERE event_name IN ('ORDER_GROUP_SUBMITTED','ORDER_SUBMITTED')"
        )
        assert cur.fetchone()["c"] == len(events)


def test_checkout_rollback_leaves_no_submission_events(postgres_database, checkout_catalog, checkout_request):
    with transaction(postgres_database) as cur:
        before = snapshot(cur)
    with pytest.raises(psycopg2.errors.RaiseException, match="batch2 checkout fault"):
        with transaction(postgres_database) as cur:
            cur.execute(
                """
                CREATE FUNCTION pg_temp.batch2_outbox_fault() RETURNS trigger
                LANGUAGE plpgsql AS $$
                BEGIN
                    IF NEW.event_name IN ('ORDER_GROUP_SUBMITTED','ORDER_SUBMITTED') THEN
                        RAISE EXCEPTION 'batch2 checkout fault';
                    END IF;
                    RETURN NEW;
                END;
                $$;
                CREATE TRIGGER batch2_outbox_fault
                BEFORE INSERT ON outbox_events
                FOR EACH ROW EXECUTE FUNCTION pg_temp.batch2_outbox_fault();
                """
            )
            POLApplicationBoundary(cur, checkout_catalog["context"]).checkout(**deepcopy(checkout_request))
    with transaction(postgres_database) as cur:
        assert snapshot(cur) == before
        assert submission_events(cur) == []


def test_existing_order_events_templates_remain_active(postgres_database, checkout_catalog, checkout_request):
    with transaction(postgres_database) as cur:
        cur.execute(
            """
            SELECT event_name FROM notification_templates
            WHERE event_name IN ('ORDER_SUBMITTED','ORDER_GROUP_SUBMITTED','ORDER_ACCEPTED','ORDER_REJECTED')
              AND enabled = TRUE
            ORDER BY event_name
            """
        )
        assert [row["event_name"] for row in cur.fetchall()] == [
            "ORDER_ACCEPTED", "ORDER_GROUP_SUBMITTED", "ORDER_REJECTED", "ORDER_SUBMITTED",
        ]
