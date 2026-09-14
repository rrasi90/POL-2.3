"""Canonical MVP Vendor Referral application service.

MVP intent:
- A vendor creates a referral code/link.
- A retailer can redeem it once during onboarding/activation.
- The attribution is immutable first-touch for the retailer.
- No monetary referral reward, wallet, credit, or complex incentive engine is active.
- Attribution is emitted as an outbox event for analytics and future commercial use.
"""

from __future__ import annotations

import secrets
import string
import uuid


class VendorReferralAccessError(PermissionError):
    pass


class VendorReferralStateError(ValueError):
    pass


class VendorReferralService:
    @staticmethod
    def _vendor_access(cur, actor_user_id: str, vendor_id: str) -> bool:
        cur.execute(
            """
            SELECT 1
            FROM vendors v
            JOIN organization_memberships om ON om.organization_id = v.organization_id
            JOIN organizations o ON o.id = om.organization_id
            WHERE v.id = %s
              AND om.user_id = %s
              AND om.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
              AND om.role IN ('VENDOR_OWNER','VENDOR_STAFF')
            LIMIT 1;
            """,
            (vendor_id, actor_user_id),
        )
        return cur.fetchone() is not None

    @staticmethod
    def _retailer_access(cur, actor_user_id: str, retailer_id: str) -> bool:
        cur.execute(
            """
            SELECT 1
            FROM retailers r
            JOIN organization_memberships om ON om.organization_id = r.organization_id
            JOIN organizations o ON o.id = om.organization_id
            WHERE r.id = %s
              AND om.user_id = %s
              AND om.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
              AND om.role IN ('RETAILER_OWNER','RETAILER_STAFF')
            LIMIT 1;
            """,
            (retailer_id, actor_user_id),
        )
        return cur.fetchone() is not None

    @staticmethod
    def _generate_code() -> str:
        alphabet = string.ascii_uppercase + string.digits
        return "POLV-" + "".join(secrets.choice(alphabet) for _ in range(8))

    @classmethod
    def create_referral(cls, cur, actor_user_id: str, vendor_id: str,
                        max_redemptions: int | None = None,
                        expires_at=None) -> dict:
        if not cls._vendor_access(cur, actor_user_id, vendor_id):
            raise VendorReferralAccessError("Actor is not an active member of this vendor.")
        if max_redemptions is not None and max_redemptions <= 0:
            raise ValueError("max_redemptions must be positive when provided.")

        code = cls._generate_code()
        referral_id = str(uuid.uuid4())
        try:
            cur.execute(
                """
                INSERT INTO vendor_referrals
                    (id, vendor_id, referral_code, status, max_redemptions,
                     expires_at, created_by_user_id)
                VALUES (%s,%s,%s,'ACTIVE',%s,%s,%s)
                RETURNING *;
                """,
                (referral_id, vendor_id, code, max_redemptions, expires_at, actor_user_id),
            )
        except Exception as exc:
            if getattr(exc, "pgcode", None) == "23505":
                raise VendorReferralStateError("Generated referral code collided; retry creation.") from exc
            raise
        return cur.fetchone()

    @classmethod
    def redeem_referral(cls, cur, actor_user_id: str, retailer_id: str,
                        referral_code: str, request_idempotency_key: str) -> dict:
        if not request_idempotency_key:
            raise ValueError("Referral redemption requires an idempotency key.")
        if not cls._retailer_access(cur, actor_user_id, retailer_id):
            raise VendorReferralAccessError("Actor is not an active member of this retailer.")

        cur.execute(
            "SELECT * FROM vendor_referral_attributions WHERE request_idempotency_key = %s",
            (request_idempotency_key,),
        )
        existing = cur.fetchone()
        if existing:
            return existing

        cur.execute(
            """
            SELECT *
            FROM vendor_referrals
            WHERE referral_code = %s
            FOR UPDATE;
            """,
            (referral_code.strip().upper(),),
        )
        referral = cur.fetchone()
        if not referral:
            raise KeyError("Referral code not found.")
        if referral["status"] != "ACTIVE":
            raise VendorReferralStateError("Referral code is not active.")
        if referral["expires_at"] is not None:
            cur.execute("SELECT now() >= %s AS expired", (referral["expires_at"],))
            if cur.fetchone()["expired"]:
                cur.execute(
                    "UPDATE vendor_referrals SET status='EXPIRED', updated_at=now() WHERE id=%s",
                    (referral["id"],),
                )
                raise VendorReferralStateError("Referral code has expired.")
        if referral["max_redemptions"] is not None and referral["redemption_count"] >= referral["max_redemptions"]:
            raise VendorReferralStateError("Referral code redemption limit reached.")

        cur.execute(
            """
            SELECT *
            FROM vendor_referral_attributions
            WHERE retailer_id = %s
            FOR UPDATE;
            """,
            (retailer_id,),
        )
        prior = cur.fetchone()
        if prior:
            return prior

        attribution_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO vendor_referral_attributions
                (id, referral_id, vendor_id, retailer_id, referred_user_id,
                 status, request_idempotency_key)
            VALUES (%s,%s,%s,%s,%s,'ATTRIBUTED',%s)
            RETURNING *;
            """,
            (attribution_id, referral["id"], referral["vendor_id"], retailer_id,
             actor_user_id, request_idempotency_key),
        )
        attribution = cur.fetchone()

        cur.execute(
            """
            UPDATE vendor_referrals
            SET redemption_count = redemption_count + 1,
                updated_at = now()
            WHERE id = %s;
            """,
            (referral["id"],),
        )

        # Analytics/domain event only: no recipient is attached because this is
        # intentionally not a notification and vendor user_id is a legacy field.
        cur.execute(
            """
            INSERT INTO outbox_events
                (id,event_id,event_name,aggregate_type,aggregate_id,payload,status,
                 target_organization_id,dedupe_key)
            SELECT gen_random_uuid(), %s, 'VENDOR_REFERRAL_REDEEMED', 'VENDOR_REFERRAL', %s,
                   jsonb_build_object(
                       'attribution_id', %s,
                       'referral_id', %s,
                       'vendor_id', %s,
                       'retailer_id', %s
                   ), 'PENDING', v.organization_id, %s
            FROM vendors v
            WHERE v.id = %s
            ON CONFLICT (event_name, dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING;
            """,
            ("vendor_referral_redeemed:" + attribution_id,
             attribution_id,
             attribution_id,
             referral["id"],
             referral["vendor_id"],
             retailer_id,
             "vendor_referral_redeemed:" + attribution_id,
             referral["vendor_id"]),
        )
        return attribution

    @staticmethod
    def activate_on_first_order(cur, retailer_id: str, order_id: str):
        cur.execute(
            """
            UPDATE vendor_referral_attributions
            SET status = CASE WHEN status = 'ATTRIBUTED' THEN 'ACTIVATED' ELSE status END,
                first_order_id = COALESCE(first_order_id, %s),
                activated_at = CASE WHEN activated_at IS NULL THEN now() ELSE activated_at END,
                updated_at = now()
            WHERE retailer_id = %s
              AND status IN ('ATTRIBUTED','ACTIVATED')
            RETURNING *;
            """,
            (order_id, retailer_id),
        )
        return cur.fetchone()
