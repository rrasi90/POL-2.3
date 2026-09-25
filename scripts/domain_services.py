"""
POL Domain & Application Services Layer
Encapsulates real platform business logic, invariant enforcement, state projection,
and multi-tenant scoping on top of PostgreSQL 18.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import json
import hashlib
from datetime import datetime, timezone, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor, Json

import secrets
import hashlib as _hashlib

from scripts.revalidation_checkout import RevalidationCheckoutService as CanonicalRevalidationCheckoutService
from scripts.canonical_integration_worker import CanonicalIntegrationWorker
from scripts.fulfillment_service import dispatch_order as canonical_dispatch_order, confirm_delivery as canonical_confirm_delivery

from scripts.operational_config import (
    RESERVATION_TTL_MINUTES,
    ALLOCATION_PLAN_TTL_MINUTES,
    VENDOR_ACCEPTANCE_SLA_HOURS,
    DISPUTE_FILING_WINDOW_HOURS,
    PILOT_COMMISSION_RATE,
    PAYMENT_CUSTODY_MODEL,
    OTP_MAX_ATTEMPTS,
    OTP_RATE_LIMIT_COUNT,
    OTP_RATE_LIMIT_WINDOW_MINUTES,
    OTP_LOCKOUT_MINUTES,
    OTP_TTL_SECONDS,
    SESSION_TTL_HOURS,
    JWT_ACCESS_TTL_SECONDS,
)
from scripts.auth_boundary import (
    encode_access_token,
    decode_access_token,
    validate_access_token,
    AuthError,
    InvalidRefreshTokenError,
    SessionExpiredError,
    SessionRevokedError,
    OTPRateLimitError,
    OTPLockoutError,
    InvalidOTPError,
    generate_refresh_token,
    hash_token,
    store_otp_hash,
    verify_otp_hash,
)

# D-018 enforcement scope: rate-limit and lockout apply to LOGIN and REGISTER only.
# ORDER_CONFIRMATION / DELIVERY_CONFIRM have separate domain scope (future policy TBD).
_D018_ENFORCED_PURPOSES = {"LOGIN", "REGISTER"}

class AuthService:
    @staticmethod
    def request_otp(cur, phone_number: str, ip_address: str, purpose: str = 'LOGIN') -> dict:
        """Request an OTP challenge. Enforces D-018 rate-limit and lockout.

        Rate-limit scope: phone+IP, 3 requests per 5 minutes.
        Lockout scope: phone only, 10 minutes after 5th failed attempt.
        D-018 enforcement applies to LOGIN/REGISTER only.
        """
        if not ip_address or ip_address.strip() == "":
            raise ValueError("IP address is required for OTP requests.")

        # Advisory lock on deterministic hash of phone+IP for serialization
        lock_key = int.from_bytes(
            _hashlib.sha256(f"{phone_number}:{ip_address}".encode()).digest()[:8],
            "big"
        ) & 0x7FFFFFFFFFFFFFFF
        cur.execute("SELECT pg_advisory_xact_lock(%s::bigint);", (lock_key,))

        # D-018 purpose policy: rate-limit and lockout apply to LOGIN/REGISTER only
        enforce = purpose in _D018_ENFORCED_PURPOSES

        # 1. Lockout check (phone-scoped, no IP filter) — only for D-018 purposes
        if enforce:
            cur.execute("""
                SELECT blocked_at FROM otp_challenges
                WHERE phone_number = %s
                  AND status = 'BLOCKED'
                  AND blocked_at > now() - interval %s
                ORDER BY blocked_at DESC LIMIT 1;
            """, (phone_number, f"{OTP_LOCKOUT_MINUTES} minutes"))
            locked = cur.fetchone()
            if locked:
                raise OTPLockoutError("Phone temporarily locked. Try again later.")

        # 2. Rate-limit check (phone+IP scoped, no purpose filter) — only for D-018 purposes
        if enforce:
            cur.execute("""
                SELECT count(*) AS cnt FROM otp_challenges
                WHERE phone_number = %s
                  AND ip_address = %s
                  AND created_at > now() - interval %s;
            """, (phone_number, ip_address, f"{OTP_RATE_LIMIT_WINDOW_MINUTES} minutes"))
            row = cur.fetchone()
            if row and row["cnt"] >= OTP_RATE_LIMIT_COUNT:
                raise OTPRateLimitError("Rate limit exceeded. Max 3 OTP requests per 5 minutes per phone+IP.")

        # 3. Generate OTP code
        otp_id = str(uuid.uuid4())
        is_prod = os.getenv("ENVIRONMENT", "").lower() in ("prod", "production") or os.getenv("POL_ENV", "").lower() in ("prod", "production")
        if is_prod:
            code = f"{secrets.randbelow(10_000):04d}"
        else:
            code = "1234"

        code_hash = store_otp_hash(code)
        cur.execute("""
            INSERT INTO otp_challenges (id, phone_number, code_hash, purpose, ip_address, attempts_count, max_attempts, status, expires_at)
            VALUES (%s, %s, %s, %s, %s, 0, %s, 'PENDING', now() + interval %s)
            RETURNING id, phone_number, status, expires_at;
        """, (otp_id, phone_number, code_hash, purpose, ip_address, OTP_MAX_ATTEMPTS, f"{OTP_TTL_SECONDS} seconds"))
        res = cur.fetchone()

        if is_prod:
            from scripts.provider_adapters import build_adapter, ProviderConfigurationError, ProviderTransientError
            try:
                adapter = build_adapter("SMS")
                adapter.send(
                    phone_number=phone_number,
                    title="POL Verification Code",
                    body=f"Your POL verification code is: {code}",
                    idempotency_key=str(otp_id),
                )
            except ProviderConfigurationError:
                raise RuntimeError("Production OTP delivery failed: SMS provider not configured. Set POL_SMS_ENDPOINT.")
            except ProviderTransientError as exc:
                raise RuntimeError(f"Production OTP delivery failed: provider transient error. {exc}") from exc
        else:
            if isinstance(res, dict):
                res["test_code"] = code

        return res

    @staticmethod
    def verify_otp(cur, phone_number: str, code: str, user_id: str, active_org_id: str) -> dict:
        """Verify OTP and issue JWT + refresh token. Enforces D-018 brute-force defense.

        On 5th failed attempt: status=BLOCKED, blocked_at=now().
        On success: creates 30-day session, issues 15-min JWT + refresh token.
        """
        # Serialize verification on the active challenge so one OTP cannot
        # be accepted successfully by concurrent requests.
        cur.execute("""
            SELECT * FROM otp_challenges
            WHERE phone_number = %s AND status = 'PENDING' AND expires_at > now()
            ORDER BY created_at DESC
            LIMIT 1
            FOR UPDATE;
        """, (phone_number,))
        challenge = cur.fetchone()
        if not challenge:
            raise ValueError("No pending OTP challenge found or code expired.")

        if not verify_otp_hash(code, challenge["code_hash"]):
            cur.execute("""
                UPDATE otp_challenges
                SET attempts_count = attempts_count + 1,
                    status = CASE WHEN attempts_count + 1 >= max_attempts THEN 'BLOCKED' ELSE 'PENDING' END,
                    blocked_at = CASE WHEN attempts_count + 1 >= max_attempts THEN now() ELSE blocked_at END
                WHERE id = %s
                RETURNING attempts_count, status;
            """, (challenge["id"],))
            upd = cur.fetchone()
            if upd["status"] == "BLOCKED":
                raise OTPLockoutError("OTP attempts exceeded limit. Phone locked for 10 minutes.")
            raise InvalidOTPError(f"Invalid OTP code. Attempt {upd['attempts_count']}/{challenge['max_attempts']}")

        cur.execute("""
            UPDATE otp_challenges SET status = 'VERIFIED', verified_at = now() WHERE id = %s;
        """, (challenge["id"],))

        # Create session (30-day refresh session)
        sess_id = str(uuid.uuid4())
        refresh_token = generate_refresh_token()
        refresh_hash = hash_token(refresh_token)

        cur.execute("""
            SELECT role FROM organization_memberships
            WHERE user_id = %s AND organization_id = %s AND status = 'ACTIVE';
        """, (user_id, active_org_id))
        mem = cur.fetchone()
        if not mem:
            raise PermissionError("User has no active membership in the selected organization.")
        role = mem["role"]

        # Issue access JWT
        access_token = encode_access_token(user_id, sess_id, active_org_id, role)
        token_hash = hash_token(access_token)

        cur.execute("""
            INSERT INTO user_sessions (id, user_id, active_organization_id, token_hash, refresh_token_hash, status, expires_at)
            VALUES (%s, %s, %s, %s, %s, 'ACTIVE', now() + interval %s)
            RETURNING id, user_id, active_organization_id, status;
        """, (sess_id, user_id, active_org_id, token_hash, refresh_hash, f"{int(SESSION_TTL_HOURS * 3600)} seconds"))
        session = cur.fetchone()

        return {
            "session": session,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": JWT_ACCESS_TTL_SECONDS,
        }

    @staticmethod
    def refresh_access_token(cur, refresh_token: str) -> dict:
        """Issue a new access JWT using a valid 30-day refresh session.

        Refresh token is NOT rotated (rotation TBD per D-018).
        """
        token_hash = hash_token(refresh_token)
        cur.execute("""
            SELECT *
            FROM user_sessions
            WHERE refresh_token_hash = %s;
        """, (token_hash,))
        session = cur.fetchone()

        if not session:
            raise InvalidRefreshTokenError("Refresh token does not match an existing session.")
        if session["status"] == "REVOKED":
            raise SessionRevokedError("Refresh session has been revoked.")
        if session["status"] == "EXPIRED" or session["expires_at"] <= datetime.now(timezone.utc):
            raise SessionExpiredError("Refresh session has expired.")

        cur.execute("""
            SELECT role
            FROM organization_memberships
            WHERE user_id = %s
              AND organization_id = %s
              AND status = 'ACTIVE';
        """, (session["user_id"], session["active_organization_id"]))
        membership = cur.fetchone()
        if not membership:
            raise InvalidRefreshTokenError("Refresh session has no active organization membership.")

        cur.execute("""
            UPDATE user_sessions
            SET last_activity_at = now()
            WHERE id = %s;
        """, (session["id"],))

        access_token = encode_access_token(
            str(session["user_id"]),
            str(session["id"]),
            str(session["active_organization_id"]),
            membership["role"],
        )

        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": JWT_ACCESS_TTL_SECONDS,
        }

    @staticmethod
    def switch_organization(cur, user_id: str, target_org_id: str, session_id: str) -> dict:
        """Switch active organization. Returns new JWT with updated org_id + role."""
        cur.execute("""
            SELECT role, status FROM organization_memberships
            WHERE user_id = %s AND organization_id = %s;
        """, (user_id, target_org_id))
        mem = cur.fetchone()
        if not mem or mem["status"] != "ACTIVE":
            raise PermissionError("User has no active membership in target organization.")

        cur.execute("""
            UPDATE user_sessions
            SET active_organization_id = %s, last_activity_at = now()
            WHERE id = %s AND status = 'ACTIVE'
            RETURNING id, active_organization_id, status;
        """, (target_org_id, session_id))
        session = cur.fetchone()

        new_access_token = encode_access_token(user_id, session_id, target_org_id, mem["role"])

        return {
            "session": session,
            "access_token": new_access_token,
        }

    @staticmethod
    def revoke_session(cur, session_id: str) -> None:
        cur.execute("""
            UPDATE user_sessions
            SET status = 'REVOKED', revoked_at = now()
            WHERE id = %s;
        """, (session_id,))

    @staticmethod
    def revoke_all_sessions(cur, user_id: str) -> int:
        cur.execute("""
            UPDATE user_sessions
            SET status = 'REVOKED', revoked_at = now()
            WHERE user_id = %s AND status = 'ACTIVE';
        """, (user_id,))
        return cur.rowcount

    @staticmethod
    def cleanup_expired_sessions(cur) -> int:
        cur.execute("""
            UPDATE user_sessions
            SET status = 'EXPIRED'
            WHERE status = 'ACTIVE' AND expires_at <= now();
        """)
        return cur.rowcount

    @staticmethod
    def authorize_action(cur, user_id: str, active_org_id: str, allowed_roles: list) -> dict:
        """
        SSoT for authorization: derives active membership role from active organization context.
        users.role is DEPRECATED and ignored.
        Supports canonical roles (ADMIN_SUPER, OPS_AGENT) and legacy aliases (SUPER_ADMIN, OPS_ADMIN).
        """
        cur.execute("""
            SELECT m.role, m.status, o.org_type, o.status as org_status
            FROM organization_memberships m
            JOIN organizations o ON m.organization_id = o.id
            WHERE m.user_id = %s AND m.organization_id = %s;
        """, (user_id, active_org_id))
        mem = cur.fetchone()
        if not mem or mem["status"] != "ACTIVE":
            raise PermissionError("Access denied: No active organization membership found.")
        if mem["org_status"] != "ACTIVE":
            raise PermissionError(f"Access denied: Organization status is {mem['org_status']}.")

        canonical_role_map = {
            "SUPER_ADMIN": "ADMIN_SUPER",
            "OPS_ADMIN": "OPS_AGENT"
        }
        resolved_user_role = canonical_role_map.get(mem["role"], mem["role"])
        resolved_allowed = {canonical_role_map.get(r, r) for r in allowed_roles}

        if resolved_user_role not in resolved_allowed:
            raise PermissionError(f"Access denied: Role '{mem['role']}' is not authorized for this action.")

        return mem


class BasketService:
    @staticmethod
    def create_basket(cur, retailer_id: str) -> str:
        basket_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO baskets (id, retailer_id, version, status)
            VALUES (%s, %s, 1, 'OPEN')
            RETURNING id;
        """, (basket_id, retailer_id))
        return cur.fetchone()["id"]

    @staticmethod
    def add_item_optimistic(cur, basket_id: str, product_id: str, quantity: int, pack_quantity: int, expected_version: int) -> int:
        cur.execute("""
            INSERT INTO basket_items (id, basket_id, product_id, requested_unit, requested_quantity, pack_quantity)
            VALUES (%s, %s, %s, 'CARTON', %s, %s);
        """, (str(uuid.uuid4()), basket_id, product_id, quantity, pack_quantity))

        cur.execute("""
            UPDATE baskets 
            SET version = version + 1, updated_at = now()
            WHERE id = %s AND version = %s
            RETURNING version;
        """, (basket_id, expected_version))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Optimistic lock conflict: basket version mismatch (expected {expected_version})")
        return row["version"]


class AllocationService:
    @staticmethod
    def create_plan(cur, basket_id: str, basket_version: int, vendor_count: int, total_toman: int) -> dict:
        plan_id = str(uuid.uuid4())
        inp_hash = hashlib.sha256(f"{basket_id}:{basket_version}:{total_toman}".encode()).hexdigest()[:16]
        cur.execute("""
            INSERT INTO allocation_plans (
                id, basket_id, basket_version, strategy, vendor_count, 
                total_estimated_toman, status, input_hash, algorithm_version, expires_at
            ) VALUES (
                %s, %s, %s, 'MULTI_VENDOR_MIN_FRAGMENTATION', %s,
                %s, 'CONFIRMED', %s, 'v1.0', now() + interval '15 minutes'
            ) RETURNING *;
        """, (plan_id, basket_id, basket_version, vendor_count, total_toman, inp_hash))
        return cur.fetchone()


class OrderGroupProjector:
    @staticmethod
    def project_group_status(cur, order_group_id: str) -> str:
        cur.execute("""
            SELECT order_status FROM orders WHERE order_group_id = %s;
        """, (order_group_id,))
        rows = cur.fetchall()
        statuses = [r["order_status"] for r in rows]

        # Empty groups are never completed: COMPLETED requires at least one child order.
        if not statuses:
            new_status = 'ACTIVE'
        elif all(s == 'DELIVERED' for s in statuses):
            new_status = 'COMPLETED'
        elif all(s in ('CANCELLED', 'REJECTED') for s in statuses):
            new_status = 'CANCELLED'
        elif any(s in ('CANCELLED', 'REJECTED') for s in statuses):
            new_status = 'PARTIALLY_COMPLETED'
        else:
            new_status = 'ACTIVE'

        cur.execute("""
            UPDATE order_groups
            SET group_status = %s
            WHERE id = %s
            RETURNING group_status;
        """, (new_status, order_group_id))
        return new_status


class CheckoutService:
    """Deprecated compatibility facade; delegates to the canonical checkout path."""

    @staticmethod
    def checkout(cur, basket_id: str, plan_id: str, retailer_id: str, idempotency_key: str,
                 address_snapshot: dict, vendor_allocations: list) -> dict:
        request_fingerprint = hashlib.sha256(
            json.dumps(
                {
                    "basket_id": basket_id,
                    "plan_id": plan_id,
                    "retailer_id": retailer_id,
                    "vendor_allocations": vendor_allocations,
                    "address_snapshot": address_snapshot,
                },
                sort_keys=True,
                default=str,
            ).encode()
        ).hexdigest()
        return RevalidationCheckoutService.revalidate_and_checkout(
            cur=cur,
            basket_id=basket_id,
            plan_id=plan_id,
            retailer_id=retailer_id,
            idempotency_key=idempotency_key,
            request_fingerprint=request_fingerprint,
            address_snapshot=address_snapshot,
            vendor_allocations=vendor_allocations,
        )


class FulfillmentService:
    """Deprecated compatibility facade; requires explicit authenticated actor context."""

    @staticmethod
    def dispatch_order(cur, order_id: str, vendor_id: str, driver_metadata: dict,
                       user_id: str | None = None, organization_id: str | None = None) -> str:
        if not user_id or not organization_id:
            raise PermissionError(
                "Legacy FulfillmentService.dispatch_order requires explicit actor context; "
                "use scripts.fulfillment_service.dispatch_order directly."
            )
        result = canonical_dispatch_order(
            cur,
            user_id=user_id,
            organization_id=organization_id,
            order_id=order_id,
            driver_name=driver_metadata.get("driver_name"),
            driver_phone=driver_metadata.get("driver_phone"),
            vehicle_plate=driver_metadata.get("vehicle_plate"),
        )
        return str(result["delivery_id"])

    @staticmethod
    def confirm_delivery_otp(cur, delivery_id: str, order_id: str, recipient_name: str,
                             otp_code: str | None = None, user_id: str | None = None,
                             organization_id: str | None = None) -> None:
        if not otp_code or not user_id or not organization_id:
            raise PermissionError(
                "Legacy FulfillmentService.confirm_delivery_otp requires authenticated actor context and OTP."
            )
        canonical_confirm_delivery(
            cur,
            user_id=user_id,
            organization_id=organization_id,
            order_id=order_id,
            recipient_name=recipient_name,
            otp_code=otp_code,
        )


class PaymentService:
    """Safe compatibility facade for direct non-custodial payment recording."""

    @staticmethod
    def record_direct_payment(cur, order_id: str, retailer_id: str, vendor_id: str,
                              amount_toman: int, verified_by_user_id: str) -> dict:
        if amount_toman <= 0:
            raise ValueError("Payment amount must be positive.")

        cur.execute(
            """
            SELECT id, retailer_id, vendor_id, total_amount_toman
            FROM orders
            WHERE id=%s
            FOR UPDATE
            """,
            (order_id,),
        )
        order = cur.fetchone()
        if not order:
            raise KeyError("Order not found.")
        if str(order["retailer_id"]) != str(retailer_id) or str(order["vendor_id"]) != str(vendor_id):
            raise PermissionError("Payment participants do not match the order.")

        cur.execute(
            """
            INSERT INTO payments (
                id, order_id, retailer_id, vendor_id, amount_toman,
                payment_method, custody_model, payment_status
            )
            VALUES (%s,%s,%s,%s,%s,'DIRECT_BANK_TRANSFER','NON_CUSTODIAL_DIRECT','PENDING')
            RETURNING *
            """,
            (str(uuid.uuid4()), order_id, retailer_id, vendor_id, amount_toman),
        )
        payment = cur.fetchone()

        return {
            "payment": payment,
            "settlement": None,
            "requires_evidence": True,
            "verified_by_user_id": verified_by_user_id,
        }


class DisputeService:
    @staticmethod
    def open_dispute(cur, order_id: str, retailer_id: str, vendor_id: str, settlement_id: str,
                     claimed_amount: int, description: str) -> str:
        if claimed_amount <= 0:
            raise ValueError("Dispute claimed amount must be positive.")

        cur.execute(
            """
            SELECT o.id, o.order_status, o.retailer_id, o.vendor_id,
                   r.organization_id AS retailer_org_id,
                   v.organization_id AS vendor_org_id,
                   d.delivered_at
            FROM orders o
            JOIN retailers r ON r.id=o.retailer_id
            JOIN vendors v ON v.id=o.vendor_id
            LEFT JOIN LATERAL (
                SELECT delivered_at
                FROM deliveries
                WHERE order_id=o.id
                  AND delivery_status='DELIVERED'
                  AND delivered_at IS NOT NULL
                ORDER BY delivered_at DESC
                LIMIT 1
            ) d ON TRUE
            WHERE o.id=%s
            FOR UPDATE
            """,
            (order_id,),
        )
        order = cur.fetchone()
        if not order:
            raise KeyError("Order not found.")
        if str(order["retailer_id"]) != str(retailer_id) or str(order["vendor_id"]) != str(vendor_id):
            raise PermissionError("Dispute parties do not match the order.")
        if order["order_status"] != "DELIVERED":
            raise ValueError("Dispute can only be opened for a delivered order.")
        delivered_at = order.get("delivered_at")
        if not delivered_at:
            raise ValueError("Delivered timestamp is required to open a dispute.")
        if delivered_at < datetime.now(timezone.utc) - timedelta(hours=4):
            raise ValueError("The four-hour dispute filing window has expired.")

        cur.execute(
            """
            SELECT id, status, vendor_id, order_id
            FROM settlements
            WHERE id=%s
            FOR UPDATE
            """,
            (settlement_id,),
        )
        settlement = cur.fetchone()
        if not settlement or str(settlement["order_id"]) != str(order_id) or str(settlement["vendor_id"]) != str(vendor_id):
            raise ValueError("Settlement does not belong to the disputed order/vendor.")

        cur.execute(
            """
            SELECT 1
            FROM disputes
            WHERE order_id=%s
              AND dispute_status IN ('OPEN','INVESTIGATING','RESOLVED')
            LIMIT 1
            """,
            (order_id,),
        )
        if cur.fetchone():
            raise ValueError("An active or unresolved dispute already exists for this order.")

        disp_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO disputes (
                id, order_id, retailer_id, vendor_id, dispute_status,
                claimed_amount_toman, description
            ) VALUES (%s,%s,%s,%s,'OPEN',%s,%s)
            RETURNING id
            """,
            (disp_id, order_id, retailer_id, vendor_id, claimed_amount, description),
        )

        cur.execute(
            "UPDATE orders SET dispute_status='OPEN' WHERE id=%s",
            (order_id,),
        )
        cur.execute(
            "UPDATE settlements SET status='DISPUTED' WHERE id=%s",
            (settlement_id,),
        )

        # Notify both commercial sides with explicit tenant routing.
        recipients = [
            (order["retailer_org_id"], "RETAILER"),
            (order["vendor_org_id"], "VENDOR"),
        ]
        for org_id, side in recipients:
            cur.execute(
                """
                SELECT om.user_id
                FROM organization_memberships om
                JOIN organizations org ON org.id=om.organization_id
                WHERE om.organization_id=%s
                  AND om.status='ACTIVE'
                  AND org.status='ACTIVE'
                  AND om.role IN ('RETAILER_OWNER','RETAILER_STAFF','VENDOR_OWNER','VENDOR_STAFF')
                ORDER BY om.user_id
                """,
                (org_id,),
            )
            for rec in cur.fetchall():
                dedupe = f"DISPUTE_OPENED:{disp_id}:{org_id}:{rec['user_id']}"
                cur.execute(
                    """
                    INSERT INTO outbox_events (
                        id,event_id,event_name,aggregate_type,aggregate_id,payload,status,
                        target_user_id,target_organization_id,dedupe_key,channel_hint
                    )
                    VALUES (
                        gen_random_uuid(),gen_random_uuid(),'DISPUTE_OPENED','ORDER',%s,
                        jsonb_build_object(
                            'dispute_id',%s,
                            'order_id',%s,
                            'claimed_amount_toman',%s,
                            'side',%s
                        ),
                        'PENDING',%s,%s,%s,'INBOX'
                    )
                    ON CONFLICT (event_name,dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING
                    """,
                    (
                        order_id, disp_id, order_id, claimed_amount, side,
                        rec["user_id"], org_id, dedupe,
                    ),
                )
        return disp_id


class NotificationService:
    """Deprecated facade; delegates to the canonical PostgreSQL outbox worker."""

    @staticmethod
    def dispatch_pending_outbox(
        cur,
        target_user_id: str = None,
        target_org_id: str = None,
        limit: int = 100,
    ) -> int:
        if target_user_id or target_org_id:
            raise PermissionError(
                "Legacy targeted notification dispatch is disabled; "
                "outbox events must contain explicit canonical routing."
            )
        if limit < 1 or limit > 10000:
            raise ValueError("Notification dispatch limit must be between 1 and 10000.")
        return CanonicalIntegrationWorker.process_pending(cur, limit=limit)


class SupportService:
    @staticmethod
    def create_case(cur, user_id: str, org_id: str, case_type: str, priority: str, 
                    subject: str, related_order_id: str = None) -> dict:
        case_id = str(uuid.uuid4())
        case_num = f"SUP-{uuid.uuid4().hex[:8].upper()}"
        cur.execute("""
            INSERT INTO support_cases (
                id, user_id, organization_id, case_number, case_type, priority, 
                status, subject, related_order_id, due_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                'OPEN', %s, %s, now() + interval '24 hours'
            ) RETURNING *;
        """, (case_id, user_id, org_id, case_num, case_type, priority, subject, related_order_id))
        return cur.fetchone()

    @staticmethod
    def add_message(cur, case_id: str, sender_user_id: str, sender_type: str, message_text: str, is_internal: bool = False) -> dict:
        msg_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO support_case_messages (
                id, support_case_id, sender_user_id, sender_type, message_text, is_internal
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            ) RETURNING *;
        """, (msg_id, case_id, sender_user_id, sender_type, message_text, is_internal))
        return cur.fetchone()

    @staticmethod
    def assign_case(cur, case_id: str, agent_user_id: str, assigned_by_user_id: str) -> None:
        cur.execute("""
            UPDATE support_case_assignments SET is_active = FALSE WHERE support_case_id = %s;
        """, (case_id,))

        cur.execute("""
            INSERT INTO support_case_assignments (
                id, support_case_id, assigned_to_user_id, assigned_by_user_id, is_active
            ) VALUES (
                %s, %s, %s, %s, TRUE
            );
        """, (str(uuid.uuid4()), case_id, agent_user_id, assigned_by_user_id))

        cur.execute("""
            UPDATE support_cases 
            SET status = 'IN_PROGRESS', assigned_at = now()
            WHERE id = %s;
        """, (case_id,))


class AuditService:
    @staticmethod
    def log(cur, actor_user_id: str, action: str, target_type: str, target_id: str, 
            state_before: dict, state_after: dict, reason: str, correlation_id: str = None) -> str:
        log_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO admin_audit_logs (
                id, actor_user_id, action, target_entity_type, target_entity_id,
                state_before, state_after, reason, correlation_id
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            ) RETURNING id;
        """, (
            log_id, actor_user_id, action, target_type, target_id,
            Json(state_before), Json(state_after), reason, correlation_id
        ))
        return cur.fetchone()["id"]


class DailyInventoryService:
    """
    Vendor Warehouse Daily Inventory Confirmation Service
    Implements:
    - 1-tap confirmation (CONFIRMED_NO_CHANGES)
    - Item delta adjustment (CONFIRMED_WITH_CHANGES)
    - Inventory confidence updates (CONFIRMED_TODAY, STALE)
    - Non-spamming deduplicated reminder dispatch
    - Anti-gaming reliability event logging
    """
    @staticmethod
    def get_or_create_daily_confirmation(cur, vendor_id: str, confirmation_date: str) -> dict:
        cur.execute("""
            SELECT * FROM daily_inventory_confirmations
            WHERE vendor_id = %s AND confirmation_date = %s;
        """, (vendor_id, confirmation_date))
        row = cur.fetchone()
        if not row:
            cur.execute("""
                INSERT INTO daily_inventory_confirmations (vendor_id, confirmation_date, status)
                VALUES (%s, %s, 'PENDING')
                RETURNING *;
            """, (vendor_id, confirmation_date))
            row = cur.fetchone()
        return row

    @staticmethod
    def confirm_no_changes(cur, vendor_id: str, actor_user_id: str, confirmation_date: str, source: str = 'WEB_PANEL') -> dict:
        """1-tap instant confirmation: 'همه موجودی‌ها درست است'"""
        cur.execute("""
            INSERT INTO daily_inventory_confirmations (
                vendor_id, confirmation_date, status, actor_user_id, confirmed_at, changed_item_count, source, updated_at
            ) VALUES (
                %s, %s, 'CONFIRMED_NO_CHANGES', %s, now(), 0, %s, now()
            )
            ON CONFLICT (vendor_id, confirmation_date) DO UPDATE SET
                status = 'CONFIRMED_NO_CHANGES',
                actor_user_id = EXCLUDED.actor_user_id,
                confirmed_at = now(),
                changed_item_count = 0,
                source = EXCLUDED.source,
                updated_at = now()
            RETURNING *;
        """, (vendor_id, confirmation_date, actor_user_id, source))
        conf = cur.fetchone()

        cur.execute("""
            UPDATE vendor_inventory vi
            SET last_confirmed_at = now(),
                inventory_confidence = 'CONFIRMED_TODAY',
                verification_source = 'DAILY_CONFIRMATION'
            FROM vendor_products vp
            WHERE vi.vendor_product_id = vp.id
              AND vp.vendor_id = %s;
        """, (vendor_id,))

        ReliabilityLedgerService.record_event(
            cur, vendor_id=vendor_id, event_type='DAILY_CONFIRMATION_COMPLETED',
            impact_score=1.0, metadata={"mode": "NO_CHANGES", "source": source}
        )

        return conf

    @staticmethod
    def confirm_with_changes(cur, vendor_id: str, actor_user_id: str, confirmation_date: str,
                             changes: list, source: str = 'WEB_PANEL') -> dict:
        """Confirmed with changes: 'چند قلم تغییر کرده است'"""
        cur.execute("""
            INSERT INTO daily_inventory_confirmations (
                vendor_id, confirmation_date, status, actor_user_id, confirmed_at, changed_item_count, source, updated_at
            ) VALUES (
                %s, %s, 'CONFIRMED_WITH_CHANGES', %s, now(), %s, %s, now()
            )
            ON CONFLICT (vendor_id, confirmation_date) DO UPDATE SET
                status = 'CONFIRMED_WITH_CHANGES',
                actor_user_id = EXCLUDED.actor_user_id,
                confirmed_at = now(),
                changed_item_count = EXCLUDED.changed_item_count,
                source = EXCLUDED.source,
                updated_at = now()
            RETURNING *;
        """, (vendor_id, confirmation_date, actor_user_id, len(changes), source))
        conf = cur.fetchone()

        for chg in changes:
            vp_id = chg["vendor_product_id"]
            decl_qty = int(chg["declared_quantity"])

            cur.execute("""
                SELECT physical_quantity FROM vendor_inventory
                WHERE vendor_product_id = %s;
            """, (vp_id,))
            inv = cur.fetchone()
            prev_qty = inv["physical_quantity"] if inv else 0

            cur.execute("""
                INSERT INTO daily_inventory_confirmation_items (
                    confirmation_id, vendor_product_id, previous_quantity, declared_quantity
                ) VALUES (%s, %s, %s, %s)
                ON CONFLICT (confirmation_id, vendor_product_id) DO UPDATE SET
                    declared_quantity = EXCLUDED.declared_quantity;
            """, (conf["id"], vp_id, prev_qty, decl_qty))

            cur.execute("""
                UPDATE vendor_inventory
                SET physical_quantity = %s,
                    last_confirmed_at = now(),
                    inventory_confidence = 'CONFIRMED_TODAY',
                    verification_source = 'DAILY_CONFIRMATION'
                WHERE vendor_product_id = %s;
            """, (decl_qty, vp_id))

        cur.execute("""
            UPDATE vendor_inventory vi
            SET last_confirmed_at = now(),
                inventory_confidence = 'CONFIRMED_TODAY',
                verification_source = 'DAILY_CONFIRMATION'
            FROM vendor_products vp
            WHERE vi.vendor_product_id = vp.id
              AND vp.vendor_id = %s;
        """, (vendor_id,))

        ReliabilityLedgerService.record_event(
            cur, vendor_id=vendor_id, event_type='DAILY_CONFIRMATION_COMPLETED',
            impact_score=1.0, metadata={"mode": "WITH_CHANGES", "items_changed": len(changes), "source": source}
        )

        return conf

    @staticmethod
    def process_daily_reminders(cur, confirmation_date: str) -> list:
        """Queue deduplicated reminders for routable vendors without aborting the whole batch.

        The DB trigger remains fail-closed for direct writes. This service performs
        the same routing pre-check first so one malformed vendor cannot prevent
        otherwise valid vendors from receiving their daily confirmation reminder.
        """
        cur.execute("""
            SELECT v.id as vendor_id, v.user_id, v.organization_id, v.business_name
            FROM vendors v
            LEFT JOIN daily_inventory_confirmations d
              ON v.id = d.vendor_id AND d.confirmation_date = %s
            WHERE d.status IS NULL OR d.status = 'PENDING';
        """, (confirmation_date,))
        pending_vendors = cur.fetchall()

        queued_events = []
        for v in pending_vendors:
            event_id = f"remind_inv_{v['vendor_id']}_{confirmation_date}"
            cur.execute("SELECT id FROM outbox_events WHERE event_id = %s;", (event_id,))
            if cur.fetchone():
                continue

            cur.execute("""
                SELECT r.user_id
                FROM vendor_inventory_responsibilities r
                WHERE r.vendor_id = %s
                  AND r.responsibility_type = 'WAREHOUSE_INVENTORY'
                  AND r.is_primary = TRUE
                  AND r.effective_from <= now()
                  AND (r.effective_until IS NULL OR r.effective_until > now())
                LIMIT 1;
            """, (v["vendor_id"],))
            responsibility = cur.fetchone()

            if not responsibility:
                # Fail closed for this vendor but keep the daily job healthy.
                # Log one operational routing exception per vendor/day.
                cur.execute("""
                    SELECT 1
                    FROM vendor_reliability_events
                    WHERE vendor_id = %s
                      AND event_type = 'DAILY_CONFIRMATION_ROUTING_ERROR'
                      AND metadata->>'confirmation_date' = %s
                    LIMIT 1;
                """, (v["vendor_id"], str(confirmation_date)))
                if not cur.fetchone():
                    ReliabilityLedgerService.record_event(
                        cur,
                        vendor_id=v["vendor_id"],
                        event_type='DAILY_CONFIRMATION_ROUTING_ERROR',
                        impact_score=-1.0,
                        metadata={
                            "confirmation_date": str(confirmation_date),
                            "reason": "NO_PRIMARY_WAREHOUSE_RESPONSIBILITY",
                            "source": "DAILY_REMINDER_SCHEDULER"
                        }
                    )
                continue

            payload = {
                "vendor_id": str(v["vendor_id"]),
                "confirmation_date": str(confirmation_date),
                "business_name": v["business_name"],
                "channel_preference": ["PUSH", "SMS"]
            }
            cur.execute("""
                INSERT INTO outbox_events (id, event_id, event_name, aggregate_type, aggregate_id, payload, status)
                VALUES (%s, %s, 'DAILY_INVENTORY_REMINDER', 'VENDOR_INVENTORY', %s, %s, 'PENDING')
                RETURNING id, event_id, aggregate_id;
            """, (str(uuid.uuid4()), event_id, v["vendor_id"], Json(payload)))
            queued_events.append(cur.fetchone())

        return queued_events

    @staticmethod
    def mark_missed_and_decay(cur, confirmation_date: str) -> int:
        """Transitions unconfirmed vendors to MISSED and decays inventory confidence to STALE"""
        cur.execute("""
            UPDATE daily_inventory_confirmations
            SET status = 'MISSED', updated_at = now()
            WHERE confirmation_date = %s AND status = 'PENDING'
            RETURNING vendor_id;
        """, (confirmation_date,))
        missed = cur.fetchall()

        for row in missed:
            v_id = row["vendor_id"]
            cur.execute("""
                UPDATE vendor_inventory vi
                SET inventory_confidence = 'STALE'
                FROM vendor_products vp
                WHERE vi.vendor_product_id = vp.id AND vp.vendor_id = %s;
            """, (v_id,))

            ReliabilityLedgerService.record_event(
                cur, vendor_id=v_id, event_type='DAILY_CONFIRMATION_MISSED',
                impact_score=-2.0, metadata={"confirmation_date": str(confirmation_date)}
            )

        return len(missed)


class FeedbackService:
    """
    Universal Feedback & Problem Reporting Service
    Implements:
    - Low-friction submission for all user roles
    - Automatic client context capture
    - Full lifecycle management (SUBMITTED -> CLOSED)
    - Admin inbox triage and replies
    - Tenant-safe isolation
    """
    @staticmethod
    def submit_feedback(cur, user_id: str, org_id: str, feedback_type: str, description: str,
                        title: str = None, priority: str = 'NORMAL', attachment_url: str = None,
                        client_context: dict = None, related_order_id: str = None) -> dict:
        f_id = str(uuid.uuid4())
        ctx = client_context or {}
        cur.execute("""
            INSERT INTO feedback_submissions (
                id, user_id, organization_id, feedback_type, priority, status,
                visibility, title, description, attachment_url, client_context,
                related_order_id, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, 'SUBMITTED',
                'PRIVATE_TO_ADMIN', %s, %s, %s, %s,
                %s, now(), now()
            ) RETURNING *;
        """, (
            f_id, user_id, org_id, feedback_type, priority,
            title or f"بازخورد {feedback_type}", description, attachment_url, Json(ctx),
            related_order_id
        ))
        fb = cur.fetchone()

        cur.execute("""
            INSERT INTO outbox_events (id, event_id, event_name, aggregate_type, aggregate_id, payload, status)
            VALUES (%s, %s, 'FEEDBACK_SUBMITTED', 'FEEDBACK', %s, %s, 'PENDING');
        """, (str(uuid.uuid4()), f"fb_ev_{f_id[:8]}", f_id, Json({"feedback_id": f_id, "type": feedback_type, "priority": priority})))

        return fb

    @staticmethod
    def triage_feedback(cur, feedback_id: str, admin_user_id: str, new_status: str,
                        priority: str = None, assigned_to_user_id: str = None, admin_notes: str = None) -> dict:
        cur.execute("""
            UPDATE feedback_submissions
            SET status = %s,
                priority = COALESCE(%s, priority),
                assigned_to_user_id = COALESCE(%s, assigned_to_user_id),
                admin_notes = COALESCE(%s, admin_notes),
                triaged_at = CASE WHEN triaged_at IS NULL THEN now() ELSE triaged_at END,
                resolved_at = CASE WHEN %s IN ('IMPLEMENTED', 'REJECTED', 'CLOSED') THEN now() ELSE resolved_at END,
                updated_at = now()
            WHERE id = %s
            RETURNING *;
        """, (new_status, priority, assigned_to_user_id, admin_notes, new_status, feedback_id))
        return cur.fetchone()

    @staticmethod
    def reply_to_feedback(cur, feedback_id: str, admin_user_id: str, reply_text: str) -> dict:
        cur.execute("""
            UPDATE feedback_submissions
            SET admin_reply = %s,
                status = CASE WHEN status = 'SUBMITTED' THEN 'IN_REVIEW' ELSE status END,
                updated_at = now()
            WHERE id = %s
            RETURNING *;
        """, (reply_text, feedback_id))
        fb = cur.fetchone()

        cur.execute("""
            INSERT INTO notifications (id, user_id, organization_id, event_name, title, body, priority)
            VALUES (%s, %s, %s, 'FEEDBACK_REPLIED', 'پاسخ به بازخورد شما', %s, 'NORMAL');
        """, (str(uuid.uuid4()), fb["user_id"], fb["organization_id"], reply_text[:100]))

        return fb

    @staticmethod
    def get_user_feedback(cur, user_id: str, org_id: str) -> list:
        """Tenant-safe feedback query"""
        cur.execute("""
            SELECT * FROM feedback_submissions
            WHERE user_id = %s OR (organization_id IS NOT NULL AND organization_id = %s)
            ORDER BY created_at DESC;
        """, (user_id, org_id))
        return cur.fetchall()

    @staticmethod
    def get_admin_inbox(cur, status_filter: str = None, priority_filter: str = None) -> list:
        query = "SELECT * FROM feedback_submissions WHERE 1=1"
        params = []
        if status_filter:
            query += " AND status = %s"
            params.append(status_filter)
        if priority_filter:
            query += " AND priority = %s"
            params.append(priority_filter)
        query += " ORDER BY CASE priority WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 WHEN 'NORMAL' THEN 3 ELSE 4 END, created_at DESC;"
        cur.execute(query, tuple(params))
        return cur.fetchall()


class RevalidationCheckoutService:
    """Compatibility facade for the canonical transactional checkout service.

    The implementation lives in scripts.revalidation_checkout. This facade keeps
    legacy imports stable while preventing a stale duplicate implementation from
    diverging from the canonical checkout contract.
    """

    @staticmethod
    def revalidate_and_checkout(
        cur,
        basket_id: str,
        plan_id: str,
        retailer_id: str,
        idempotency_key: str,
        address_snapshot: dict,
        vendor_allocations: list,
        request_fingerprint: str | None = None,
    ) -> dict:
        if request_fingerprint is None:
            request_fingerprint = hashlib.sha256(
                json.dumps(
                    {
                        "basket_id": basket_id,
                        "plan_id": plan_id,
                        "retailer_id": retailer_id,
                        "vendor_allocations": vendor_allocations,
                        "address_snapshot": address_snapshot,
                    },
                    sort_keys=True,
                    default=str,
                ).encode("utf-8")
            ).hexdigest()

        return CanonicalRevalidationCheckoutService.revalidate_and_checkout(
            cur=cur,
            basket_id=basket_id,
            plan_id=plan_id,
            retailer_id=retailer_id,
            idempotency_key=idempotency_key,
            request_fingerprint=request_fingerprint,
            address_snapshot=address_snapshot,
            vendor_allocations=vendor_allocations,
        )

class ReliabilityLedgerService:
    """
    Vendor Operational Reliability Ledger
    Event-based ledger to record and analyze raw operational signals
    """
    @staticmethod
    def record_event(cur, vendor_id: str, event_type: str, order_id: str = None,
                     impact_score: float = 0.0, declared_val: dict = None,
                     observed_val: dict = None, metadata: dict = None) -> str:
        ev_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO vendor_reliability_events (
                id, vendor_id, event_type, order_id, impact_score, declared_value, observed_value, metadata, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, now()
            ) RETURNING id;
        """, (
            ev_id, vendor_id, event_type, order_id, impact_score,
            Json(declared_val) if declared_val else None,
            Json(observed_val) if observed_val else None,
            Json(metadata or {})
        ))
        return cur.fetchone()["id"]

    @staticmethod
    def get_reliability_summary(cur, vendor_id: str) -> dict:
        cur.execute("""
            SELECT event_type, count(*) as count, sum(impact_score) as total_impact
            FROM vendor_reliability_events
            WHERE vendor_id = %s
            GROUP BY event_type;
        """, (vendor_id,))
        rows = cur.fetchall()
        return {r["event_type"]: {"count": r["count"], "total_impact": float(r["total_impact"] or 0.0)} for r in rows}
