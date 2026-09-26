"""HTTP transport tests for invoice / settlement read model routes — Stage 28."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import psycopg2
import pytest
from fastapi.testclient import TestClient
from psycopg2.extras import RealDictCursor

from scripts.api.main import app
from scripts.auth_boundary import encode_access_token, hash_token


JWT_SECRET = "test-secret-key-for-auth-contract-tests-only-32bytes!!"


@pytest.fixture
def api_env(monkeypatch):
    pg_port = (
        os.environ.get("POL_API_DB_PORT")
        or os.environ.get("POL_PG_PORT")
        or os.environ.get("PGPORT")
        or "5432"
    )
    monkeypatch.setenv("POL_API_DB_NAME", "pol_test")
    monkeypatch.setenv("POL_API_DB_HOST", os.environ.get("PGHOST", "127.0.0.1"))
    monkeypatch.setenv("POL_API_DB_PORT", pg_port)
    monkeypatch.setenv("POL_JWT_SECRET", JWT_SECRET)
    monkeypatch.setenv("ENVIRONMENT", "test")


def _db():
    port = int(
        os.environ.get("POL_API_DB_PORT")
        or os.environ.get("POL_PG_PORT")
        or os.environ.get("PGPORT", "5432")
    )
    return psycopg2.connect(
        dbname="pol_test",
        host=os.environ.get("POL_API_DB_HOST", os.environ.get("PGHOST", "127.0.0.1")),
        port=port,
        user=os.environ.get("POL_API_DB_USER", os.environ.get("PGUSER", "postgres")),
    )


def _create_session(cur, user_id, org_id):
    session_id = str(uuid4())
    cur.execute(
        "INSERT INTO user_sessions (id, user_id, active_organization_id, token_hash, status, expires_at) "
        "VALUES (%s, %s, %s, %s, 'ACTIVE', %s)",
        (session_id, user_id, org_id, hash_token(session_id),
         datetime.now(timezone.utc) + timedelta(hours=1)),
    )
    return session_id


def _seed_finance(suffix):
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            retailer_user = str(uuid4())
            retailer_org = str(uuid4())
            retailer_id = str(uuid4())
            vendor_user = str(uuid4())
            vendor_org = str(uuid4())
            vendor_id = str(uuid4())
            brand_id = str(uuid4())
            category_id = str(uuid4())
            subcategory_id = str(uuid4())
            product_id = str(uuid4())
            vendor_product_id = str(uuid4())
            basket_id = str(uuid4())
            plan_id = str(uuid4())
            order_group_id = str(uuid4())
            order_id = str(uuid4())
            order_item_id = str(uuid4())
            invoice_id = str(uuid4())
            invoice_number = f"INV-{uuid4().hex[:8].upper()}"
            settlement_id = str(uuid4())

            cur.execute(
                "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Retailer', 'RETAILER_OWNER')",
                (retailer_user, f"+9891{uuid4().int % 100000000:08d}"),
            )
            cur.execute(
                "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'R Org', 'RETAILER', 'ACTIVE')",
                (retailer_org,),
            )
            cur.execute(
                "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'RETAILER_OWNER', 'ACTIVE')",
                (str(uuid4()), retailer_org, retailer_user),
            )
            cur.execute(
                "INSERT INTO retailers (id, user_id, organization_id, store_name, city, neighborhood, address) VALUES (%s, %s, %s, 'Store', 'Ahvaz', 'N', 'A')",
                (retailer_id, retailer_user, retailer_org),
            )

            cur.execute(
                "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Vendor', 'VENDOR_OWNER')",
                (vendor_user, f"+9891{uuid4().int % 100000000:08d}"),
            )
            cur.execute(
                "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'V Org', 'VENDOR', 'ACTIVE')",
                (vendor_org,),
            )
            cur.execute(
                "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')",
                (str(uuid4()), vendor_org, vendor_user),
            )
            cur.execute(
                "INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman, status) "
                "VALUES (%s, %s, %s, 'Vendor', 'Ahvaz', 1000000, 'ACTIVE')",
                (vendor_id, vendor_user, vendor_org),
            )

            cur.execute(
                "INSERT INTO brands (id, name_fa, slug) VALUES (%s, %s, %s)",
                (brand_id, f"B{suffix}", f"b-{suffix}"),
            )
            cur.execute(
                "INSERT INTO categories (id, name_fa, slug) VALUES (%s, %s, %s)",
                (category_id, f"C{suffix}", f"c-{suffix}"),
            )
            cur.execute(
                "INSERT INTO subcategories (id, category_id, name_fa, slug) VALUES (%s, %s, %s, %s)",
                (subcategory_id, category_id, f"S{suffix}", f"s-{suffix}"),
            )
            cur.execute(
                "INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id, is_active) "
                "VALUES (%s, %s, %s, %s, %s, %s, TRUE)",
                (product_id, f"SKU-{suffix}", f"P{suffix}", brand_id, category_id, subcategory_id),
            )
            cur.execute(
                "INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity, sales_unit, is_active, listing_status) "
                "VALUES (%s, %s, %s, %s, 'CARTON', 4, 'CARTON', TRUE, 'ACTIVE')",
                (vendor_product_id, vendor_id, product_id, f"VP-{suffix}"),
            )

            cur.execute(
                "INSERT INTO baskets (id, retailer_id, status, version) VALUES (%s, %s, 'OPEN', 1)",
                (basket_id, retailer_id),
            )
            cur.execute(
                "INSERT INTO allocation_plans (id, basket_id, basket_version, status, strategy, vendor_count, total_estimated_toman, expires_at) "
                "VALUES (%s, %s, 1, 'CONFIRMED', 'SINGLE_VENDOR', 1, 5000000, now() + interval '15 minutes')",
                (plan_id, basket_id),
            )

            cur.execute(
                "INSERT INTO order_groups (id, basket_id, retailer_id, checkout_idempotency_key, "
                "total_amount_toman, order_count, group_status) "
                "VALUES (%s, %s, %s, %s, 5000000, 1, 'ACTIVE')",
                (order_group_id, basket_id, retailer_id, str(uuid4())),
            )
            cur.execute(
                "INSERT INTO orders (id, order_number, order_group_id, allocation_plan_id, "
                "retailer_id, vendor_id, order_status, total_amount_toman, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, 'DELIVERED', 5000000, now(), now())",
                (order_id, f"ORD-{suffix}", order_group_id, plan_id, retailer_id, vendor_id),
            )
            cur.execute(
                "INSERT INTO order_items (id, order_id, product_id, vendor_product_id, "
                "product_name_snapshot, brand_name_snapshot, vendor_sku_snapshot, "
                "packaging_unit_snapshot, pack_quantity_snapshot, ordered_quantity, "
                "unit_price_toman, total_line_amount_toman, fulfillment_status) "
                "VALUES (%s, %s, %s, %s, 'Product', 'Brand', 'VS', 'CARTON', 4, 10, 500000, 5000000, 'FULFILLED')",
                (order_item_id, order_id, product_id, vendor_product_id),
            )

            cur.execute(
                "INSERT INTO invoices (id, invoice_number, order_id, retailer_organization_id, vendor_organization_id, "
                "total_amount, currency, status, issued_at, created_at) "
                "VALUES (%s, %s, %s, %s, %s, 5000000, 'TOMAN', 'ISSUED', now(), now())",
                (invoice_id, invoice_number, order_id, retailer_org, vendor_org),
            )
            cur.execute(
                "INSERT INTO invoice_items (id, invoice_id, order_item_id, product_name, quantity, unit_price, total_line_amount) "
                "VALUES (%s, %s, %s, 'Product A', 10, 500000, 5000000)",
                (str(uuid4()), invoice_id, order_item_id),
            )

            cur.execute(
                "INSERT INTO payments (id, order_id, retailer_id, vendor_id, payment_status, payment_method, amount_toman) "
                "VALUES (%s, %s, %s, %s, 'SUCCESS', 'CASH_ON_DELIVERY', 5000000)",
                (str(uuid4()), order_id, retailer_id, vendor_id),
            )

            cur.execute(
                "INSERT INTO settlements (id, order_id, vendor_id, gross_amount_toman, commission_rate, "
                "commission_amount_toman, adjustment_amount_toman, net_vendor_amount_toman, status, created_at) "
                "VALUES (%s, %s, %s, 5000000, 0.050, 250000, 0, 4750000, 'CALCULATED', now())",
                (settlement_id, order_id, vendor_id),
            )
            adj_id = str(uuid4())
            cur.execute(
                "INSERT INTO settlement_adjustments (id, settlement_id, adjustment_type, amount_toman, reason, applied_by_user_id, created_at) "
                "VALUES (%s, %s, 'SHORTAGE_DEDUCTION', 50000, 'Test deduction', %s, now())",
                (adj_id, settlement_id, vendor_user),
            )

            r_session = _create_session(cur, retailer_user, retailer_org)
            v_session = _create_session(cur, vendor_user, vendor_org)

        conn.commit()

        r_token = encode_access_token(retailer_user, r_session, retailer_org, "RETAILER_OWNER")
        v_token = encode_access_token(vendor_user, v_session, vendor_org, "VENDOR_OWNER")

        return {
            "retailer_user": retailer_user,
            "retailer_org": retailer_org,
            "vendor_user": vendor_user,
            "vendor_org": vendor_org,
            "retailer_id": retailer_id,
            "vendor_id": vendor_id,
            "order_id": order_id,
            "order_item_id": order_item_id,
            "invoice_id": invoice_id,
            "invoice_number": invoice_number,
            "settlement_id": settlement_id,
            "adj_id": adj_id,
            "r_token": r_token,
            "v_token": v_token,
        }
    finally:
        conn.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app, raise_server_exceptions=False)


class TestInvoiceList:
    def test_vendor_list_own_invoices(self, client):
        data = _seed_finance(uuid4().hex[:8])
        resp = client.get("/api/v1/invoices", headers={"Authorization": f"Bearer {data['v_token']}"})
        assert resp.status_code == 200
        body = resp.json()["data"]
        assert isinstance(body["invoices"], list)
        assert len(body["invoices"]) >= 1
        assert body["invoices"][0]["vendor_organization_id"] == data["vendor_org"]

    def test_retailer_list_own_invoices(self, client):
        data = _seed_finance(uuid4().hex[:8])
        resp = client.get("/api/v1/invoices", headers={"Authorization": f"Bearer {data['r_token']}"})
        assert resp.status_code == 200
        body = resp.json()["data"]
        assert isinstance(body["invoices"], list)
        assert len(body["invoices"]) >= 1
        assert body["invoices"][0]["retailer_organization_id"] == data["retailer_org"]

    def test_ops_list_cross_tenant_invoices(self, client):
        data = _seed_finance(uuid4().hex[:8])
        op_user = str(uuid4())
        op_org = str(uuid4())
        membership_id = str(uuid4())
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO users (id, phone_number, full_name, role, is_active) VALUES (%s, %s, 'Ops', 'ADMIN_SUPER', TRUE)",
                    (op_user, f"+9891{uuid4().int % 100000000:08d}"),
                )
                cur.execute(
                    "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Ops Org', 'OPERATOR', 'ACTIVE')",
                    (op_org,),
                )
                cur.execute(
                    "INSERT INTO organization_memberships (id, organization_id, user_id, role, status, is_primary) VALUES (%s, %s, %s, 'ADMIN_SUPER', 'ACTIVE', TRUE)",
                    (membership_id, op_org, op_user),
                )
                session_id = _create_session(cur, op_user, op_org)
            conn.commit()
            op_token = encode_access_token(op_user, session_id, op_org, "ADMIN_SUPER")

            resp = client.get("/api/v1/invoices", headers={"Authorization": f"Bearer {op_token}"})
            assert resp.status_code == 200
            invoices = resp.json()["data"]["invoices"]
            assert any(item["id"] == data["invoice_id"] for item in invoices)
            assert any(item["vendor_organization_id"] == data["vendor_org"] for item in invoices)
            assert any(item["retailer_organization_id"] == data["retailer_org"] for item in invoices)
        finally:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM user_sessions WHERE user_id=%s", (op_user,))
                cur.execute("DELETE FROM organization_memberships WHERE id=%s", (membership_id,))
                cur.execute("DELETE FROM organizations WHERE id=%s", (op_org,))
                cur.execute("DELETE FROM users WHERE id=%s", (op_user,))
            conn.commit()
            conn.close()


class TestInvoiceGet:
    def test_vendor_get_invoice_detail(self, client):
        data = _seed_finance(uuid4().hex[:8])
        resp = client.get(f"/api/v1/invoices/{data['invoice_id']}", headers={"Authorization": f"Bearer {data['v_token']}"})
        assert resp.status_code == 200
        inv = resp.json()["data"]
        assert inv["id"] == data["invoice_id"]
        assert inv["invoice_number"] == data["invoice_number"]
        assert len(inv["items"]) == 1
        assert inv["items"][0]["product_name"] == "Product A"
        assert inv["items"][0]["quantity"] == 10

    def test_retailer_get_invoice_detail(self, client):
        data = _seed_finance(uuid4().hex[:8])
        resp = client.get(f"/api/v1/invoices/{data['invoice_id']}", headers={"Authorization": f"Bearer {data['r_token']}"})
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == data["invoice_id"]

    def test_wrong_tenant_cannot_access_invoice(self, client):
        data = _seed_finance(uuid4().hex[:8])
        wrong_user = str(uuid4())
        wrong_org = str(uuid4())
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Wrong', 'RETAILER_OWNER')",
                    (wrong_user, f"+9891{uuid4().int % 100000000:08d}"),
                )
                cur.execute(
                    "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Wrong Org', 'RETAILER', 'ACTIVE')",
                    (wrong_org,),
                )
                cur.execute(
                    "INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'RETAILER_OWNER', 'ACTIVE')",
                    (str(uuid4()), wrong_org, wrong_user),
                )
                wrong_session = _create_session(cur, wrong_user, wrong_org)
            conn.commit()
            wrong_token = encode_access_token(wrong_user, wrong_session, wrong_org, "RETAILER_OWNER")
        finally:
            conn.close()
        resp = client.get(f"/api/v1/invoices/{data['invoice_id']}", headers={"Authorization": f"Bearer {wrong_token}"})
        assert resp.status_code == 403


class TestInvoiceByOrder:
    def test_retailer_get_invoice_for_order(self, client):
        data = _seed_finance(uuid4().hex[:8])
        resp = client.get(f"/api/v1/orders/{data['order_id']}/invoice", headers={"Authorization": f"Bearer {data['r_token']}"})
        assert resp.status_code == 200
        inv = resp.json()["data"]
        assert inv["order_id"] == data["order_id"]
        assert inv["id"] == data["invoice_id"]


class TestSettlementList:
    def test_vendor_list_settlements(self, client):
        data = _seed_finance(uuid4().hex[:8])
        resp = client.get("/api/v1/vendors/settlements", headers={"Authorization": f"Bearer {data['v_token']}"})
        assert resp.status_code == 200
        body = resp.json()["data"]
        assert isinstance(body["settlements"], list)
        assert len(body["settlements"]) >= 1
        assert body["settlements"][0]["vendor_id"] == data["vendor_id"]

    def test_retailer_cannot_list_settlements(self, client):
        data = _seed_finance(uuid4().hex[:8])
        resp = client.get("/api/v1/vendors/settlements", headers={"Authorization": f"Bearer {data['r_token']}"})
        assert resp.status_code == 403


class TestSettlementGet:
    def test_settlement_detail_includes_adjustments(self, client):
        data = _seed_finance(uuid4().hex[:8])
        resp = client.get(f"/api/v1/settlements/{data['settlement_id']}", headers={"Authorization": f"Bearer {data['v_token']}"})
        assert resp.status_code == 200
        st = resp.json()["data"]
        assert st["id"] == data["settlement_id"]
        assert st["status"] == "CALCULATED"
        assert len(st["adjustments"]) == 1
        assert st["adjustments"][0]["adjustment_type"] == "SHORTAGE_DEDUCTION"
        assert st["adjustments"][0]["amount_toman"] == 50000

    def test_retailer_cannot_get_settlement(self, client):
        data = _seed_finance(uuid4().hex[:8])
        resp = client.get(f"/api/v1/settlements/{data['settlement_id']}", headers={"Authorization": f"Bearer {data['r_token']}"})
        assert resp.status_code == 403


class TestFinanceAuth:
    def test_unauthenticated_rejected_invoices(self, client):
        resp = client.get("/api/v1/invoices")
        assert resp.status_code == 401

    def test_unauthenticated_rejected_settlements(self, client):
        resp = client.get("/api/v1/vendors/settlements")
        assert resp.status_code == 401
