"""Framework-agnostic POL application boundary.

HTTP/GraphQL/RPC adapters should translate transport payloads into these command
methods. Domain tables must not be written directly by client-facing code.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from psycopg2.extras import Json

from scripts.checkout_gateway import CanonicalCheckoutGateway
from scripts.canonical_feedback import CanonicalFeedbackService
from scripts.canonical_basket_allocation import CanonicalBasketAllocationService
from scripts.canonical_partial_acceptance import CanonicalPartialAcceptanceService
from scripts.canonical_vendor_order import CanonicalVendorOrderService
from scripts.canonical_support import CanonicalSupportService
from scripts.fulfillment_service import (
    mark_preparing as _mark_preparing,
    mark_ready as _mark_ready,
    dispatch_order as _dispatch_order,
    transition_delivery_stage as _transition_delivery_stage,
    confirm_delivery as _confirm_delivery,
)
from scripts.payment_reconciliation_worker import PaymentReconciliationWorker
from scripts.provider_delivery_worker import ProviderDeliveryWorker
from scripts.operational_config import PILOT_COMMISSION_RATE
from scripts.returns_rma import CanonicalReturnService
from scripts.media_service import MediaService
from scripts.user_profiles import UserProfileService
from scripts.vendor_referral import VendorReferralService
from scripts.vendor_acceptance_timeout_worker import VendorAcceptanceTimeoutWorker


@dataclass(frozen=True)
class ApplicationContext:
    user_id: str
    organization_id: str | None
    correlation_id: str


class POLApplicationBoundary:
    """The sole client-facing command/query facade for MVP routes."""

    def __init__(self, cur, context: ApplicationContext):
        self.cur = cur
        self.context = context

    def media_presign(self, *, mime_type, file_size_bytes, target_type, target_id, filename=None):
        if not self.context.organization_id:
            raise PermissionError("Media upload requires an active organization context.")
        return MediaService.presign(
            self.cur,
            user_id=self.context.user_id,
            organization_id=self.context.organization_id,
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
            target_type=target_type,
            target_id=str(target_id),
            filename=filename,
        )

    def media_confirm_upload(self, *, media_id, target_type, target_id):
        if not self.context.organization_id:
            raise PermissionError("Media confirmation requires an active organization context.")
        return MediaService.confirm_upload(
            self.cur,
            user_id=self.context.user_id,
            organization_id=self.context.organization_id,
            media_id=str(media_id),
            target_type=target_type,
            target_id=str(target_id),
        )

    def profile_get(self):
        return UserProfileService.get_my_profile(
            self.cur, self.context.user_id, self.context.organization_id
        )

    def profile_completion(self):
        return UserProfileService.profile_completion(
            self.cur, self.context.user_id, self.context.organization_id
        )

    def profile_update(self, *, fields):
        return UserProfileService.update_my_profile(
            self.cur, self.context.user_id, fields
        )

    def profile_membership_update(self, *, fields):
        if not self.context.organization_id:
            raise PermissionError("Membership profile update requires an organization context.")
        return UserProfileService.update_membership_profile(
            self.cur, self.context.user_id, self.context.organization_id, fields
        )

    def basket_create(self):
        return CanonicalBasketAllocationService.create_basket(
            self.cur, self.context.user_id, self.context.organization_id
        )

    def basket_add_item(self, *, basket_id, product_id, quantity, pack_quantity, expected_version):
        return CanonicalBasketAllocationService.add_item(
            self.cur,
            self.context.user_id,
            self.context.organization_id,
            basket_id,
            product_id,
            quantity,
            pack_quantity,
            expected_version,
        )

    def basket_allocation_preview(self, *, basket_id):
        return CanonicalBasketAllocationService.allocation_preview(
            self.cur, self.context.user_id, self.context.organization_id, basket_id
        )

    def checkout(self, *, basket_id, plan_id, retailer_id, idempotency_key, address_snapshot, vendor_allocations):
        self._verify_retailer_actor(retailer_id)
        result = CanonicalCheckoutGateway.checkout(
            cur=self.cur,
            basket_id=basket_id,
            plan_id=plan_id,
            retailer_id=retailer_id,
            idempotency_key=idempotency_key,
            address_snapshot=address_snapshot,
            vendor_allocations=vendor_allocations,
        )
        for order in result.get("orders", []):
            VendorReferralService.activate_on_first_order(self.cur, retailer_id, str(order["id"]))
        return result

    def checkout_from_allocation_plan(
        self,
        *,
        allocation_plan_id,
        delivery_address,
        preferred_payment_method,
        idempotency_key,
    ):
        """Resolve the authenticated retailer allocation plan and execute canonical checkout."""
        self.cur.execute(
            """
            SELECT r.id AS retailer_id, b.id AS basket_id
            FROM allocation_plans ap
            JOIN baskets b ON b.id = ap.basket_id
            JOIN retailers r ON r.id = b.retailer_id
            JOIN organizations o ON o.id = r.organization_id
            JOIN organization_memberships om
              ON om.organization_id = r.organization_id
            WHERE ap.id = %s
              AND om.user_id = %s
              AND om.organization_id = %s
              AND om.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
              AND om.role IN ('RETAILER_OWNER', 'RETAILER_STAFF')
            LIMIT 1
            """,
            (allocation_plan_id, self.context.user_id, self.context.organization_id),
        )
        owner = self.cur.fetchone()
        if not owner:
            raise PermissionError(
                "Allocation plan is not accessible from the active retailer organization."
            )

        retailer_id = str(owner["retailer_id"])
        basket_id = str(owner["basket_id"])
        self._verify_retailer_actor(retailer_id)

        self.cur.execute(
            """
            SELECT vendor_id, vendor_product_id, allocated_quantity,
                   unit_price_snapshot_toman, line_total_toman, status
            FROM allocation_items
            WHERE allocation_plan_id = %s
            ORDER BY id
            """,
            (allocation_plan_id,),
        )
        allocation_rows = self.cur.fetchall()
        vendor_allocations = [
            {
                "vendor_id": str(row["vendor_id"]),
                "vendor_product_id": str(row["vendor_product_id"]),
                "quantity": int(row["allocated_quantity"]),
                "unit_price_toman": int(row["unit_price_snapshot_toman"]),
                "amount_toman": int(row["line_total_toman"]),
            }
            for row in allocation_rows
            if row["status"] in ("ALLOCATED", "PARTIALLY_ALLOCATED")
        ]

        # Payment execution is a separate canonical order/payment capability.
        # The current order schema has no payment-method persistence field, so
        # transport accepts the documented preference without inventing storage.
        _ = preferred_payment_method

        result = self.checkout(
            basket_id=basket_id,
            plan_id=str(allocation_plan_id),
            retailer_id=retailer_id,
            idempotency_key=idempotency_key,
            address_snapshot={"address": delivery_address},
            vendor_allocations=vendor_allocations,
        )

        if result.get("idempotent_replay"):
            group = result["order_group"]
            orders = result["orders"]
            group_status = group["group_status"]
            total_amount_toman = int(group["total_amount_toman"])
            order_group_id = str(group["id"])
        else:
            order_group_id = str(result["order_group_id"])
            orders = result["orders"]
            self.cur.execute(
                """
                SELECT group_status, total_amount_toman
                FROM order_groups
                WHERE id = %s
                """,
                (order_group_id,),
            )
            group = self.cur.fetchone()
            if not group:
                raise RuntimeError("Checkout succeeded but the order group could not be loaded.")
            group_status = group["group_status"]
            total_amount_toman = int(group["total_amount_toman"])

        return {
            "order_group_id": order_group_id,
            "group_status": group_status,
            "total_amount_toman": total_amount_toman,
            "child_orders": [
                {
                    "order_id": str(order["id"]),
                    "vendor_id": str(order["vendor_id"]),
                    "order_status": order["order_status"],
                    "subtotal_toman": int(order["total_amount_toman"]),
                }
                for order in orders
            ],
            "idempotent_replay": bool(result.get("idempotent_replay", False)),
        }

    def vendor_order_accept(self, *, order_id):
        return CanonicalVendorOrderService.accept_order(
            self.cur,
            user_id=self.context.user_id,
            organization_id=self.context.organization_id,
            order_id=order_id,
        )

    def vendor_order_reject(self, *, order_id, rejection_reason):
        return CanonicalVendorOrderService.reject_order(
            self.cur,
            user_id=self.context.user_id,
            organization_id=self.context.organization_id,
            order_id=order_id,
            rejection_reason=rejection_reason,
        )

    def vendor_partial_acceptance_propose(self, *, order_id, idempotency_key, items):
        return CanonicalPartialAcceptanceService.propose(
            self.cur,
            user_id=self.context.user_id,
            organization_id=self.context.organization_id,
            order_id=order_id,
            idempotency_key=idempotency_key,
            items=items,
        )

    def retailer_partial_acceptance_approve(self, *, order_id, proposal_id):
        return CanonicalPartialAcceptanceService.approve(
            self.cur,
            user_id=self.context.user_id,
            organization_id=self.context.organization_id,
            order_id=order_id,
            proposal_id=proposal_id,
        )

    def retailer_partial_acceptance_decline(self, *, order_id, proposal_id, reason=None):
        return CanonicalPartialAcceptanceService.decline(
            self.cur,
            user_id=self.context.user_id,
            organization_id=self.context.organization_id,
            order_id=order_id,
            proposal_id=proposal_id,
            reason=reason,
        )

    # ── Order Query Methods (Stage 20) ──────────────────────────────

    def _resolve_actor_role(self):
        if not self.context.organization_id:
            raise PermissionError("Order query requires an organization context.")
        self.cur.execute(
            "SELECT role FROM organization_memberships WHERE organization_id = %s AND user_id = %s AND status = 'ACTIVE'",
            (self.context.organization_id, self.context.user_id),
        )
        row = self.cur.fetchone()
        if not row:
            raise PermissionError("User is not an active member of the organization.")
        role = row["role"] if isinstance(row, dict) else row[0]
        if role.startswith("VENDOR"):
            return "VENDOR"
        if role.startswith("RETAILER"):
            return "RETAILER"
        if role.startswith("ADMIN") or role.startswith("OPS"):
            return "ADMIN"
        raise PermissionError(f"Role {role} does not have order query access.")

    def order_list(self, *, status=None, offset=0, limit=50):
        actor_role = self._resolve_actor_role()
        params: list = []
        if actor_role == "RETAILER":
            params.append(self.context.organization_id)
            where = "o.retailer_id IN (SELECT id FROM retailers WHERE organization_id = %s)"
        elif actor_role == "VENDOR":
            params.append(self.context.organization_id)
            where = "o.vendor_id IN (SELECT id FROM vendors WHERE organization_id = %s)"
        else:
            where = "1 = 1"
        if status:
            params.append(status)
            where += f" AND o.order_status = %s"
        params.extend([limit, offset])
        self.cur.execute(
            f"""
            SELECT o.id, o.order_number, o.order_status, o.dispute_status,
                   o.total_amount_toman, o.created_at, o.updated_at,
                   o.vendor_id, o.retailer_id,
                   og.id AS order_group_id, og.group_status
            FROM orders o
            JOIN order_groups og ON og.id = o.order_group_id
            WHERE {where}
            ORDER BY o.created_at DESC
            LIMIT %s OFFSET %s
            """,
            params,
        )
        orders = [dict(r) for r in self.cur.fetchall()]
        for o in orders:
            o["id"] = str(o["id"])
            o["vendor_id"] = str(o["vendor_id"])
            o["retailer_id"] = str(o["retailer_id"])
            o["order_group_id"] = str(o["order_group_id"])
        return {"orders": orders, "limit": limit, "offset": offset}

    def order_get(self, *, order_id):
        actor_role = self._resolve_actor_role()
        self.cur.execute(
            """
            SELECT o.*, og.group_status, og.basket_id, og.total_amount_toman AS group_total_toman,
                   og.order_count AS group_order_count
            FROM orders o
            JOIN order_groups og ON og.id = o.order_group_id
            WHERE o.id = %s
            """,
            (order_id,),
        )
        order = self.cur.fetchone()
        if not order:
            raise ValueError("Order not found.")
        order = dict(order)
        if actor_role == "RETAILER":
            org_check = self.cur.execute(
                "SELECT id FROM retailers WHERE id = %s AND organization_id = %s",
                (order["retailer_id"], self.context.organization_id),
            ) or True
            self.cur.execute(
                "SELECT 1 FROM retailers WHERE id = %s AND organization_id = %s",
                (order["retailer_id"], self.context.organization_id),
            )
            if not self.cur.fetchone():
                raise PermissionError("Access denied.")
        elif actor_role == "VENDOR":
            self.cur.execute(
                "SELECT 1 FROM vendors WHERE id = %s AND organization_id = %s",
                (order["vendor_id"], self.context.organization_id),
            )
            if not self.cur.fetchone():
                raise PermissionError("Access denied.")
        order["id"] = str(order["id"])
        order["vendor_id"] = str(order["vendor_id"])
        order["retailer_id"] = str(order["retailer_id"])
        order["order_group_id"] = str(order["order_group_id"])
        order["basket_id"] = str(order.get("basket_id", ""))
        order["allocation_plan_id"] = str(order.get("allocation_plan_id", ""))
        return order

    def order_items_list(self, *, order_id):
        self.order_get(order_id=order_id)
        self.cur.execute(
            """
            SELECT id, product_id, vendor_product_id, product_name_snapshot,
                   brand_name_snapshot, vendor_sku_snapshot, packaging_unit_snapshot,
                   pack_quantity_snapshot, ordered_quantity, accepted_quantity,
                   delivered_quantity, unit_price_toman, total_line_amount_toman,
                   fulfillment_status, dispute_reason
            FROM order_items
            WHERE order_id = %s
            ORDER BY created_at ASC
            """,
            (order_id,),
        )
        items = [dict(r) for r in self.cur.fetchall()]
        for item in items:
            item["id"] = str(item["id"])
            item["product_id"] = str(item["product_id"])
            item["vendor_product_id"] = str(item["vendor_product_id"])
        return {"order_id": order_id, "items": items}

    def order_group_get(self, *, order_group_id):
        actor_role = self._resolve_actor_role()
        self.cur.execute(
            """
            SELECT og.*,
                   r.store_name AS retailer_name,
                   array_agg(DISTINCT v.business_name) AS vendor_names
            FROM order_groups og
            LEFT JOIN retailers r ON r.id = og.retailer_id
            LEFT JOIN orders o ON o.order_group_id = og.id
            LEFT JOIN vendors v ON v.id = o.vendor_id
            WHERE og.id = %s
            GROUP BY og.id, r.store_name
            """,
            (order_group_id,),
        )
        group = self.cur.fetchone()
        if not group:
            raise ValueError("Order group not found.")
        group = dict(group)
        if actor_role == "RETAILER":
            self.cur.execute(
                "SELECT 1 FROM retailers WHERE id = %s AND organization_id = %s",
                (group["retailer_id"], self.context.organization_id),
            )
            if not self.cur.fetchone():
                raise PermissionError("Access denied.")
        elif actor_role == "VENDOR":
            self.cur.execute(
                "SELECT 1 FROM orders WHERE order_group_id = %s AND vendor_id IN "
                "(SELECT id FROM vendors WHERE organization_id = %s)",
                (order_group_id, self.context.organization_id),
            )
            if not self.cur.fetchone():
                raise PermissionError("Access denied.")
        group["id"] = str(group["id"])
        group["basket_id"] = str(group.get("basket_id", ""))
        group["retailer_id"] = str(group["retailer_id"])
        group["vendor_names"] = group["vendor_names"] or []
        return group

    def order_group_child_orders(self, *, order_group_id):
        self.order_group_get(order_group_id=order_group_id)
        self.cur.execute(
            """
            SELECT o.id, o.order_number, o.order_status, o.dispute_status,
                   o.total_amount_toman, o.vendor_id, o.created_at, o.updated_at,
                   v.business_name AS vendor_name
            FROM orders o
            JOIN vendors v ON v.id = o.vendor_id
            WHERE o.order_group_id = %s
            ORDER BY o.created_at ASC
            """,
            (order_group_id,),
        )
        orders = [dict(r) for r in self.cur.fetchall()]
        for o in orders:
            o["id"] = str(o["id"])
            o["vendor_id"] = str(o["vendor_id"])
        return {"order_group_id": order_group_id, "orders": orders}

    def order_timeline(self, *, order_id):
        self.order_get(order_id=order_id)
        self.cur.execute(
            """
            SELECT id, event_type, from_status, to_status,
                   actor_user_id, actor_organization_id, event_data, created_at
            FROM order_timeline_events
            WHERE order_id = %s
            ORDER BY created_at ASC
            """,
            (order_id,),
        )
        events = [dict(r) for r in self.cur.fetchall()]
        for ev in events:
            ev["id"] = str(ev["id"])
            ev["actor_user_id"] = str(ev["actor_user_id"]) if ev["actor_user_id"] else None
            ev["actor_organization_id"] = str(ev["actor_organization_id"]) if ev["actor_organization_id"] else None
        return {"order_id": order_id, "events": events}

    # ── Fulfillment Methods (Stage 22) ─────────────────────────────

    def vendor_mark_preparing(self, *, order_id):
        return _mark_preparing(
            self.cur,
            user_id=self.context.user_id,
            organization_id=self.context.organization_id,
            order_id=order_id,
        )

    def vendor_mark_ready(self, *, order_id):
        return _mark_ready(
            self.cur,
            user_id=self.context.user_id,
            organization_id=self.context.organization_id,
            order_id=order_id,
        )

    def vendor_dispatch_order(self, *, order_id, driver_name=None, vehicle_plate=None, driver_phone=None):
        return _dispatch_order(
            self.cur,
            user_id=self.context.user_id,
            organization_id=self.context.organization_id,
            order_id=order_id,
            driver_name=driver_name,
            vehicle_plate=vehicle_plate,
            driver_phone=driver_phone,
        )

    def vendor_delivery_stage(self, *, order_id, target_status, reason=None):
        return _transition_delivery_stage(
            self.cur,
            user_id=self.context.user_id,
            organization_id=self.context.organization_id,
            order_id=order_id,
            target_status=target_status,
            reason=reason,
        )

    def retailer_confirm_delivery(self, *, order_id, recipient_name=None,
                                    otp_code=None, proof_type="OTP_CODE",
                                    proof_media_id=None, issue_reported=None):
        return _confirm_delivery(
            self.cur,
            user_id=self.context.user_id,
            organization_id=self.context.organization_id,
            order_id=order_id,
            recipient_name=recipient_name,
            otp_code=otp_code,
            proof_type=proof_type,
            proof_media_id=proof_media_id,
            issue_reported=issue_reported,
        )

    # ── Delivery Tracking Methods (Stage 23) ───────────────────────

    def delivery_get(self, *, order_id):
        self.order_get(order_id=order_id)
        self.cur.execute(
            """
            SELECT d.id, d.order_id, d.vendor_id, d.delivery_status, d.driver_name,
                   d.vehicle_plate, d.driver_phone, d.dispatched_at, d.delivered_at, d.created_at
            FROM deliveries d
            WHERE d.order_id = %s
            ORDER BY d.created_at DESC LIMIT 1
            """,
            (order_id,),
        )
        delivery = self.cur.fetchone()
        if not delivery:
            raise ValueError("No delivery record found for this order.")
        delivery = dict(delivery)
        delivery["id"] = str(delivery["id"])
        delivery["order_id"] = str(delivery["order_id"])
        delivery["vendor_id"] = str(delivery["vendor_id"])
        return delivery

    def delivery_proof(self, *, order_id):
        self.order_get(order_id=order_id)
        self.cur.execute(
            """
            SELECT pod.id, pod.delivery_id, pod.accepted_by_name, pod.accepted_at,
                   pod.otp_verified, pod.issue_reported_at_delivery
            FROM proof_of_delivery pod
            JOIN deliveries d ON d.id = pod.delivery_id
            WHERE d.order_id = %s
            ORDER BY pod.accepted_at DESC LIMIT 1
            """,
            (order_id,),
        )
        proof = self.cur.fetchone()
        if not proof:
            return None
        proof = dict(proof)
        proof["id"] = str(proof["id"])
        proof["delivery_id"] = str(proof["delivery_id"])
        return proof

    # ── Delivery Exception Methods (Stage 25) ──────────────────────

    def report_delivery_exception(self, *, delivery_id, order_id,
                                   exception_type, description=None):
        from scripts.delivery_exceptions import report_delivery_exception as _report
        return _report(
            self.cur,
            user_id=self.context.user_id,
            organization_id=self.context.organization_id,
            delivery_id=delivery_id,
            order_id=order_id,
            exception_type=exception_type,
            description=description,
        )

    def resolve_delivery_exception(self, *, exception_id,
                                    resolution_type, resolution_note=None):
        from scripts.delivery_exceptions import resolve_delivery_exception as _resolve
        return _resolve(
            self.cur,
            user_id=self.context.user_id,
            organization_id=self.context.organization_id,
            exception_id=exception_id,
            resolution_type=resolution_type,
            resolution_note=resolution_note,
        )

    def escalate_delivery_exception(self, *, exception_id, reason=None):
        from scripts.delivery_exceptions import escalate_delivery_exception as _escalate
        return _escalate(
            self.cur,
            user_id=self.context.user_id,
            organization_id=self.context.organization_id,
            exception_id=exception_id,
            reason=reason,
        )

    def delivery_exceptions_list(self, *, order_id=None, delivery_id=None,
                                  status=None, offset=0, limit=50):
        from scripts.delivery_exceptions import list_delivery_exceptions as _list
        return _list(
            self.cur,
            order_id=order_id,
            delivery_id=delivery_id,
            status=status,
            offset=offset,
            limit=limit,
        )

    def delivery_exception_get(self, *, exception_id):
        from scripts.delivery_exceptions import get_delivery_exception as _get
        result = _get(self.cur, exception_id=exception_id)
        if not result:
            raise ValueError("Delivery exception not found.")
        return result

    def feedback_list(self):
        if not self.context.organization_id:
            raise PermissionError("Feedback query requires an organization context.")
        return CanonicalFeedbackService.list_for_user(self.cur, self.context.user_id, self.context.organization_id)

    def feedback_admin_inbox(self, *, organization_id, status=None, priority=None):
        return CanonicalFeedbackService.list_for_admin(
            self.cur, self.context.user_id, organization_id, status=status, priority=priority
        )

    def feedback_reply(self, *, feedback_id, reply_text, next_status="IN_REVIEW"):
        return CanonicalFeedbackService.reply(
            self.cur, self.context.user_id, feedback_id, reply_text, next_status=next_status
        )

    def support_create(self, *, organization_id, case_type, subject, related_order_id=None, priority="NORMAL"):
        if self.context.organization_id != str(organization_id):
            raise PermissionError("Support target organization must match the active tenant context.")
        return CanonicalSupportService.create_case(
            self.cur, self.context.user_id, organization_id, case_type,
            subject, related_order_id=related_order_id, priority=priority
        )

    def support_list(self):
        if not self.context.organization_id:
            raise PermissionError("Support case listing requires an organization context.")
        return CanonicalSupportService.list_cases(
            self.cur, self.context.user_id, self.context.organization_id
        )

    def support_get(self, *, case_id):
        return CanonicalSupportService.get_case(self.cur, self.context.user_id, case_id)

    def support_message(self, *, case_id, message_text, internal=False):
        return CanonicalSupportService.add_message(
            self.cur, self.context.user_id, case_id, message_text, internal=internal
        )

    def support_assign(self, *, case_id, assignee_user_id):
        return CanonicalSupportService.assign(self.cur, self.context.user_id, case_id, assignee_user_id)

    def support_transition(self, *, case_id, target_status, resolution_code=None, resolution_note=None):
        return CanonicalSupportService.transition(
            self.cur, self.context.user_id, case_id, target_status,
            resolution_code=resolution_code, resolution_note=resolution_note
        )

    def create_vendor_referral(self, *, vendor_id, max_redemptions=None, expires_at=None):
        return VendorReferralService.create_referral(
            self.cur, self.context.user_id, vendor_id,
            max_redemptions=max_redemptions, expires_at=expires_at
        )

    def redeem_vendor_referral(self, *, retailer_id, referral_code, request_idempotency_key):
        if self.context.organization_id is None:
            raise PermissionError("Referral redemption requires an organization context.")
        self._verify_retailer_actor(retailer_id)
        return VendorReferralService.redeem_referral(
            self.cur, self.context.user_id, retailer_id,
            referral_code, request_idempotency_key
        )

    def return_request(self, *, order_id, order_items, reason, idempotency_key, claimed_refund_amount_toman):
        return CanonicalReturnService.request_return(
            self.cur, self.context.user_id, order_id, order_items,
            reason, idempotency_key, claimed_refund_amount_toman,
            organization_id=self.context.organization_id,
        )

    def return_transition(self, *, return_id, target_status, reason=None, approved_refund_amount_toman=None):
        return CanonicalReturnService.transition(
            self.cur, self.context.user_id, return_id, target_status,
            reason=reason, approved_refund_amount_toman=approved_refund_amount_toman,
            organization_id=self.context.organization_id,
        )

    def return_get(self, *, return_id):
        if not self.context.organization_id:
            raise PermissionError("Return query requires an organization context.")
        self.cur.execute(
            "SELECT * FROM returns WHERE id = %s", (return_id,)
        )
        ret = self.cur.fetchone()
        if not ret:
            raise KeyError("Return not found.")
        ret = dict(ret)
        self.cur.execute(
            "SELECT id FROM retailers WHERE id = %s AND organization_id = %s",
            (ret["retailer_id"], self.context.organization_id),
        )
        if not self.cur.fetchone():
            self.cur.execute(
                "SELECT id FROM vendors WHERE id = %s AND organization_id = %s",
                (ret["vendor_id"], self.context.organization_id),
            )
            if not self.cur.fetchone():
                raise PermissionError("Access denied.")
        self.cur.execute(
            "SELECT * FROM return_items WHERE return_id = %s", (return_id,)
        )
        ret["items"] = [dict(i) for i in self.cur.fetchall()]
        return ret

    def returns_list(self, *, order_id):
        if not self.context.organization_id:
            raise PermissionError("Return query requires an organization context.")
        self.cur.execute(
            "SELECT * FROM returns WHERE order_id = %s ORDER BY created_at DESC",
            (order_id,),
        )
        returns = [dict(r) for r in self.cur.fetchall()]
        filtered = []
        for ret in returns:
            self.cur.execute(
                "SELECT id FROM retailers WHERE id = %s AND organization_id = %s",
                (ret["retailer_id"], self.context.organization_id),
            )
            if self.cur.fetchone():
                filtered.append(ret)
                continue
            self.cur.execute(
                "SELECT id FROM vendors WHERE id = %s AND organization_id = %s",
                (ret["vendor_id"], self.context.organization_id),
            )
            if self.cur.fetchone():
                filtered.append(ret)
        return {"returns": filtered, "count": len(filtered)}

    def dispute_open(self, *, order_id, claimed_amount_toman, description, evidence_media_id=None):
        if not self.context.organization_id:
            raise PermissionError("Dispute open requires an organization context.")

        # Client-facing dispute creation uses the same canonical domain service
        # as the master E2E so settlement, filing-window and outbox rules cannot diverge.
        from scripts.domain_services import DisputeService

        self.cur.execute(
            """
            SELECT o.retailer_id, o.vendor_id, s.id AS settlement_id
            FROM orders o
            JOIN settlements s ON s.order_id=o.id
            JOIN retailers r ON r.id=o.retailer_id
            WHERE o.id=%s
              AND r.organization_id=%s
              AND s.status <> 'DISPUTED'
            ORDER BY s.created_at DESC
            LIMIT 1
            """,
            (order_id, self.context.organization_id),
        )
        context = self.cur.fetchone()
        if not context:
            raise ValueError("No eligible settlement found for this retailer order.")

        disp_id = DisputeService.open_dispute(
            self.cur,
            str(order_id),
            str(context["retailer_id"]),
            str(context["vendor_id"]),
            str(context["settlement_id"]),
            int(claimed_amount_toman),
            description,
        )

        if evidence_media_id:
            self.cur.execute(
                """
                SELECT id
                FROM media_assets
                WHERE id=%s
                  AND uploaded_by_user_id=%s
                  AND status='READY'
                """,
                (evidence_media_id, self.context.user_id),
            )
            if not self.cur.fetchone():
                raise PermissionError("Evidence media must be a READY asset owned by the current user.")
            self.cur.execute(
                "UPDATE disputes SET evidence_media_id=%s WHERE id=%s",
                (evidence_media_id, disp_id),
            )

        self.cur.execute("SELECT * FROM disputes WHERE id=%s", (disp_id,))
        return dict(self.cur.fetchone())

    def dispute_get(self, *, dispute_id):
        if not self.context.organization_id:
            raise PermissionError("Dispute query requires an organization context.")
        self.cur.execute(
            "SELECT * FROM disputes WHERE id = %s", (dispute_id,)
        )
        disp = self.cur.fetchone()
        if not disp:
            raise KeyError("Dispute not found.")
        disp = dict(disp)
        self.cur.execute(
            "SELECT id FROM retailers WHERE id = %s AND organization_id = %s",
            (disp["retailer_id"], self.context.organization_id),
        )
        if not self.cur.fetchone():
            self.cur.execute(
                "SELECT id FROM vendors WHERE id = %s AND organization_id = %s",
                (disp["vendor_id"], self.context.organization_id),
            )
            if not self.cur.fetchone():
                raise PermissionError("Access denied.")
        return disp

    def disputes_list(self, *, order_id):
        if not self.context.organization_id:
            raise PermissionError("Dispute query requires an organization context.")
        self.cur.execute(
            "SELECT * FROM disputes WHERE order_id = %s ORDER BY opened_at DESC",
            (order_id,),
        )
        disputes = [dict(d) for d in self.cur.fetchall()]
        filtered = []
        for disp in disputes:
            self.cur.execute(
                "SELECT id FROM retailers WHERE id = %s AND organization_id = %s",
                (disp["retailer_id"], self.context.organization_id),
            )
            if self.cur.fetchone():
                filtered.append(disp)
                continue
            self.cur.execute(
                "SELECT id FROM vendors WHERE id = %s AND organization_id = %s",
                (disp["vendor_id"], self.context.organization_id),
            )
            if self.cur.fetchone():
                filtered.append(disp)
        return {"disputes": filtered, "count": len(filtered)}

    def process_vendor_acceptance_timeouts(self, *, limit=100):
        self._require_ops_context()
        return VendorAcceptanceTimeoutWorker.process_expired(self.cur, limit=limit)

    def reconcile_payments(self, *, limit=50):
        self._require_ops_context()
        return PaymentReconciliationWorker.process_pending(self.cur, limit=limit)

    # ── Reconciliation Exception Management (Stage 29) ──────────────

    def reconciliation_cases_list(self, *, status=None, offset=0, limit=50):
        self._require_ops_context()
        params: list = []
        where = ""
        if status:
            where = "WHERE c.status = %s"
            params.append(status)
        self.cur.execute(
            f"""
            SELECT c.id, c.payment_id, c.status, c.expected_amount_toman,
                   c.observed_amount_toman, c.external_reference,
                   c.resolution_reason, c.resolved_by_user_id,
                   c.opened_at, c.resolved_at, c.attempt_count
            FROM payment_reconciliation_cases c
            {where}
            ORDER BY c.opened_at DESC
            LIMIT %s OFFSET %s
            """,
            (*params, limit, offset),
        )
        rows = self.cur.fetchall()
        return [
            {k: str(v) if hasattr(v, 'hex') else v for k, v in dict(row).items()}
            for row in rows
        ]

    def reconciliation_case_get(self, *, case_id):
        self._require_ops_context()
        self.cur.execute(
            """
            SELECT c.id, c.payment_id, c.status, c.expected_amount_toman,
                   c.observed_amount_toman, c.external_reference,
                   c.resolution_reason, c.resolved_by_user_id,
                   c.opened_at, c.resolved_at, c.attempt_count
            FROM payment_reconciliation_cases c
            WHERE c.id = %s
            """,
            (case_id,),
        )
        row = self.cur.fetchone()
        if not row:
            raise KeyError(f"Reconciliation case {case_id} not found.")
        return {k: str(v) if hasattr(v, 'hex') else v for k, v in dict(row).items()}

    def reconciliation_case_resolve(self, *, case_id, resolution_note=None):
        self._require_ops_context()
        self.cur.execute(
            "SELECT id, status FROM payment_reconciliation_cases WHERE id = %s",
            (case_id,),
        )
        row = self.cur.fetchone()
        if not row:
            raise KeyError(f"Reconciliation case {case_id} not found.")
        case = dict(row)
        if case["status"] in ("RESOLVED", "CANCELLED"):
            raise ValueError(f"Cannot resolve case in '{case['status']}' status.")
        resolved_status = "MATCHED" if case["status"] in ("OPEN", "MISMATCH", "PARTIALLY_MATCHED") else "RESOLVED"
        self.cur.execute(
            """
            UPDATE payment_reconciliation_cases
            SET status = %s,
                resolved_at = now(),
                resolved_by_user_id = %s,
                resolution_reason = COALESCE(%s, resolution_reason)
            WHERE id = %s
            RETURNING id, payment_id, status, expected_amount_toman,
                      observed_amount_toman, external_reference,
                      resolution_reason, resolved_by_user_id,
                      opened_at, resolved_at, attempt_count
            """,
            (resolved_status, self.context.user_id, resolution_note, case_id),
        )
        updated = self.cur.fetchone()
        return {k: str(v) if hasattr(v, 'hex') else v for k, v in dict(updated).items()}

    # ── Payment Evidence (Stage 27) ─────────────────────────────────

    VALID_EVIDENCE_TYPES = frozenset({
        "BANK_REFERENCE", "POS_REFERENCE", "RECEIPT_IMAGE",
        "VENDOR_CONFIRMATION", "RETAILER_CONFIRMATION",
    })

    def submit_payment_evidence(self, *, order_id, evidence_type, reference_number, amount_toman, notes=None):
        if evidence_type not in self.VALID_EVIDENCE_TYPES:
            raise ValueError(
                f"Invalid evidence_type '{evidence_type}'. "
                f"Must be one of: {', '.join(sorted(self.VALID_EVIDENCE_TYPES))}"
            )
        if not self.context.organization_id:
            raise PermissionError("Payment evidence requires an active organization context.")

        # Locate the order and its payment
        self.cur.execute(
            """
            SELECT o.id AS order_id, o.retailer_id, o.vendor_id,
                   p.id AS payment_id, p.payment_status, p.retailer_id AS pay_retailer_id,
                   p.vendor_id AS pay_vendor_id
            FROM orders o
            JOIN payments p ON p.order_id = o.id
            WHERE o.id = %s
            LIMIT 1
            """,
            (order_id,),
        )
        row = self.cur.fetchone()
        if not row:
            raise ValueError(f"Order {order_id} not found or has no payment.")

        # Tenant check: actor must belong to the retailer or vendor org of this order
        pay_retailer_id = str(row["pay_retailer_id"])
        pay_vendor_id = str(row["pay_vendor_id"])
        actor_org = self.context.organization_id

        self.cur.execute(
            """
            SELECT 1
            FROM organization_memberships om
            JOIN organizations o ON o.id = om.organization_id
            WHERE om.user_id = %s
              AND om.organization_id = %s
              AND om.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
              AND (
                  (om.role IN ('RETAILER_OWNER','RETAILER_STAFF')
                   AND EXISTS (SELECT 1 FROM retailers r WHERE r.id = %s AND r.organization_id = %s))
                  OR
                  (om.role IN ('VENDOR_OWNER','VENDOR_STAFF')
                   AND EXISTS (SELECT 1 FROM vendors v WHERE v.id = %s AND v.organization_id = %s))
              )
            LIMIT 1
            """,
            (self.context.user_id, actor_org,
             pay_retailer_id, actor_org,
             pay_vendor_id, actor_org),
        )
        if not self.cur.fetchone():
            raise PermissionError("Actor is not an authorized member of this order's retailer or vendor tenant.")

        evidence_id = str(uuid4())
        self.cur.execute(
            """
            INSERT INTO payment_evidence (
                id, payment_id, evidence_type, external_reference,
                claimed_amount_toman, observed_amount_toman,
                captured_by_user_id, observation_scope, metadata
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s,
                %s, 'SINGLE_PAYMENT', %s
            ) RETURNING *;
            """,
            (
                evidence_id, str(row["payment_id"]), evidence_type, reference_number,
                amount_toman, amount_toman,
                self.context.user_id,
                Json({"notes": notes} if notes else {}),
            ),
        )
        ev = self.cur.fetchone()
        return {
            "evidence_id": str(ev["id"]),
            "payment_id": str(ev["payment_id"]),
            "evidence_type": ev["evidence_type"],
            "reference_number": ev["external_reference"],
            "amount_toman": int(ev["claimed_amount_toman"]),
            "captured_at": ev["captured_at"].isoformat() if ev["captured_at"] else None,
        }

    def get_payment_evidence(self, *, order_id):
        if not self.context.organization_id:
            raise PermissionError("Payment evidence requires an active organization context.")

        self.cur.execute(
            """
            SELECT p.id AS payment_id
            FROM payments p
            WHERE p.order_id = %s
            LIMIT 1
            """,
            (order_id,),
        )
        pay = self.cur.fetchone()
        if not pay:
            raise ValueError(f"Order {order_id} has no payment record.")

        self.cur.execute(
            """
            SELECT pe.id, pe.evidence_type, pe.external_reference,
                   pe.claimed_amount_toman, pe.observed_amount_toman,
                   pe.captured_at, pe.captured_by_user_id, pe.observation_scope,
                   pe.metadata
            FROM payment_evidence pe
            WHERE pe.payment_id = %s
            ORDER BY pe.captured_at ASC
            """,
            (str(pay["payment_id"]),),
        )
        rows = self.cur.fetchall()
        return [
            {
                "evidence_id": str(r["id"]),
                "evidence_type": r["evidence_type"],
                "reference_number": r["external_reference"],
                "amount_toman": int(r["claimed_amount_toman"]) if r["claimed_amount_toman"] is not None else None,
                "captured_at": r["captured_at"].isoformat() if r["captured_at"] else None,
                "observation_scope": r["observation_scope"],
            }
            for r in rows
        ]

    def verify_payment(self, *, order_id, notes=None):
        if not self.context.organization_id:
            raise PermissionError("Payment verification requires an active organization context.")

        self.cur.execute(
            """
            SELECT p.*, v.organization_id AS vendor_org_id,
                   r.organization_id AS retailer_org_id
            FROM payments p
            JOIN vendors v ON v.id=p.vendor_id
            JOIN retailers r ON r.id=p.retailer_id
            WHERE p.order_id=%s
            ORDER BY p.created_at DESC, p.id DESC
            LIMIT 1
            FOR UPDATE OF p
            """,
            (order_id,),
        )
        pay = self.cur.fetchone()
        if not pay:
            raise ValueError(f"Order {order_id} has no payment record.")

        if str(pay["vendor_org_id"]) != self.context.organization_id:
            raise PermissionError("Only the vendor tenant may verify a payment.")

        if pay["payment_status"] == "SUCCESS":
            return {
                "payment_id": str(pay["id"]),
                "status": "SUCCESS",
                "message": "Payment already verified.",
                "idempotent_replay": True,
            }

        self.cur.execute(
            """
            SELECT id, evidence_type, external_reference,
                   claimed_amount_toman, observed_amount_toman,
                   captured_at
            FROM payment_evidence
            WHERE payment_id=%s
            ORDER BY captured_at DESC, id DESC
            FOR UPDATE
            """,
            (str(pay["id"]),),
        )
        evidences = self.cur.fetchall()
        matching = [
            ev for ev in evidences
            if ev["claimed_amount_toman"] is not None
            and ev["observed_amount_toman"] is not None
            and int(ev["claimed_amount_toman"]) == int(pay["amount_toman"])
            and int(ev["observed_amount_toman"]) == int(pay["amount_toman"])
        ]
        if not matching:
            raise ValueError(
                "Payment verification requires a trusted evidence record whose observed and claimed amount exactly matches the payment amount."
            )
        evidence = matching[0]

        cur_ref = evidence["external_reference"]
        self.cur.execute(
            """
            UPDATE payments
            SET payment_status='SUCCESS',
                reference_number=COALESCE(reference_number,%s),
                verified_by=%s,
                verified_at=COALESCE(verified_at,now()),
                paid_at=COALESCE(paid_at,now())
            WHERE id=%s AND payment_status IN ('PENDING','INITIATED')
            RETURNING *
            """,
            (cur_ref, self.context.user_id, str(pay["id"])),
        )
        updated = self.cur.fetchone()
        if not updated:
            # Another verifier committed the terminal result; return the canonical replay.
            self.cur.execute("SELECT * FROM payments WHERE id=%s", (str(pay["id"]),))
            replay = self.cur.fetchone()
            if replay and replay["payment_status"] == "SUCCESS":
                return {
                    "payment_id": str(replay["id"]),
                    "status": "SUCCESS",
                    "message": "Payment already verified.",
                    "idempotent_replay": True,
                }
            raise ValueError("Payment cannot be verified in its current status.")

        gross = int(updated["amount_toman"])
        commission = int(round(gross * float(PILOT_COMMISSION_RATE)))

        self.cur.execute(
            """
            SELECT id, status
            FROM settlements
            WHERE order_id=%s AND vendor_id=%s
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            FOR UPDATE
            """,
            (str(updated["order_id"]), str(updated["vendor_id"])),
        )
        settlement = self.cur.fetchone()
        if settlement is None:
            self.cur.execute(
                """
                INSERT INTO settlements (
                    id, order_id, vendor_id, gross_amount_toman,
                    commission_rate, commission_amount_toman,
                    net_vendor_amount_toman, status
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,'CALCULATED')
                RETURNING id, status
                """,
                (
                    str(uuid4()), str(updated["order_id"]), str(updated["vendor_id"]),
                    gross, PILOT_COMMISSION_RATE, commission, gross - commission,
                ),
            )
            settlement = self.cur.fetchone()
        elif settlement["status"] == "PENDING":
            self.cur.execute(
                """
                UPDATE settlements
                SET status='CALCULATED'
                WHERE id=%s
                RETURNING id, status
                """,
                (str(settlement["id"]),),
            )
            settlement = self.cur.fetchone()

        # Invoice creation remains governed by the open invoice-timing decision.
        # When an invoice already exists and exactly matches the payment amount,
        # mark it paid as part of this verification transaction.
        self.cur.execute(
            """
            UPDATE invoices
            SET status='PAID'
            WHERE order_id=%s
              AND total_amount=%s
              AND status IN ('ISSUED','ADJUSTED')
            RETURNING id
            """,
            (str(updated["order_id"]), gross),
        )

        self.cur.execute(
            """
            INSERT INTO outbox_events (
                id, event_id, event_name, aggregate_type, aggregate_id,
                payload, status, target_user_id, target_organization_id,
                dedupe_key, channel_hint
            )
            SELECT
                gen_random_uuid(), gen_random_uuid(), 'PAYMENT_VERIFIED', 'PAYMENT', %s,
                jsonb_build_object(
                    'payment_id', %s,
                    'order_id', %s,
                    'amount_toman', %s,
                    'evidence_id', %s
                ),
                'PENDING', om.user_id, om.organization_id,
                %s, 'INBOX'
            FROM organization_memberships om
            JOIN organizations org ON org.id=om.organization_id
            WHERE om.organization_id=%s
              AND om.status='ACTIVE'
              AND org.status='ACTIVE'
              AND om.role IN ('RETAILER_OWNER','RETAILER_STAFF')
            ON CONFLICT (event_name,dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING
            """,
            (
                str(updated["id"]), str(updated["id"]), str(updated["order_id"]),
                gross, str(evidence["id"]),
                f"payment_verified:{updated['id']}",
                str(pay["retailer_org_id"]),
            ),
        )

        return {
            "payment_id": str(updated["id"]),
            "status": "SUCCESS",
            "verified_at": updated["verified_at"].isoformat() if updated["verified_at"] else None,
            "evidence_id": str(evidence["id"]),
            "settlement_id": str(settlement["id"]) if settlement else None,
            "idempotent_replay": False,
        }


    def deliver_external_notifications(self, *, limit=100):
        self._require_ops_context()
        return ProviderDeliveryWorker.process_pending(self.cur, limit=limit)

    # ── Invoice / Settlement Read Model (Stage 28) ─────────────────

    def invoices_list(self, *, offset=0, limit=50):
        actor_role = self._resolve_actor_role()
        params: list = []
        if actor_role == "RETAILER":
            params.append(self.context.organization_id)
            where = "i.retailer_organization_id = %s"
        elif actor_role == "VENDOR":
            params.append(self.context.organization_id)
            where = "i.vendor_organization_id = %s"
        else:
            params.append(self.context.organization_id)
            where = "(i.retailer_organization_id = %s OR i.vendor_organization_id = %s)"
            params.append(self.context.organization_id)
        params.extend([limit, offset])
        self.cur.execute(
            f"""
            SELECT i.id, i.invoice_number, i.order_id, i.total_amount,
                   i.currency, i.status, i.issued_at, i.created_at,
                   i.retailer_organization_id, i.vendor_organization_id
            FROM invoices i
            WHERE {where}
            ORDER BY i.created_at DESC
            LIMIT %s OFFSET %s
            """,
            params,
        )
        invoices = [dict(r) for r in self.cur.fetchall()]
        for inv in invoices:
            inv["id"] = str(inv["id"])
            inv["order_id"] = str(inv["order_id"])
            inv["retailer_organization_id"] = str(inv["retailer_organization_id"])
            inv["vendor_organization_id"] = str(inv["vendor_organization_id"])
        return {"invoices": invoices, "limit": limit, "offset": offset}

    def invoice_get(self, *, invoice_id):
        actor_role = self._resolve_actor_role()
        self.cur.execute(
            "SELECT * FROM invoices WHERE id = %s",
            (invoice_id,),
        )
        inv = self.cur.fetchone()
        if not inv:
            raise KeyError("Invoice not found.")
        inv = dict(inv)
        if actor_role == "RETAILER":
            if str(inv["retailer_organization_id"]) != self.context.organization_id:
                raise PermissionError("Access denied.")
        elif actor_role == "VENDOR":
            if str(inv["vendor_organization_id"]) != self.context.organization_id:
                raise PermissionError("Access denied.")
        inv["id"] = str(inv["id"])
        inv["order_id"] = str(inv["order_id"])
        inv["retailer_organization_id"] = str(inv["retailer_organization_id"])
        inv["vendor_organization_id"] = str(inv["vendor_organization_id"])
        self.cur.execute(
            "SELECT id, invoice_id, order_item_id, product_name, quantity, unit_price, total_line_amount "
            "FROM invoice_items WHERE invoice_id = %s ORDER BY id",
            (invoice_id,),
        )
        inv["items"] = []
        for item in self.cur.fetchall():
            item = dict(item)
            item["id"] = str(item["id"])
            item["invoice_id"] = str(item["invoice_id"])
            if item["order_item_id"] is not None:
                item["order_item_id"] = str(item["order_item_id"])
            inv["items"].append(item)
        return inv

    def invoice_by_order(self, *, order_id):
        self.order_get(order_id=order_id)
        self.cur.execute(
            "SELECT id FROM invoices WHERE order_id = %s LIMIT 1",
            (order_id,),
        )
        inv_row = self.cur.fetchone()
        if not inv_row:
            raise KeyError("No invoice found for this order.")
        return self.invoice_get(invoice_id=str(inv_row["id"]))

    def settlements_list(self, *, offset=0, limit=50):
        actor_role = self._resolve_actor_role()
        if actor_role != "VENDOR":
            raise PermissionError("Settlement listing is restricted to vendor tenants.")
        params = [self.context.organization_id, limit, offset]
        self.cur.execute(
            """
            SELECT s.id, s.order_id, s.vendor_id, s.gross_amount_toman,
                   s.commission_rate, s.commission_amount_toman,
                   s.adjustment_amount_toman, s.net_vendor_amount_toman,
                   s.status, s.settled_at, s.settlement_batch_id, s.created_at
            FROM settlements s
            JOIN vendors v ON v.id = s.vendor_id
            WHERE v.organization_id = %s
            ORDER BY s.created_at DESC
            LIMIT %s OFFSET %s
            """,
            params,
        )
        settlements = [dict(r) for r in self.cur.fetchall()]
        for s in settlements:
            s["id"] = str(s["id"])
            s["order_id"] = str(s["order_id"])
            s["vendor_id"] = str(s["vendor_id"])
        return {"settlements": settlements, "limit": limit, "offset": offset}

    def settlement_get(self, *, settlement_id):
        actor_role = self._resolve_actor_role()
        if actor_role != "VENDOR":
            raise PermissionError("Settlement detail is restricted to vendor tenants.")
        self.cur.execute(
            """
            SELECT s.* FROM settlements s
            JOIN vendors v ON v.id = s.vendor_id
            WHERE s.id = %s AND v.organization_id = %s
            """,
            (settlement_id, self.context.organization_id),
        )
        st = self.cur.fetchone()
        if not st:
            raise KeyError("Settlement not found.")
        st = dict(st)
        st["id"] = str(st["id"])
        st["order_id"] = str(st["order_id"])
        st["vendor_id"] = str(st["vendor_id"])
        self.cur.execute(
            "SELECT id, settlement_id, dispute_id, adjustment_type, amount_toman, reason, created_at "
            "FROM settlement_adjustments WHERE settlement_id = %s ORDER BY created_at",
            (settlement_id,),
        )
        st["adjustments"] = []
        for adj in self.cur.fetchall():
            adj = dict(adj)
            adj["id"] = str(adj["id"])
            adj["settlement_id"] = str(adj["settlement_id"])
            if adj["dispute_id"] is not None:
                adj["dispute_id"] = str(adj["dispute_id"])
            st["adjustments"].append(adj)
        return st

    def _verify_retailer_actor(self, retailer_id):
        self.cur.execute(
            """
            SELECT 1
            FROM retailers r
            JOIN organization_memberships om ON om.organization_id = r.organization_id
            JOIN organizations o ON o.id = r.organization_id
            WHERE r.id = %s
              AND om.user_id = %s
              AND om.organization_id = %s
              AND om.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
              AND om.role IN ('RETAILER_OWNER','RETAILER_STAFF')
            LIMIT 1
            """,
            (retailer_id, self.context.user_id, self.context.organization_id),
        )
        if not self.cur.fetchone():
            raise PermissionError("Actor is not an active member of the retailer tenant.")

    def _require_ops_context(self):
        if not self.context.organization_id:
            raise PermissionError("Operational workers require an active organization context.")
        self.cur.execute(
            """
            SELECT 1
            FROM organization_memberships om
            JOIN organizations o ON o.id = om.organization_id
            WHERE om.user_id = %s
              AND om.organization_id = %s
              AND om.status = 'ACTIVE'
              AND om.role IN ('ADMIN_SUPER','OPS_AGENT','SUPER_ADMIN','OPS_ADMIN')
              AND o.org_type = 'OPERATOR'
              AND o.status = 'ACTIVE'
            LIMIT 1;
            """,
            (self.context.user_id, self.context.organization_id),
        )
        if not self.cur.fetchone():
            raise PermissionError("Only active operator staff may execute operational workers.")

    def catalog_search(self, query: str, category_id: str | None = None, limit: int = 20):
        self.cur.execute(
            """
            SELECT p.id, p.master_sku, p.canonical_name_fa, p.base_unit,
                   p.default_pack_unit, p.default_pack_quantity,
                   b.name_fa AS brand_name, c.name_fa AS category_name,
                   sc.name_fa AS subcategory_name,
                   COALESCE(
                       similarity(p.canonical_name_fa, %s), 0
                   ) AS relevance
            FROM products p
            JOIN brands b ON b.id = p.brand_id
            JOIN categories c ON c.id = p.category_id
            JOIN subcategories sc ON sc.id = p.subcategory_id
            WHERE p.is_active = TRUE
              AND (
                  p.canonical_name_fa ILIKE %s
                  OR b.name_fa ILIKE %s
                  OR p.master_sku ILIKE %s
                  OR similarity(p.canonical_name_fa, %s) > 0.15
              )
              AND (%s::uuid IS NULL OR p.category_id = %s::uuid)
            ORDER BY relevance DESC, p.canonical_name_fa
            LIMIT %s
            """,
            (query, f"%{query}%", f"%{query}%", f"%{query}%", query, category_id, category_id, limit),
        )
        return self.cur.fetchall()

    def catalog_match_barcode(self, *, raw_barcode: str, scan_source: str):
        normalized = raw_barcode.strip()
        if not normalized:
            raise ValueError("Barcode is required.")
        self.cur.execute(
            """
            SELECT p.id, p.master_sku, p.canonical_name_fa,
                   b.name_fa AS brand_name, p.default_pack_quantity, ma.storage_key AS image_url
            FROM product_identifiers pi
            JOIN products p ON p.id = pi.product_id AND p.is_active = TRUE
            JOIN brands b ON b.id = p.brand_id
            LEFT JOIN LATERAL (
                SELECT ma.storage_key
                FROM product_media pm
                JOIN media_assets ma ON ma.id = pm.media_asset_id AND ma.status = 'READY'
                WHERE pm.product_id = p.id
                ORDER BY pm.is_primary DESC, pm.display_order, pm.created_at
                LIMIT 1
            ) ma ON TRUE
            LEFT JOIN vendors v ON v.id = pi.vendor_id
            WHERE pi.identifier_value = %s
              AND (pi.vendor_id IS NULL OR v.organization_id = %s::uuid)
            ORDER BY pi.vendor_id NULLS FIRST, pi.is_primary DESC
            LIMIT 1
            """,
            (normalized, self.context.organization_id),
        )
        row = self.cur.fetchone()
        if not row:
            return {
                "match_status": "NO_MATCH",
                "confidence_score": 0.0,
                "suggested_action": "CREATE_PRODUCT_CANDIDATE",
            }
        result = dict(row)
        result["id"] = str(result["id"])
        return {
            "match_status": "EXACT",
            "confidence_score": 1.0,
            "product": {
                "id": result["id"],
                "master_sku": result["master_sku"],
                "canonical_name_fa": result["canonical_name_fa"],
                "brand_name": result["brand_name"],
                "default_pack_quantity": result["default_pack_quantity"],
                "image_url": result.get("image_url"),
            },
        }

    def catalog_create_product_candidate(self, *, proposed_title: str, proposed_brand: str | None, barcode: str | None, vendor_sku: str | None, photo_asset_id: str | None):
        if not self.context.organization_id:
            raise PermissionError("Candidate creation requires an active organization context.")
        self.cur.execute(
            "SELECT id, user_id FROM vendors WHERE organization_id = %s::uuid AND status = 'ACTIVE' LIMIT 1",
            (self.context.organization_id,),
        )
        vendor = self.cur.fetchone()
        if not vendor:
            raise PermissionError("No active vendor exists for this organization.")
        if photo_asset_id:
            self.cur.execute(
                "SELECT id FROM media_assets WHERE id=%s AND uploaded_by_user_id=%s AND status='READY'",
                (photo_asset_id, self.context.user_id),
            )
            if not self.cur.fetchone():
                raise PermissionError("Candidate photo must be a READY asset owned by the current user.")
        candidate_id = str(uuid4())
        self.cur.execute(
            """
            INSERT INTO product_candidates (id, vendor_id, proposed_title, proposed_brand, barcode, vendor_sku, photo_asset_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'PENDING_REVIEW')
            RETURNING id, status
            """,
            (candidate_id, str(vendor["id"]), proposed_title.strip(), proposed_brand, barcode, vendor_sku, photo_asset_id),
        )
        row = self.cur.fetchone()
        if vendor_sku:
            self.cur.execute(
                """
                INSERT INTO vendor_products (vendor_id, product_id, candidate_id, vendor_sku, listing_status, is_active)
                VALUES (%s, NULL, %s, %s, 'DRAFT_PENDING_CATALOG', FALSE)
                ON CONFLICT (vendor_id, vendor_sku) DO UPDATE SET candidate_id = EXCLUDED.candidate_id, listing_status = 'DRAFT_PENDING_CATALOG', is_active = FALSE
                RETURNING id
                """,
                (str(vendor["id"]), candidate_id, vendor_sku.strip()),
            )
            vendor_product_id = str(self.cur.fetchone()["id"])
            self.cur.execute(
                """
                INSERT INTO vendor_inventory (vendor_product_id, inventory_unit, physical_quantity, reserved_quantity, moq, freshness_status)
                VALUES (%s, 'CARTON', 0, 0, 1, 'UNKNOWN')
                ON CONFLICT (vendor_product_id) DO NOTHING
                """,
                (vendor_product_id,),
            )
        self.cur.execute(
            """
            INSERT INTO outbox_events (id, event_id, event_name, aggregate_type, aggregate_id, payload, status)
            VALUES (%s, %s, 'product_candidate_created', 'PRODUCT_CANDIDATE', %s, %s, 'PENDING')
            ON CONFLICT DO NOTHING
            """,
            (str(uuid4()), str(uuid4()), candidate_id, Json({"candidate_id": candidate_id, "vendor_id": str(vendor["id"]), "status": "PENDING_REVIEW"})),
        )
        return {
            "candidate_id": candidate_id,
            "status": row["status"],
            "message": "کاندیدا با موفقیت ثبت شد و در کارتابل بررسی تیم کاتالوگ قرار گرفت.",
        }

    def catalog_products_search(self, *, query: str, category_id: str | None = None, page: int = 1, limit: int = 20):
        if page < 1 or limit < 1 or limit > 100:
            raise ValueError("Invalid pagination.")
        offset = (page - 1) * limit
        self.cur.execute(
            """
            SELECT count(*) AS total
            FROM products p
            JOIN brands b ON b.id = p.brand_id
            WHERE p.is_active = TRUE
              AND (
                p.canonical_name_fa ILIKE %s
                OR b.name_fa ILIKE %s
                OR p.master_sku ILIKE %s
                OR similarity(p.canonical_name_fa, %s) > 0.15
              )
              AND (%s::uuid IS NULL OR p.category_id = %s::uuid)
            """,
            (f"%{query}%", f"%{query}%", f"%{query}%", query, category_id, category_id),
        )
        total = int(self.cur.fetchone()["total"])

        self.cur.execute(
            """
            SELECT p.id, p.master_sku, p.canonical_name_fa,
                   b.name_fa AS brand_name,
                   p.default_pack_unit AS pack_unit,
                   p.default_pack_quantity AS pack_quantity,
                   COALESCE(price.lowest_price, NULL) AS lowest_unit_price_toman,
                   COALESCE(stock.available_vendors_count, 0) AS available_vendors_count,
                   media.primary_image_url
            FROM products p
            JOIN brands b ON b.id = p.brand_id
            LEFT JOIN LATERAL (
                SELECT MIN(vpr.price_toman) AS lowest_price
                FROM vendor_products vprp
                JOIN vendor_prices vpr
                  ON vpr.vendor_product_id = vprp.id AND vpr.is_current = TRUE
                JOIN vendors vv ON vv.id = vprp.vendor_id AND vv.status = 'ACTIVE'
                WHERE vprp.product_id = p.id
                  AND vprp.is_active = TRUE
                  AND vprp.listing_status = 'ACTIVE'
            ) price ON TRUE
            LEFT JOIN LATERAL (
                SELECT count(DISTINCT vprp.vendor_id) AS available_vendors_count
                FROM vendor_products vprp
                JOIN vendors vv ON vv.id = vprp.vendor_id AND vv.status = 'ACTIVE'
                JOIN vendor_inventory vi ON vi.vendor_product_id = vprp.id
                WHERE vprp.product_id = p.id
                  AND vprp.is_active = TRUE
                  AND vprp.listing_status = 'ACTIVE'
                  AND vi.available_quantity > 0
            ) stock ON TRUE
            LEFT JOIN LATERAL (
                SELECT CASE
                    WHEN ma.storage_key LIKE 'http://%%' OR ma.storage_key LIKE 'https://%%' THEN ma.storage_key
                    ELSE NULL
                END AS primary_image_url
                FROM product_media pm
                JOIN media_assets ma ON ma.id = pm.media_asset_id AND ma.status = 'READY'
                WHERE pm.product_id = p.id
                ORDER BY pm.is_primary DESC, pm.display_order, pm.created_at
                LIMIT 1
            ) media ON TRUE
            WHERE p.is_active = TRUE
              AND (
                p.canonical_name_fa ILIKE %s
                OR b.name_fa ILIKE %s
                OR p.master_sku ILIKE %s
                OR similarity(p.canonical_name_fa, %s) > 0.15
              )
              AND (%s::uuid IS NULL OR p.category_id = %s::uuid)
            ORDER BY similarity(p.canonical_name_fa, %s) DESC, p.canonical_name_fa
            LIMIT %s OFFSET %s
            """,
            (f"%{query}%", f"%{query}%", f"%{query}%", query, category_id, category_id, query, limit, offset),
        )
        rows = []
        for row in self.cur.fetchall():
            item = dict(row)
            item["id"] = str(item["id"])
            rows.append(item)
        return {
            "products": rows,
            "pagination": {"page": page, "limit": limit, "total": total},
        }

    def catalog_categories(self):
        self.cur.execute(
            """
            SELECT c.id, c.name_fa, c.slug, c.icon_url, c.display_order,
                   COALESCE(
                       json_agg(
                           json_build_object(
                               'id', sc.id, 'name_fa', sc.name_fa,
                               'slug', sc.slug, 'display_order', sc.display_order
                           ) ORDER BY sc.display_order, sc.name_fa
                       ) FILTER (WHERE sc.id IS NOT NULL),
                       '[]'::json
                   ) AS subcategories
            FROM categories c
            LEFT JOIN subcategories sc ON sc.category_id = c.id
            GROUP BY c.id, c.name_fa, c.slug, c.icon_url, c.display_order
            ORDER BY c.display_order, c.name_fa
            """
        )
        return self.cur.fetchall()

    def catalog_product_detail(self, product_id: str):
        self.cur.execute(
            """
            SELECT p.id, p.master_sku, p.canonical_name_fa, p.base_unit,
                   p.default_pack_unit, p.default_pack_quantity,
                   p.net_weight_grams, p.volume_ml, p.dimensions_cm,
                   p.description, p.is_active, p.is_verified,
                   b.id AS brand_id, b.name_fa AS brand_name,
                   c.id AS category_id, c.name_fa AS category_name,
                   sc.id AS subcategory_id, sc.name_fa AS subcategory_name
            FROM products p
            JOIN brands b ON b.id = p.brand_id
            JOIN categories c ON c.id = p.category_id
            JOIN subcategories sc ON sc.id = p.subcategory_id
            WHERE p.id = %s::uuid AND p.is_active = TRUE
            """,
            (product_id,),
        )
        product = self.cur.fetchone()
        if not product:
            raise KeyError("Product not found.")

        self.cur.execute(
            """
            SELECT pi.identifier_type, pi.identifier_value,
                   pi.identifier_scope, pi.packaging_scope
            FROM product_identifiers pi
            WHERE pi.product_id = %s::uuid
            ORDER BY pi.is_primary DESC, pi.identifier_type
            """,
            (product_id,),
        )
        product["identifiers"] = self.cur.fetchall()

        self.cur.execute(
            """
            SELECT ma.id, ma.storage_key, ma.mime_type, pm.is_primary, pm.display_order
            FROM product_media pm
            JOIN media_assets ma ON ma.id = pm.media_asset_id
            WHERE pm.product_id = %s::uuid AND ma.status = 'READY'
            ORDER BY pm.is_primary DESC, pm.display_order
            """,
            (product_id,),
        )
        product["media"] = self.cur.fetchall()

        return product

    def vendor_catalog_list_products(self):
        """List vendor products for the current vendor organization."""
        if not self.context.organization_id:
            raise PermissionError("Vendor catalog requires an active organization context.")
        self.cur.execute(
            """
            SELECT vp.id, vp.vendor_sku, vp.packaging_unit, vp.pack_quantity,
                   vp.sales_unit, vp.is_active, vp.listing_status,
                   vp.product_id, vp.candidate_id,
                   p.canonical_name_fa, p.master_sku,
               vi.physical_quantity, vi.reserved_quantity, vi.available_quantity,
                   vi.moq, vi.freshness_status,
                   vp_price.price_toman
            FROM vendor_products vp
            JOIN vendors v ON v.id = vp.vendor_id
            LEFT JOIN products p ON p.id = vp.product_id
            LEFT JOIN vendor_inventory vi ON vi.vendor_product_id = vp.id
            LEFT JOIN vendor_prices vp_price
                ON vp_price.vendor_product_id = vp.id AND vp_price.is_current = TRUE
            WHERE v.organization_id = %s::uuid
              AND v.status = 'ACTIVE'
            ORDER BY vp.created_at DESC
            """,
            (self.context.organization_id,),
        )
        return self.cur.fetchall()

    def vendor_catalog_create_product(
        self,
        *,
        vendor_sku: str,
        product_id: str | None = None,
        candidate_id: str | None = None,
        packaging_unit: str = "CARTON",
        pack_quantity: int = 12,
        sales_unit: str = "CARTON",
        initial_price_toman: int | None = None,
        moq: int = 1,
    ):
        """Create a new vendor product listing."""
        if not self.context.organization_id:
            raise PermissionError("Vendor catalog requires an active organization context.")

        if not product_id and not candidate_id:
            raise ValueError("Either product_id or candidate_id is required.")

        self.cur.execute(
            "SELECT id FROM vendors WHERE organization_id = %s::uuid AND status = 'ACTIVE'",
            (self.context.organization_id,),
        )
        vendor = self.cur.fetchone()
        if not vendor:
            raise PermissionError("No active vendor found for the current organization.")
        vendor_id = str(vendor["id"])

        self.cur.execute(
            "SELECT id FROM vendor_products WHERE vendor_id = %s::uuid AND vendor_sku = %s",
            (vendor_id, vendor_sku),
        )
        if self.cur.fetchone():
            raise ValueError(f"Vendor SKU '{vendor_sku}' already exists for this vendor.")

        listing_status = "ACTIVE" if product_id else "DRAFT_PENDING_CATALOG"

        self.cur.execute(
            """
            INSERT INTO vendor_products (
                id, vendor_id, product_id, candidate_id, vendor_sku,
                packaging_unit, pack_quantity, sales_unit,
                is_active, listing_status
            ) VALUES (gen_random_uuid(), %s::uuid, %s::uuid, %s::uuid,
                      %s, %s, %s, %s, TRUE, %s)
            RETURNING id
            """,
            (
                vendor_id,
                product_id,
                candidate_id,
                vendor_sku,
                packaging_unit,
                pack_quantity,
                sales_unit,
                listing_status,
            ),
        )
        new_id = str(self.cur.fetchone()["id"])

        self.cur.execute(
            """
            INSERT INTO vendor_inventory (
                vendor_product_id, inventory_unit, physical_quantity,
                reserved_quantity, moq, freshness_status
            ) VALUES (%s::uuid, %s, 0, 0, %s, 'UNKNOWN')
            """,
            (new_id, packaging_unit, moq),
        )

        if initial_price_toman:
            self.cur.execute(
                "INSERT INTO vendor_prices (vendor_product_id, price_toman, is_current) VALUES (%s::uuid, %s, TRUE)",
                (new_id, initial_price_toman),
            )

        return {
            "vendor_product_id": new_id,
            "vendor_sku": vendor_sku,
            "listing_status": listing_status,
            "packaging_unit": packaging_unit,
            "pack_quantity": pack_quantity,
            "moq": moq,
        }

    def vendor_catalog_update_product(
        self,
        *,
        vendor_product_id: str,
        packaging_unit: str | None = None,
        pack_quantity: int | None = None,
        sales_unit: str | None = None,
        moq: int | None = None,
        is_active: bool | None = None,
    ):
        """Update vendor product packaging, MOQ, or active status."""
        if not self.context.organization_id:
            raise PermissionError("Vendor catalog requires an active organization context.")

        self.cur.execute(
            """
            SELECT vp.id, vp.vendor_id
            FROM vendor_products vp
            JOIN vendors v ON v.id = vp.vendor_id
            WHERE vp.id = %s::uuid AND v.organization_id = %s::uuid AND v.status = 'ACTIVE'
            """,
            (vendor_product_id, self.context.organization_id),
        )
        row = self.cur.fetchone()
        if not row:
            raise PermissionError("Vendor product not found or not accessible from this organization.")

        updates = []
        params = []
        if packaging_unit is not None:
            updates.append("packaging_unit = %s")
            params.append(packaging_unit)
        if pack_quantity is not None:
            updates.append("pack_quantity = %s")
            params.append(pack_quantity)
        if sales_unit is not None:
            updates.append("sales_unit = %s")
            params.append(sales_unit)
        if is_active is not None:
            updates.append("is_active = %s")
            params.append(is_active)

        if updates:
            updates.append("updated_at = now()")
            params.append(vendor_product_id)
            self.cur.execute(
                f"UPDATE vendor_products SET {', '.join(updates)} WHERE id = %s::uuid",
                params,
            )

        if moq is not None:
            self.cur.execute(
                "UPDATE vendor_inventory SET moq = %s WHERE vendor_product_id = %s::uuid",
                (moq, vendor_product_id),
            )

        return {"vendor_product_id": vendor_product_id, "updated": True}

    def vendor_price_history(self, vendor_product_id: str):
        """Get full price history for a vendor product (tenant-scoped)."""
        if not self.context.organization_id:
            raise PermissionError("Pricing requires an active organization context.")
        self._assert_vendor_product_ownership(vendor_product_id)
        self.cur.execute(
            """
            SELECT id, price_toman, effective_from, effective_to,
                   is_current
            FROM vendor_prices
            WHERE vendor_product_id = %s::uuid
            ORDER BY effective_from DESC
            """,
            (vendor_product_id,),
        )
        return self.cur.fetchall()

    def vendor_price_current(self, vendor_product_id: str):
        """Get current active price for a vendor product (tenant-scoped)."""
        if not self.context.organization_id:
            raise PermissionError("Pricing requires an active organization context.")
        self._assert_vendor_product_ownership(vendor_product_id)
        self.cur.execute(
            """
            SELECT id, price_toman, effective_from, is_current
            FROM vendor_prices
            WHERE vendor_product_id = %s::uuid AND is_current = TRUE
            """,
            (vendor_product_id,),
        )
        row = self.cur.fetchone()
        if not row:
            raise KeyError("No current price found for this vendor product.")
        return row

    def vendor_price_set(
        self,
        *,
        vendor_product_id: str,
        price_toman: int,
    ):
        """Set a new current price for a vendor product.

        The DB trigger trg_close_vendor_price_version auto-closes the previous
        current price's effective_to when the new current price is inserted.
        The GiST exclusion constraint prevents overlapping price windows.
        """
        if not self.context.organization_id:
            raise PermissionError("Pricing requires an active organization context.")
        self._assert_vendor_product_ownership(vendor_product_id)

        if price_toman <= 0:
            raise ValueError("Price must be positive.")

        self.cur.execute(
            """
            UPDATE vendor_prices
            SET is_current = FALSE, effective_to = now()
            WHERE vendor_product_id = %s::uuid AND is_current = TRUE
            """,
            (vendor_product_id,),
        )

        self.cur.execute(
            """
            INSERT INTO vendor_prices (vendor_product_id, price_toman, is_current, effective_from)
            VALUES (%s::uuid, %s, TRUE, now())
            RETURNING id, price_toman, effective_from, is_current
            """,
            (vendor_product_id, price_toman),
        )
        return self.cur.fetchone()

    def catalog_compare_prices(self, product_id: str):
        """Compare prices across all vendors for a given product (tenant-agnostic)."""
        self.cur.execute(
            """
            SELECT vp.id AS vendor_product_id, vp.vendor_sku,
                   vp.packaging_unit, vp.pack_quantity,
                   v.business_name, v.status AS vendor_status,
                   vp_price.price_toman,
                   vi.available_quantity, vi.moq
            FROM vendor_products vp
            JOIN vendors v ON v.id = vp.vendor_id
            LEFT JOIN vendor_prices vp_price
                ON vp_price.vendor_product_id = vp.id AND vp_price.is_current = TRUE
            LEFT JOIN vendor_inventory vi ON vi.vendor_product_id = vp.id
            WHERE vp.product_id = %s::uuid
              AND vp.is_active = TRUE
              AND vp.listing_status = 'ACTIVE'
              AND v.status = 'ACTIVE'
            ORDER BY vp_price.price_toman ASC NULLS LAST
            """,
            (product_id,),
        )
        return self.cur.fetchall()

    def _assert_vendor_product_ownership(self, vendor_product_id: str):
        """Verify the current organization owns this vendor product."""
        self.cur.execute(
            """
            SELECT 1 FROM vendor_products vp
            JOIN vendors v ON v.id = vp.vendor_id
            WHERE vp.id = %s::uuid
              AND v.organization_id = %s::uuid
              AND v.status = 'ACTIVE'
            """,
            (vendor_product_id, self.context.organization_id),
        )
        if not self.cur.fetchone():
            raise PermissionError("Vendor product not found or not accessible from this organization.")

    def vendor_inventory_get(self, vendor_product_id: str):
        """Get inventory details for a vendor product (tenant-scoped)."""
        if not self.context.organization_id:
            raise PermissionError("Inventory requires an active organization context.")
        self._assert_vendor_product_ownership(vendor_product_id)
        self.cur.execute(
            """
            SELECT vi.vendor_product_id, vi.inventory_unit, vi.physical_quantity,
                   vi.reserved_quantity, vi.available_quantity, vi.moq,
                   vi.freshness_status, vi.inventory_confidence,
                   vi.verification_source, vi.last_confirmed_at, vi.updated_at
            FROM vendor_inventory vi
            WHERE vi.vendor_product_id = %s::uuid
            """,
            (vendor_product_id,),
        )
        row = self.cur.fetchone()
        if not row:
            raise KeyError("Inventory record not found for this vendor product.")
        return row

    def vendor_inventory_adjust(
        self,
        *,
        vendor_product_id: str,
        new_physical_quantity: int,
        reason: str = "MANUAL_EDIT",
    ):
        """Adjust physical inventory quantity (tenant-scoped, logged to audit)."""
        if not self.context.organization_id:
            raise PermissionError("Inventory requires an active organization context.")
        self._assert_vendor_product_ownership(vendor_product_id)

        if new_physical_quantity < 0:
            raise ValueError("Physical quantity cannot be negative.")

        self.cur.execute(
            "SELECT physical_quantity FROM vendor_inventory WHERE vendor_product_id = %s::uuid",
            (vendor_product_id,),
        )
        inv = self.cur.fetchone()
        if not inv:
            raise KeyError("Inventory record not found.")

        old_qty = int(inv["physical_quantity"])
        delta = new_physical_quantity - old_qty

        self.cur.execute(
            """
            UPDATE vendor_inventory
            SET physical_quantity = %s, updated_at = now()
            WHERE vendor_product_id = %s::uuid
            """,
            (new_physical_quantity, vendor_product_id),
        )

        self.cur.execute(
            """
            SELECT v.id AS vendor_id FROM vendor_products vp
            JOIN vendors v ON v.id = vp.vendor_id
            WHERE vp.id = %s::uuid
            """,
            (vendor_product_id,),
        )
        vendor = self.cur.fetchone()

        self.cur.execute(
            """
            INSERT INTO inventory_audit_log (
                vendor_id, vendor_product_id, old_quantity, new_quantity,
                source_trigger, actor_user_id
            ) VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s::uuid)
            """,
            (vendor["vendor_id"], vendor_product_id, old_qty, new_physical_quantity,
             reason, self.context.user_id),
        )

        self.cur.execute(
            """
            UPDATE vendor_inventory
            SET freshness_status = CASE
                WHEN physical_quantity > 0 THEN 'FRESH'
                ELSE freshness_status
            END,
            inventory_confidence = 'CONFIRMED_TODAY',
            verification_source = 'MANUAL',
            last_confirmed_at = now()
            WHERE vendor_product_id = %s::uuid
            """,
            (vendor_product_id,),
        )

        return {
            "vendor_product_id": vendor_product_id,
            "old_quantity": old_qty,
            "new_quantity": new_physical_quantity,
            "delta": delta,
        }

    def catalog_inventory_compare(self, product_id: str):
        """Compare inventory across vendors for a given product (tenant-agnostic)."""
        self.cur.execute(
            """
            SELECT vp.id AS vendor_product_id, vp.vendor_sku,
                   vp.packaging_unit, vp.pack_quantity,
                   v.business_name, v.status AS vendor_status,
                   vi.physical_quantity, vi.reserved_quantity,
                   vi.available_quantity, vi.moq, vi.freshness_status,
                   vp_price.price_toman
            FROM vendor_products vp
            JOIN vendors v ON v.id = vp.vendor_id
            JOIN vendor_inventory vi ON vi.vendor_product_id = vp.id
            LEFT JOIN vendor_prices vp_price
                ON vp_price.vendor_product_id = vp.id AND vp_price.is_current = TRUE
            WHERE vp.product_id = %s::uuid
              AND vp.is_active = TRUE
              AND vp.listing_status = 'ACTIVE'
              AND v.status = 'ACTIVE'
            ORDER BY vi.available_quantity DESC
            """,
            (product_id,),
        )
        return self.cur.fetchall()

    def catalog_product_vendors(self, product_id: str):
        self.cur.execute(
            """
            SELECT vp.id AS vendor_product_id, vp.vendor_sku,
                   vp.packaging_unit, vp.pack_quantity, vp.sales_unit,
                   vi.physical_quantity, vi.available_quantity, vi.moq,
                   vi.freshness_status,
                   vp_price.price_toman,
                   v.id AS vendor_id, v.business_name, v.status AS vendor_status
            FROM vendor_products vp
            JOIN vendors v ON v.id = vp.vendor_id
            JOIN vendor_inventory vi ON vi.vendor_product_id = vp.id
            LEFT JOIN vendor_prices vp_price
                ON vp_price.vendor_product_id = vp.id AND vp_price.is_current = TRUE
            WHERE vp.product_id = %s::uuid
              AND vp.is_active = TRUE
              AND vp.listing_status = 'ACTIVE'
              AND v.status = 'ACTIVE'
            ORDER BY vp_price.price_toman ASC NULLS LAST
            """,
            (product_id,),
        )
        return self.cur.fetchall()

    # -- Public storefront + unified search (auth-free; context may be None) ----

    def storefront_list_vendors(
        self, *, query=None, category_id=None, limit=20, offset=0
    ):
        """List ACTIVE vendors for public storefront browse (R-17 / V-14)."""
        where = ["v.status = 'ACTIVE'"]
        params: list = []
        if query:
            where.append(
                "(v.business_name ILIKE %s OR v.cluster_location ILIKE %s"
                " OR v.warehouse_address ILIKE %s)"
            )
            like = f"%{query}%"
            params.extend([like, like, like])
        if category_id:
            where.append(
                "EXISTS (SELECT 1 FROM vendor_products vp"
                " JOIN products p ON p.id = vp.product_id"
                " WHERE vp.vendor_id = v.id AND p.category_id = %s::uuid"
                " AND vp.listing_status = 'ACTIVE' AND vp.is_active = TRUE)"
            )
            params.append(category_id)
        where_sql = " AND ".join(where)
        self.cur.execute(
            f"SELECT count(*) AS total FROM vendors v WHERE {where_sql}", params
        )
        total = int(self.cur.fetchone()["total"])
        self.cur.execute(
            f"""
            SELECT v.id,
                   v.business_name,
                   v.business_name AS name,
                   v.business_name AS display_name,
                   v.cluster_location AS city,
                   NULL::text AS description,
                   TRUE AS is_active,
                   v.created_at,
                   (SELECT count(*) FROM vendor_products vp
                    WHERE vp.vendor_id = v.id
                      AND vp.is_active = TRUE
                      AND vp.listing_status = 'ACTIVE') AS product_count
            FROM vendors v
            WHERE {where_sql}
            ORDER BY v.business_name
            LIMIT %s OFFSET %s
            """,
            params + [limit, offset],
        )
        return {"items": self.cur.fetchall(), "total": total}

    def storefront_vendor_detail(self, vendor_id: str):
        """Public vendor storefront detail (R-18)."""
        self.cur.execute(
            """
            SELECT v.id,
                   v.business_name,
                   v.business_name AS name,
                   v.business_name AS display_name,
                   v.cluster_location AS city,
                   NULL::text AS description,
                   TRUE AS is_active,
                   v.created_at,
                   (SELECT count(*) FROM vendor_products vp
                    WHERE vp.vendor_id = v.id
                      AND vp.is_active = TRUE
                      AND vp.listing_status = 'ACTIVE') AS product_count
            FROM vendors v
            WHERE v.id = %s::uuid AND v.status = 'ACTIVE'
            """,
            (vendor_id,),
        )
        row = self.cur.fetchone()
        if not row:
            raise ValueError("Vendor not found.")
        return row

    def storefront_vendor_products(
        self,
        *,
        vendor_id,
        category_id=None,
        query=None,
        sort="name",
        limit=20,
        offset=0,
    ):
        """Public product list for one vendor storefront (R-18 / V-14)."""
        self.cur.execute(
            "SELECT id FROM vendors WHERE id = %s::uuid AND status = 'ACTIVE'",
            (vendor_id,),
        )
        if not self.cur.fetchone():
            raise ValueError("Vendor not found.")
        where = [
            "vp.vendor_id = %s::uuid",
            "vp.is_active = TRUE",
            "vp.listing_status = 'ACTIVE'",
            "p.is_active = TRUE",
        ]
        params: list = [vendor_id]
        if category_id:
            where.append("p.category_id = %s::uuid")
            params.append(category_id)
        if query:
            where.append(
                "(p.canonical_name_fa ILIKE %s OR p.master_sku ILIKE %s"
                " OR vp.vendor_sku ILIKE %s)"
            )
            like = f"%{query}%"
            params.extend([like, like, like])
        where_sql = " AND ".join(where)
        self.cur.execute(
            f"""
            SELECT count(*) AS total
            FROM vendor_products vp
            JOIN products p ON p.id = vp.product_id
            WHERE {where_sql}
            """,
            params,
        )
        total = int(self.cur.fetchone()["total"])
        order_by = {
            "name": "p.canonical_name_fa ASC",
            "price": "pr.price_toman ASC NULLS LAST",
            "newest": "vp.created_at DESC",
        }.get(sort, "p.canonical_name_fa ASC")
        self.cur.execute(
            f"""
            SELECT vp.id, vp.product_id,
                   p.canonical_name_fa AS product_name,
                   p.canonical_name_fa AS name,
                   b.name_fa AS brand_name,
                   pr.price_toman,
                   vi.available_quantity AS stock_quantity,
                   vp.packaging_unit,
                   (vp.is_active AND vp.listing_status = 'ACTIVE') AS is_available
            FROM vendor_products vp
            JOIN products p ON p.id = vp.product_id
            LEFT JOIN brands b ON b.id = p.brand_id
            LEFT JOIN vendor_inventory vi ON vi.vendor_product_id = vp.id
            LEFT JOIN vendor_prices pr
                ON pr.vendor_product_id = vp.id AND pr.is_current = TRUE
            WHERE {where_sql}
            ORDER BY {order_by}
            LIMIT %s OFFSET %s
            """,
            params + [limit, offset],
        )
        return {"items": self.cur.fetchall(), "total": total}

    def unified_search(self, *, query, result_type=None, limit=20, offset=0):
        """Search products + vendors + categories in one call (G-003 REAL /search)."""
        products: list = []
        vendors: list = []
        categories: list = []
        if result_type in (None, "product"):
            self.cur.execute(
                """
                SELECT p.id, p.master_sku, p.canonical_name_fa, p.base_unit,
                       p.default_pack_unit, p.default_pack_quantity,
                       b.name_fa AS brand_name, c.name_fa AS category_name,
                       sc.name_fa AS subcategory_name,
                       COALESCE(similarity(p.canonical_name_fa, %s), 0) AS relevance
                FROM products p
                LEFT JOIN brands b ON b.id = p.brand_id
                JOIN categories c ON c.id = p.category_id
                LEFT JOIN subcategories sc ON sc.id = p.subcategory_id
                WHERE p.is_active = TRUE
                  AND (
                      p.canonical_name_fa ILIKE %s
                      OR COALESCE(b.name_fa, '') ILIKE %s
                      OR p.master_sku ILIKE %s
                      OR similarity(p.canonical_name_fa, %s) > 0.15
                  )
                ORDER BY relevance DESC, p.canonical_name_fa
                LIMIT %s OFFSET %s
                """,
                (
                    query,
                    f"%{query}%",
                    f"%{query}%",
                    f"%{query}%",
                    query,
                    limit,
                    offset,
                ),
            )
            products = self.cur.fetchall()
        if result_type in (None, "vendor"):
            self.cur.execute(
                """
                SELECT v.id, v.business_name, v.business_name AS name,
                       v.cluster_location AS city, v.created_at
                FROM vendors v
                WHERE v.status = 'ACTIVE'
                  AND (v.business_name ILIKE %s OR v.cluster_location ILIKE %s)
                ORDER BY v.business_name
                LIMIT %s OFFSET %s
                """,
                (f"%{query}%", f"%{query}%", limit, offset),
            )
            vendors = self.cur.fetchall()
        if result_type in (None, "category"):
            self.cur.execute(
                """
                SELECT c.id, c.name_fa, c.slug, c.icon_url, c.display_order
                FROM categories c
                WHERE c.name_fa ILIKE %s OR c.slug ILIKE %s
                ORDER BY c.display_order, c.name_fa
                LIMIT %s OFFSET %s
                """,
                (f"%{query}%", f"%{query}%", limit, offset),
            )
            categories = self.cur.fetchall()
        return {
            "products": products,
            "vendors": vendors,
            "categories": categories,
        }

    def daily_inventory_get(self, confirmation_date: str):
        """Get daily confirmation status for the current vendor (tenant-scoped)."""
        from scripts import daily_inventory_boundary
        if not self.context.organization_id:
            raise PermissionError("Daily inventory requires an active organization context.")
        self.cur.execute(
            "SELECT id FROM vendors WHERE organization_id = %s::uuid AND status = 'ACTIVE'",
            (self.context.organization_id,),
        )
        vendor = self.cur.fetchone()
        if not vendor:
            raise PermissionError("No active vendor found for this organization.")
        return daily_inventory_boundary.get_or_create_daily_confirmation(
            self.cur, str(vendor["id"]), confirmation_date,
        )

    def daily_inventory_confirm_no_changes(self, confirmation_date: str):
        """1-tap instant confirmation (tenant-scoped)."""
        from scripts import daily_inventory_boundary
        if not self.context.organization_id:
            raise PermissionError("Daily inventory requires an active organization context.")
        self.cur.execute(
            "SELECT id FROM vendors WHERE organization_id = %s::uuid AND status = 'ACTIVE'",
            (self.context.organization_id,),
        )
        vendor = self.cur.fetchone()
        if not vendor:
            raise PermissionError("No active vendor found for this organization.")
        return daily_inventory_boundary.confirm_no_changes(
            self.cur, str(vendor["id"]), self.context.user_id, confirmation_date,
        )

    # ── Admin Audit & Exception Dashboard (Stage 34) ──────────────

    def admin_audit_logs_list(self, *, offset=0, limit=50):
        self._require_ops_context()
        self.cur.execute(
            """
            SELECT al.id, al.actor_user_id, al.action, al.target_entity_type,
                   al.target_entity_id, al.state_before, al.state_after,
                   al.reason, al.ip_address, al.correlation_id, al.created_at,
                   u.full_name AS actor_name
            FROM admin_audit_logs al
            JOIN users u ON u.id = al.actor_user_id
            ORDER BY al.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        )
        rows = self.cur.fetchall()
        return [
            {
                "id": str(r["id"]),
                "actor_user_id": str(r["actor_user_id"]),
                "actor_name": r["actor_name"],
                "action": r["action"],
                "target_entity_type": r["target_entity_type"],
                "target_entity_id": str(r["target_entity_id"]) if r["target_entity_id"] else None,
                "state_before": r["state_before"],
                "state_after": r["state_after"],
                "reason": r["reason"],
                "ip_address": r["ip_address"],
                "correlation_id": r["correlation_id"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            }
            for r in rows
        ]

    def admin_exceptions_dashboard(self):
        self._require_ops_context()

        self.cur.execute(
            """
            SELECT count(*) AS total,
                   count(*) FILTER (WHERE status IN ('REPORTED','UNDER_REVIEW')) AS open_count,
                   count(*) FILTER (WHERE status = 'RESOLVED') AS resolved_count,
                   count(*) FILTER (WHERE status = 'ESCALATED') AS escalated_count
            FROM delivery_exceptions
            """
        )
        de = dict(self.cur.fetchone())

        self.cur.execute(
            """
            SELECT count(*) AS total,
                   count(*) FILTER (WHERE dispute_status IN ('OPEN','INVESTIGATING')) AS open_disputes
            FROM disputes
            """
        )
        dp = dict(self.cur.fetchone())

        self.cur.execute(
            """
            SELECT count(*) AS total,
                   count(*) FILTER (WHERE status = 'OPEN') AS open_cases
            FROM support_cases
            """
        )
        sc = dict(self.cur.fetchone())

        return {
            "delivery_exceptions": de,
            "disputes": dp,
            "support_cases": sc,
        }

    # ── Referral Management (Stage 34) ────────────────────────────

    def referral_create(self, *, referred_retailer_id, referral_code):
        if not self.context.organization_id:
            raise PermissionError("Referral creation requires an organization context.")
        self.cur.execute(
            """
            SELECT 1
            FROM organization_memberships om
            JOIN organizations o ON o.id = om.organization_id
            WHERE om.user_id = %s
              AND om.organization_id = %s
              AND om.status = 'ACTIVE'
              AND om.role IN ('VENDOR_OWNER','VENDOR_STAFF')
              AND o.org_type = 'VENDOR'
              AND o.status = 'ACTIVE'
            LIMIT 1;
            """,
            (self.context.user_id, self.context.organization_id),
        )
        if not self.cur.fetchone():
            raise PermissionError("Only active vendor members may create referrals.")

        self.cur.execute(
            "SELECT id FROM vendors WHERE organization_id = %s AND status = 'ACTIVE'",
            (self.context.organization_id,),
        )
        vendor = self.cur.fetchone()
        if not vendor:
            raise ValueError("No active vendor found for this organization.")

        self.cur.execute(
            "SELECT id FROM retailers WHERE id = %s",
            (referred_retailer_id,),
        )
        if not self.cur.fetchone():
            raise ValueError("Referred retailer not found.")

        referral_id = str(uuid4())
        self.cur.execute(
            """
            INSERT INTO vendor_referrals
                (id, vendor_id, referral_code, status, created_by_user_id)
            VALUES (%s, %s, %s, 'ACTIVE', %s)
            RETURNING id, vendor_id, referral_code, status, created_at
            """,
            (referral_id, str(vendor["id"]), referral_code, self.context.user_id),
        )
        row = self.cur.fetchone()
        return {
            "id": str(row["id"]),
            "vendor_id": str(row["vendor_id"]),
            "referral_code": row["referral_code"],
            "status": row["status"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        }

    def referral_list(self, *, offset=0, limit=50):
        if not self.context.organization_id:
            raise PermissionError("Referral listing requires an organization context.")
        self.cur.execute(
            """
            SELECT 1
            FROM organization_memberships om
            JOIN organizations o ON o.id = om.organization_id
            WHERE om.user_id = %s
              AND om.organization_id = %s
              AND om.status = 'ACTIVE'
              AND om.role IN ('VENDOR_OWNER','VENDOR_STAFF')
              AND o.org_type = 'VENDOR'
              AND o.status = 'ACTIVE'
            LIMIT 1;
            """,
            (self.context.user_id, self.context.organization_id),
        )
        if not self.cur.fetchone():
            raise PermissionError("Only active vendor members may list referrals.")

        self.cur.execute(
            "SELECT id FROM vendors WHERE organization_id = %s AND status = 'ACTIVE'",
            (self.context.organization_id,),
        )
        vendor = self.cur.fetchone()
        if not vendor:
            return {"referrals": [], "limit": limit, "offset": offset}

        self.cur.execute(
            """
            SELECT id, vendor_id, referral_code, status, redemption_count,
                   created_at, updated_at
            FROM vendor_referrals
            WHERE vendor_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """,
            (str(vendor["id"]), limit, offset),
        )
        rows = self.cur.fetchall()
        referrals = [
            {
                "id": str(r["id"]),
                "vendor_id": str(r["vendor_id"]),
                "referral_code": r["referral_code"],
                "status": r["status"],
                "redemption_count": int(r["redemption_count"]),
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                "updated_at": r["updated_at"].isoformat() if r["updated_at"] else None,
            }
            for r in rows
        ]
        return {"referrals": referrals, "limit": limit, "offset": offset}

    def referral_get(self, *, referral_id):
        if not self.context.organization_id:
            raise PermissionError("Referral query requires an organization context.")
        self.cur.execute(
            """
            SELECT vr.id, vr.vendor_id, vr.referral_code, vr.status,
                   vr.redemption_count, vr.created_at, vr.updated_at
            FROM vendor_referrals vr
            JOIN vendors v ON v.id = vr.vendor_id
            WHERE vr.id = %s AND v.organization_id = %s
            """,
            (referral_id, self.context.organization_id),
        )
        row = self.cur.fetchone()
        if not row:
            raise KeyError("Referral not found.")
        return {
            "id": str(row["id"]),
            "vendor_id": str(row["vendor_id"]),
            "referral_code": row["referral_code"],
            "status": row["status"],
            "redemption_count": int(row["redemption_count"]),
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
        }

    def referral_redeem(self, *, referral_id):
        if not self.context.organization_id:
            raise PermissionError("Referral redemption requires an organization context.")
        self.cur.execute(
            """
            SELECT vr.id, vr.vendor_id, vr.status, vr.redemption_count,
                   vr.max_redemptions
            FROM vendor_referrals vr
            JOIN vendors v ON v.id = vr.vendor_id
            WHERE vr.id = %s AND v.organization_id = %s
            """,
            (referral_id, self.context.organization_id),
        )
        row = self.cur.fetchone()
        if not row:
            raise KeyError("Referral not found.")
        referral = dict(row)
        if referral["status"] != "ACTIVE":
            raise ValueError(f"Referral is in '{referral['status']}' status and cannot be redeemed.")
        if referral["max_redemptions"] is not None and referral["redemption_count"] >= referral["max_redemptions"]:
            raise ValueError("Referral redemption limit reached.")
        self.cur.execute(
            """
            UPDATE vendor_referrals
            SET status = 'ACTIVE',
                redemption_count = redemption_count + 1,
                updated_at = now()
            WHERE id = %s
            RETURNING id, vendor_id, referral_code, status, redemption_count, updated_at
            """,
            (referral_id,),
        )
        updated = self.cur.fetchone()
        return {
            "id": str(updated["id"]),
            "vendor_id": str(updated["vendor_id"]),
            "referral_code": updated["referral_code"],
            "status": updated["status"],
            "redemption_count": int(updated["redemption_count"]),
            "updated_at": updated["updated_at"].isoformat() if updated["updated_at"] else None,
        }

    def daily_inventory_confirm_with_changes(self, confirmation_date: str, changes: list):
        """Confirm with item quantity changes (tenant-scoped)."""
        from scripts import daily_inventory_boundary
        if not self.context.organization_id:
            raise PermissionError("Daily inventory requires an active organization context.")
        self.cur.execute(
            "SELECT id FROM vendors WHERE organization_id = %s::uuid AND status = 'ACTIVE'",
            (self.context.organization_id,),
        )
        vendor = self.cur.fetchone()
        if not vendor:
            raise PermissionError("No active vendor found for this organization.")
        return daily_inventory_boundary.confirm_with_changes(
            self.cur, str(vendor["id"]), self.context.user_id, confirmation_date, changes,
        )

    # ── Field Tasks / Vendor-Retailer Onboarding (Stage 35) ────────

    def field_tasks_list(self, *, status=None, offset=0, limit=50):
        """List field tasks assigned to the current user."""
        params: list = [
            self.context.user_id,
        ]
        where = "WHERE ft.assigned_to_user_id = %s"
        if status:
            params.append(status)
            where += " AND ft.status = %s"
        params.extend([limit, offset])
        self.cur.execute(
            f"""
            SELECT ft.id, ft.task_type, ft.target_organization_id,
                   ft.assigned_to_user_id, ft.status, ft.due_date,
                   ft.completed_at, ft.notes, ft.created_at, ft.updated_at
            FROM field_tasks ft
            {where}
            ORDER BY ft.created_at DESC
            LIMIT %s OFFSET %s
            """,
            params,
        )
        rows = self.cur.fetchall()
        tasks = []
        for r in rows:
            d = dict(r)
            d["id"] = str(d["id"])
            d["target_organization_id"] = str(d["target_organization_id"]) if d["target_organization_id"] else None
            d["assigned_to_user_id"] = str(d["assigned_to_user_id"])
            d["completed_at"] = d["completed_at"].isoformat() if d["completed_at"] else None
            d["due_date"] = d["due_date"].isoformat() if d["due_date"] else None
            d["created_at"] = d["created_at"].isoformat() if d["created_at"] else None
            d["updated_at"] = d["updated_at"].isoformat() if d["updated_at"] else None
            tasks.append(d)
        return {"tasks": tasks, "limit": limit, "offset": offset}

    def field_task_get(self, *, task_id):
        """Get a single field task (must be assigned to the current user)."""
        self.cur.execute(
            """
            SELECT ft.id, ft.task_type, ft.target_organization_id,
                   ft.assigned_to_user_id, ft.status, ft.due_date,
                   ft.completed_at, ft.notes, ft.created_at, ft.updated_at
            FROM field_tasks ft
            WHERE ft.id = %s
            """,
            (task_id,),
        )
        row = self.cur.fetchone()
        if not row:
            raise KeyError("Field task not found.")
        task = dict(row)
        if str(task["assigned_to_user_id"]) != self.context.user_id:
            raise PermissionError("Access denied.")
        task["id"] = str(task["id"])
        task["target_organization_id"] = str(task["target_organization_id"]) if task["target_organization_id"] else None
        task["assigned_to_user_id"] = str(task["assigned_to_user_id"])
        task["completed_at"] = task["completed_at"].isoformat() if task["completed_at"] else None
        task["due_date"] = task["due_date"].isoformat() if task["due_date"] else None
        task["created_at"] = task["created_at"].isoformat() if task["created_at"] else None
        task["updated_at"] = task["updated_at"].isoformat() if task["updated_at"] else None
        return task

    def field_task_update(self, *, task_id, status=None, notes=None):
        """Update a field task's status or notes (must be assigned to the current user)."""
        self.cur.execute(
            "SELECT id, assigned_to_user_id, status FROM field_tasks WHERE id = %s",
            (task_id,),
        )
        row = self.cur.fetchone()
        if not row:
            raise KeyError("Field task not found.")
        task = dict(row)
        if str(task["assigned_to_user_id"]) != self.context.user_id:
            raise PermissionError("Access denied.")
        updates = []
        params = []
        if status is not None:
            updates.append("status = %s")
            params.append(status)
            if status == "COMPLETED":
                updates.append("completed_at = now()")
        if notes is not None:
            updates.append("notes = %s")
            params.append(notes)
        if not updates:
            return self.field_task_get(task_id=task_id)
        updates.append("updated_at = now()")
        params.append(task_id)
        self.cur.execute(
            f"""
            UPDATE field_tasks SET {', '.join(updates)}
            WHERE id = %s
            RETURNING id, task_type, target_organization_id, assigned_to_user_id,
                      status, due_date, completed_at, notes, created_at, updated_at
            """,
            params,
        )
        updated = self.cur.fetchone()
        d = dict(updated)
        d["id"] = str(d["id"])
        d["target_organization_id"] = str(d["target_organization_id"]) if d["target_organization_id"] else None
        d["assigned_to_user_id"] = str(d["assigned_to_user_id"])
        d["completed_at"] = d["completed_at"].isoformat() if d["completed_at"] else None
        d["due_date"] = d["due_date"].isoformat() if d["due_date"] else None
        d["created_at"] = d["created_at"].isoformat() if d["created_at"] else None
        d["updated_at"] = d["updated_at"].isoformat() if d["updated_at"] else None
        return d

    def field_task_create(self, *, task_type, assigned_to_user_id, target_organization_id=None, notes=None):
        """Create a field task (admin/operator only)."""
        self._require_ops_context()
        self.cur.execute(
            """
            SELECT 1 FROM users WHERE id = %s
            """,
            (assigned_to_user_id,),
        )
        if not self.cur.fetchone():
            raise ValueError("Assigned user not found.")
        self.cur.execute(
            """
            INSERT INTO field_tasks (task_type, assigned_to_user_id, target_organization_id, notes)
            VALUES (%s, %s, %s, %s)
            RETURNING id, task_type, target_organization_id, assigned_to_user_id,
                      status, due_date, completed_at, notes, created_at, updated_at
            """,
            (task_type, assigned_to_user_id, target_organization_id, notes),
        )
        row = self.cur.fetchone()
        d = dict(row)
        d["id"] = str(d["id"])
        d["target_organization_id"] = str(d["target_organization_id"]) if d["target_organization_id"] else None
        d["assigned_to_user_id"] = str(d["assigned_to_user_id"])
        d["completed_at"] = d["completed_at"].isoformat() if d["completed_at"] else None
        d["due_date"] = d["due_date"].isoformat() if d["due_date"] else None
        d["created_at"] = d["created_at"].isoformat() if d["created_at"] else None
        d["updated_at"] = d["updated_at"].isoformat() if d["updated_at"] else None
        return d

    # ── Notification Logical Layer (Stage 32) ──────────────────────

    def notifications_list(self, *, status=None, offset=0, limit=50):
        where_clauses = ["n.user_id = %s"]
        params: list = [self.context.user_id]
        if self.context.organization_id:
            where_clauses.append("n.organization_id = %s")
            params.append(self.context.organization_id)
        where_sql = " AND ".join(where_clauses)
        self.cur.execute(
            f"""
            SELECT n.id, n.event_name, n.title, n.body, n.priority, n.created_at,
                   ui.is_read, ui.read_at, ui.deep_link
            FROM notifications n
            LEFT JOIN user_inbox_items ui
              ON ui.notification_id = n.id
             AND ui.user_id = n.user_id
             AND (ui.organization_id = n.organization_id OR ui.organization_id IS NULL)
            WHERE {where_sql} """
            f"ORDER BY n.created_at DESC LIMIT %s OFFSET %s",
            (*params, limit, offset),
        )
        return [dict(r) for r in self.cur.fetchall()]

    def inbox_list(self, *, is_read=None, category=None, limit=20, offset=0):
        where = ["ui.user_id = %s"]
        params = [self.context.user_id]
        if self.context.organization_id:
            where.append("ui.organization_id = %s")
            params.append(self.context.organization_id)
        if is_read is not None:
            where.append("ui.is_read = %s")
            params.append(is_read)
        if category:
            where.append("ui.category = %s")
            params.append(category)
        where_sql = " AND ".join(where)
        self.cur.execute(
            f"""
            SELECT ui.id, ui.notification_id, ui.title, ui.body, ui.category,
                   ui.deep_link, ui.is_read, ui.read_at, ui.created_at
            FROM user_inbox_items ui
            WHERE {where_sql}
            ORDER BY ui.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (*params, limit, offset),
        )
        items = [dict(r) for r in self.cur.fetchall()]
        self.cur.execute(
            f"SELECT COUNT(*) AS count FROM user_inbox_items ui WHERE {where_sql} AND ui.is_read = FALSE",
            tuple(params),
        )
        unread_count = int(self.cur.fetchone()["count"])
        for item in items:
            item["id"] = str(item["id"])
            item["notification_id"] = str(item["notification_id"]) if item["notification_id"] else None
        return {"items": items, "unread_count": unread_count, "limit": limit, "offset": offset}

    def inbox_mark_read(self, *, item_id):
        where = "id = %s AND user_id = %s"
        params = [item_id, self.context.user_id]
        if self.context.organization_id:
            where += " AND organization_id = %s"
            params.append(self.context.organization_id)
        self.cur.execute(
            f"""
            UPDATE user_inbox_items
            SET is_read = TRUE, read_at = COALESCE(read_at, now())
            WHERE {where}
            RETURNING id, is_read, read_at
            """,
            tuple(params),
        )
        row = self.cur.fetchone()
        if not row:
            raise PermissionError("Inbox item not found or outside active organization.")
        self.cur.execute(
            "SELECT COUNT(*) AS count FROM user_inbox_items WHERE user_id=%s AND is_read=FALSE"
            + (" AND organization_id=%s" if self.context.organization_id else ""),
            (self.context.user_id, self.context.organization_id) if self.context.organization_id else (self.context.user_id,),
        )
        unread_count = int(self.cur.fetchone()["count"])
        return {"id": str(row["id"]), "is_read": True, "read_at": row["read_at"].isoformat(), "unread_count": unread_count}

    def inbox_mark_all_read(self):
        where = "user_id = %s"
        params = [self.context.user_id]
        if self.context.organization_id:
            where += " AND organization_id = %s"
            params.append(self.context.organization_id)
        self.cur.execute(
            f"""
            UPDATE user_inbox_items
            SET is_read = TRUE, read_at = COALESCE(read_at, now())
            WHERE {where} AND is_read = FALSE
            """,
            tuple(params),
        )
        marked_count = self.cur.rowcount
        return {"marked_count": marked_count, "unread_count": 0}

    def notification_preferences_get(self):
        self.cur.execute(
            "SELECT user_id, category, push_enabled, sms_enabled "
            "FROM notification_preferences WHERE user_id = %s",
            (self.context.user_id,),
        )
        return [dict(r) for r in self.cur.fetchall()]

    def notification_preferences_update(self, *, event_name, channel, is_enabled):
        channel_lower = channel.lower()
        if channel_lower not in ("push", "sms"):
            raise ValueError(f"Invalid channel: {channel}. Must be PUSH or SMS.")
        if channel_lower == "push":
            self.cur.execute(
                "INSERT INTO notification_preferences (user_id, category, push_enabled, sms_enabled) "
                "VALUES (%s, %s, %s, true) "
                "ON CONFLICT (user_id, category) DO UPDATE SET push_enabled = EXCLUDED.push_enabled, updated_at = now()",
                (self.context.user_id, event_name, is_enabled),
            )
        else:
            self.cur.execute(
                "INSERT INTO notification_preferences (user_id, category, push_enabled, sms_enabled) "
                "VALUES (%s, %s, true, %s) "
                "ON CONFLICT (user_id, category) DO UPDATE SET sms_enabled = EXCLUDED.sms_enabled, updated_at = now()",
                (self.context.user_id, event_name, is_enabled),
            )
        return {"event_name": event_name, "channel": channel, "is_enabled": is_enabled}

    # ── Field Tasks (Stage 35) ────────────────────────────────────

    def field_tasks_list(self, *, status=None, offset=0, limit=50):
        where_clauses = ["ft.assigned_to_user_id = %s"]
        params: list = [self.context.user_id]
        if status:
            where_clauses.append("ft.status = %s")
            params.append(status)
        where_sql = " AND ".join(where_clauses)
        self.cur.execute(
            f"SELECT ft.id, ft.task_type, ft.status, ft.notes, ft.created_at, ft.completed_at "
            f"FROM field_tasks ft WHERE {where_sql} "
            f"ORDER BY ft.created_at DESC LIMIT %s OFFSET %s",
            (*params, limit, offset),
        )
        return [dict(r) for r in self.cur.fetchall()]

    def field_task_get(self, *, task_id):
        self.cur.execute(
            "SELECT id, task_type, assigned_to_user_id, target_organization_id, "
            "status, notes, due_date, completed_at, created_at "
            "FROM field_tasks WHERE id = %s",
            (task_id,),
        )
        row = self.cur.fetchone()
        if not row:
            raise ValueError("Field task not found.")
        return dict(row)

    def field_task_update(self, *, task_id, status=None, notes=None):
        updates = []
        params: list = []
        if status:
            updates.append("status = %s")
            params.append(status)
        if notes:
            updates.append("notes = %s")
            params.append(notes)
        if not updates:
            raise ValueError("No fields to update.")
        updates.append("updated_at = now()")
        params.append(task_id)
        self.cur.execute(
            f"UPDATE field_tasks SET {', '.join(updates)} WHERE id = %s "
            "RETURNING id, task_type, status, notes, created_at, updated_at",
            tuple(params),
        )
        row = self.cur.fetchone()
        if not row:
            raise ValueError("Field task not found.")
        return dict(row)

    def field_task_create(self, *, task_type, assigned_to_user_id,
                          retailer_id=None, vendor_id=None, notes=None):
        self._require_ops_context()
        self.cur.execute(
            "INSERT INTO field_tasks (task_type, assigned_to_user_id, notes) "
            "VALUES (%s, %s, %s) "
            "RETURNING id, task_type, status, notes, created_at",
            (task_type, assigned_to_user_id, notes),
        )
        row = self.cur.fetchone()
        return dict(row)
