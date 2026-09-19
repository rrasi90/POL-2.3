"""Unit tests for checkout gateway fingerprint and idempotency replay — Stage 19.

Tests fingerprint determinism, sensitivity, and idempotency replay behavior.
"""

from __future__ import annotations

from uuid import uuid4

import psycopg2
import pytest
from psycopg2.extras import RealDictCursor

from scripts.checkout_gateway import CanonicalCheckoutGateway
from scripts.migration_runner import get_connection


def _base_payload():
    return {
        "basket_id": str(uuid4()),
        "plan_id": str(uuid4()),
        "retailer_id": str(uuid4()),
        "address_snapshot": {"city": "Ahvaz", "address": "Test"},
        "vendor_allocations": [
            {"vendor_id": str(uuid4()), "product_id": str(uuid4()), "quantity": 10},
        ],
    }


def test_fingerprint_is_deterministic():
    p = _base_payload()
    fp1 = CanonicalCheckoutGateway._fingerprint(**p)
    fp2 = CanonicalCheckoutGateway._fingerprint(**p)
    assert fp1 == fp2


def test_fingerprint_changes_with_basket_id():
    p1 = _base_payload()
    p2 = {**p1, "basket_id": str(uuid4())}
    assert CanonicalCheckoutGateway._fingerprint(**p1) != CanonicalCheckoutGateway._fingerprint(**p2)


def test_fingerprint_changes_with_plan_id():
    p1 = _base_payload()
    p2 = {**p1, "plan_id": str(uuid4())}
    assert CanonicalCheckoutGateway._fingerprint(**p1) != CanonicalCheckoutGateway._fingerprint(**p2)


def test_fingerprint_changes_with_retailer_id():
    p1 = _base_payload()
    p2 = {**p1, "retailer_id": str(uuid4())}
    assert CanonicalCheckoutGateway._fingerprint(**p1) != CanonicalCheckoutGateway._fingerprint(**p2)


def test_fingerprint_changes_with_allocation_quantity():
    p1 = _base_payload()
    p2 = {**p1, "vendor_allocations": [{"vendor_id": str(uuid4()), "product_id": str(uuid4()), "quantity": 20}]}
    assert CanonicalCheckoutGateway._fingerprint(**p1) != CanonicalCheckoutGateway._fingerprint(**p2)


def test_fingerprint_changes_with_address():
    p1 = _base_payload()
    p2 = {**p1, "address_snapshot": {"city": "Tehran", "address": "Different"}}
    assert CanonicalCheckoutGateway._fingerprint(**p1) != CanonicalCheckoutGateway._fingerprint(**p2)


def test_fingerprint_is_sha256_hex():
    p = _base_payload()
    fp = CanonicalCheckoutGateway._fingerprint(**p)
    assert len(fp) == 64
    assert all(c in "0123456789abcdef" for c in fp)


def test_replay_returns_none_when_no_existing_order():
    conn, _ = get_connection("pol_test")
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            result = CanonicalCheckoutGateway._replay_existing(
                cur, str(uuid4()), str(uuid4()), "fake-fingerprint",
            )
            assert result is None
    finally:
        conn.close()


def test_replay_rejects_cross_retailer():
    port = 55432
    conn = psycopg2.connect(dbname="pol_test", host="127.0.0.1", port=port, user="postgres")
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                retailer_user = str(uuid4())
                retailer_org = str(uuid4())
                retailer_id = str(uuid4())
                cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'R', 'RETAILER_OWNER')",
                            (retailer_user, f"+9891{uuid4().int % 100000000:08d}"))
                cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'R Org', 'RETAILER', 'ACTIVE')",
                            (retailer_org,))
                cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'RETAILER_OWNER', 'ACTIVE')",
                            (str(uuid4()), retailer_org, retailer_user))
                cur.execute("INSERT INTO retailers (id, user_id, organization_id, store_name, city, neighborhood, address) VALUES (%s, %s, %s, 'Store', 'Ahvaz', 'N', 'A')",
                            (retailer_id, retailer_user, retailer_org))
                basket_id = str(uuid4())
                cur.execute("INSERT INTO baskets (id, retailer_id, status, version) VALUES (%s, %s, 'OPEN', 1)",
                            (basket_id, retailer_id))
                group_id = str(uuid4())
                idempotency_key = str(uuid4())
                cur.execute(
                    "INSERT INTO order_groups (id, basket_id, retailer_id, checkout_idempotency_key, total_amount_toman, order_count, group_status) "
                    "VALUES (%s, %s, %s, %s, 5000000, 1, 'ACTIVE')",
                    (group_id, basket_id, retailer_id, idempotency_key),
                )
        other_retailer = str(uuid4())
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            with pytest.raises(ValueError, match="another retailer"):
                CanonicalCheckoutGateway._replay_existing(
                    cur, idempotency_key, other_retailer, "any-fingerprint",
                )
    finally:
        conn.close()


def test_replay_rejects_fingerprint_mismatch():
    port = 55432
    conn = psycopg2.connect(dbname="pol_test", host="127.0.0.1", port=port, user="postgres")
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                retailer_user = str(uuid4())
                retailer_org = str(uuid4())
                retailer_id = str(uuid4())
                cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'R', 'RETAILER_OWNER')",
                            (retailer_user, f"+9891{uuid4().int % 100000000:08d}"))
                cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'R Org', 'RETAILER', 'ACTIVE')",
                            (retailer_org,))
                cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'RETAILER_OWNER', 'ACTIVE')",
                            (str(uuid4()), retailer_org, retailer_user))
                cur.execute("INSERT INTO retailers (id, user_id, organization_id, store_name, city, neighborhood, address) VALUES (%s, %s, %s, 'Store', 'Ahvaz', 'N', 'A')",
                            (retailer_id, retailer_user, retailer_org))
                basket_id = str(uuid4())
                cur.execute("INSERT INTO baskets (id, retailer_id, status, version) VALUES (%s, %s, 'OPEN', 1)",
                            (basket_id, retailer_id))
                group_id = str(uuid4())
                idempotency_key = str(uuid4())
                stored_fp = "original-fingerprint-abc123"
                cur.execute(
                    "INSERT INTO order_groups (id, basket_id, retailer_id, checkout_idempotency_key, "
                    "total_amount_toman, order_count, group_status, checkout_request_fingerprint) "
                    "VALUES (%s, %s, %s, %s, 5000000, 1, 'ACTIVE', %s)",
                    (group_id, basket_id, retailer_id, idempotency_key, stored_fp),
                )
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            with pytest.raises(ValueError, match="different checkout request payload"):
                CanonicalCheckoutGateway._replay_existing(
                    cur, idempotency_key, retailer_id, "different-fingerprint-xyz",
                )
    finally:
        conn.close()


def test_replay_returns_existing_order_on_match():
    port = 55432
    conn = psycopg2.connect(dbname="pol_test", host="127.0.0.1", port=port, user="postgres")
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                retailer_user = str(uuid4())
                retailer_org = str(uuid4())
                retailer_id = str(uuid4())
                cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'R', 'RETAILER_OWNER')",
                            (retailer_user, f"+9891{uuid4().int % 100000000:08d}"))
                cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'R Org', 'RETAILER', 'ACTIVE')",
                            (retailer_org,))
                cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'RETAILER_OWNER', 'ACTIVE')",
                            (str(uuid4()), retailer_org, retailer_user))
                cur.execute("INSERT INTO retailers (id, user_id, organization_id, store_name, city, neighborhood, address) VALUES (%s, %s, %s, 'Store', 'Ahvaz', 'N', 'A')",
                            (retailer_id, retailer_user, retailer_org))
                basket_id = str(uuid4())
                cur.execute("INSERT INTO baskets (id, retailer_id, status, version) VALUES (%s, %s, 'OPEN', 1)",
                            (basket_id, retailer_id))
                group_id = str(uuid4())
                idempotency_key = str(uuid4())
                stored_fp = "same-fingerprint"
                cur.execute(
                    "INSERT INTO order_groups (id, basket_id, retailer_id, checkout_idempotency_key, "
                    "total_amount_toman, order_count, group_status, checkout_request_fingerprint) "
                    "VALUES (%s, %s, %s, %s, 5000000, 1, 'ACTIVE', %s)",
                    (group_id, basket_id, retailer_id, idempotency_key, stored_fp),
                )
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            result = CanonicalCheckoutGateway._replay_existing(
                cur, idempotency_key, retailer_id, stored_fp,
            )
            assert result is not None
            assert result["idempotent_replay"] is True
            assert str(result["order_group"]["id"]) == group_id
    finally:
        conn.close()
