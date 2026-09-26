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
        environment = os.getenv("ENVIRONMENT", "").lower()
        pol_environment = os.getenv("POL_ENV", "").lower()
        is_prod = environment in ("prod", "production") or pol_environment in ("prod", "production")
        is_test = environment == "test"
        # Deterministic OTP is strictly test-only. Any non-test environment,
        # including an unset/unknown environment, must use a cryptographically
        # random code so a deployment misconfiguration cannot silently expose 1234.
        if is_test and not is_prod:
            code = "1234"
        else:
            code = f"{secrets.randbelow(10_000):04d}"

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
        elif is_test and isinstance(res, dict):
            # Test-only convenience: expose the deterministic code only when the
            # environment is explicitly set to "test".
            res["test_code"] = code

        return res

    @staticmethod
    def verify_otp(cur, phone_number: str, code: str, user_id: str, active_org_id: str) -> dict:
        """Verify OTP only for the identity and active membership bound to the phone.

        Caller-supplied identity/organization identifiers are independently
        checked against database truth before any session is created.
        """
        cur.execute("""
            SELECT id
            FROM users
            WHERE phone_number = %s
              AND is_active = TRUE
            LIMIT 1;
        """, (phone_number,))
        phone_user = cur.fetchone()
        if not phone_user:
            raise PermissionError("Phone number is not bound to an active user.")
        if str(phone_user["id"]) != str(user_id):
            raise PermissionError("OTP identity does not match requested user.")

        cur.execute("""
            SELECT m.role, o.status AS organization_status
            FROM organization_memberships m
            JOIN organizations o ON o.id = m.organization_id
            WHERE m.user_id = %s
              AND m.organization_id = %s
              AND m.status = 'ACTIVE'
              AND o.status = 'ACTIVE';
        """, (user_id, active_org_id))
        requested_membership = cur.fetchone()
        if not requested_membership:
            raise PermissionError("User has no active membership in the selected organization.")

        # Serialize verification on the active login/register challenge so an
        # OTP minted for ORDER_CONFIRMATION / DELIVERY_CONFIRM can never become
        # an authentication credential.
        cur.execute("""
            SELECT * FROM otp_challenges
            WHERE phone_number = %s
              AND purpose IN ('LOGIN', 'REGISTER')
              AND status = 'PENDING'
              AND expires_at > now()
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
            UPDATE otp_challenges
            SET status = 'VERIFIED', verified_at = now()
            WHERE id = %s;
        """, (challenge["id"],))

        sess_id = str(uuid.uuid4())
        refresh_token = generate_refresh_token()
        refresh_hash = hash_token(refresh_token)
        role = requested_membership["role"]

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
        """Rotate a valid refresh token and issue a fresh access token.

        The presented refresh token is single-use. Replay of the old token
        fails because its persisted hash is atomically replaced.
        """
        token_hash = hash_token(refresh_token)
        cur.execute("""
            SELECT *
            FROM user_sessions
            WHERE refresh_token_hash = %s
            FOR UPDATE;
        """, (token_hash,))
        session = cur.fetchone()

        if not session:
            raise InvalidRefreshTokenError("Refresh token does not match an existing session.")
        if session["status"] == "REVOKED":
            raise SessionRevokedError("Refresh session has been revoked.")
        if session["status"] == "EXPIRED" or session["expires_at"] <= datetime.now(timezone.utc):
            raise SessionExpiredError("Refresh session has expired.")

        cur.execute("""
            SELECT
                m.role,
                m.status AS membership_status,
                u.is_active AS user_is_active,
                o.status AS organization_status
            FROM organization_memberships m
            JOIN users u ON u.id = m.user_id
            JOIN organizations o ON o.id = m.organization_id
            WHERE m.user_id = %s
              AND m.organization_id = %s
              AND m.status = 'ACTIVE';
        """, (session["user_id"], session["active_organization_id"]))
        membership = cur.fetchone()
        if not membership:
            raise InvalidRefreshTokenError("Refresh session has no active organization membership.")
        if not membership["user_is_active"]:
            raise InvalidRefreshTokenError("User is inactive.")
        if membership["organization_status"] != "ACTIVE":
            raise InvalidRefreshTokenError("Organization is not active.")

        next_refresh_token = generate_refresh_token()
        next_refresh_hash = hash_token(next_refresh_token)
        cur.execute("""
            UPDATE user_sessions
            SET refresh_token_hash = %s,
                last_activity_at = now()
            WHERE id = %s
              AND status = 'ACTIVE'
            RETURNING id;
        """, (next_refresh_hash, session["id"]))
        rotated = cur.fetchone()
        if not rotated:
            raise InvalidRefreshTokenError("Refresh session is no longer active.")

        access_token = encode_access_token(
            str(session["user_id"]),
            str(session["id"]),
            str(session["active_organization_id"]),
            membership["role"],
        )

        return {
            "access_token": access_token,
            "refresh_token": next_refresh_token,
            "token_type": "Bearer",
            "expires_in": JWT_ACCESS_TTL_SECONDS,
        }

    @staticmethod
    def switch_organization(cur, user_id: str, target_org_id: str, session_id: str) -> dict:
        """Switch active organization only on a session owned by the caller."""
        cur.execute("""
            SELECT id, user_id, status, expires_at
            FROM user_sessions
            WHERE id = %s
            FOR UPDATE;
        """, (session_id,))
        session = cur.fetchone()
        if not session:
            raise AuthError("Session not found.")
        if str(session["user_id"]) != str(user_id):
            raise PermissionError("Session does not belong to authenticated user.")
        if session["status"] == "REVOKED":
            raise SessionRevokedError("Session has been revoked.")
        if session["status"] == "EXPIRED" or session["expires_at"] <= datetime.now(timezone.utc):
            raise SessionExpiredError("Session has expired.")

        cur.execute("""
            SELECT
                m.role,
                m.status AS membership_status,
                u.is_active AS user_is_active,
                o.status AS org_status
            FROM organization_memberships m
            JOIN users u ON u.id = m.user_id
            JOIN organizations o ON o.id = m.organization_id
            WHERE m.user_id = %s AND m.organization_id = %s;
        """, (user_id, target_org_id))
        mem = cur.fetchone()
        if not mem or mem["membership_status"] != "ACTIVE":
            raise PermissionError("User has no active membership in target organization.")
        if not mem["user_is_active"]:
            raise PermissionError("User is inactive.")
        if mem["org_status"] != "ACTIVE":
            raise PermissionError("Target organization is not active.")

        cur.execute("""
            UPDATE user_sessions
            SET active_organization_id = %s, last_activity_at = now()
            WHERE id = %s AND user_id = %s AND status = 'ACTIVE'
            RETURNING id, active_organization_id, status;
        """, (target_org_id, session_id, user_id))
        updated_session = cur.fetchone()
        if not updated_session:
            raise AuthError("Session is no longer active.")

        new_access_token = encode_access_token(user_id, session_id, target_org_id, mem["role"])

        return {
            "session": updated_session,
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
            SELECT
                m.role,
                m.status,
                o.org_type,
                o.status AS org_status,
                u.is_active AS user_is_active
            FROM organization_memberships m
            JOIN organizations o ON m.organization_id = o.id
            JOIN users u ON m.user_id = u.id
            WHERE m.user_id = %s AND m.organization_id = %s;
        """, (user_id, active_org_id))
        mem = cur.fetchone()
        if not mem or mem["status"] != "ACTIVE":
            raise PermissionError("Access denied: No active organization membership found.")
        if not mem["user_is_active"]:
            raise PermissionError("Access denied: User is inactive.")
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
    def create_plan(cur, basket_id: str, basket_version: int, vendor_count: int, total_toman: int, input_hash: str | None = None) -> dict:
        plan_id = str(uuid.uuid4())
        inp_hash = input_hash or hashlib.sha256(f"{basket_id}:{basket_version}:{total_toman}".encode()).hexdigest()
        cur.execute("""
            INSERT INTO allocation_plans (
                id, basket_id, basket_version, strategy, vendor_count, 
                total_estimated_toman, status, input_hash, algorithm_version, expires_at
            ) VALUES (
                %s, %s, %s, 'MULTI_VENDOR_MIN_FRAGMENTATION', %s,
                %s, 'CONFIRMED', %s, 'v1.1', now() + interval '15 minutes'
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

        # This compatibility service receives the actor explicitly, so bind it
        # to the retailer tenant before any financial mutation. Authorization
        # is never inferred from user-supplied ids alone.
        cur.execute(
            """
            SELECT 1
            FROM organization_memberships om
            JOIN retailers r ON r.organization_id = om.organization_id
            JOIN organizations o ON o.id = om.organization_id
            WHERE om.user_id = %s
              AND r.id = %s
              AND om.status = 'ACTIVE'
              AND om.role IN ('RETAILER_OWNER','RETAILER_STAFF')
              AND o.status = 'ACTIVE'
            LIMIT 1
            """,
            (verified_by_user_id, retailer_id),
        )
        if not cur.fetchone():
            raise PermissionError("Payment actor is not an authorized member of the retailer tenant.")

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
                   v.organization_id AS vendor_org_id
            FROM orders o
            JOIN retailers r ON r.id=o.retailer_id
            JOIN vendors v ON v.id=o.vendor_id
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
        cur.execute(
            """
            SELECT delivered_at
            FROM deliveries
            WHERE order_id=%s
              AND delivery_status='DELIVERED'
              AND delivered_at IS NOT NULL
            ORDER BY delivered_at DESC
            LIMIT 1
            """,
            (order_id,),
        )
        delivery = cur.fetchone()
        delivered_at = delivery["delivered_at"] if delivery else None
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

        # Evidence may be attached after the dispute is created, but only when
        # the authenticated uploader owns a READY media asset. The HTTP boundary
        # performs this check before calling this service when evidence is supplied.

        # Notify commercial parties and the operations/admin workbench.
        recipients = [
            (order["retailer_org_id"], "RETAILER", ("RETAILER_OWNER", "RETAILER_STAFF")),
            (order["vendor_org_id"], "VENDOR", ("VENDOR_OWNER", "VENDOR_STAFF")),
        ]
        for org_id, side, roles in recipients:
            cur.execute(
                """
                SELECT om.user_id
                FROM organization_memberships om
                JOIN organizations org ON org.id=om.organization_id
                JOIN users u ON u.id=om.user_id
                WHERE om.organization_id=%s
                  AND om.status='ACTIVE'
                  AND u.is_active=TRUE
                  AND org.status='ACTIVE'
                  AND om.role = ANY(%s)
                ORDER BY om.user_id
                """,
                (org_id, list(roles)),
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

        cur.execute(
            """
            SELECT om.user_id, om.organization_id
            FROM organization_memberships om
            JOIN organizations org ON org.id=om.organization_id
            JOIN users u ON u.id=om.user_id
            WHERE org.org_type='OPERATOR'
              AND org.status='ACTIVE'
              AND om.status='ACTIVE'
              AND u.is_active=TRUE
              AND om.role = ANY(%s)
            ORDER BY om.organization_id, om.user_id
            """,
            (["OPS_AGENT", "OPS_ADMIN", "ADMIN_SUPER", "SUPER_ADMIN"],),
        )
        for rec in cur.fetchall():
            org_id = rec["organization_id"]
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
                        'side','OPS'
                    ),
                    'PENDING',%s,%s,%s,'INBOX'
                )
                ON CONFLICT (event_name,dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING
                """,
                (
                    order_id, disp_id, order_id, claimed_amount,
                    rec["user_id"], org_id, dedupe,
                ),
            )

        return disp_id


    @staticmethod
    def resolve_dispute(
        cur,
        dispute_id: str,
        actor_user_id: str,
        outcome: str,
        approved_amount: int,
        reason: str,
    ) -> dict:
        allowed = {
            "ADJUSTED_SHORTAGE": "SHORTAGE_DEDUCTION",
            "REPLACEMENT_ORDER": None,
            "REJECTED_CLAIM": None,
            "MUTUAL_AGREEMENT": "DAMAGE_COMPENSATION",
        }
        if outcome not in allowed:
            raise ValueError("Unsupported dispute resolution outcome.")
        if approved_amount < 0:
            raise ValueError("Approved amount cannot be negative.")
        if not reason or not reason.strip():
            raise ValueError("Resolution reason is required.")

        cur.execute(
            """
            SELECT d.*,
                   s.id AS settlement_id,
                   s.status AS settlement_status,
                   s.gross_amount_toman,
                   s.commission_amount_toman,
                   s.adjustment_amount_toman,
                   s.net_vendor_amount_toman,
                   ro.organization_id AS retailer_org_id,
                   vo.organization_id AS vendor_org_id
            FROM disputes d
            JOIN settlements s ON s.order_id=d.order_id AND s.vendor_id=d.vendor_id
            JOIN retailers r ON r.id=d.retailer_id
            JOIN vendors v ON v.id=d.vendor_id
            JOIN organizations ro ON ro.id=r.organization_id
            JOIN organizations vo ON vo.id=v.organization_id
            WHERE d.id=%s
            ORDER BY s.created_at DESC
            LIMIT 1
            FOR UPDATE
            """,
            (dispute_id,),
        )
        dispute = cur.fetchone()
        if not dispute:
            raise KeyError("Dispute not found.")
        if dispute["dispute_status"] not in ("OPEN", "INVESTIGATING"):
            if dispute["dispute_status"] == "CLOSED":
                return {
                    "id": str(dispute["id"]),
                    "dispute_status": "CLOSED",
                    "resolution_outcome": dispute["resolution_outcome"],
                    "approved_amount_toman": int(dispute["approved_amount_toman"] or 0),
                    "idempotent_replay": True,
                }
            raise ValueError("Only OPEN or INVESTIGATING disputes may be resolved.")
        if approved_amount > int(dispute["claimed_amount_toman"]):
            raise ValueError("Approved amount cannot exceed the claimed amount.")
        if outcome == "REJECTED_CLAIM" and approved_amount != 0:
            raise ValueError("Rejected claims must have approved amount 0.")

        adjustment_type = allowed[outcome]
        if adjustment_type and approved_amount > 0:
            cur.execute(
                """
                INSERT INTO settlement_adjustments
                    (id, settlement_id, dispute_id, adjustment_type, amount_toman,
                     reason, applied_by_user_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                RETURNING id
                """,
                (
                    str(uuid4()),
                    dispute["settlement_id"],
                    dispute_id,
                    adjustment_type,
                    approved_amount,
                    reason.strip(),
                    actor_user_id,
                ),
            )

        cur.execute(
            """
            SELECT COALESCE(SUM(amount_toman),0)::BIGINT AS total_adjustments
            FROM settlement_adjustments
            WHERE settlement_id=%s
            """,
            (dispute["settlement_id"],),
        )
        total_adjustments = int(cur.fetchone()["total_adjustments"])
        gross = int(dispute["gross_amount_toman"])
        commission = int(dispute["commission_amount_toman"])
        net = gross - commission - total_adjustments

        cur.execute(
            """
            UPDATE settlements
            SET adjustment_amount_toman=%s,
                net_vendor_amount_toman=%s,
                status='RECONCILED'
            WHERE id=%s
            RETURNING id, adjustment_amount_toman, net_vendor_amount_toman, status
            """,
            (-total_adjustments, net, dispute["settlement_id"]),
        )
        settlement = dict(cur.fetchone())

        cur.execute(
            """
            UPDATE disputes
            SET dispute_status='CLOSED',
                resolution_outcome=%s,
                approved_amount_toman=%s,
                assigned_ops_user_id=%s,
                resolved_at=now(),
                closed_at=now()
            WHERE id=%s
            RETURNING *
            """,
            (outcome, approved_amount, actor_user_id, dispute_id),
        )
        resolved = dict(cur.fetchone())

        cur.execute(
            """
            UPDATE orders
            SET dispute_status='CLOSED', updated_at=now()
            WHERE id=%s
            """,
            (dispute["order_id"],),
        )

        for org_id, side, roles in (
            (dispute["retailer_org_id"], "RETAILER", ("RETAILER_OWNER", "RETAILER_STAFF")),
            (dispute["vendor_org_id"], "VENDOR", ("VENDOR_OWNER", "VENDOR_STAFF")),
        ):
            cur.execute(
                """
                SELECT om.user_id
                FROM organization_memberships om
                JOIN organizations org ON org.id=om.organization_id
                JOIN users u ON u.id=om.user_id
                WHERE om.organization_id=%s
                  AND om.status='ACTIVE'
                  AND u.is_active=TRUE
                  AND org.status='ACTIVE'
                  AND om.role = ANY(%s)
                ORDER BY om.user_id
                """,
                (org_id, list(roles)),
            )
            for rec in cur.fetchall():
                dedupe = f"DISPUTE_RESOLVED:{dispute_id}:{org_id}:{rec['user_id']}"
                cur.execute(
                    """
                    INSERT INTO outbox_events
                        (id,event_id,event_name,aggregate_type,aggregate_id,payload,status,
                         target_user_id,target_organization_id,dedupe_key,channel_hint)
                    VALUES
                        (gen_random_uuid(),gen_random_uuid(),'DISPUTE_RESOLVED','ORDER',%s,
                         jsonb_build_object(
                            'dispute_id',%s,
                            'order_id',%s,
                            'outcome',%s,
                            'approved_amount_toman',%s,
                            'side',%s
                         ),
                         'PENDING',%s,%s,%s,'INBOX')
                    ON CONFLICT (event_name,dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING
                    """,
                    (
                        dispute["order_id"], dispute_id, dispute["order_id"], outcome,
                        approved_amount, side, rec["user_id"], org_id, dedupe,
                    ),
                )

        return {
            "id": str(resolved["id"]),
            "order_id": str(resolved["order_id"]),
            "dispute_status": resolved["dispute_status"],
            "resolution_outcome": resolved["resolution_outcome"],
            "approved_amount_toman": int(resolved["approved_amount_toman"] or 0),
            "settlement_id": str(dispute["settlement_id"]),
            "settlement_status": settlement["status"],
            "adjustment_amount_toman": int(settlement["adjustment_amount_toman"]),
            "net_vendor_amount_toman": int(settlement["net_vendor_amount_toman"]),
            "resolved_at": resolved["resolved_at"].isoformat() if resolved["resolved_at"] else None,
            "closed_at": resolved["closed_at"].isoformat() if resolved["closed_at"] else None,
            "idempotent_replay": False,
        }


    @staticmethod
    def _record_dispute_event(cur, dispute_id, from_status, to_status, actor_user_id,
                              organization_id, reason=None, event_data=None):
        cur.execute(
            """
            INSERT INTO dispute_events
                (dispute_id, from_status, to_status, actor_user_id,
                 actor_organization_id, reason, event_data)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                dispute_id, from_status, to_status, actor_user_id,
                organization_id, reason, Json(event_data or {}),
            ),
        )

    @staticmethod
    def _notify_dispute_transition(cur, dispute, event_name, actor_user_id, payload):
        recipients = [
            (dispute["retailer_org_id"], ("RETAILER_OWNER", "RETAILER_STAFF")),
            (dispute["vendor_org_id"], ("VENDOR_OWNER", "VENDOR_STAFF")),
        ]
        for org_id, roles in recipients:
            cur.execute(
                """
                SELECT om.user_id
                FROM organization_memberships om
                JOIN users u ON u.id=om.user_id
                JOIN organizations o ON o.id=om.organization_id
                WHERE om.organization_id=%s
                  AND om.status='ACTIVE'
                  AND u.is_active=TRUE
                  AND o.status='ACTIVE'
                  AND om.role=ANY(%s)
                ORDER BY om.user_id
                """,
                (org_id, list(roles)),
            )
            for rec in cur.fetchall():
                dedupe=f"{event_name}:{dispute['id']}:{org_id}:{rec['user_id']}"
                event_payload=dict(payload)
                event_payload["actor_user_id"]=str(actor_user_id)
                cur.execute(
                    """
                    INSERT INTO outbox_events
                        (id,event_id,event_name,aggregate_type,aggregate_id,payload,status,
                         target_user_id,target_organization_id,dedupe_key,channel_hint)
                    VALUES
                        (gen_random_uuid(),gen_random_uuid(),%s,'DISPUTE',%s,%s,'PENDING',
                         %s,%s,%s,'INBOX')
                    ON CONFLICT (event_name,dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING
                    """,
                    (
                        event_name, str(dispute["id"]), Json(event_payload),
                        rec["user_id"], org_id, dedupe,
                    ),
                )

    @classmethod
    def open_dispute_v2(
        cls, cur, *, order_id, retailer_id, vendor_id, claimed_amount,
        description, evidence_media_id, items, actor_user_id, organization_id,
        idempotency_key,
    ):
        if not organization_id:
            raise PermissionError("Dispute requires an organization context.")
        if not idempotency_key:
            raise ValueError("Dispute creation requires an idempotency key.")
        if claimed_amount <= 0:
            raise ValueError("Dispute claimed amount must be positive.")
        if not evidence_media_id:
            raise ValueError("Dispute evidence is required.")
        if not items:
            raise ValueError("At least one dispute item is required.")

        fingerprint = hashlib.sha256(json.dumps({
            "order_id": str(order_id),
            "claimed_amount_toman": int(claimed_amount),
            "description": str(description).strip(),
            "evidence_media_id": str(evidence_media_id),
            "items": sorted([
                {
                    "order_item_id": str(x["order_item_id"]),
                    "quantity": int(x["quantity"]),
                    "claimed_amount_toman": int(x["claimed_amount_toman"]),
                    "reason_code": str(x["reason_code"]),
                } for x in items
            ], key=lambda x: x["order_item_id"]),
        }, sort_keys=True).encode()).hexdigest()

        cur.execute(
            """
            SELECT d.*, r.organization_id AS retailer_org_id,
                   v.organization_id AS vendor_org_id
            FROM disputes d
            JOIN retailers r ON r.id=d.retailer_id
            JOIN vendors v ON v.id=d.vendor_id
            WHERE d.idempotency_key=%s
            LIMIT 1
            FOR UPDATE
            """,
            (idempotency_key,),
        )
        existing = cur.fetchone()
        if existing:
            if str(existing["retailer_id"]) != str(retailer_id):
                raise PermissionError("Dispute replay does not belong to the active retailer.")
            if existing["idempotency_fingerprint"] != fingerprint:
                raise ValueError("Dispute idempotency key was reused with different request data.")
            return dict(existing, idempotent_replay=True)

        cur.execute(
            """
            SELECT o.id, o.order_status, o.retailer_id, o.vendor_id,
                   r.organization_id AS retailer_org_id,
                   v.organization_id AS vendor_org_id
            FROM orders o
            JOIN retailers r ON r.id=o.retailer_id
            JOIN vendors v ON v.id=o.vendor_id
            WHERE o.id=%s
              AND o.retailer_id=%s
              AND o.vendor_id=%s
              AND r.organization_id=%s
              AND v.organization_id IS NOT NULL
            FOR UPDATE
            """,
            (order_id, retailer_id, vendor_id, organization_id),
        )
        order = cur.fetchone()
        if not order:
            raise KeyError("Order not found or not in the active retailer tenant.")
        if order["order_status"] != "DELIVERED":
            raise ValueError("Dispute can only be opened for a delivered order.")

        cur.execute(
            """
            SELECT id, delivered_at, delivery_status
            FROM deliveries
            WHERE order_id=%s
              AND delivery_status='DELIVERED'
              AND delivered_at IS NOT NULL
            ORDER BY delivered_at DESC
            LIMIT 1
            """,
            (order_id,),
        )
        delivery = cur.fetchone()
        if not delivery:
            raise ValueError("Delivered timestamp is required to open a dispute.")
        if delivery["delivered_at"] < datetime.now(timezone.utc) - timedelta(hours=4):
            raise ValueError("The four-hour dispute filing window has expired.")

        cur.execute(
            """
            SELECT id, status
            FROM settlements
            WHERE order_id=%s AND vendor_id=%s
              AND status IN ('CALCULATED','RECONCILED')
            ORDER BY created_at DESC
            LIMIT 1
            FOR UPDATE
            """,
            (order_id, vendor_id),
        )
        settlement = cur.fetchone()
        if not settlement:
            raise ValueError("No dispute-eligible settlement exists for this order.")

        cur.execute(
            """
            SELECT 1 FROM disputes
            WHERE order_id=%s
              AND dispute_status IN ('OPEN','INVESTIGATING','RESOLVED')
            LIMIT 1
            """,
            (order_id,),
        )
        if cur.fetchone():
            raise ValueError("An active or unresolved dispute already exists for this order.")

        cur.execute(
            """
            SELECT oi.id, oi.delivered_quantity, oi.ordered_quantity, oi.unit_price_toman
            FROM order_items oi
            WHERE oi.order_id=%s
            FOR UPDATE
            """,
            (order_id,),
        )
        order_items = {str(x["id"]): x for x in cur.fetchall()}
        if not order_items:
            raise ValueError("Disputed order has no order items.")

        normalized_items=[]
        item_claim_total=0
        for raw in items:
            item_id=str(raw["order_item_id"])
            if item_id not in order_items:
                raise ValueError("Dispute item does not belong to the order.")
            qty=int(raw["quantity"])
            item_claim=int(raw["claimed_amount_toman"])
            if qty <= 0 or item_claim <= 0:
                raise ValueError("Dispute item quantity and claim must be positive.")
            delivered=int(order_items[item_id]["delivered_quantity"] or 0)
            if qty > delivered:
                raise ValueError("Dispute quantity cannot exceed delivered quantity.")
            if item_claim > qty * int(order_items[item_id]["unit_price_toman"]):
                raise ValueError("Dispute item claim exceeds delivered line value.")
            item_claim_total += item_claim
            normalized_items.append((item_id, qty, item_claim, str(raw["reason_code"])))

        if item_claim_total != int(claimed_amount):
            raise ValueError("Dispute item claims must sum exactly to the dispute claimed amount.")

        # The evidence exists before the dispute id does. Validate owner, tenant
        # and READY lifecycle now; bind the asset either to this order or to the
        # newly-created dispute when the media pipeline already supports that target.
        cur.execute(
            """
            SELECT id, status, uploaded_by_user_id, upload_target_type, upload_target_id
            FROM media_assets
            WHERE id=%s
            FOR SHARE
            """,
            (str(evidence_media_id),),
        )
        media = cur.fetchone()
        if not media:
            raise ValueError("Dispute evidence media was not found.")
        if str(media["status"]).upper() != "READY":
            raise ValueError("Dispute evidence media must be READY.")
        if str(media["uploaded_by_user_id"]) != str(actor_user_id):
            raise PermissionError("Dispute evidence media is not owned by the current user.")
        if str(media["upload_target_type"] or "").upper() == "ORDER" and str(media["upload_target_id"]) != str(order_id):
            raise PermissionError("Dispute evidence media is not bound to the disputed order.")
        if str(media["upload_target_type"] or "").upper() not in {"ORDER", "DISPUTE"}:
            raise ValueError("Dispute evidence media purpose is not valid.")

        disp_id=str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO disputes
                (id,order_id,retailer_id,vendor_id,dispute_status,
                 claimed_amount_toman,approved_amount_toman,evidence_media_id,
                 description,idempotency_key,idempotency_fingerprint,created_by_user_id)
            VALUES (%s,%s,%s,%s,'OPEN',%s,0,%s,%s,%s,%s,%s)
            RETURNING *
            """,
            (
                disp_id, order_id, retailer_id, vendor_id, claimed_amount,
                evidence_media_id, description.strip(), idempotency_key,
                fingerprint, actor_user_id,
            ),
        )
        dispute=dict(cur.fetchone())
        for item_id, qty, item_claim, reason_code in normalized_items:
            cur.execute(
                """
                INSERT INTO dispute_items
                    (dispute_id,order_item_id,quantity,claimed_amount_toman,reason_code)
                VALUES (%s,%s,%s,%s,%s)
                """,
                (disp_id, item_id, qty, item_claim, reason_code),
            )

        cur.execute(
            "UPDATE orders SET dispute_status='OPEN', updated_at=now() WHERE id=%s",
            (order_id,),
        )
        cur.execute(
            "UPDATE settlements SET status='DISPUTED' WHERE id=%s AND status IN ('CALCULATED','RECONCILED')",
            (settlement["id"],),
        )
        if cur.rowcount != 1:
            raise ValueError("Settlement changed state while opening the dispute.")

        cls._record_dispute_event(
            cur, disp_id, None, "OPEN", actor_user_id, organization_id,
            reason="Dispute opened",
            event_data={"claimed_amount_toman": int(claimed_amount)},
        )
        cls._notify_dispute_transition(
            cur, dict(dispute, retailer_org_id=order["retailer_org_id"], vendor_org_id=order["vendor_org_id"]),
            "DISPUTE_OPENED",
            actor_user_id,
            {"dispute_id": disp_id, "order_id": str(order_id),
             "claimed_amount_toman": int(claimed_amount)},
        )
        dispute["id"]=str(dispute["id"])
        dispute["idempotent_replay"]=False
        return dispute

    @classmethod
    def investigate_dispute(cls, cur, *, dispute_id, actor_user_id, organization_id, reason):
        if not organization_id:
            raise PermissionError("Dispute investigation requires an organization context.")
        # Only operator staff can advance into INVESTIGATING.
        cur.execute(
            """
            SELECT 1 FROM organization_memberships om
            JOIN organizations o ON o.id=om.organization_id
            WHERE om.user_id=%s AND om.organization_id=%s
              AND om.status='ACTIVE' AND o.org_type='OPERATOR' AND o.status='ACTIVE'
              AND om.role=ANY(%s)
            LIMIT 1
            """,
            (actor_user_id, organization_id, ["OPS_AGENT","OPS_ADMIN","ADMIN_SUPER","SUPER_ADMIN"]),
        )
        if not cur.fetchone():
            raise PermissionError("Only active operator staff may investigate disputes.")
        cur.execute("SELECT * FROM disputes WHERE id=%s FOR UPDATE", (dispute_id,))
        dispute=cur.fetchone()
        if not dispute:
            raise KeyError("Dispute not found.")
        cur.execute(
            """
            SELECT r.organization_id AS retailer_org_id,
                   v.organization_id AS vendor_org_id
            FROM disputes d
            JOIN retailers r ON r.id=d.retailer_id
            JOIN vendors v ON v.id=d.vendor_id
            WHERE d.id=%s
            """,
            (dispute_id,),
        )
        orgs=cur.fetchone()
        if not orgs or str(orgs["retailer_org_id"]) == str(organization_id) or str(orgs["vendor_org_id"]) == str(organization_id):
            # organization_id is the operator tenant for this command; commercial
            # orgs remain notification recipients.
            pass
        dispute={**dict(dispute), "retailer_org_id": orgs["retailer_org_id"], "vendor_org_id": orgs["vendor_org_id"]}
        if dispute["dispute_status"] == "INVESTIGATING":
            return dict(dispute, idempotent_replay=True)
        if dispute["dispute_status"] != "OPEN":
            raise ValueError("Only OPEN disputes may move to INVESTIGATING.")
        before=dispute["dispute_status"]
        cur.execute(
            "UPDATE disputes SET dispute_status='INVESTIGATING', assigned_ops_user_id=%s WHERE id=%s RETURNING *",
            (actor_user_id, dispute_id),
        )
        updated=cur.fetchone()
        cls._record_dispute_event(cur, dispute_id, before, "INVESTIGATING", actor_user_id, organization_id, reason)
        cls._notify_dispute_transition(
            cur, {**dict(updated), "retailer_org_id": None, "vendor_org_id": None},
            "DISPUTE_INVESTIGATING", actor_user_id,
            {"dispute_id": str(dispute_id)}
        )
        return dict(updated)

    @classmethod
    def resolve_canonical(cls, cur, *, dispute_id, actor_user_id, organization_id,
                          outcome, approved_amount, reason):
        if not organization_id:
            raise PermissionError("Dispute resolution requires an organization context.")
        if approved_amount < 0:
            raise ValueError("Approved amount cannot be negative.")
        if not reason or not reason.strip():
            raise ValueError("Resolution reason is required.")
        allowed = {"ADJUSTED_SHORTAGE":"SHORTAGE_DEDUCTION","REPLACEMENT_ORDER":None,
                   "REJECTED_CLAIM":None,"MUTUAL_AGREEMENT":"DAMAGE_COMPENSATION"}
        if outcome not in allowed:
            raise ValueError("Unsupported dispute resolution outcome.")
        cur.execute(
            """
            SELECT d.*,
                   s.id AS settlement_id, s.status AS settlement_status,
                   s.gross_amount_toman, s.commission_amount_toman,
                   ro.organization_id AS retailer_org_id,
                   vo.organization_id AS vendor_org_id
            FROM disputes d
            JOIN settlements s ON s.order_id=d.order_id AND s.vendor_id=d.vendor_id
            JOIN retailers r ON r.id=d.retailer_id
            JOIN vendors v ON v.id=d.vendor_id
            JOIN organizations ro ON ro.id=r.organization_id
            JOIN organizations vo ON vo.id=v.organization_id
            WHERE d.id=%s
            ORDER BY s.created_at DESC LIMIT 1
            FOR UPDATE
            """,
            (dispute_id,),
        )
        d=cur.fetchone()
        if not d:
            raise KeyError("Dispute not found.")
        if d["dispute_status"] == "RESOLVED":
            return {"id":str(d["id"]),"dispute_status":"RESOLVED",
                    "approved_amount_toman":int(d["approved_amount_toman"] or 0),
                    "resolution_outcome":d["resolution_outcome"],"idempotent_replay":True}
        if d["dispute_status"] != "INVESTIGATING":
            raise ValueError("Only INVESTIGATING disputes may be resolved.")
        if approved_amount > int(d["claimed_amount_toman"]):
            raise ValueError("Approved amount cannot exceed the claimed amount.")
        if outcome == "REJECTED_CLAIM" and approved_amount != 0:
            raise ValueError("Rejected claims must have approved amount 0.")

        adjustment_type=allowed[outcome]
        if adjustment_type and approved_amount > 0:
            cur.execute(
                """
                INSERT INTO settlement_adjustments
                    (id,settlement_id,dispute_id,adjustment_type,amount_toman,reason,applied_by_user_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                (str(uuid4()),d["settlement_id"],dispute_id,adjustment_type,
                 approved_amount,reason.strip(),actor_user_id),
            )

        cur.execute(
            """
            UPDATE disputes
            SET dispute_status='RESOLVED',
                resolution_outcome=%s,
                approved_amount_toman=%s,
                assigned_ops_user_id=%s,
                resolved_at=now()
            WHERE id=%s
            RETURNING *
            """,
            (outcome, approved_amount, actor_user_id, dispute_id),
        )
        resolved=cur.fetchone()
        projection="RESOLVED_ADJUSTED" if approved_amount > 0 else "RESOLVED_REJECTED"
        cur.execute("UPDATE orders SET dispute_status=%s, updated_at=now() WHERE id=%s",
                    (projection,d["order_id"]))
        cls._record_dispute_event(
            cur, dispute_id, "INVESTIGATING", "RESOLVED", actor_user_id, organization_id, reason,
            {"outcome": outcome, "approved_amount_toman": int(approved_amount)},
        )
        cls._notify_dispute_transition(
            cur, d, "DISPUTE_RESOLVED", actor_user_id,
            {"dispute_id": str(dispute_id), "order_id": str(d["order_id"]),
             "outcome": outcome, "approved_amount_toman": int(approved_amount)},
        )
        return {
            "id":str(resolved["id"]), "order_id":str(resolved["order_id"]),
            "dispute_status":"RESOLVED", "resolution_outcome":outcome,
            "approved_amount_toman":int(approved_amount),
            "settlement_id":str(d["settlement_id"]),
            "settlement_status":d["settlement_status"],
            "idempotent_replay":False,
        }

    @classmethod
    def close_canonical(cls, cur, *, dispute_id, actor_user_id, organization_id, reason):
        cur.execute(
            "SELECT * FROM disputes WHERE id=%s FOR UPDATE",
            (dispute_id,),
        )
        d=cur.fetchone()
        if not d:
            raise KeyError("Dispute not found.")
        if d["dispute_status"] == "CLOSED":
            return dict(d, idempotent_replay=True)
        if d["dispute_status"] != "RESOLVED":
            raise ValueError("Only RESOLVED disputes may be closed.")
        approved=int(d["approved_amount_toman"] or 0)
        if approved > 0:
            cur.execute(
                """
                SELECT COALESCE(SUM(amount_toman),0) AS completed_refund
                FROM refunds
                WHERE dispute_id=%s AND status='COMPLETED'
                """,
                (dispute_id,),
            )
            completed_refund = int(cur.fetchone()["completed_refund"])
            if completed_refund != approved:
                raise ValueError(
                    "Resolved disputes with a positive award require a completed refund "
                    "whose total amount exactly equals the approved award."
                )
        cur.execute(
            "UPDATE disputes SET dispute_status='CLOSED', closed_at=now() WHERE id=%s RETURNING *",
            (dispute_id,),
        )
        closed=cur.fetchone()
        cur.execute("UPDATE orders SET dispute_status='CLOSED', updated_at=now() WHERE id=%s", (d["order_id"],))
        cls._record_dispute_event(cur, dispute_id, "RESOLVED", "CLOSED", actor_user_id, organization_id, reason)
        return dict(closed)


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

        result = dict(row)
        cur.execute("""
            SELECT vp.id AS vendor_product_id,
                   p.id AS product_id,
                   p.canonical_name_fa AS product_name,
                   vi.physical_quantity AS expected_quantity,
                   COALESCE(dci.declared_quantity, vi.physical_quantity, 0) AS confirmed_quantity
            FROM vendor_products vp
            JOIN products p ON p.id = vp.product_id
            LEFT JOIN vendor_inventory vi ON vi.vendor_product_id = vp.id
            LEFT JOIN daily_inventory_confirmation_items dci
              ON dci.confirmation_id = %s AND dci.vendor_product_id = vp.id
            WHERE vp.vendor_id = %s AND vp.is_active = TRUE
            ORDER BY p.canonical_name_fa, vp.id
        """, (result["id"], vendor_id))
        result["lines"] = [dict(line, id=str(line["vendor_product_id"])) for line in cur.fetchall()]
        return result

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
