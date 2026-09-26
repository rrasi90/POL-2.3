from __future__ import annotations

import os
from uuid import uuid4

import psycopg2
import pytest
from psycopg2.extras import RealDictCursor

from scripts.media_service import MAX_UPLOAD_BYTES, MediaError, _magic_mime, _target_key, _validate_bound_upload_target


def test_media_magic_bytes_are_strict():
    assert _magic_mime(b"\xff\xd8\xffJPEG") == "image/jpeg"
    assert _magic_mime(b"\x89PNG\r\n\x1a\nPNG") == "image/png"
    assert _magic_mime(b"RIFF0000WEBP") == "image/webp"
    try:
        _magic_mime(b"MZnot-an-image")
    except MediaError:
        pass
    else:
        raise AssertionError("Non-image magic bytes must be rejected.")


def test_media_target_keys_never_use_client_filename():
    media_id = "4f57e0d5-5d0b-4cc9-9f8b-000000000001"
    key = _target_key("DISPUTE", "dispute-123", media_id)
    assert key == f"disputes/dispute-123/evidence/{media_id}.webp"
    assert "php" not in key.lower()
    assert ".." not in key


def test_media_upload_limit_is_five_megabytes():
    assert MAX_UPLOAD_BYTES == 5 * 1024 * 1024


def test_presigned_upload_target_cannot_be_retargeted():
    media = {
        "upload_target_type": "CANDIDATE",
        "upload_target_id": "11111111-1111-1111-1111-111111111111",
    }
    _validate_bound_upload_target(
        media,
        "CANDIDATE",
        "11111111-1111-1111-1111-111111111111",
    )
    try:
        _validate_bound_upload_target(
            media,
            "DISPUTE",
            "22222222-2222-2222-2222-222222222222",
        )
    except MediaError:
        pass
    else:
        raise AssertionError("A presigned media upload must not be confirmable for a different target.")


def _db():
    return psycopg2.connect(
        dbname=os.environ.get("POL_API_DB_NAME", "pol_test"),
        host=os.environ.get("POL_API_DB_HOST", os.environ.get("PGHOST", "127.0.0.1")),
        port=int(os.environ.get("POL_API_DB_PORT", os.environ.get("POL_PG_PORT", "5432"))),
        user=os.environ.get("POL_API_DB_USER", os.environ.get("PGUSER", "postgres")),
    )


@pytest.fixture
def media_authorization_env():
    conn = _db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    suffix = uuid4().hex[:10]
    vendor_user = str(uuid4())
    vendor_org = str(uuid4())
    other_user = str(uuid4())
    other_org = str(uuid4())
    ops_user = str(uuid4())
    ops_org = str(uuid4())
    brand_id = str(uuid4())
    category_id = str(uuid4())
    subcategory_id = str(uuid4())
    product_id = str(uuid4())
    vendor_id = str(uuid4())
    vendor_product_id = str(uuid4())
    vendor_membership_id = str(uuid4())
    other_membership_id = str(uuid4())
    ops_membership_id = str(uuid4())

    try:
        for user_id, phone, role, name in (
            (vendor_user, f"+9891{uuid4().int % 100000000:08d}", "VENDOR_OWNER", "Media Vendor"),
            (other_user, f"+9891{uuid4().int % 100000000:08d}", "VENDOR_OWNER", "Other Media Vendor"),
            (ops_user, f"+9891{uuid4().int % 100000000:08d}", "OPS_AGENT", "Media Ops"),
        ):
            cur.execute(
                """
                INSERT INTO users (id, phone_number, full_name, role, is_active)
                VALUES (%s,%s,%s,%s,TRUE)
                """,
                (user_id, phone, name, role),
            )

        cur.execute(
            "INSERT INTO organizations (id,name,org_type,status) VALUES (%s,%s,'VENDOR','ACTIVE')",
            (vendor_org, f"Media Vendor Org {suffix}"),
        )
        cur.execute(
            "INSERT INTO organizations (id,name,org_type,status) VALUES (%s,%s,'VENDOR','ACTIVE')",
            (other_org, f"Other Vendor Org {suffix}"),
        )
        cur.execute(
            "INSERT INTO organizations (id,name,org_type,status) VALUES (%s,%s,'OPERATOR','ACTIVE')",
            (ops_org, f"Ops Org {suffix}"),
        )

        cur.execute(
            """
            INSERT INTO organization_memberships
                (id,organization_id,user_id,role,status,is_primary)
            VALUES (%s,%s,%s,'VENDOR_OWNER','ACTIVE',TRUE)
            """,
            (vendor_membership_id, vendor_org, vendor_user),
        )
        cur.execute(
            """
            INSERT INTO organization_memberships
                (id,organization_id,user_id,role,status,is_primary)
            VALUES (%s,%s,%s,'VENDOR_OWNER','ACTIVE',TRUE)
            """,
            (other_membership_id, other_org, other_user),
        )
        cur.execute(
            """
            INSERT INTO organization_memberships
                (id,organization_id,user_id,role,status,is_primary)
            VALUES (%s,%s,%s,'OPS_AGENT','ACTIVE',TRUE)
            """,
            (ops_membership_id, ops_org, ops_user),
        )

        cur.execute(
            "INSERT INTO brands (id,name_fa,slug) VALUES (%s,%s,%s)",
            (brand_id, f"Media Brand {suffix}", f"media-brand-{suffix}"),
        )
        cur.execute(
            "INSERT INTO categories (id,name_fa,slug) VALUES (%s,%s,%s)",
            (category_id, f"Media Category {suffix}", f"media-category-{suffix}"),
        )
        cur.execute(
            """
            INSERT INTO subcategories (id,category_id,name_fa,slug)
            VALUES (%s,%s,%s,%s)
            """,
            (subcategory_id, category_id, f"Media Subcategory {suffix}", f"media-sub-{suffix}"),
        )
        cur.execute(
            """
            INSERT INTO products
                (id,master_sku,canonical_name_fa,brand_id,category_id,subcategory_id,is_active)
            VALUES (%s,%s,%s,%s,%s,%s,TRUE)
            """,
            (
                product_id,
                f"POL-MEDIA-{suffix}",
                f"Media Product {suffix}",
                brand_id,
                category_id,
                subcategory_id,
            ),
        )
        cur.execute(
            """
            INSERT INTO vendors
                (id,user_id,organization_id,business_name,warehouse_address,min_order_value_toman,status)
            VALUES (%s,%s,%s,%s,'Ahvaz Hub',1000000,'ACTIVE')
            """,
            (vendor_id, vendor_user, vendor_org, f"Media Vendor {suffix}"),
        )
        cur.execute(
            """
            INSERT INTO vendor_products
                (id,vendor_id,product_id,vendor_sku,packaging_unit,pack_quantity,sales_unit,is_active,listing_status)
            VALUES (%s,%s,%s,%s,'CARTON',4,'CARTON',TRUE,'ACTIVE')
            """,
            (vendor_product_id, vendor_id, product_id, f"MEDIA-{suffix}"),
        )
        conn.commit()

        yield {
            "conn": conn,
            "cur": cur,
            "product_id": product_id,
            "vendor_user": vendor_user,
            "vendor_org": vendor_org,
            "other_user": other_user,
            "other_org": other_org,
            "ops_user": ops_user,
            "ops_org": ops_org,
        }
    finally:
        conn.rollback()
        cur.execute("DELETE FROM vendor_products WHERE id=%s", (vendor_product_id,))
        cur.execute("DELETE FROM vendors WHERE id=%s", (vendor_id,))
        cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
        cur.execute("DELETE FROM subcategories WHERE id=%s", (subcategory_id,))
        cur.execute("DELETE FROM categories WHERE id=%s", (category_id,))
        cur.execute("DELETE FROM brands WHERE id=%s", (brand_id,))
        cur.execute(
            "DELETE FROM organization_memberships WHERE id IN (%s,%s,%s)",
            (vendor_membership_id, other_membership_id, ops_membership_id),
        )
        cur.execute("DELETE FROM organizations WHERE id IN (%s,%s,%s)", (vendor_org, other_org, ops_org))
        cur.execute("DELETE FROM users WHERE id IN (%s,%s,%s)", (vendor_user, other_user, ops_user))
        conn.commit()
        cur.close()
        conn.close()


def test_vendor_can_attach_media_only_to_an_associated_product(media_authorization_env):
    env = media_authorization_env
    result = _authorize_target(
        env["cur"],
        env["vendor_user"],
        env["vendor_org"],
        "PRODUCT",
        env["product_id"],
    )
    assert result["provenance"] == "VENDOR_UPLOADED"


def test_unrelated_vendor_cannot_attach_media_to_other_vendor_product(media_authorization_env):
    env = media_authorization_env
    with pytest.raises(PermissionError, match="active organization"):
        _authorize_target(
            env["cur"],
            env["other_user"],
            env["other_org"],
            "PRODUCT",
            env["product_id"],
        )


def test_ops_product_media_uses_pol_owned_provenance(media_authorization_env):
    env = media_authorization_env
    result = _authorize_target(
        env["cur"],
        env["ops_user"],
        env["ops_org"],
        "PRODUCT",
        env["product_id"],
    )
    assert result["provenance"] == "POL_OWNED"
