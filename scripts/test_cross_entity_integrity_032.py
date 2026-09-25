import psycopg2
import pytest
from uuid import uuid4

from scripts.test_e2e_mvp_platform import checkout_catalog, checkout_request, postgres_database, transaction


def _checkout(cur, catalog, request):
    from scripts.application_boundary import POLApplicationBoundary

    result = POLApplicationBoundary(cur, catalog["context"]).checkout(**request)
    return result


@pytest.fixture
def checkout_result(postgres_database, checkout_catalog, checkout_request):
    with transaction(postgres_database) as cur:
        return _checkout(cur, checkout_catalog, checkout_request)


def _order_and_item_ids(cur, result):
    cur.execute(
        "SELECT id, vendor_id, retailer_id FROM orders WHERE order_group_id=%s ORDER BY vendor_id",
        (result["order_group_id"],),
    )
    orders = cur.fetchall()
    order_a = orders[0]
    cur.execute(
        "SELECT * FROM order_items WHERE order_id=%s ORDER BY id LIMIT 1",
        (order_a["id"],),
    )
    return order_a, cur.fetchone()


def test_order_item_rejects_cross_vendor_product(postgres_database, checkout_catalog, checkout_request, checkout_result):
    with pytest.raises(psycopg2.Error, match="ORDER_ITEM_VENDOR_MISMATCH"):
        with transaction(postgres_database) as cur:
            order_a, item = _order_and_item_ids(cur, checkout_result)
            cur.execute(
                """
                SELECT vp.id
                FROM vendor_products vp
                WHERE vp.id <> %s AND vp.vendor_id <> %s
                ORDER BY vp.id
                LIMIT 1
                """,
                (item["vendor_product_id"], order_a["vendor_id"]),
            )
            other_vendor_product = cur.fetchone()["id"]
            cur.execute(
                "UPDATE order_items SET vendor_product_id=%s WHERE id=%s",
                (other_vendor_product, item["id"]),
            )


def test_payment_rejects_cross_vendor_context(postgres_database, checkout_result):
    with pytest.raises(psycopg2.Error, match="PAYMENT_PARTICIPANT_MISMATCH"):
        with transaction(postgres_database) as cur:
            order_a, _ = _order_and_item_ids(cur, checkout_result)
            cur.execute(
                "SELECT id FROM vendors WHERE id <> %s ORDER BY id LIMIT 1",
                (order_a["vendor_id"],),
            )
            other_vendor = cur.fetchone()["id"]
            cur.execute(
                """
                INSERT INTO payments (
                    id, order_id, retailer_id, vendor_id, amount_toman,
                    payment_method, payment_status, custody_model
                )
                VALUES (%s,%s,%s,%s,1000,'POS_DRIVER','PENDING','NON_CUSTODIAL_DIRECT')
                """,
                (str(uuid4()), order_a["id"], order_a["retailer_id"], other_vendor),
            )


def test_settlement_rejects_cross_vendor_context(postgres_database, checkout_result):
    with pytest.raises(psycopg2.Error, match="SETTLEMENT_VENDOR_MISMATCH"):
        with transaction(postgres_database) as cur:
            order_a, _ = _order_and_item_ids(cur, checkout_result)
            cur.execute(
                "SELECT id FROM vendors WHERE id <> %s ORDER BY id LIMIT 1",
                (order_a["vendor_id"],),
            )
            other_vendor = cur.fetchone()["id"]
            cur.execute(
                """
                INSERT INTO settlements (
                    id, order_id, vendor_id, gross_amount_toman,
                    net_vendor_amount_toman, status
                )
                VALUES (%s,%s,%s,1000,1000,'PENDING')
                """,
                (str(uuid4()), order_a["id"], other_vendor),
            )


def test_delivery_rejects_cross_vendor_context(postgres_database, checkout_result):
    with pytest.raises(psycopg2.Error, match="DELIVERY_VENDOR_MISMATCH"):
        with transaction(postgres_database) as cur:
            order_a, _ = _order_and_item_ids(cur, checkout_result)
            cur.execute(
                "SELECT id FROM vendors WHERE id <> %s ORDER BY id LIMIT 1",
                (order_a["vendor_id"],),
            )
            other_vendor = cur.fetchone()["id"]
            cur.execute(
                """
                INSERT INTO deliveries (id, order_id, vendor_id, delivery_status)
                VALUES (%s,%s,%s,'ASSIGNED')
                """,
                (str(uuid4()), order_a["id"], other_vendor),
            )


def test_refund_rejects_cross_order_payment_lineage(postgres_database, checkout_result):
    with pytest.raises(psycopg2.Error, match="REFUND_PAYMENT_LINEAGE_MISMATCH"):
        with transaction(postgres_database) as cur:
            order_a, _ = _order_and_item_ids(cur, checkout_result)
            cur.execute(
                "SELECT id, order_id, retailer_id, vendor_id FROM orders WHERE id <> %s ORDER BY id LIMIT 1",
                (order_a["id"],),
            )
            order_b = cur.fetchone()
            cur.execute(
                """
                INSERT INTO payments (
                    id, order_id, retailer_id, vendor_id, amount_toman,
                    payment_method, payment_status, custody_model
                )
                VALUES (%s,%s,%s,%s,1,'POS_DRIVER','PENDING','NON_CUSTODIAL_DIRECT')
                RETURNING id
                """,
                (str(uuid4()), order_b["id"], order_b["retailer_id"], order_b["vendor_id"]),
            )
            payment_id = cur.fetchone()["id"]
            cur.execute(
                """
                INSERT INTO refunds (
                    id, order_id, payment_id, retailer_id, amount_toman, reason, status
                )
                VALUES (%s,%s,%s,%s,1,'integrity test','PENDING')
                """,
                (str(uuid4()), order_a["id"], payment_id, order_a["retailer_id"]),
            )


def test_order_item_quantity_invariants(postgres_database, checkout_result):
    with pytest.raises(psycopg2.Error, match="ORDER_ITEM_ACCEPTED_QUANTITY_INVALID"):
        with transaction(postgres_database) as cur:
            _, item = _order_and_item_ids(cur, checkout_result)
            cur.execute(
                "UPDATE order_items SET accepted_quantity = ordered_quantity + 1 WHERE id=%s",
                (item["id"],),
            )

    with pytest.raises(psycopg2.Error, match="ORDER_ITEM_DELIVERED_QUANTITY_INVALID"):
        with transaction(postgres_database) as cur:
            _, item = _order_and_item_ids(cur, checkout_result)
            cur.execute(
                "UPDATE order_items SET delivered_quantity = ordered_quantity + 1 WHERE id=%s",
                (item["id"],),
            )


def test_append_only_order_timeline_is_enforced(postgres_database, checkout_result):
    with pytest.raises(psycopg2.Error, match="order_timeline_events is append-only"):
        with transaction(postgres_database) as cur:
            order_a, _ = _order_and_item_ids(cur, checkout_result)
            event_id = str(uuid4())
            cur.execute(
                """
                INSERT INTO order_timeline_events
                    (id, order_id, event_type, to_status)
                VALUES (%s,%s,'INTEGRITY_TEST','SUBMITTED')
                """,
                (event_id, order_a["id"]),
            )
            cur.execute("DELETE FROM order_timeline_events WHERE id=%s", (event_id,))


def test_append_only_admin_audit_is_enforced(postgres_database, checkout_catalog, checkout_result):
    with pytest.raises(psycopg2.Error, match="admin_audit_logs is append-only"):
        with transaction(postgres_database) as cur:
            user_id = checkout_catalog["context"].user_id
            log_id = str(uuid4())
            cur.execute(
                """
                INSERT INTO admin_audit_logs (
                    id, actor_user_id, action, target_entity_type, target_entity_id,
                    state_before, state_after, reason
                )
                VALUES (%s,%s,'INTEGRITY_TEST','ORDER',%s,'{}'::jsonb,'{}'::jsonb,'test')
                """,
                (log_id, user_id, checkout_result["order_group_id"]),
            )
            cur.execute(
                "UPDATE admin_audit_logs SET reason='mutated' WHERE id=%s",
                (log_id,),
            )


def test_migration_032_triggers_are_installed(postgres_database):
    with transaction(postgres_database) as cur:
        cur.execute(
            """
            SELECT tgname
            FROM pg_trigger
            WHERE NOT tgisinternal
              AND tgname IN (
                  'trg_validate_order_item_context_v032',
                  'trg_validate_payment_context_v032',
                  'trg_validate_settlement_context_v032',
                  'trg_validate_refund_context_v032',
                  'trg_validate_delivery_context_v032',
                  'trg_order_timeline_append_only_v032',
                  'trg_return_events_append_only_v032',
                  'trg_admin_audit_append_only_v032',
                  'trg_domain_events_append_only_v032'
              )
            ORDER BY tgname
            """
        )
        names = [row["tgname"] for row in cur.fetchall()]
        assert len(names) == 9
