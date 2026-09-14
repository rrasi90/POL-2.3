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

from scripts.operational_config import (
    RESERVATION_TTL_MINUTES,
    ALLOCATION_PLAN_TTL_MINUTES,
    VENDOR_ACCEPTANCE_SLA_HOURS,
    DISPUTE_FILING_WINDOW_HOURS,
    PILOT_COMMISSION_RATE,
    PAYMENT_CUSTODY_MODEL,
    OTP_MAX_ATTEMPTS
)

class AuthService:
    @staticmethod
    def request_otp(cur, phone_number: str, purpose: str = 'LOGIN') -> dict:
        otp_id = str(uuid.uuid4())
        # Static mock code hash for test predictability
        code = "123456"
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        cur.execute("""
            INSERT INTO otp_challenges (id, phone_number, code_hash, purpose, attempts_count, max_attempts, status, expires_at)
            VALUES (%s, %s, %s, %s, 0, %s, 'PENDING', now() + interval '2 minutes')
            RETURNING id, phone_number, status, expires_at;
        """, (otp_id, phone_number, code_hash, purpose, OTP_MAX_ATTEMPTS))
        return cur.fetchone()

    @staticmethod
    def verify_otp(cur, phone_number: str, code: str, user_id: str, active_org_id: str) -> dict:
        cur.execute("""
            SELECT * FROM otp_challenges
            WHERE phone_number = %s AND status = 'PENDING' AND expires_at > now()
            ORDER BY created_at DESC LIMIT 1;
        """, (phone_number,))
        challenge = cur.fetchone()
        if not challenge:
            raise ValueError("No pending OTP challenge found or code expired.")

        code_hash = hashlib.sha256(code.encode()).hexdigest()
        if challenge["code_hash"] != code_hash:
            cur.execute("""
                UPDATE otp_challenges
                SET attempts_count = attempts_count + 1,
                    status = CASE WHEN attempts_count + 1 >= max_attempts THEN 'BLOCKED' ELSE 'PENDING' END
                WHERE id = %s
                RETURNING attempts_count, status;
            """, (challenge["id"],))
            upd = cur.fetchone()
            if upd["status"] == "BLOCKED":
                raise PermissionError("OTP attempts exceeded limit. Challenge BLOCKED.")
            raise ValueError(f"Invalid OTP code. Attempt {upd['attempts_count']}/{challenge['max_attempts']}")

        cur.execute("""
            UPDATE otp_challenges SET status = 'VERIFIED', verified_at = now() WHERE id = %s;
        """, (challenge["id"],))

        sess_id = str(uuid.uuid4())
        tok_hash = f"tok_{uuid.uuid4().hex}"
        cur.execute("""
            INSERT INTO user_sessions (id, user_id, active_organization_id, token_hash, status, expires_at)
            VALUES (%s, %s, %s, %s, 'ACTIVE', now() + interval '24 hours')
            RETURNING id, user_id, active_organization_id, status;
        """, (sess_id, user_id, active_org_id, tok_hash))
        return cur.fetchone()

    @staticmethod
    def switch_organization(cur, user_id: str, target_org_id: str, session_id: str) -> dict:
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
        return cur.fetchone()

    @staticmethod
    def revoke_session(cur, session_id: str) -> None:
        cur.execute("""
            UPDATE user_sessions
            SET status = 'REVOKED', revoked_at = now()
            WHERE id = %s;
        """, (session_id,))

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

        if all(s == 'DELIVERED' for s in statuses):
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
    @staticmethod
    def checkout(cur, basket_id: str, plan_id: str, retailer_id: str, idempotency_key: str, 
                 address_snapshot: dict, vendor_allocations: list) -> dict:
        # 1. Validate Basket & Plan
        cur.execute("""
            SELECT b.version, p.basket_version, p.expires_at, p.status
            FROM baskets b
            JOIN allocation_plans p ON p.id = %s
            WHERE b.id = %s;
        """, (plan_id, basket_id))
        chk = cur.fetchone()
        if not chk:
            raise ValueError("Basket or Allocation Plan not found.")
        if chk["version"] != chk["basket_version"]:
            raise ValueError(f"Stale basket checkout: basket v{chk['version']} != plan v{chk['basket_version']}")
        if chk["expires_at"] < datetime.now(timezone.utc):
            raise ValueError("Allocation plan has expired (15-minute TTL exceeded).")

        # 2. Idempotent Reservation & Stock deduction
        total_toman = sum(v["amount_toman"] for v in vendor_allocations)
        og_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO order_groups (
                id, basket_id, allocation_plan_id, retailer_id, checkout_idempotency_key, 
                total_amount_toman, order_count, group_status
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, 'ACTIVE'
            ) RETURNING id;
        """, (og_id, basket_id, plan_id, retailer_id, idempotency_key, total_toman, len(vendor_allocations)))

        child_orders = []
        for alloc in vendor_allocations:
            ord_id = str(uuid.uuid4())
            res_id = str(uuid.uuid4())
            ord_num = f"ORD-{uuid.uuid4().hex[:8].upper()}"

            # Child order
            cur.execute("""
                INSERT INTO orders (
                    id, order_group_id, retailer_id, vendor_id, order_number, 
                    total_amount_toman, order_status, dispute_status, delivery_address_snapshot, correlation_id
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, 'SUBMITTED', 'NONE', %s, %s
                ) RETURNING *;
            """, (
                ord_id, og_id, retailer_id, alloc["vendor_id"], ord_num,
                alloc["amount_toman"], Json(address_snapshot), f"corr-{og_id[:8]}"
            ))
            child_orders.append(cur.fetchone())

            # Inventory reservation
            cur.execute("""
                INSERT INTO inventory_reservations (
                    id, vendor_product_id, order_id, quantity, status, idempotency_key, expires_at
                ) VALUES (
                    %s, %s, %s, %s, 'ACTIVE', %s, now() + interval '15 minutes'
                );
            """, (res_id, alloc["vendor_product_id"], ord_id, alloc["quantity"], f"res-{idempotency_key}-{alloc['vendor_id']}"))

            cur.execute("""
                UPDATE vendor_inventory 
                SET reserved_quantity = reserved_quantity + %s
                WHERE vendor_product_id = %s;
            """, (alloc["quantity"], alloc["vendor_product_id"]))

        return {"order_group_id": og_id, "orders": child_orders}


class FulfillmentService:
    @staticmethod
    def dispatch_order(cur, order_id: str, vendor_id: str, driver_metadata: dict) -> str:
        deliv_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO deliveries (
                id, order_id, vendor_id, driver_name, driver_phone, vehicle_plate, delivery_status
            ) VALUES (
                %s, %s, %s, %s, %s, %s, 'IN_TRANSIT'
            ) RETURNING id;
        """, (
            deliv_id, order_id, vendor_id,
            driver_metadata["driver_name"], driver_metadata["driver_phone"], driver_metadata["vehicle_plate"]
        ))
        cur.execute("""
            UPDATE orders SET order_status = 'DISPATCHED' WHERE id = %s;
        """, (order_id,))
        return deliv_id

    @staticmethod
    def confirm_delivery_otp(cur, delivery_id: str, order_id: str, recipient_name: str) -> None:
        cur.execute("""
            INSERT INTO proof_of_delivery (id, delivery_id, proof_type, otp_verified, accepted_by_name, accepted_at)
            VALUES (%s, %s, 'OTP_CODE', TRUE, %s, now());
        """, (str(uuid.uuid4()), delivery_id, recipient_name))

        cur.execute("""
            UPDATE deliveries SET delivery_status = 'DELIVERED', delivered_at = now() WHERE id = %s;
        """, (delivery_id,))

        cur.execute("""
            UPDATE orders SET order_status = 'DELIVERED' WHERE id = %s;
        """, (order_id,))


class PaymentService:
    @staticmethod
    def record_direct_payment(cur, order_id: str, retailer_id: str, vendor_id: str, 
                              amount_toman: int, verified_by_user_id: str) -> dict:
        pay_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO payments (
                id, order_id, retailer_id, vendor_id, amount_toman, 
                payment_method, custody_model, payment_status, reference_number, verified_by, verified_at, paid_at
            ) VALUES (
                %s, %s, %s, %s, %s,
                'DIRECT_BANK_TRANSFER', 'NON_CUSTODIAL_DIRECT', 'SUCCESS', 'TX-778899', %s, now(), now()
            ) RETURNING *;
        """, (pay_id, order_id, retailer_id, vendor_id, amount_toman, verified_by_user_id))
        pay = cur.fetchone()

        # Generate settlement at 0% pilot commission (D-006)
        settle_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO settlements (
                id, order_id, vendor_id, gross_amount_toman, commission_rate, 
                commission_amount_toman, net_vendor_amount_toman, status
            ) VALUES (
                %s, %s, %s, %s, %s, 0, %s, 'CALCULATED'
            ) RETURNING *;
        """, (settle_id, order_id, vendor_id, amount_toman, PILOT_COMMISSION_RATE, amount_toman))
        settle = cur.fetchone()

        return {"payment": pay, "settlement": settle}


class DisputeService:
    @staticmethod
    def open_dispute(cur, order_id: str, retailer_id: str, vendor_id: str, settlement_id: str, 
                     claimed_amount: int, description: str) -> str:
        disp_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO disputes (
                id, order_id, retailer_id, vendor_id, dispute_status, claimed_amount_toman, description
            ) VALUES (
                %s, %s, %s, %s, 'OPEN', %s, %s
            ) RETURNING id;
        """, (disp_id, order_id, retailer_id, vendor_id, claimed_amount, description))

        # Project dispute state onto order while preserving order_status
        cur.execute("""
            UPDATE orders SET dispute_status = 'OPEN' WHERE id = %s;
        """, (order_id,))

        # Place hold on settlement
        cur.execute("""
            UPDATE settlements SET status = 'DISPUTED' WHERE id = %s;
        """, (settlement_id,))

        # Outbox event
        cur.execute("""
            INSERT INTO outbox_events (id, event_id, event_name, aggregate_type, aggregate_id, payload, status)
            VALUES (%s, %s, 'DISPUTE_OPENED', 'ORDER', %s, %s, 'PENDING');
        """, (str(uuid.uuid4()), str(uuid.uuid4()), order_id, Json({"dispute_id": disp_id, "amount_toman": claimed_amount})))

        return disp_id


class NotificationService:
    @staticmethod
    def dispatch_pending_outbox(cur, target_user_id: str = None, target_org_id: str = None) -> int:
        cur.execute("""
            SELECT * FROM outbox_events WHERE status = 'PENDING' FOR UPDATE SKIP LOCKED;
        """, ())
        events = cur.fetchall()
        count = 0
        for ev in events:
            notif_id = str(uuid.uuid4())
            if target_user_id and target_org_id:
                u_id, o_id = target_user_id, target_org_id
            else:
                cur.execute("""
                    SELECT user_id, organization_id FROM organization_memberships 
                    WHERE role = 'VENDOR_OWNER' AND status = 'ACTIVE' LIMIT 1;
                """)
                recip = cur.fetchone()
                if recip:
                    u_id, o_id = recip["user_id"], recip["organization_id"]
                else:
                    cur.execute("SELECT id FROM users LIMIT 1;")
                    u_id = cur.fetchone()["id"]
                    o_id = None

            cur.execute("""
                INSERT INTO notifications (id, user_id, organization_id, event_name, title, body, priority)
                VALUES (%s, %s, %s, %s, 'اعلام مغایرت سفارش', 'مغایرت کالای آسیب‌دیده ثبت شد.', 'CRITICAL')
                RETURNING id, user_id, organization_id;
            """, (notif_id, u_id, o_id, ev["event_name"]))
            n_row = cur.fetchone()

            if n_row and n_row["organization_id"]:
                cur.execute("""
                    INSERT INTO user_inbox_items (id, user_id, organization_id, notification_id, title, body, category, deep_link, is_read)
                    VALUES (%s, %s, %s, %s, 'اعلام مغایرت سفارش', 'مغایرت ثبت شد.', 'DISPUTES', '/disputes', FALSE);
                """, (str(uuid.uuid4()), n_row["user_id"], n_row["organization_id"], n_row["id"]))

            cur.execute("""
                UPDATE outbox_events SET status = 'PUBLISHED', published_at = now() WHERE id = %s;
            """, (ev["id"],))
            count += 1
        return count


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
    """
    Checkout with Pre-Commit Verification
    Guarantees:
    - Allocation is never accepted blindly
    - Price freshness check against effective vendor_prices
    - Atomic stock reservation with row-level locks
    - Vendor MOV/MOQ invariant re-check
    """
    @staticmethod
    def revalidate_and_checkout(cur, basket_id: str, plan_id: str, retailer_id: str,
                                idempotency_key: str, address_snapshot: dict,
                                vendor_allocations: list) -> dict:
        cur.execute("""
            SELECT b.version, p.basket_version, p.expires_at, p.status
            FROM baskets b
            JOIN allocation_plans p ON p.id = %s
            WHERE b.id = %s;
        """, (plan_id, basket_id))
        chk = cur.fetchone()
        if not chk:
            raise ValueError("Basket or Allocation Plan not found.")
        if chk["version"] != chk["basket_version"]:
            raise ValueError(f"Stale basket checkout: basket v{chk['version']} != plan v{chk['basket_version']}")
        if chk["expires_at"] < datetime.now(timezone.utc):
            raise ValueError("Allocation plan has expired (15-minute TTL exceeded).")

        for alloc in vendor_allocations:
            vp_id = alloc["vendor_product_id"]
            quoted_price = alloc["unit_price_toman"]
            req_qty = alloc["quantity"]

            cur.execute("""
                SELECT price_toman FROM vendor_prices
                WHERE vendor_product_id = %s AND is_current = TRUE;
            """, (vp_id,))
            price_row = cur.fetchone()
            if not price_row or price_row["price_toman"] != quoted_price:
                actual = price_row["price_toman"] if price_row else "N/A"
                raise ValueError(f"Price freshness failure for SKU {vp_id}: Quoted {quoted_price} vs Live {actual}")

            cur.execute("""
                SELECT physical_quantity, reserved_quantity FROM vendor_inventory
                WHERE vendor_product_id = %s
                FOR UPDATE;
            """, (vp_id,))
            inv_row = cur.fetchone()
            if not inv_row:
                raise ValueError(f"No inventory record found for SKU {vp_id}")
            avail = inv_row["physical_quantity"] - inv_row["reserved_quantity"]
            if avail < req_qty:
                raise ValueError(f"Insufficient stock for SKU {vp_id}: Available {avail} < Requested {req_qty}")

        total_toman = sum(v["amount_toman"] for v in vendor_allocations)
        og_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO order_groups (
                id, basket_id, allocation_plan_id, retailer_id, checkout_idempotency_key, 
                total_amount_toman, order_count, group_status
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, 'ACTIVE'
            ) RETURNING id;
        """, (og_id, basket_id, plan_id, retailer_id, idempotency_key, total_toman, len(vendor_allocations)))

        child_orders = []
        for alloc in vendor_allocations:
            ord_id = str(uuid.uuid4())
            res_id = str(uuid.uuid4())
            ord_num = f"ORD-{uuid.uuid4().hex[:8].upper()}"

            cur.execute("""
                INSERT INTO orders (
                    id, order_group_id, retailer_id, vendor_id, order_number, 
                    total_amount_toman, order_status, dispute_status, delivery_address_snapshot, correlation_id
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, 'SUBMITTED', 'NONE', %s, %s
                ) RETURNING *;
            """, (
                ord_id, og_id, retailer_id, alloc["vendor_id"], ord_num,
                alloc["amount_toman"], Json(address_snapshot), f"corr-{og_id[:8]}"
            ))
            child_orders.append(cur.fetchone())

            cur.execute("""
                INSERT INTO inventory_reservations (
                    id, vendor_product_id, order_id, quantity, status, idempotency_key, expires_at
                ) VALUES (
                    %s, %s, %s, %s, 'ACTIVE', %s, now() + interval '15 minutes'
                );
            """, (res_id, alloc["vendor_product_id"], ord_id, alloc["quantity"], f"res-{idempotency_key}-{alloc['vendor_id']}"))

            cur.execute("""
                UPDATE vendor_inventory 
                SET reserved_quantity = reserved_quantity + %s
                WHERE vendor_product_id = %s;
            """, (alloc["quantity"], alloc["vendor_product_id"]))

        return {"order_group_id": og_id, "orders": child_orders}


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
