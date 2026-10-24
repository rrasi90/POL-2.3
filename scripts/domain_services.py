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
        # random code so a deployment misconfiguration cannot silently expose 123456.
        if is_test and not is_prod:
            code = "123456"
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
    """Canonical dispute chain (G-421..G-437).

    Lifecycle: OPEN -> INVESTIGATING -> RESOLVED -> CLOSED.
    - Admission: DELIVERED-only gate, four-hour filing window, mandatory
      READY/owner/order-bound evidence media, item-level claim scope,
      key+fingerprint idempotency, state-aware locked settlement attach.
    - Every transition writes the append-only `dispute_events` stream and
      maintains the `orders.dispute_status` projection.
    - Outbox events are limited to the two templated canonical events
      (DISPUTE_OPENED, DISPUTE_RESOLVED) so the worker never meets an orphaned
      contract; INVESTIGATING/CLOSED are covered by dispute_events + audit.
    """

    @staticmethod
    def _dispute_fingerprint(parts: dict) -> str:
        import hashlib
        import json as _json

        canonical = _json.dumps(parts, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def _record_dispute_event(cur, *, dispute_id, from_status, to_status,
                              actor_user_id, organization_id, reason=None,
                              event_data=None):
        cur.execute(
            """
            INSERT INTO dispute_events (
                id, dispute_id, from_status, to_status,
                actor_user_id, actor_organization_id, reason, event_data
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                str(uuid.uuid4()), dispute_id, from_status, to_status,
                actor_user_id, organization_id, reason, Json(event_data or {}),
            ),
        )

    @staticmethod
    def _dispute_replay_payload(cur, dispute_id):
        cur.execute(
            """
            SELECT d.id, d.order_id, d.dispute_status, d.claimed_amount_toman,
                   d.resolution_outcome, d.approved_amount_toman,
                   s.status AS settlement_status
            FROM disputes d
            LEFT JOIN settlements s ON s.order_id = d.order_id
            WHERE d.id = %s
            ORDER BY s.created_at DESC NULLS LAST
            LIMIT 1;
            """,
            (dispute_id,),
        )
        row = cur.fetchone()
        if not row:
            raise ValueError("Dispute not found.")
        return {
            "id": str(row["id"]),
            "dispute_id": str(row["id"]),
            "order_id": str(row["order_id"]),
            "dispute_status": row["dispute_status"],
            "resolution_outcome": row["resolution_outcome"],
            "approved_amount_toman": row["approved_amount_toman"],
            "settlement_status": row["settlement_status"],
            "idempotent_replay": True,
        }

    @staticmethod
    def open_dispute(cur, *args, **kwargs):
        """Legacy dispute writer intentionally disabled.

        All dispute creation must pass through open_dispute_v2 so the evidence,
        item-level claim, tenant, idempotency, SLA and settlement invariants are
        applied consistently.
        """
        raise RuntimeError(
            "Legacy DisputeService.open_dispute is disabled; use open_dispute_v2."
        )

    @staticmethod
    def open_dispute_v2(cur, *, order_id, retailer_id, vendor_id, claimed_amount,
                        description, evidence_media_id, items, actor_user_id,
                        organization_id, idempotency_key=None):
        from scripts.operational_config import DISPUTE_FILING_WINDOW_HOURS

        if not description or not str(description).strip():
            raise ValueError("Dispute description is required.")
        if claimed_amount is None or int(claimed_amount) <= 0:
            raise ValueError("claimed_amount_toman must be positive.")
        if not evidence_media_id:
            raise ValueError("Dispute admission requires evidence_media_id.")
        if not items:
            raise ValueError("Dispute admission requires item-level claim scope.")

        normalized_items = []
        for item in items:
            order_item_id = str(item.get("order_item_id") or "")
            quantity = int(item.get("quantity") or 0)
            item_amount = int(item.get("claimed_amount_toman") or 0)
            reason_code = str(item.get("reason_code") or "").strip()
            if not order_item_id or quantity <= 0 or item_amount <= 0 or not reason_code:
                raise ValueError(
                    "Each dispute item requires order_item_id, positive quantity, "
                    "positive claimed_amount_toman and a reason_code."
                )
            normalized_items.append({
                "order_item_id": order_item_id,
                "quantity": quantity,
                "claimed_amount_toman": item_amount,
                "reason_code": reason_code,
            })
        claimed_amount = int(claimed_amount)

        fingerprint = DisputeService._dispute_fingerprint({
            "order_id": order_id,
            "retailer_id": retailer_id,
            "vendor_id": vendor_id,
            "claimed_amount_toman": claimed_amount,
            "description": description,
            "evidence_media_id": str(evidence_media_id),
            "items": normalized_items,
            "actor_user_id": actor_user_id,
        })

        if idempotency_key:
            cur.execute(
                "SELECT id, idempotency_fingerprint FROM disputes "
                "WHERE idempotency_key = %s LIMIT 1;",
                (idempotency_key,),
            )
            existing = cur.fetchone()
            if existing:
                if existing["idempotency_fingerprint"] != fingerprint:
                    raise ValueError(
                        "Idempotency key was already used with a different "
                        "dispute payload."
                    )
                return DisputeService._dispute_replay_payload(cur, existing["id"])

        cur.execute(
            "SELECT id FROM disputes WHERE idempotency_fingerprint = %s LIMIT 1;",
            (fingerprint,),
        )
        replay = cur.fetchone()
        if replay:
            return DisputeService._dispute_replay_payload(cur, replay["id"])

        # G-422: delivered-only gate + four-hour filing window.
        cur.execute(
            """
            SELECT o.order_status, d.id AS delivery_id, d.delivered_at
            FROM orders o
            LEFT JOIN deliveries d
              ON d.order_id = o.id AND d.delivery_status = 'DELIVERED'
            WHERE o.id = %s AND o.retailer_id = %s AND o.vendor_id = %s
            FOR UPDATE OF o;
            """,
            (order_id, retailer_id, vendor_id),
        )
        order = cur.fetchone()
        if not order:
            raise ValueError("Order not found for the active retailer tenant.")
        if order["order_status"] != "DELIVERED" or order["delivery_id"] is None:
            raise ValueError("Disputes can only be opened for delivered orders.")
        cur.execute(
            "SELECT (now() > %s + make_interval(hours => %s)) AS expired;",
            (order["delivered_at"], DISPUTE_FILING_WINDOW_HOURS),
        )
        if cur.fetchone()["expired"]:
            raise ValueError(
                "Dispute filing window has expired ("
                f"{DISPUTE_FILING_WINDOW_HOURS} hours after delivery)."
            )

        # G-423/G-436: evidence must be READY, owned by the actor and pre-bound
        # to this order (order-scoped authorization per migration 065).
        cur.execute(
            """
            SELECT id FROM media_assets
            WHERE id = %s AND status = 'READY'
              AND uploaded_by_user_id = %s
              AND upload_target_type = 'ORDER' AND upload_target_id = %s;
            """,
            (str(evidence_media_id), actor_user_id, order_id),
        )
        if not cur.fetchone():
            raise ValueError(
                "Dispute evidence must be READY media owned by the reporter and "
                "uploaded for this order."
            )

        # G-424: item-level scope validated against the order's own items.
        for item in normalized_items:
            cur.execute(
                """
                SELECT id, ordered_quantity
                FROM order_items
                WHERE id = %s AND order_id = %s;
                """,
                (item["order_item_id"], order_id),
            )
            row = cur.fetchone()
            if not row:
                raise ValueError("Dispute item does not belong to this order.")
            if item["quantity"] > int(row["ordered_quantity"]):
                raise ValueError(
                    "Disputed quantity exceeds the ordered quantity."
                )

        claimed_sum = sum(item["claimed_amount_toman"] for item in normalized_items)
        if claimed_sum > claimed_amount:
            raise ValueError(
                "Item-level claimed amounts exceed the claimed dispute amount."
            )

        # G-429/G-430: state-aware settlement attach under a row lock with a
        # status-conditioned atomic update.
        cur.execute(
            """
            SELECT id, status FROM settlements
            WHERE order_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            FOR UPDATE;
            """,
            (order_id,),
        )
        settlement = cur.fetchone()
        settlement_status = None
        if settlement:
            if settlement["status"] == "CLOSED":
                raise ValueError(
                    "Cannot open a dispute against a closed settlement."
                )
            if settlement["status"] in ("PENDING", "CALCULATED", "RECONCILED"):
                cur.execute(
                    """
                    UPDATE settlements SET status = 'DISPUTED'
                    WHERE id = %s
                      AND status IN ('PENDING','CALCULATED','RECONCILED');
                    """,
                    (settlement["id"],),
                )
                if cur.rowcount != 1:
                    raise ValueError(
                        "Settlement state changed during dispute admission."
                    )
            settlement_status = "DISPUTED"

        dispute_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO disputes (
                id, order_id, retailer_id, vendor_id, dispute_status,
                claimed_amount_toman, description, evidence_media_id,
                created_by_user_id, idempotency_key, idempotency_fingerprint
            ) VALUES (%s, %s, %s, %s, 'OPEN', %s, %s, %s, %s, %s, %s);
            """,
            (
                dispute_id, order_id, retailer_id, vendor_id, claimed_amount,
                description, str(evidence_media_id), actor_user_id,
                idempotency_key, fingerprint,
            ),
        )
        for item in normalized_items:
            cur.execute(
                """
                INSERT INTO dispute_items (
                    id, dispute_id, order_item_id, quantity,
                    claimed_amount_toman, reason_code
                ) VALUES (%s, %s, %s, %s, %s, %s);
                """,
                (
                    str(uuid.uuid4()), dispute_id, item["order_item_id"],
                    item["quantity"], item["claimed_amount_toman"],
                    item["reason_code"],
                ),
            )

        # Re-bind the evidence to its final aggregate (ORDER -> DISPUTE).
        cur.execute(
            """
            UPDATE media_assets
            SET upload_target_type = 'DISPUTE', upload_target_id = %s
            WHERE id = %s AND upload_target_type = 'ORDER'
              AND upload_target_id = %s;
            """,
            (dispute_id, str(evidence_media_id), order_id),
        )

        cur.execute(
            "UPDATE orders SET dispute_status = 'OPEN', updated_at = now() "
            "WHERE id = %s;",
            (order_id,),
        )
        DisputeService._record_dispute_event(
            cur, dispute_id=dispute_id, from_status=None, to_status="OPEN",
            actor_user_id=actor_user_id, organization_id=organization_id,
            reason=description,
            event_data={
                "order_id": order_id,
                "claimed_amount_toman": claimed_amount,
            },
        )

        # Templated canonical event: notify the vendor organization only (the
        # dispute is against the vendor; the reporter already knows).
        cur.execute(
            """
            INSERT INTO outbox_events (
                id, event_id, event_name, aggregate_type, aggregate_id, payload,
                status, target_user_id, target_organization_id, dedupe_key,
                channel_hint, created_at
            )
            SELECT gen_random_uuid(), gen_random_uuid(), 'DISPUTE_OPENED', 'DISPUTE', %s,
                   %s::jsonb, 'PENDING', om.user_id, om.organization_id,
                   %s || ':' || om.user_id::text, 'INBOX', now()
            FROM organization_memberships om
            WHERE om.organization_id = (
                    SELECT organization_id FROM vendors WHERE id = %s
                  )
              AND om.status = 'ACTIVE'
              AND om.role IN ('VENDOR_OWNER','VENDOR_STAFF')
            ON CONFLICT (event_name, dedupe_key) WHERE dedupe_key IS NOT NULL
            DO NOTHING;
            """,
            (
                dispute_id,
                Json({
                    "dispute_id": dispute_id,
                    "order_id": order_id,
                    "claimed_amount_toman": claimed_amount,
                }),
                f"DISPUTE_OPENED:{dispute_id}", vendor_id,
            ),
        )

        return {
            "id": dispute_id,
            "dispute_id": dispute_id,
            "order_id": order_id,
            "dispute_status": "OPEN",
            "claimed_amount_toman": claimed_amount,
            "description": description,
            "evidence_media_id": str(evidence_media_id),
            "items": normalized_items,
            "settlement_status": settlement_status,
            "idempotent_replay": False,
        }

    @staticmethod
    def investigate_dispute(cur, *, dispute_id, actor_user_id, organization_id,
                            reason=None):
        cur.execute(
            "SELECT id, order_id, dispute_status FROM disputes "
            "WHERE id = %s FOR UPDATE;",
            (dispute_id,),
        )
        dispute = cur.fetchone()
        if not dispute:
            raise KeyError("Dispute not found.")
        if dispute["dispute_status"] == "INVESTIGATING":
            return DisputeService._dispute_replay_payload(cur, dispute_id)
        if dispute["dispute_status"] != "OPEN":
            raise ValueError(
                "Cannot investigate a dispute in status "
                f"'{dispute['dispute_status']}'."
            )
        cur.execute(
            """
            UPDATE disputes
            SET dispute_status = 'INVESTIGATING', assigned_ops_user_id = %s
            WHERE id = %s;
            """,
            (actor_user_id, dispute_id),
        )
        cur.execute(
            "UPDATE orders SET dispute_status = 'INVESTIGATING', updated_at = now() "
            "WHERE id = %s;",
            (dispute["order_id"],),
        )
        DisputeService._record_dispute_event(
            cur, dispute_id=dispute_id, from_status="OPEN",
            to_status="INVESTIGATING", actor_user_id=actor_user_id,
            organization_id=organization_id, reason=reason,
        )
        return {
            "id": str(dispute["id"]),
            "dispute_id": str(dispute["id"]),
            "dispute_status": "INVESTIGATING",
            "assigned_ops_user_id": str(actor_user_id),
            "idempotent_replay": False,
        }

    @staticmethod
    def resolve_dispute(cur, *args, **kwargs):
        """Legacy dispute resolver intentionally disabled."""
        raise RuntimeError(
            "Legacy DisputeService.resolve_dispute is disabled; use resolve_canonical."
        )

    @staticmethod
    def resolve_canonical(cur, *, dispute_id, actor_user_id, organization_id,
                          outcome, approved_amount, reason=None):
        allowed_outcomes = ("ADJUSTED_SHORTAGE", "REPLACEMENT_ORDER",
                            "REJECTED_CLAIM", "MUTUAL_AGREEMENT")
        if outcome not in allowed_outcomes:
            raise ValueError(
                f"Invalid resolution outcome: {outcome}. Must be one of "
                f"{allowed_outcomes}."
            )
        approved_amount = int(approved_amount)
        if approved_amount < 0:
            raise ValueError("approved_amount_toman cannot be negative.")
        # G-426 (mirrors the migration-062 boundary invariants):
        if outcome in ("REJECTED_CLAIM", "REPLACEMENT_ORDER") and approved_amount != 0:
            raise ValueError(
                f"{outcome} resolutions must carry a zero cash award."
            )
        if outcome == "ADJUSTED_SHORTAGE" and approved_amount <= 0:
            raise ValueError(
                "ADJUSTED_SHORTAGE resolutions require a positive award."
            )

        cur.execute(
            """
            SELECT id, order_id, dispute_status, claimed_amount_toman
            FROM disputes
            WHERE id = %s
            FOR UPDATE;
            """,
            (dispute_id,),
        )
        dispute = cur.fetchone()
        if not dispute:
            raise KeyError("Dispute not found.")
        if dispute["dispute_status"] == "RESOLVED":
            cur.execute(
                "SELECT resolution_outcome, approved_amount_toman FROM disputes "
                "WHERE id = %s;",
                (dispute_id,),
            )
            row = cur.fetchone()
            if (row["resolution_outcome"] == outcome
                    and int(row["approved_amount_toman"] or 0) == approved_amount):
                return DisputeService._dispute_replay_payload(cur, dispute_id)
            raise ValueError(
                "Dispute is already resolved with a different outcome/amount."
            )
        if dispute["dispute_status"] != "INVESTIGATING":
            raise ValueError(
                "Dispute resolution requires the INVESTIGATING state."
            )
        if approved_amount > int(dispute["claimed_amount_toman"]):
            raise ValueError("Resolution cannot exceed the claimed amount.")

        # G-429/G-430: state-aware settlement read under row lock.
        cur.execute(
            """
            SELECT id, status FROM settlements
            WHERE order_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            FOR UPDATE;
            """,
            (dispute["order_id"],),
        )
        settlement = cur.fetchone()
        if not settlement:
            raise ValueError("No settlement exists for the disputed order.")
        if settlement["status"] == "CLOSED":
            raise ValueError(
                "Cannot resolve a dispute against a closed settlement."
            )
        if settlement["status"] != "DISPUTED":
            raise ValueError(
                f"Settlement is '{settlement['status']}'; expected the DISPUTED "
                "state for dispute resolution."
            )

        if outcome == "ADJUSTED_SHORTAGE" and approved_amount > 0:
            cur.execute(
                """
                INSERT INTO settlement_adjustments (
                    id, settlement_id, dispute_id, adjustment_type,
                    amount_toman, reason, applied_by_user_id
                ) VALUES (%s, %s, %s, 'SHORTAGE_DEDUCTION', %s, %s, %s);
                """,
                (
                    str(uuid.uuid4()), settlement["id"], dispute_id,
                    approved_amount, reason, actor_user_id,
                ),
            )
            cur.execute(
                """
                UPDATE settlements
                SET adjustment_amount_toman = COALESCE(adjustment_amount_toman, 0) + %s,
                    net_vendor_amount_toman = gross_amount_toman
                        - COALESCE(commission_amount_toman, 0)
                        - (COALESCE(adjustment_amount_toman, 0) + %s)
                WHERE id = %s;
                """,
                (approved_amount, approved_amount, settlement["id"]),
            )

        cur.execute(
            """
            UPDATE disputes
            SET dispute_status = 'RESOLVED', resolution_outcome = %s,
                approved_amount_toman = %s, resolved_at = now()
            WHERE id = %s;
            """,
            (outcome, approved_amount, dispute_id),
        )
        cur.execute(
            "UPDATE orders SET dispute_status = 'RESOLVED', updated_at = now() "
            "WHERE id = %s;",
            (dispute["order_id"],),
        )
        DisputeService._record_dispute_event(
            cur, dispute_id=dispute_id, from_status="INVESTIGATING",
            to_status="RESOLVED", actor_user_id=actor_user_id,
            organization_id=organization_id, reason=reason,
            event_data={
                "outcome": outcome,
                "approved_amount_toman": approved_amount,
            },
        )

        # Templated canonical event to both parties (retailer + vendor orgs).
        resolved_payload = Json({
            "dispute_id": dispute_id,
            "order_id": dispute["order_id"],
            "resolution_outcome": outcome,
            "approved_amount_toman": approved_amount,
        })
        for party in ("retailer", "vendor"):
            org_sql = (
                "SELECT organization_id FROM retailers WHERE id = "
                "(SELECT retailer_id FROM disputes WHERE id = %(did)s)"
                if party == "retailer"
                else "SELECT organization_id FROM vendors WHERE id = "
                     "(SELECT vendor_id FROM disputes WHERE id = %(did)s)"
            )
            cur.execute(
                """
                INSERT INTO outbox_events (
                    id, event_id, event_name, aggregate_type, aggregate_id,
                    payload, status, target_user_id, target_organization_id,
                    dedupe_key, channel_hint, created_at
                )
                SELECT gen_random_uuid(), gen_random_uuid(), 'DISPUTE_RESOLVED',
                       'DISPUTE', %(dispute_id)s, %(payload)s::jsonb, 'PENDING',
                       om.user_id, om.organization_id,
                       %(dedupe)s || ':' || om.user_id::text, 'INBOX', now()
                FROM organization_memberships om
                WHERE om.organization_id = (""" + org_sql + """)
                  AND om.status = 'ACTIVE'
                ON CONFLICT (event_name, dedupe_key) WHERE dedupe_key IS NOT NULL
                DO NOTHING;
                """,
                {
                    "did": dispute_id,
                    "dispute_id": dispute_id,
                    "payload": resolved_payload,
                    "dedupe": f"DISPUTE_RESOLVED:{dispute_id}",
                },
            )

        return {
            "id": str(dispute["id"]),
            "dispute_id": str(dispute["id"]),
            "dispute_status": "RESOLVED",
            "resolution_outcome": outcome,
            "approved_amount_toman": approved_amount,
            "settlement_status": "DISPUTED",
            "idempotent_replay": False,
        }

    @staticmethod
    def close_canonical(cur, *, dispute_id, actor_user_id, organization_id,
                        reason=None):
        cur.execute(
            """
            SELECT id, order_id, dispute_status, approved_amount_toman
            FROM disputes
            WHERE id = %s
            FOR UPDATE;
            """,
            (dispute_id,),
        )
        dispute = cur.fetchone()
        if not dispute:
            raise KeyError("Dispute not found.")
        if dispute["dispute_status"] == "CLOSED":
            return DisputeService._dispute_replay_payload(cur, dispute_id)
        if dispute["dispute_status"] != "RESOLVED":
            raise ValueError("Only a RESOLVED dispute can be closed.")
        if int(dispute["approved_amount_toman"] or 0) > 0:
            # Same invariant as the migration-062 boundary, surfaced as a 422
            # instead of a DB error: the award must be fully refunded first.
            cur.execute(
                """
                SELECT COALESCE(SUM(amount_toman), 0) AS refunded
                FROM refunds
                WHERE dispute_id = %s AND status = 'COMPLETED';
                """,
                (dispute_id,),
            )
            refunded = int(cur.fetchone()["refunded"])
            if refunded != int(dispute["approved_amount_toman"]):
                raise ValueError(
                    "Dispute close requires completed refunds totalling the "
                    "approved award."
                )
        cur.execute(
            "UPDATE disputes SET dispute_status = 'CLOSED', closed_at = now() "
            "WHERE id = %s;",
            (dispute_id,),
        )
        cur.execute(
            "UPDATE orders SET dispute_status = 'CLOSED', updated_at = now() "
            "WHERE id = %s;",
            (dispute["order_id"],),
        )
        DisputeService._record_dispute_event(
            cur, dispute_id=dispute_id, from_status="RESOLVED",
            to_status="CLOSED", actor_user_id=actor_user_id,
            organization_id=organization_id, reason=reason,
        )
        return {
            "id": str(dispute["id"]),
            "dispute_id": str(dispute["id"]),
            "dispute_status": "CLOSED",
            "idempotent_replay": False,
        }


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
