"""HTTP regression tests for the remediation management surface."""

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


def _session(cur, user_id, org_id):
    sid = str(uuid4())
    token = encode_access_token(user_id, sid, org_id, "SUPER_ADMIN")
    cur.execute(
        """
        INSERT INTO user_sessions
            (id, user_id, active_organization_id, token_hash, status, expires_at)
        VALUES (%s,%s,%s,%s,'ACTIVE',%s)
        """,
        (sid, user_id, org_id, hash_token(token), datetime.now(timezone.utc) + timedelta(hours=1)),
    )
    return sid, token


@pytest.fixture(scope="module")
def management_env():
    conn = _db()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        admin_user = str(uuid4())
        admin_org = str(uuid4())
        vendor_user = str(uuid4())
        vendor_org = str(uuid4())
        cur.execute(
            "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s,%s,'Management Admin','SUPER_ADMIN')",
            (admin_user, f"+9891{uuid4().hex[:8]}"),
        )
        cur.execute(
            "INSERT INTO organizations (id,name,org_type,status) VALUES (%s,'Ops Test','OPERATOR','ACTIVE')",
            (admin_org,),
        )
        cur.execute(
            """
            INSERT INTO organization_memberships
                (id,organization_id,user_id,role,status,is_primary)
            VALUES (%s,%s,%s,'SUPER_ADMIN','ACTIVE',TRUE)
            """,
            (str(uuid4()), admin_org, admin_user),
        )
        cur.execute(
            "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s,%s,'Management Vendor','VENDOR_OWNER')",
            (vendor_user, f"+9891{uuid4().hex[:8]}"),
        )
        cur.execute(
            "INSERT INTO organizations (id,name,org_type,status) VALUES (%s,'Vendor Test','VENDOR','ACTIVE')",
            (vendor_org,),
        )
        cur.execute(
            """
            INSERT INTO organization_memberships
                (id,organization_id,user_id,role,status,is_primary)
            VALUES (%s,%s,%s,'VENDOR_OWNER','ACTIVE',TRUE)
            """,
            (str(uuid4()), vendor_org, vendor_user),
        )
        vendor_id = str(uuid4())
        cur.execute(
            """
            INSERT INTO vendors
                (id,user_id,organization_id,business_name,warehouse_address,min_order_value_toman,status)
            VALUES (%s,%s,%s,'Management Vendor','Ahvaz',1000000,'ACTIVE')
            """,
            (vendor_id, vendor_user, vendor_org),
        )
        sid_a, token_a = _session(cur, admin_user, admin_org)
        sid_v = str(uuid4())
        token_v = encode_access_token(vendor_user, sid_v, vendor_org, "VENDOR_OWNER")
        cur.execute(
            """
            INSERT INTO user_sessions
                (id,user_id,active_organization_id,token_hash,status,expires_at)
            VALUES (%s,%s,%s,%s,'ACTIVE',%s)
            """,
            (sid_v, vendor_user, vendor_org, hash_token(token_v), datetime.now(timezone.utc) + timedelta(hours=1)),
        )
    conn.commit()
    yield {
        "conn": conn,
        "admin": token_a,
        "vendor": token_v,
        "admin_user": admin_user,
        "admin_org": admin_org,
        "vendor_user": vendor_user,
        "vendor_org": vendor_org,
        "vendor_id": vendor_id,
        "session_ids": [sid_a, sid_v],
    }
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM inventory_audit_log WHERE vendor_id=%s", (vendor_id,))
            cur.execute("DELETE FROM vendor_inventory WHERE vendor_product_id IN (SELECT id FROM vendor_products WHERE vendor_id=%s)", (vendor_id,))
            cur.execute("DELETE FROM vendor_prices WHERE vendor_product_id IN (SELECT id FROM vendor_products WHERE vendor_id=%s)", (vendor_id,))
            cur.execute("DELETE FROM vendor_products WHERE vendor_id=%s", (vendor_id,))
            cur.execute("DELETE FROM vendors WHERE id=%s", (vendor_id,))
            cur.execute("DELETE FROM organization_memberships WHERE user_id IN (%s,%s)", (admin_user, vendor_user))
            cur.execute("DELETE FROM user_sessions WHERE user_id IN (%s,%s)", (admin_user, vendor_user))
            cur.execute("DELETE FROM users WHERE id IN (%s,%s)", (admin_user, vendor_user))
            cur.execute("DELETE FROM organizations WHERE id IN (%s,%s)", (admin_org, vendor_org))
        conn.commit()
    finally:
        conn.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app, raise_server_exceptions=False)


def test_vendor_customers_and_staff_are_tenant_scoped(client, management_env):
    resp = client.get(
        "/api/v1/vendors/customers",
        headers={"Authorization": f"Bearer {management_env['vendor']}"},
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert resp.json()["data"]["customers"] == []

    phone = f"+9891{uuid4().hex[:8]}"
    invite = client.post(
        "/api/v1/vendors/staff/invite",
        headers={"Authorization": f"Bearer {management_env['vendor']}"},
        json={"phone_number": phone, "full_name": "Invited Staff"},
    )
    assert invite.status_code == 201
    data = invite.json()["data"]
    assert data["role"] == "VENDOR_STAFF"
    assert data["status"] == "INVITED"

    conn = management_env["conn"]
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM organization_memberships
                WHERE organization_id=%s AND user_id=%s
                """,
                (management_env["vendor_org"], data["user_id"]),
            )
            cur.execute("DELETE FROM users WHERE id=%s", (data["user_id"],))
        conn.commit()
    finally:
        conn.rollback()


def test_vendor_owner_cannot_suspend_last_active_owner(client, management_env):
    conn = management_env["conn"]
    membership_id = str(uuid4())
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id
                FROM organization_memberships
                WHERE organization_id=%s AND user_id=%s
                  AND role='VENDOR_OWNER' AND status='ACTIVE'
                LIMIT 1
                """,
                (management_env["vendor_org"], management_env["vendor_user"]),
            )
            row = cur.fetchone()
            assert row is not None
            membership_id = str(row[0])

        response = client.patch(
            f"/api/v1/vendors/staff/{membership_id}",
            headers={"Authorization": f"Bearer {management_env['vendor']}"},
            json={"status": "SUSPENDED"},
        )
        assert response.status_code == 422

        with conn.cursor() as cur:
            cur.execute(
                "SELECT status FROM organization_memberships WHERE id=%s",
                (membership_id,),
            )
            assert cur.fetchone()[0] == "ACTIVE"
    finally:
        conn.rollback()

def test_only_vendor_owner_can_invite_staff(client, management_env):
    resp = client.post(
        "/api/v1/vendors/staff/invite",
        headers={"Authorization": f"Bearer {management_env['admin']}"},
        json={"phone_number": f"+9891{uuid4().hex[:8]}", "full_name": "Denied Staff"},
    )
    assert resp.status_code == 403


def test_admin_user_org_permission_and_global_returns_routes(client, management_env):
    headers = {"Authorization": f"Bearer {management_env['admin']}"}
    users = client.get("/api/v1/admin/users", headers=headers)
    orgs = client.get("/api/v1/admin/organizations", headers=headers)
    permissions = client.get("/api/v1/ops/permissions", headers=headers)
    returns = client.get("/api/v1/ops/returns", headers=headers)

    assert users.status_code == 200
    assert orgs.status_code == 200
    assert permissions.status_code == 200
    assert returns.status_code == 200
    assert "SUPER_ADMIN" in permissions.json()["data"]["roles"]


def test_management_routes_reject_unauthenticated(client):
    assert client.get("/api/v1/vendors/customers").status_code == 401
    assert client.get("/api/v1/admin/users").status_code == 401
    assert client.get("/api/v1/ops/permissions").status_code == 401



def test_broadcast_and_category_admin_routes_use_real_boundary(client, management_env):
    headers = {"Authorization": f"Bearer {management_env['admin']}"}

    created = client.post(
        "/api/v1/admin/broadcasts",
        headers=headers,
        json={
            "title": "Remediation test",
            "body": "No-op test notification",
            "target_criteria": {"org_type": "OPERATOR", "status": "ACTIVE"},
        },
    )
    assert created.status_code == 201
    broadcast = created.json()["data"]
    assert broadcast["status"] == "DRAFT"
    assert broadcast["estimated_recipient_count"] >= 1

    dispatched = client.post(
        "/api/v1/admin/broadcasts/" + broadcast["id"] + "/dispatch",
        headers=headers,
        json={"approve": True},
    )
    assert dispatched.status_code == 200
    assert dispatched.json()["data"]["status"] == "COMPLETED"

    category = client.post(
        "/api/v1/admin/categories",
        headers=headers,
        json={
            "name_fa": "Remediation Category",
            "slug": "remediation-category-" + uuid4().hex[:8],
            "display_order": 999,
        },
    )
    assert category.status_code == 201
    cat = category.json()["data"]
    assert cat["display_order"] == 999

    updated = client.patch(
        "/api/v1/admin/categories/" + cat["id"],
        headers=headers,
        json={"name_fa": "Remediation Category Updated", "display_order": 1000},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["name_fa"] == "Remediation Category Updated"

    with management_env["conn"].cursor() as cur:
        cur.execute("DELETE FROM broadcast_messages WHERE id=%s", (broadcast["id"],))
        cur.execute("DELETE FROM categories WHERE id=%s", (cat["id"],))
    management_env["conn"].commit()


def test_broadcast_and_category_mutations_reject_non_admin_context(client, management_env):
    headers = {"Authorization": f"Bearer {management_env['vendor']}"}
    broadcast = client.post(
        "/api/v1/admin/broadcasts",
        headers=headers,
        json={"title": "Denied", "body": "Denied", "target_criteria": {}},
    )
    category = client.post(
        "/api/v1/admin/categories",
        headers=headers,
        json={"name_fa": "Denied", "slug": "denied-" + uuid4().hex[:8]},
    )
    assert broadcast.status_code == 403
    assert category.status_code == 403



def test_continuous_inventory_scan_and_publish(client, management_env):
    suffix = uuid4().hex[:8]
    conn = management_env["conn"]
    try:
        brand_id = str(uuid4())
        category_id = str(uuid4())
        subcategory_id = str(uuid4())
        product_id = str(uuid4())
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO brands (id,name_fa,slug) VALUES (%s,%s,%s)",
            (brand_id, "Inventory Test Brand", "inv-brand-" + suffix),
        )
        cur.execute(
            "INSERT INTO categories (id,name_fa,slug) VALUES (%s,%s,%s)",
            (category_id, "Inventory Test Category", "inv-cat-" + suffix),
        )
        cur.execute(
            "INSERT INTO subcategories (id,category_id,name_fa,slug) VALUES (%s,%s,%s,%s)",
            (subcategory_id, category_id, "Inventory Test Sub", "inv-sub-" + suffix),
        )
        cur.execute(
            """
            INSERT INTO products
                (id,master_sku,canonical_name_fa,brand_id,category_id,subcategory_id,is_active)
            VALUES (%s,%s,%s,%s,%s,%s,TRUE)
            """,
            (product_id, "MASTER-" + suffix, "Inventory Product", brand_id, category_id, subcategory_id),
        )
        conn.commit()
    finally:
        if "cur" in locals():
            cur.close()

    scan = client.post(
        "/api/v1/vendors/inventory/continuous-scan",
        headers={"Authorization": "Bearer " + management_env["vendor"]},
        json={
            "product_id": product_id,
            "vendor_sku": "VSKU-" + suffix,
            "packaging_unit": "CARTON",
            "pack_quantity": 2,
            "physical_quantity": 50,
            "unit_price_toman": 380000,
            "consumer_price_per_unit_toman": 420000,
            "session_id": "scan-" + suffix,
        },
    )
    assert scan.status_code == 200
    scan_data = scan.json()["data"]
    assert scan_data["available_quantity"] == 50
    assert scan_data["listing_status"] == "DRAFT_PENDING_CATALOG"

    publish = client.post(
        "/api/v1/vendors/inventory/publish",
        headers={"Authorization": "Bearer " + management_env["vendor"]},
        json={"session_id": "scan-" + suffix},
    )
    assert publish.status_code == 200
    assert publish.json()["data"]["status"] == "PUBLISHED"
    assert publish.json()["data"]["published_count"] == 1

    replay = client.post(
        "/api/v1/vendors/inventory/publish",
        headers={"Authorization": "Bearer " + management_env["vendor"]},
        json={"session_id": "scan-" + suffix},
    )
    assert replay.status_code == 200
    assert replay.json()["data"]["idempotent_replay"] is True

    with conn.cursor() as cur:
        cur.execute("DELETE FROM inventory_audit_log WHERE vendor_product_id IN (SELECT id FROM vendor_products WHERE vendor_id=%s AND vendor_sku=%s)", (management_env["vendor_id"], "VSKU-" + suffix))
        cur.execute("DELETE FROM vendor_prices WHERE vendor_product_id IN (SELECT id FROM vendor_products WHERE vendor_id=%s AND vendor_sku=%s)", (management_env["vendor_id"], "VSKU-" + suffix))
        cur.execute("DELETE FROM vendor_inventory WHERE vendor_product_id IN (SELECT id FROM vendor_products WHERE vendor_id=%s AND vendor_sku=%s)", (management_env["vendor_id"], "VSKU-" + suffix))
        cur.execute("DELETE FROM inventory_scan_sessions WHERE vendor_id=%s AND external_session_id=%s", (management_env["vendor_id"], "scan-" + suffix))
        cur.execute("DELETE FROM vendor_products WHERE vendor_id=%s AND vendor_sku=%s", (management_env["vendor_id"], "VSKU-" + suffix))
        cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
        cur.execute("DELETE FROM subcategories WHERE id=%s", (subcategory_id,))
        cur.execute("DELETE FROM categories WHERE id=%s", (category_id,))
        cur.execute("DELETE FROM brands WHERE id=%s", (brand_id,))
    conn.commit()

def test_product_candidate_review_http_is_tenant_and_idempotent(client, management_env):
    conn = management_env["conn"]
    candidate_id = str(uuid4())
    suffix = uuid4().hex[:8]
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO product_candidates
                    (id, vendor_id, proposed_title, proposed_brand, barcode, vendor_sku)
                VALUES (%s,%s,%s,%s,%s,%s)
                """,
                (
                    candidate_id,
                    management_env["vendor_id"],
                    "Candidate " + suffix,
                    "Test Brand",
                    "6261234567890",
                    "CAND-" + suffix,
                ),
            )
        conn.commit()

        admin_headers = {"Authorization": f"Bearer {management_env['admin']}"}
        vendor_headers = {"Authorization": f"Bearer {management_env['vendor']}"}

        listed = client.get(
            "/api/v1/admin/product-candidates",
            headers=admin_headers,
            params={"status": "PENDING_REVIEW", "query": suffix},
        )
        assert listed.status_code == 200
        rows = listed.json()["data"]["candidates"]
        assert any(row["candidate_id"] == candidate_id for row in rows)

        denied = client.get(
            "/api/v1/admin/product-candidates",
            headers=vendor_headers,
        )
        assert denied.status_code == 403

        reviewed = client.patch(
            "/api/v1/admin/product-candidates/" + candidate_id,
            headers=admin_headers,
            json={"action": "REJECT", "reason": "Not a canonical catalog item."},
        )
        assert reviewed.status_code == 200
        assert reviewed.json()["data"]["status"] == "REJECTED"
        assert reviewed.json()["data"]["idempotent_replay"] is False

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT target_user_id, target_organization_id, dedupe_key
                FROM outbox_events
                WHERE event_name='PRODUCT_CANDIDATE_REVIEWED' AND aggregate_id=%s
                """,
                (candidate_id,),
            )
            event = cur.fetchone()
            assert event is not None
            assert str(event["target_user_id"]) == management_env["vendor_user"]
            assert str(event["target_organization_id"]) == management_env["vendor_org"]
            assert event["dedupe_key"] == "PRODUCT_CANDIDATE_REVIEWED:" + candidate_id

        replay = client.patch(
            "/api/v1/admin/product-candidates/" + candidate_id,
            headers=admin_headers,
            json={"action": "REJECT", "reason": "Replay should not mutate again."},
        )
        assert replay.status_code == 200
        replay_data = replay.json()["data"]
        assert replay_data["status"] == "REJECTED"
        assert replay_data["idempotent_replay"] is True

        direct = client.post(
            "/api/v1/product-candidates",
            headers=vendor_headers,
            json={
                "proposed_title": "Direct Candidate " + suffix,
                "proposed_brand": "Test Brand",
                "barcode": "6261234567891",
                "vendor_sku": "DIRECT-" + suffix,
            },
        )
        replay_direct = client.post(
            "/api/v1/product-candidates",
            headers=vendor_headers,
            json={
                "proposed_title": "Direct Candidate " + suffix,
                "proposed_brand": "Test Brand",
                "barcode": "6261234567891",
                "vendor_sku": "DIRECT-" + suffix,
            },
        )
        assert direct.status_code == 201
        assert replay_direct.status_code == 201
        assert direct.json()["data"]["candidate_id"] == replay_direct.json()["data"]["candidate_id"]
        assert replay_direct.json()["data"]["idempotent_replay"] is True

        non_admin_review = client.patch(
            "/api/v1/admin/product-candidates/" + candidate_id,
            headers=vendor_headers,
            json={"action": "REJECT", "reason": "Denied."},
        )
        assert non_admin_review.status_code == 403
    finally:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM outbox_events WHERE aggregate_id IN (SELECT id FROM product_candidates WHERE vendor_id=%s)",
                (management_env["vendor_id"],),
            )
            cur.execute(
                "DELETE FROM admin_audit_logs WHERE target_entity_type='PRODUCT_CANDIDATE' AND target_entity_id IN (SELECT id FROM product_candidates WHERE vendor_id=%s)",
                (management_env["vendor_id"],),
            )
            cur.execute(
                "DELETE FROM vendor_inventory WHERE vendor_product_id IN (SELECT id FROM vendor_products WHERE vendor_id=%s)",
                (management_env["vendor_id"],),
            )
            cur.execute("DELETE FROM vendor_products WHERE vendor_id=%s", (management_env["vendor_id"],))
            cur.execute("DELETE FROM product_candidates WHERE vendor_id=%s", (management_env["vendor_id"],))
        conn.commit()



def test_vendor_permission_editor_http_lifecycle(client, management_env):
    conn = management_env["conn"]
    staff_user = str(uuid4())
    membership_id = str(uuid4())
    headers = {"Authorization": f"Bearer {management_env['vendor']}"}

    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (id, phone_number, full_name, role, is_active) VALUES (%s,%s,'Permission Staff','VENDOR_STAFF',TRUE)",
                (staff_user, f"+9891{uuid4().hex[:8]}"),
            )
            cur.execute(
                """
                INSERT INTO organization_memberships
                    (id, organization_id, user_id, role, status, is_primary)
                VALUES (%s,%s,%s,'VENDOR_STAFF','ACTIVE',FALSE)
                """,
                (membership_id, management_env["vendor_org"], staff_user),
            )
        conn.commit()

        initial = client.get(
            f"/api/v1/vendors/staff/{membership_id}/permissions",
            headers=headers,
        )
        assert initial.status_code == 200
        initial_data = initial.json()["data"]
        assert initial_data["role"] == "VENDOR_STAFF"
        assert "inventory.scan" in initial_data["effective_permissions"]
        assert "inventory.adjust" in initial_data["grantable_permissions"]

        granted = client.post(
            f"/api/v1/vendors/staff/{membership_id}/permissions",
            headers=headers,
            json={
                "permission_key": "price.manage",
                "reason": "Temporary price lead duty",
                "client": "TEST",
            },
        )
        assert granted.status_code == 200
        assert granted.json()["data"]["status"] == "GRANTED"

        detail = client.get(
            f"/api/v1/vendors/staff/{membership_id}/permissions",
            headers=headers,
        )
        assert detail.status_code == 200
        assert "price.manage" in detail.json()["data"]["effective_permissions"]

        replay = client.post(
            f"/api/v1/vendors/staff/{membership_id}/permissions",
            headers=headers,
            json={
                "permission_key": "price.manage",
                "reason": "Replay",
                "client": "TEST",
            },
        )
        assert replay.status_code == 200
        assert replay.json()["data"]["idempotent_replay"] is True

        audit = client.get(
            f"/api/v1/ops/permissions/audit?membership_id={membership_id}",
            headers=headers,
        )
        assert audit.status_code == 200
        assert any(
            item["action"] == "GRANT" and item["permission_key"] == "price.manage"
            for item in audit.json()["data"]["items"]
        )

        revoked = client.post(
            f"/api/v1/vendors/staff/{membership_id}/permissions/price.manage/revoke",
            headers=headers,
            json={"reason": "Duty ended", "client": "TEST"},
        )
        assert revoked.status_code == 200
        assert revoked.json()["data"]["status"] == "REVOKED"

        final = client.get(
            f"/api/v1/vendors/staff/{membership_id}/permissions",
            headers=headers,
        )
        assert final.status_code == 200
        assert "price.manage" not in final.json()["data"]["effective_permissions"]

        replay_revoke = client.post(
            f"/api/v1/vendors/staff/{membership_id}/permissions/price.manage/revoke",
            headers=headers,
            json={"reason": "Replay", "client": "TEST"},
        )
        assert replay_revoke.status_code == 200
        assert replay_revoke.json()["data"]["idempotent_replay"] is True
    finally:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM delegated_permission_grants WHERE membership_id=%s",
                (membership_id,),
            )
            cur.execute(
                "DELETE FROM permission_audit_events WHERE membership_id=%s",
                (membership_id,),
            )
            cur.execute(
                "DELETE FROM organization_memberships WHERE id=%s",
                (membership_id,),
            )
            cur.execute("DELETE FROM users WHERE id=%s", (staff_user,))
        conn.commit()
