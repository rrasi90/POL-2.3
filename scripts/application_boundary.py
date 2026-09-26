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
from scripts.canonical_retailer_order import CanonicalRetailerOrderService
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
from scripts.privacy_lifecycle import PrivacyLifecycleService
from scripts.vendor_referral import VendorReferralService
from scripts.vendor_acceptance_timeout_worker import VendorAcceptanceTimeoutWorker
from scripts.reservation_expiry_worker import ReservationExpiryWorker
FIELD_TASK_TRANSITIONS = {
    "ASSIGNED": {"IN_PROGRESS", "FAILED", "CANCELLED"},
    "IN_PROGRESS": {"COMPLETED", "FAILED", "CANCELLED"},
    "FAILED": {"IN_PROGRESS", "CANCELLED"},
    "COMPLETED": set(),
    "CANCELLED": set(),
}


from scripts.permissions import (
    BASE_ROLE_PERMISSIONS,
    CANONICAL_PERMISSIONS,
    effective_permissions,
    grant_permission,
    membership_permissions,
    permission_audit,
    require_permission,
    revoke_permission,
)


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

    def media_presign_resumable(self, *, mime_type, file_size_bytes, target_type, target_id, filename=None):
        if not self.context.organization_id:
            raise PermissionError("Media upload requires an active organization context.")
        return MediaService.presign_resumable(
            self.cur, user_id=self.context.user_id, organization_id=self.context.organization_id,
            mime_type=mime_type, file_size_bytes=file_size_bytes, target_type=target_type,
            target_id=str(target_id), filename=filename,
        )

    def media_complete_resumable(self, *, session_id, parts):
        if not self.context.organization_id:
            raise PermissionError("Media completion requires an active organization context.")
        return MediaService.complete_resumable(
            self.cur, user_id=self.context.user_id, organization_id=self.context.organization_id,
            session_id=str(session_id), parts=[item if isinstance(item, dict) else item.model_dump() for item in parts],
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

    def privacy_export(self):
        return PrivacyLifecycleService.request_export(self.cur, self.context.user_id)

    def privacy_delete_account(self):
        return PrivacyLifecycleService.request_deletion(self.cur, self.context.user_id)

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

    def basket_current(self):
        retailer, basket = CanonicalBasketAllocationService._basket_for_context(
            self.cur, self.context.user_id, self.context.organization_id,
            self._current_basket_id(),
        )
        self.cur.execute(
            """
            SELECT bi.id, bi.product_id, p.master_sku, p.canonical_name_fa,
                   bi.requested_quantity, bi.requested_unit, bi.pack_quantity
            FROM basket_items bi
            JOIN products p ON p.id = bi.product_id
            WHERE bi.basket_id = %s
            ORDER BY bi.created_at, bi.id
            """,
            (basket["id"],),
        )
        items = [dict(row, id=str(row["id"]), product_id=str(row["product_id"])) for row in self.cur.fetchall()]
        return {
            "basket_id": str(basket["id"]),
            "retailer_id": str(retailer["retailer_id"]),
            "status": basket["status"],
            "version": int(basket["version"]),
            "items": items,
        }

    def _current_basket_id(self):
        self.cur.execute(
            """
            SELECT b.id
            FROM baskets b
            JOIN retailers r ON r.id = b.retailer_id
            WHERE r.organization_id = %s
              AND b.status = 'OPEN'
            ORDER BY b.updated_at DESC, b.id DESC
            LIMIT 1
            """,
            (self.context.organization_id,),
        )
        row = self.cur.fetchone()
        if not row:
            raise KeyError("No OPEN basket exists for the active retailer organization.")
        return str(row["id"])

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
              AND om.role = 'RETAILER_OWNER'
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

    def retailer_order_cancel(self, *, order_id, reason='RETAILER_CANCELLED'):
        self.cur.execute("SELECT retailer_id FROM orders WHERE id=%s", (order_id,))
        row = self.cur.fetchone()
        if not row:
            raise KeyError(f"Order {order_id} not found.")
        self._verify_retailer_actor(row["retailer_id"])
        return CanonicalRetailerOrderService.cancel_order(
            self.cur, user_id=self.context.user_id, organization_id=self.context.organization_id,
            order_id=order_id, reason=reason,
        )

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

    def partial_acceptance_proposals_list(self, *, order_id, status=None, offset=0, limit=50):
        actor_role = self._resolve_actor_role()
        clauses = ["p.order_id = %s"]
        params: list = [order_id]

        if actor_role == "RETAILER":
            clauses.append(
                "p.retailer_id IN (SELECT id FROM retailers WHERE organization_id = %s)"
            )
            params.append(self.context.organization_id)
        elif actor_role == "VENDOR":
            clauses.append(
                "p.vendor_id IN (SELECT id FROM vendors WHERE organization_id = %s)"
            )
            params.append(self.context.organization_id)

        if status:
            clauses.append("p.status = %s")
            params.append(status)

        where_sql = " AND ".join(clauses)
        params.extend([limit, offset])
        self.cur.execute(
            f"""
            SELECT
                p.id AS proposal_id,
                p.order_id,
                p.vendor_id,
                p.retailer_id,
                p.proposed_by_user_id,
                p.status,
                p.decision_by_user_id,
                p.decision_reason,
                p.decided_at,
                p.created_at,
                p.updated_at,
                o.order_number,
                COALESCE(
                    json_agg(
                        json_build_object(
                            'order_item_id', pi.order_item_id,
                            'accepted_quantity', pi.accepted_quantity,
                            'reason', pi.reason
                        )
                        ORDER BY pi.order_item_id
                    ) FILTER (WHERE pi.id IS NOT NULL),
                    '[]'::json
                ) AS items
            FROM order_partial_acceptance_proposals p
            JOIN orders o ON o.id = p.order_id
            LEFT JOIN order_partial_acceptance_proposal_items pi
              ON pi.proposal_id = p.id
            WHERE {where_sql}
            GROUP BY p.id, o.order_number
            ORDER BY p.created_at DESC, p.id
            LIMIT %s OFFSET %s
            """,
            tuple(params),
        )
        proposals = []
        for row in self.cur.fetchall():
            item = dict(row)
            item["proposal_id"] = str(item["proposal_id"])
            item["order_id"] = str(item["order_id"])
            item["vendor_id"] = str(item["vendor_id"])
            item["retailer_id"] = str(item["retailer_id"])
            item["proposed_by_user_id"] = str(item["proposed_by_user_id"])
            item["decision_by_user_id"] = (
                str(item["decision_by_user_id"])
                if item["decision_by_user_id"] else None
            )
            for field in ("decided_at", "created_at", "updated_at"):
                if item[field]:
                    item[field] = item[field].isoformat()
            proposals.append(item)

        return {
            "proposals": proposals,
            "limit": limit,
            "offset": offset,
        }

    # ── Order Query Methods (Stage 20) ──────────────────────────────

    def _current_vendor_for_context(self):
        if not self.context.organization_id:
            return None
        self.cur.execute(
            """
            SELECT v.id, v.organization_id, v.user_id, v.business_name, v.status
            FROM vendors v
            WHERE v.organization_id=%s
              AND v.status='ACTIVE'
            ORDER BY v.id
            LIMIT 1
            """,
            (self.context.organization_id,),
        )
        return self.cur.fetchone()

    def _resolve_actor_role(self):
        if not self.context.organization_id:
            raise PermissionError("Order query requires an organization context.")
        self.cur.execute(
            """
            SELECT om.role
            FROM organization_memberships om
            JOIN organizations o ON o.id=om.organization_id
            JOIN users u ON u.id=om.user_id
            WHERE om.organization_id=%s
              AND om.user_id=%s
              AND om.status='ACTIVE'
              AND o.status='ACTIVE'
              AND u.is_active=TRUE
            """,
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
                                    proof_media_id=None, issue_reported=None, delivered_items=None):
        if otp_code:
            # G-438: the attempt cap must survive per-request rollback, so each
            # verification attempt is recorded in an independent transaction
            # before the confirmation transaction starts. An expired or already
            # consumed OTP is not counted; the canonical service still raises
            # the precise error for those cases.
            self._record_delivery_otp_attempt(order_id)
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
            delivered_items=delivered_items,
        )

    # ── Delivery Tracking Methods (Stage 23) ───────────────────────


    _DELIVERY_OTP_MAX_ATTEMPTS = 5

    def _record_delivery_otp_attempt(self, order_id):
        """Record one delivery-OTP verification attempt atomically and durably.

        Uses an independent connection so the counter survives the rollback of
        the rejected confirmation request. Concurrent verifications serialize on
        the delivery_otp_attempts row; the cap (5, per D-018 max-attempts policy)
        is enforced by the guarded RETURNING increment.
        """
        from scripts.api.db import get_runtime_connection

        conn = get_runtime_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO delivery_otp_attempts AS a (delivery_id, attempt_count, last_attempt_at)
                    SELECT d.id, 1, now()
                    FROM deliveries d
                    WHERE d.order_id = %s
                      AND d.delivery_otp IS NOT NULL
                      AND d.delivery_otp_used_at IS NULL
                      AND (d.delivery_otp_expires_at IS NULL OR d.delivery_otp_expires_at > now())
                    ON CONFLICT (delivery_id) DO UPDATE
                      SET attempt_count = a.attempt_count + 1,
                          last_attempt_at = now(),
                          updated_at = now()
                    RETURNING attempt_count;
                    """,
                    (order_id,),
                )
                row = cur.fetchone()
                conn.commit()
                if row and int(row[0]) > self._DELIVERY_OTP_MAX_ATTEMPTS:
                    raise ValueError("Delivery OTP attempt limit has been reached.")
        finally:
            conn.close()

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
            user_id=self.context.user_id,
            organization_id=self.context.organization_id,
            order_id=order_id,
            delivery_id=delivery_id,
            status=status,
            offset=offset,
            limit=limit,
        )

    def delivery_exception_get(self, *, exception_id):
        from scripts.delivery_exceptions import get_delivery_exception as _get
        result = _get(
            self.cur,
            user_id=self.context.user_id,
            organization_id=self.context.organization_id,
            exception_id=exception_id,
        )
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

    def return_refund_approve(self, *, return_id, reason=None):
        return CanonicalReturnService.approve_refund(
            self.cur, self.context.user_id, return_id,
            self.context.organization_id, reason=reason,
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

    def dispute_open(self, *, order_id, claimed_amount_toman, description,
                     evidence_media_id, items, idempotency_key):
        if not self.context.organization_id:
            raise PermissionError("Dispute open requires an organization context.")
        from scripts.canonical_dispute import CanonicalDisputeService

        # Resolve the retailer/vendor parties from the active tenant rather than
        # accepting them from the client.
        self.cur.execute(
            """
            SELECT o.retailer_id, o.vendor_id
            FROM orders o
            JOIN retailers r ON r.id=o.retailer_id
            WHERE o.id=%s AND r.organization_id=%s
            LIMIT 1
            """,
            (order_id, self.context.organization_id),
        )
        context = self.cur.fetchone()
        if not context:
            raise PermissionError("Order is not in the active retailer tenant.")

        normalized_items = [
            {
                "order_item_id": str(x.order_item_id),
                "quantity": int(x.quantity),
                "claimed_amount_toman": int(x.claimed_amount_toman),
                "reason_code": str(x.reason_code),
            } if hasattr(x, "order_item_id") else {
                "order_item_id": str(x["order_item_id"]),
                "quantity": int(x["quantity"]),
                "claimed_amount_toman": int(x["claimed_amount_toman"]),
                "reason_code": str(x["reason_code"]),
            }
            for x in items
        ]
        return CanonicalDisputeService.open_dispute_v2(
            self.cur,
            order_id=str(order_id),
            retailer_id=str(context["retailer_id"]),
            vendor_id=str(context["vendor_id"]),
            claimed_amount=int(claimed_amount_toman),
            description=str(description),
            evidence_media_id=str(evidence_media_id),
            items=normalized_items,
            actor_user_id=str(self.context.user_id),
            organization_id=str(self.context.organization_id),
            idempotency_key=str(idempotency_key),
        )


    def dispute_investigate(self, *, dispute_id, reason=None):
        self._require_dispute_resolution_context()
        from scripts.canonical_dispute import CanonicalDisputeService
        result = CanonicalDisputeService.investigate_dispute(
            self.cur,
            dispute_id=str(dispute_id),
            actor_user_id=str(self.context.user_id),
            organization_id=str(self.context.organization_id),
            reason=reason.strip() if reason else None,
        )
        self.cur.execute(
            """
            INSERT INTO admin_audit_logs
                (actor_user_id, action, target_entity_type, target_entity_id,
                 state_after, reason, correlation_id)
            VALUES (%s,'DISPUTE_INVESTIGATING','DISPUTE',%s,%s,%s,%s)
            """,
            (self.context.user_id, dispute_id, Json(result), reason, self.context.correlation_id),
        )
        return result


    def dispute_resolve(self, *, dispute_id, outcome, approved_amount_toman, reason):
        self._require_dispute_resolution_context()
        from scripts.canonical_dispute import CanonicalDisputeService
        result = CanonicalDisputeService.resolve_canonical(
            self.cur,
            dispute_id=str(dispute_id),
            actor_user_id=str(self.context.user_id),
            organization_id=str(self.context.organization_id),
            outcome=outcome,
            approved_amount=int(approved_amount_toman),
            reason=reason,
        )
        self.cur.execute(
            """
            INSERT INTO admin_audit_logs
                (actor_user_id, action, target_entity_type, target_entity_id,
                 state_before, state_after, reason, correlation_id)
            VALUES (%s,'DISPUTE_RESOLVED','DISPUTE',%s,%s,%s,%s,%s)
            """,
            (
                self.context.user_id, dispute_id,
                Json({"status": "INVESTIGATING"}),
                Json(result), reason.strip(), self.context.correlation_id,
            ),
        )
        return result


    def dispute_close(self, *, dispute_id, reason=None):
        self._require_dispute_resolution_context()
        from scripts.canonical_dispute import CanonicalDisputeService
        result = CanonicalDisputeService.close_canonical(
            self.cur,
            dispute_id=str(dispute_id),
            actor_user_id=str(self.context.user_id),
            organization_id=str(self.context.organization_id),
            reason=reason.strip() if reason else None,
        )
        self.cur.execute(
            """
            INSERT INTO admin_audit_logs
                (actor_user_id, action, target_entity_type, target_entity_id,
                 state_after, reason, correlation_id)
            VALUES (%s,'DISPUTE_CLOSED','DISPUTE',%s,%s,%s,%s)
            """,
            (self.context.user_id, dispute_id, Json(result), reason, self.context.correlation_id),
        )
        return result


    def refund_issue(self, *, dispute_id, amount_toman, payment_id=None,
                     reason="", idempotency_key=None):
        from scripts.refund_service import RefundService
        return RefundService.issue_from_dispute(
            self.cur,
            actor_user_id=str(self.context.user_id),
            organization_id=str(self.context.organization_id),
            dispute_id=str(dispute_id),
            amount_toman=int(amount_toman),
            payment_id=str(payment_id) if payment_id else None,
            reason=str(reason),
            idempotency_key=str(idempotency_key) if idempotency_key else None,
            correlation_id=self.context.correlation_id,
        )


    def refund_approve(self, *, refund_id, reason=""):
        from scripts.refund_service import RefundService
        return RefundService.approve(
            self.cur,
            actor_user_id=str(self.context.user_id),
            organization_id=str(self.context.organization_id),
            refund_id=str(refund_id),
            reason=str(reason),
            correlation_id=self.context.correlation_id,
        )


    def refund_complete(self, *, refund_id, reason=""):
        from scripts.refund_service import RefundService
        return RefundService.complete(
            self.cur,
            actor_user_id=str(self.context.user_id),
            organization_id=str(self.context.organization_id),
            refund_id=str(refund_id),
            reason=str(reason),
            correlation_id=self.context.correlation_id,
        )


    def refund_get(self, *, refund_id):
        from scripts.refund_service import RefundService
        return RefundService.get(
            self.cur,
            actor_user_id=str(self.context.user_id),
            organization_id=str(self.context.organization_id),
            refund_id=str(refund_id),
        )


    def refunds_list(self, *, offset=0, limit=50):
        from scripts.refund_service import RefundService
        return RefundService.list(
            self.cur,
            actor_user_id=str(self.context.user_id),
            organization_id=str(self.context.organization_id),
            limit=int(limit),
            offset=int(offset),
        )

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

    def process_reservation_expiries(self, *, limit=100):
        self._require_ops_context()
        return ReservationExpiryWorker.process_expired(self.cur, limit=limit)

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

    def submit_payment_evidence(self, *, order_id, evidence_type, reference_number,
                                  amount_toman, payment_id=None, evidence_media_id=None, notes=None):
        if evidence_type not in self.VALID_EVIDENCE_TYPES:
            raise ValueError(
                f"Invalid evidence_type '{evidence_type}'. "
                f"Must be one of: {', '.join(sorted(self.VALID_EVIDENCE_TYPES))}"
            )
        if not self.context.organization_id:
            raise PermissionError("Payment evidence requires an active organization context.")

        # Locate exactly one payment. An order with multiple payment records
        # must identify the intended payment explicitly.
        if payment_id:
            self.cur.execute(
                """
                SELECT o.id AS order_id, o.retailer_id, o.vendor_id,
                       p.id AS payment_id, p.payment_status,
                       p.retailer_id AS pay_retailer_id,
                       p.vendor_id AS pay_vendor_id,
                       p.amount_toman AS payment_amount_toman
                FROM orders o
                JOIN payments p ON p.order_id=o.id
                WHERE o.id=%s AND p.id=%s
                FOR UPDATE OF p
                """,
                (order_id, payment_id),
            )
            row=self.cur.fetchone()
        else:
            self.cur.execute(
                """
                SELECT o.id AS order_id, o.retailer_id, o.vendor_id,
                       p.id AS payment_id, p.payment_status,
                       p.retailer_id AS pay_retailer_id,
                       p.vendor_id AS pay_vendor_id,
                       p.amount_toman AS payment_amount_toman
                FROM orders o
                JOIN payments p ON p.order_id=o.id
                WHERE o.id=%s
                ORDER BY p.created_at DESC, p.id DESC
                LIMIT 2
                FOR UPDATE OF p
                """,
                (order_id,),
            )
            rows=self.cur.fetchall()
            if len(rows) != 1:
                raise ValueError("Explicit payment_id is required when an order has multiple payment records.")
            row=rows[0]

        if not row:
            raise ValueError(f"Order {order_id} not found or selected payment does not exist.")

        # Tenant check: actor must belong to the retailer or vendor org of this order
        pay_retailer_id = str(row["pay_retailer_id"])
        pay_vendor_id = str(row["pay_vendor_id"])
        actor_org = self.context.organization_id

        self.cur.execute(
            """
            SELECT 1
            FROM organization_memberships om
            JOIN organizations o ON o.id = om.organization_id
            JOIN users u ON u.id = om.user_id
            WHERE om.user_id = %s
              AND om.organization_id = %s
              AND om.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
              AND u.is_active = TRUE
              AND (
                  (om.role = 'RETAILER_OWNER'
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

        if int(amount_toman) <= 0:
            raise ValueError("Payment evidence amount must be positive.")
        if int(amount_toman) > int(row["payment_amount_toman"]):
            raise ValueError("Payment evidence amount exceeds the selected payment amount.")

        if evidence_type == "RECEIPT_IMAGE" and not evidence_media_id:
            raise ValueError("RECEIPT_IMAGE requires evidence_media_id.")
        if evidence_media_id:
            self.cur.execute(
                """
                SELECT id, status, uploaded_by_user_id, upload_target_type, upload_target_id
                FROM media_assets
                WHERE id=%s
                FOR SHARE
                """,
                (str(evidence_media_id),),
            )
            media = self.cur.fetchone()
            if not media:
                raise ValueError("Payment evidence media was not found.")
            if str(media["status"]).upper() != "READY":
                raise ValueError("Payment evidence media must be READY.")
            if str(media["uploaded_by_user_id"]) != str(self.context.user_id):
                raise PermissionError("Payment evidence media is not owned by the current actor.")
            target_type = str(media["upload_target_type"] or "").upper()
            target_id = str(media["upload_target_id"]) if media["upload_target_id"] else None
            if target_type == "ORDER":
                if target_id != str(row["order_id"]):
                    raise PermissionError("Payment evidence media is not bound to this order.")
            elif target_type == "PAYMENT":
                if target_id != str(row["payment_id"]):
                    raise PermissionError("Payment evidence media is not bound to this payment.")
            else:
                raise PermissionError("Payment evidence media must be bound to this order or payment.")

        evidence_id = str(uuid4())
        self.cur.execute(
            """
            INSERT INTO payment_evidence (
                id, payment_id, evidence_type, external_reference,
                claimed_amount_toman, observed_amount_toman,
                evidence_media_id, captured_by_user_id, observation_scope, metadata
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, 'SINGLE_PAYMENT', %s
            )
            ON CONFLICT (external_reference) WHERE external_reference IS NOT NULL
            DO NOTHING
            RETURNING *;
            """,
            (
                evidence_id, str(row["payment_id"]), evidence_type, reference_number,
                amount_toman, amount_toman, str(evidence_media_id) if evidence_media_id else None,
                self.context.user_id,
                Json({"notes": notes} if notes else {}),
            ),
        )
        ev = self.cur.fetchone()
        if ev is None and reference_number:
            self.cur.execute(
                """
                SELECT id, payment_id, evidence_type, external_reference,
                       claimed_amount_toman, captured_at, captured_by_user_id
                FROM payment_evidence
                WHERE external_reference=%s
                LIMIT 1
                """,
                (reference_number,),
            )
            existing = self.cur.fetchone()
            if not existing:
                raise RuntimeError("Payment evidence replay conflict could not be resolved.")
            if str(existing["payment_id"]) != str(row["payment_id"]):
                raise ValueError("This external reference is already attached to another payment.")
            return {
                "evidence_id": str(existing["id"]),
                "payment_id": str(existing["payment_id"]),
                "evidence_type": existing["evidence_type"],
                "reference_number": existing["external_reference"],
                "amount_toman": int(existing["claimed_amount_toman"]),
                "captured_at": existing["captured_at"].isoformat() if existing["captured_at"] else None,
                "idempotent_replay": True,
            }
        return {
            "evidence_id": str(ev["id"]),
            "payment_id": str(ev["payment_id"]),
            "evidence_type": ev["evidence_type"],
            "reference_number": ev["external_reference"],
            "amount_toman": int(ev["claimed_amount_toman"]),
            "captured_at": ev["captured_at"].isoformat() if ev["captured_at"] else None,
            "idempotent_replay": False,
        }

    def get_payment_evidence(self, *, order_id):
        if not self.context.organization_id:
            raise PermissionError("Payment evidence requires an active organization context.")

        self.cur.execute(
            """
            SELECT p.id AS payment_id,
                   p.retailer_id,
                   p.vendor_id,
                   r.organization_id AS retailer_org_id,
                   v.organization_id AS vendor_org_id
            FROM payments p
            JOIN retailers r ON r.id=p.retailer_id
            JOIN vendors v ON v.id=p.vendor_id
            WHERE p.order_id=%s
            ORDER BY p.created_at DESC, p.id DESC
            LIMIT 1
            """,
            (order_id,),
        )
        pay = self.cur.fetchone()
        if not pay:
            raise ValueError(f"Order {order_id} has no payment record.")

        self.cur.execute(
            """
            SELECT 1
            FROM organization_memberships om
            JOIN organizations o ON o.id=om.organization_id
            JOIN users u ON u.id=om.user_id
            WHERE om.user_id=%s
              AND om.organization_id=%s
              AND om.status='ACTIVE'
              AND o.status='ACTIVE'
              AND u.is_active=TRUE
              AND (
                 (om.organization_id=%s AND om.role IN ('RETAILER_OWNER','RETAILER_STAFF'))
                 OR
                 (om.organization_id=%s AND om.role IN ('VENDOR_OWNER','VENDOR_STAFF'))
              )
            LIMIT 1
            """,
            (
                self.context.user_id,
                self.context.organization_id,
                pay["retailer_org_id"],
                pay["vendor_org_id"],
            ),
        )
        if not self.cur.fetchone():
            raise PermissionError("Actor is not authorized to read this payment evidence.")

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

    def verify_payment(self, *, order_id, notes=None, payment_id=None):
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
              AND (%s::uuid IS NULL OR p.id=%s::uuid)
            ORDER BY p.created_at DESC, p.id DESC
            LIMIT 1
            FOR UPDATE OF p
            """,
            (order_id, payment_id, payment_id),
        )
        pay = self.cur.fetchone()
        if not pay:
            raise ValueError(f"Order {order_id} has no payment record.")

        self.cur.execute(
            """
            SELECT 1
            FROM organization_memberships om
            JOIN organizations o ON o.id=om.organization_id
            JOIN users u ON u.id=om.user_id
            WHERE om.user_id=%s
              AND om.organization_id=%s
              AND om.status='ACTIVE'
              AND o.status='ACTIVE'
              AND u.is_active=TRUE
              AND om.role IN ('VENDOR_OWNER','OPS_AGENT','OPS_ADMIN','ADMIN_SUPER','SUPER_ADMIN')
            LIMIT 1
            """,
            (self.context.user_id, self.context.organization_id),
        )
        if not self.cur.fetchone() or str(pay["vendor_org_id"]) != str(self.context.organization_id):
            raise PermissionError("Only an active vendor/operations actor may verify this payment.")

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
            # Operator administration is intentionally cross-tenant for read-only
            # invoice visibility, matching the RBAC/API contract. Tenant users are
            # already handled by the RETAILER/VENDOR branches above.
            where = "1 = 1"
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

    def catalog_create_product_candidate(
        self,
        *,
        proposed_title: str,
        proposed_brand: str | None,
        barcode: str | None,
        vendor_sku: str | None,
        photo_asset_id: str | None,
    ):
        if not self.context.organization_id:
            raise PermissionError("Candidate creation requires an active organization context.")

        self.cur.execute(
            """
            SELECT 1
            FROM organization_memberships
            WHERE user_id=%s
              AND organization_id=%s
              AND role IN ('VENDOR_OWNER','VENDOR_STAFF')
              AND status='ACTIVE'
            LIMIT 1
            """,
            (self.context.user_id, self.context.organization_id),
        )
        if not self.cur.fetchone():
            raise PermissionError("Only active vendor members may create product candidates.")

        self.cur.execute(
            """
            SELECT id, user_id
            FROM vendors
            WHERE organization_id=%s::uuid AND status='ACTIVE'
            ORDER BY id
            LIMIT 1
            """,
            (self.context.organization_id,),
        )
        vendor = self.cur.fetchone()
        if not vendor:
            raise PermissionError("No active vendor exists for this organization.")

        normalized_barcode = None
        if barcode:
            normalized_barcode = "".join(ch for ch in str(barcode).strip() if ch.isalnum())
            if len(normalized_barcode) < 8 or len(normalized_barcode) > 32:
                raise ValueError("Barcode must contain between 8 and 32 alphanumeric characters.")

        normalized_vendor_sku = vendor_sku.strip() if vendor_sku and vendor_sku.strip() else None
        proposed_title = proposed_title.strip()
        if not proposed_title:
            raise ValueError("proposed_title is required.")

        if photo_asset_id:
            self.cur.execute(
                "SELECT id FROM media_assets WHERE id=%s AND uploaded_by_user_id=%s AND status='READY'",
                (photo_asset_id, self.context.user_id),
            )
            if not self.cur.fetchone():
                raise PermissionError("Candidate photo must be a READY asset owned by the current user.")

        vendor_id = str(vendor["id"])

        # Serialize the natural-key check so two concurrent submissions cannot
        # create/replace competing candidate associations for one vendor SKU.
        if normalized_vendor_sku:
            self.cur.execute(
                "SELECT pg_advisory_xact_lock(hashtext(%s))",
                (f"{vendor_id}:{normalized_vendor_sku}",),
            )
            self.cur.execute(
                """
                SELECT id, product_id, candidate_id, listing_status
                FROM vendor_products
                WHERE vendor_id=%s AND vendor_sku=%s
                FOR UPDATE
                """,
                (vendor_id, normalized_vendor_sku),
            )
            existing_vp = self.cur.fetchone()
            if existing_vp:
                if existing_vp["product_id"]:
                    raise ValueError("vendor_sku is already bound to a canonical product.")
                if existing_vp["candidate_id"]:
                    self.cur.execute(
                        "SELECT id, status FROM product_candidates WHERE id=%s FOR UPDATE",
                        (existing_vp["candidate_id"],),
                    )
                    candidate = self.cur.fetchone()
                    if candidate and candidate["status"] != "REJECTED":
                        return {
                            "candidate_id": str(candidate["id"]),
                            "vendor_product_id": str(existing_vp["id"]),
                            "status": candidate["status"],
                            "listing_status": existing_vp["listing_status"],
                            "idempotent_replay": True,
                            "message": "کاندیدای موجود برای این SKU بازگردانده شد.",
                        }
                    raise ValueError("vendor_sku is linked to a rejected candidate; use the existing resolution workflow.")

        if normalized_barcode and not normalized_vendor_sku:
            self.cur.execute(
                """
                SELECT id, status
                FROM product_candidates
                WHERE vendor_id=%s
                  AND barcode=%s
                  AND status='PENDING_REVIEW'
                ORDER BY created_at DESC
                LIMIT 1
                FOR UPDATE
                """,
                (vendor_id, normalized_barcode),
            )
            existing_candidate = self.cur.fetchone()
            if existing_candidate:
                return {
                    "candidate_id": str(existing_candidate["id"]),
                    "status": existing_candidate["status"],
                    "idempotent_replay": True,
                    "message": "کاندیدای باز موجود برای این بارکد بازگردانده شد.",
                }

        candidate_id = str(uuid4())
        if normalized_barcode and not normalized_vendor_sku:
            self.cur.execute(
                """
                INSERT INTO product_candidates
                    (id, vendor_id, proposed_title, proposed_brand, barcode, vendor_sku, photo_asset_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'PENDING_REVIEW')
                ON CONFLICT (vendor_id, barcode)
                    WHERE barcode IS NOT NULL AND status = 'PENDING_REVIEW'
                DO NOTHING
                RETURNING id, status
                """,
                (
                    candidate_id,
                    vendor_id,
                    proposed_title,
                    proposed_brand,
                    normalized_barcode,
                    normalized_vendor_sku,
                    photo_asset_id,
                ),
            )
            row = self.cur.fetchone()
            if row is None:
                self.cur.execute(
                    """
                    SELECT id, status
                    FROM product_candidates
                    WHERE vendor_id=%s
                      AND barcode=%s
                      AND status='PENDING_REVIEW'
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (vendor_id, normalized_barcode),
                )
                row = self.cur.fetchone()
                if not row:
                    raise RuntimeError("Pending barcode candidate disappeared during idempotent replay.")
                return {
                    "candidate_id": str(row["id"]),
                    "vendor_product_id": None,
                    "status": row["status"],
                    "listing_status": None,
                    "idempotent_replay": True,
                    "message": "کاندیدای باز موجود برای این بارکد بازگردانده شد.",
                }
        else:
            self.cur.execute(
                """
                INSERT INTO product_candidates
                    (id, vendor_id, proposed_title, proposed_brand, barcode, vendor_sku, photo_asset_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'PENDING_REVIEW')
                RETURNING id, status
                """,
                (
                    candidate_id,
                    vendor_id,
                    proposed_title,
                    proposed_brand,
                    normalized_barcode,
                    normalized_vendor_sku,
                    photo_asset_id,
                ),
            )
            row = self.cur.fetchone()

        vendor_product_id = None
        if normalized_vendor_sku:
            self.cur.execute(
                """
                INSERT INTO vendor_products
                    (vendor_id, product_id, candidate_id, vendor_sku, listing_status, is_active)
                VALUES (%s, NULL, %s, %s, 'DRAFT_PENDING_CATALOG', FALSE)
                RETURNING id
                """,
                (vendor_id, candidate_id, normalized_vendor_sku),
            )
            vendor_product_id = str(self.cur.fetchone()["id"])
            self.cur.execute(
                """
                INSERT INTO vendor_inventory
                    (vendor_product_id, inventory_unit, physical_quantity, reserved_quantity, moq, freshness_status)
                VALUES (%s, 'CARTON', 0, 0, 1, 'UNKNOWN')
                ON CONFLICT (vendor_product_id) DO NOTHING
                """,
                (vendor_product_id,),
            )

        self.cur.execute(
            """
            INSERT INTO outbox_events (
                id, event_id, event_name, aggregate_type, aggregate_id, payload, status,
                target_user_id, target_organization_id, dedupe_key, channel_hint
            )
            VALUES (
                %s, %s, 'product_candidate_created', 'PRODUCT_CANDIDATE', %s, %s, 'PENDING',
                %s, %s, %s, 'INBOX'
            )
            ON CONFLICT (event_name, dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING
            """,
            (
                str(uuid4()),
                str(uuid4()),
                candidate_id,
                Json({
                    "candidate_id": candidate_id,
                    "vendor_id": vendor_id,
                    "barcode": normalized_barcode,
                    "vendor_sku": normalized_vendor_sku,
                    "status": "PENDING_REVIEW",
                }),
                str(vendor["user_id"]),
                str(self.context.organization_id),
                "PRODUCT_CANDIDATE_CREATED:" + candidate_id,
            ),
        )
        return {
            "candidate_id": candidate_id,
            "vendor_product_id": vendor_product_id,
            "status": row["status"],
            "listing_status": "DRAFT_PENDING_CATALOG" if vendor_product_id else None,
            "idempotent_replay": False,
            "message": "کاندیدا با موفقیت ثبت شد و در کارتابل بررسی تیم کاتالوگ قرار گرفت.",
        }

    def admin_product_candidates_list(self, *, status="PENDING_REVIEW", query=None, offset=0, limit=50):
        self._require_catalog_admin()
        allowed = {"PENDING_REVIEW", "APPROVED_CANONICAL", "MERGED_EXISTING", "REJECTED"}
        if status and status not in allowed:
            raise ValueError("Invalid candidate status.")
        params = []
        clauses = ["1=1"]
        if status:
            clauses.append("pc.status=%s")
            params.append(status)
        if query:
            needle = "%" + query.strip() + "%"
            clauses.append("(pc.proposed_title ILIKE %s OR COALESCE(pc.proposed_brand,'') ILIKE %s OR COALESCE(pc.barcode,'') ILIKE %s OR COALESCE(pc.vendor_sku,'') ILIKE %s)")
            params.extend([needle, needle, needle, needle])
        where = " AND ".join(clauses)
        params.extend([limit, offset])
        self.cur.execute(
            f"""
            SELECT
                pc.id AS candidate_id,
                pc.vendor_id,
                v.business_name AS vendor_name,
                pc.proposed_title,
                pc.proposed_brand,
                pc.barcode,
                pc.vendor_sku,
                pc.photo_asset_id,
                pc.status,
                pc.resolved_product_id,
                pc.reviewed_by_user_id,
                pc.review_notes,
                pc.created_at,
                pc.resolved_at
            FROM product_candidates pc
            JOIN vendors v ON v.id=pc.vendor_id
            WHERE {where}
            ORDER BY
                CASE pc.status WHEN 'PENDING_REVIEW' THEN 0 ELSE 1 END,
                pc.created_at ASC,
                pc.id
            LIMIT %s OFFSET %s
            """,
            tuple(params),
        )
        rows=[]
        for row in self.cur.fetchall():
            item=dict(row)
            for key in ("candidate_id","vendor_id","photo_asset_id","resolved_product_id","reviewed_by_user_id"):
                if item.get(key):
                    item[key]=str(item[key])
            for key in ("created_at","resolved_at"):
                if item.get(key):
                    item[key]=item[key].isoformat()
            rows.append(item)
        return {"candidates": rows, "status": status, "limit": limit, "offset": offset}

    def admin_product_candidate_review(
        self,
        *,
        candidate_id,
        action,
        reason,
        brand_id=None,
        category_id=None,
        subcategory_id=None,
        canonical_name_fa=None,
        target_product_id=None,
    ):
        self._require_catalog_admin()
        if not reason or not reason.strip():
            raise ValueError("Review reason is required.")
        if action not in {"APPROVE_CANONICAL", "MERGE_EXISTING", "REJECT"}:
            raise ValueError("Unsupported candidate review action.")

        self.cur.execute(
            """
            SELECT pc.*, v.organization_id AS vendor_organization_id, v.user_id AS vendor_user_id
            FROM product_candidates pc
            JOIN vendors v ON v.id=pc.vendor_id
            WHERE pc.id=%s
            FOR UPDATE
            """,
            (candidate_id,),
        )
        candidate=self.cur.fetchone()
        if not candidate:
            raise KeyError("Product candidate not found.")
        if candidate["status"] != "PENDING_REVIEW":
            return {
                "candidate_id": str(candidate["id"]),
                "status": candidate["status"],
                "resolved_product_id": str(candidate["resolved_product_id"]) if candidate["resolved_product_id"] else None,
                "idempotent_replay": True,
            }

        resolved_product_id=None
        if action == "MERGE_EXISTING":
            if not target_product_id:
                raise ValueError("target_product_id is required for MERGE_EXISTING.")
            self.cur.execute(
                "SELECT id FROM products WHERE id=%s AND is_active=TRUE FOR UPDATE",
                (target_product_id,),
            )
            if not self.cur.fetchone():
                raise KeyError("Target product not found or inactive.")
            resolved_product_id=str(target_product_id)
        elif action == "APPROVE_CANONICAL":
            for field_name, field_value in (
                ("brand_id", brand_id), ("category_id", category_id), ("subcategory_id", subcategory_id)
            ):
                if not field_value:
                    raise ValueError(field_name + " is required for APPROVE_CANONICAL.")
            name = (canonical_name_fa or candidate["proposed_title"] or "").strip()
            if not name:
                raise ValueError("canonical_name_fa is required for APPROVE_CANONICAL.")

            self.cur.execute(
                "SELECT 1 FROM brands WHERE id=%s",
                (brand_id,),
            )
            if not self.cur.fetchone():
                raise KeyError("Brand not found.")
            self.cur.execute(
                "SELECT 1 FROM categories WHERE id=%s",
                (category_id,),
            )
            if not self.cur.fetchone():
                raise KeyError("Category not found.")
            self.cur.execute(
                "SELECT 1 FROM subcategories WHERE id=%s AND category_id=%s",
                (subcategory_id, category_id),
            )
            if not self.cur.fetchone():
                raise ValueError("Subcategory does not belong to the selected category.")

            master_sku = None
            for _ in range(5):
                probe = "POL-PRD-" + uuid4().hex[:10].upper()
                self.cur.execute("SELECT 1 FROM products WHERE master_sku=%s", (probe,))
                if not self.cur.fetchone():
                    master_sku=probe
                    break
            if not master_sku:
                raise RuntimeError("Unable to allocate a unique master SKU.")

            self.cur.execute(
                """
                INSERT INTO products
                    (id,master_sku,canonical_name_fa,brand_id,category_id,subcategory_id,
                     is_active,is_verified)
                VALUES (%s,%s,%s,%s,%s,%s,TRUE,TRUE)
                RETURNING id
                """,
                (str(uuid4()), master_sku, name, brand_id, category_id, subcategory_id),
            )
            resolved_product_id=str(self.cur.fetchone()["id"])

        if candidate["vendor_sku"]:
            self.cur.execute(
                """
                UPDATE vendor_products
                SET product_id=%s,
                    listing_status=CASE WHEN %s='REJECT' THEN 'SUSPENDED' ELSE 'ACTIVE' END,
                    is_active=CASE WHEN %s='REJECT' THEN FALSE ELSE TRUE END,
                    updated_at=now()
                WHERE candidate_id=%s
                """,
                (resolved_product_id, action, action, candidate_id),
            )

        if action == "APPROVE_CANONICAL" and candidate["barcode"]:
            normalized = "".join(ch for ch in str(candidate["barcode"]) if ch.isalnum())
            self.cur.execute(
                "SELECT id, product_id FROM product_identifiers WHERE identifier_value=%s FOR UPDATE",
                (normalized,),
            )
            existing_identifier=self.cur.fetchone()
            if existing_identifier and str(existing_identifier["product_id"]) != str(resolved_product_id):
                raise ValueError("Barcode already belongs to a different canonical product.")
            if not existing_identifier:
                identifier_type = "EAN13" if normalized.isdigit() and len(normalized)==13 else ("UPC_A" if normalized.isdigit() and len(normalized)==12 else "INTERNAL_BARCODE")
                self.cur.execute(
                    """
                    INSERT INTO product_identifiers
                        (product_id,vendor_id,identifier_scope,identifier_type,identifier_value,
                         packaging_scope,source,confidence_score,is_primary)
                    VALUES (%s,NULL,'GLOBAL',%s,%s,'UNIT','CATALOG_REVIEW',1.00,TRUE)
                    """,
                    (resolved_product_id, identifier_type, normalized),
                )

        new_status = "APPROVED_CANONICAL" if action == "APPROVE_CANONICAL" else ("MERGED_EXISTING" if action == "MERGE_EXISTING" else "REJECTED")
        self.cur.execute(
            """
            UPDATE product_candidates
            SET status=%s,
                resolved_product_id=%s,
                reviewed_by_user_id=%s,
                review_notes=%s,
                resolved_at=now()
            WHERE id=%s
            RETURNING id,status,resolved_product_id,reviewed_by_user_id,resolved_at
            """,
            (new_status, resolved_product_id, self.context.user_id, reason.strip(), candidate_id),
        )
        reviewed=dict(self.cur.fetchone())

        self.cur.execute(
            """
            INSERT INTO admin_audit_logs
                (actor_user_id, action, target_entity_type, target_entity_id,
                 state_after, reason, correlation_id)
            VALUES (%s,'PRODUCT_CANDIDATE_REVIEWED','PRODUCT_CANDIDATE',%s,%s,%s,%s)
            """,
            (
                self.context.user_id,
                candidate_id,
                Json({
                    "status": new_status,
                    "resolved_product_id": resolved_product_id,
                    "action": action,
                }),
                reason.strip(),
                self.context.correlation_id,
            ),
        )

        self.cur.execute(
            """
            INSERT INTO outbox_events
                (id,event_id,event_name,aggregate_type,aggregate_id,payload,status,
                 target_user_id,target_organization_id,dedupe_key,channel_hint)
            VALUES
                (gen_random_uuid(),gen_random_uuid(),'PRODUCT_CANDIDATE_REVIEWED',
                 'PRODUCT_CANDIDATE',%s,%s,'PENDING',%s,%s,%s,'INBOX')
            ON CONFLICT (event_name,dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING
            """,
            (
                candidate_id,
                Json({
                    "candidate_id": candidate_id,
                    "status": new_status,
                    "resolved_product_id": resolved_product_id,
                    "reviewed_by_user_id": str(self.context.user_id),
                }),
                candidate["vendor_user_id"],
                candidate["vendor_organization_id"],
                "PRODUCT_CANDIDATE_REVIEWED:" + str(candidate_id),
            ),
        )
        return {
            "candidate_id": str(reviewed["id"]),
            "status": reviewed["status"],
            "resolved_product_id": str(reviewed["resolved_product_id"]) if reviewed["resolved_product_id"] else None,
            "reviewed_by_user_id": str(reviewed["reviewed_by_user_id"]) if reviewed["reviewed_by_user_id"] else None,
            "resolved_at": reviewed["resolved_at"].isoformat() if reviewed["resolved_at"] else None,
            "idempotent_replay": False,
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

    def catalog_barcode_match(
        self,
        *,
        barcode: str,
        proposed_title: str | None = None,
        vendor_sku: str | None = None,
        packaging_unit: str = "UNIT",
        pack_quantity: int = 1,
        create_candidate: bool = False,
    ):
        normalized = "".join(ch for ch in (barcode or "").strip() if ch.isalnum())
        if not normalized or len(normalized) < 8 or len(normalized) > 32:
            raise ValueError("Barcode must contain between 8 and 32 alphanumeric characters.")
        if pack_quantity < 1:
            raise ValueError("pack_quantity must be positive.")

        vendor = self._current_vendor_for_context() if self.context.organization_id else None
        vendor_id = str(vendor["id"]) if vendor else None

        self.cur.execute(
            """
            SELECT DISTINCT
                pi.id AS identifier_id,
                pi.identifier_type,
                pi.identifier_value,
                pi.identifier_scope,
                pi.packaging_scope,
                pi.source,
                pi.confidence_score,
                p.id AS product_id,
                p.master_sku,
                p.canonical_name_fa,
                p.base_unit,
                p.default_pack_unit,
                p.default_pack_quantity,
                b.name_fa AS brand_name
            FROM product_identifiers pi
            JOIN products p ON p.id = pi.product_id
            LEFT JOIN brands b ON b.id = p.brand_id
            WHERE pi.identifier_value = %s
              AND p.is_active = TRUE
              AND (
                    pi.vendor_id IS NULL
                    OR pi.vendor_id = %s::uuid
              )
            ORDER BY
                CASE WHEN pi.vendor_id IS NULL THEN 0 ELSE 1 END,
                pi.confidence_score DESC,
                pi.id
            """,
            (normalized, vendor_id),
        )
        matches = [dict(row) for row in self.cur.fetchall()]

        product_ids = {str(row["product_id"]) for row in matches}
        if len(product_ids) == 1:
            row = matches[0]
            return {
                "match_type": "EXACT",
                "confidence_score": float(row["confidence_score"]),
                "product": {
                    "id": str(row["product_id"]),
                    "master_sku": row["master_sku"],
                    "canonical_name_fa": row["canonical_name_fa"],
                    "brand_name": row["brand_name"],
                    "base_unit": row["base_unit"],
                    "default_pack_unit": row["default_pack_unit"],
                    "default_pack_quantity": row["default_pack_quantity"],
                },
                "identifier": {
                    "id": str(row["identifier_id"]),
                    "identifier_type": row["identifier_type"],
                    "identifier_value": row["identifier_value"],
                    "identifier_scope": row["identifier_scope"],
                    "packaging_scope": row["packaging_scope"],
                    "source": row["source"],
                },
                "candidate_id": None,
                "vendor_product_id": None,
            }

        if len(product_ids) > 1:
            return {
                "match_type": "AMBIGUOUS",
                "confidence_score": 0.0,
                "products": [
                    {
                        "id": str(row["product_id"]),
                        "master_sku": row["master_sku"],
                        "canonical_name_fa": row["canonical_name_fa"],
                        "brand_name": row["brand_name"],
                    }
                    for row in matches
                ],
                "candidate_id": None,
                "vendor_product_id": None,
            }

        if not create_candidate:
            return {
                "match_type": "NO_MATCH",
                "confidence_score": 0.0,
                "product": None,
                "candidate_id": None,
                "vendor_product_id": None,
            }

        if not vendor_id:
            raise PermissionError("Creating an unmatched barcode candidate requires an active vendor context.")
        if not proposed_title or not proposed_title.strip():
            raise ValueError("proposed_title is required when creating a barcode candidate.")

        candidate_vendor_sku = vendor_sku.strip() if vendor_sku and vendor_sku.strip() else None
        existing_vp = None
        if candidate_vendor_sku:
            self.cur.execute(
                """
                SELECT vp.id, vp.product_id, vp.candidate_id, vp.listing_status,
                       pc.barcode AS candidate_barcode
                FROM vendor_products vp
                LEFT JOIN product_candidates pc ON pc.id = vp.candidate_id
                WHERE vp.vendor_id=%s AND vp.vendor_sku=%s
                FOR UPDATE
                """,
                (vendor_id, candidate_vendor_sku),
            )
            existing_vp = self.cur.fetchone()
        if existing_vp and existing_vp["product_id"]:
            raise ValueError("vendor_sku is already bound to a canonical product.")
        if existing_vp and existing_vp["candidate_id"]:
            if existing_vp["candidate_barcode"] not in (None, normalized):
                raise ValueError("vendor_sku is already bound to a different barcode candidate.")
            candidate_id = str(existing_vp["candidate_id"])
            return {
                "match_type": "NO_MATCH",
                "confidence_score": 0.0,
                "product": None,
                "candidate_id": candidate_id,
                "vendor_product_id": str(existing_vp["id"]),
                "listing_status": existing_vp["listing_status"],
                "idempotent_replay": True,
            }

        self.cur.execute(
            """
            SELECT id
            FROM product_candidates
            WHERE vendor_id=%s
              AND barcode=%s
              AND status='PENDING_REVIEW'
            ORDER BY created_at DESC
            LIMIT 1
            FOR UPDATE
            """,
            (vendor_id, normalized),
        )
        candidate = self.cur.fetchone()
        candidate_replayed = bool(candidate)
        candidate_created = False
        if candidate:
            candidate_id = str(candidate["id"])
        else:
            candidate_id = str(uuid4())
            self.cur.execute(
                """
                INSERT INTO product_candidates
                    (id,vendor_id,proposed_title,barcode,vendor_sku,status)
                VALUES (%s,%s,%s,%s,%s,'PENDING_REVIEW')
                ON CONFLICT (vendor_id, barcode)
                    WHERE barcode IS NOT NULL AND status='PENDING_REVIEW'
                DO NOTHING
                RETURNING id
                """,
                (
                    candidate_id,
                    vendor_id,
                    proposed_title.strip(),
                    normalized,
                    candidate_vendor_sku,
                ),
            )
            inserted = self.cur.fetchone()
            if inserted:
                candidate_created = True
                candidate_id = str(inserted["id"])
            else:
                candidate_replayed = True
                self.cur.execute(
                    """
                    SELECT id
                    FROM product_candidates
                    WHERE vendor_id=%s
                      AND barcode=%s
                      AND status='PENDING_REVIEW'
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (vendor_id, normalized),
                )
                candidate = self.cur.fetchone()
                if not candidate:
                    raise RuntimeError(
                        "Concurrent barcode candidate insert conflicted but the winning candidate could not be re-read."
                    )
                candidate_id = str(candidate["id"])

        vendor_product_id = None
        listing_status = None
        vendor_product_created = False
        if candidate_vendor_sku:
            vendor_product_id = str(uuid4())
            self.cur.execute(
                """
                INSERT INTO vendor_products
                    (id,vendor_id,product_id,candidate_id,vendor_sku,
                     packaging_unit,pack_quantity,sales_unit,is_active,listing_status)
                VALUES (%s,%s,NULL,%s,%s,%s,%s,%s,FALSE,'DRAFT_PENDING_CATALOG')
                ON CONFLICT (vendor_id, vendor_sku)
                DO NOTHING
                RETURNING id, listing_status
                """,
                (
                    vendor_product_id,
                    vendor_id,
                    candidate_id,
                    candidate_vendor_sku,
                    packaging_unit.strip(),
                    int(pack_quantity),
                    packaging_unit.strip(),
                ),
            )
            inserted_vp = self.cur.fetchone()
            if inserted_vp:
                vendor_product_created = True
                vendor_product_id = str(inserted_vp["id"])
                listing_status = inserted_vp["listing_status"]
            else:
                self.cur.execute(
                    """
                    SELECT vp.id, vp.product_id, vp.candidate_id, vp.listing_status,
                           pc.barcode AS candidate_barcode
                    FROM vendor_products vp
                    LEFT JOIN product_candidates pc ON pc.id = vp.candidate_id
                    WHERE vp.vendor_id=%s AND vp.vendor_sku=%s
                    FOR UPDATE
                    """,
                    (vendor_id, candidate_vendor_sku),
                )
                winner_vp = self.cur.fetchone()
                if not winner_vp:
                    raise RuntimeError(
                        "Concurrent vendor SKU insert conflicted but the winning vendor product could not be re-read."
                    )
                if winner_vp["product_id"]:
                    raise ValueError("vendor_sku is already bound to a canonical product.")
                if str(winner_vp["candidate_id"]) != candidate_id:
                    raise ValueError("vendor_sku is already bound to a different product candidate.")
                if winner_vp["candidate_barcode"] not in (None, normalized):
                    raise ValueError("vendor_sku is already bound to a different barcode candidate.")
                vendor_product_id = str(winner_vp["id"])
                listing_status = winner_vp["listing_status"]
                candidate_replayed = True

        if candidate_created:
            self.cur.execute(
                """
                INSERT INTO outbox_events
                    (id,event_id,event_name,aggregate_type,aggregate_id,payload,status,
                     target_user_id,target_organization_id,dedupe_key,channel_hint)
                VALUES
                    (gen_random_uuid(),gen_random_uuid(),'product_candidate_created',
                     'PRODUCT_CANDIDATE',%s,
                     jsonb_build_object(
                        'candidate_id',%s,
                        'vendor_id',%s,
                        'barcode',%s,
                        'vendor_sku',%s,
                        'proposed_title',%s
                     ),
                     'PENDING',%s,%s,%s,'INBOX')
                ON CONFLICT (event_name,dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING
                """,
                (
                    candidate_id,
                    candidate_id,
                    vendor_id,
                    normalized,
                    candidate_vendor_sku,
                    proposed_title.strip(),
                    str(vendor_id),
                    str(self.context.organization_id),
                    "PRODUCT_CANDIDATE_CREATED:" + candidate_id,
                ),
            )

        return {
            "match_type": "NO_MATCH",
            "confidence_score": 0.0,
            "product": None,
            "candidate_id": candidate_id,
            "vendor_product_id": vendor_product_id,
            "listing_status": listing_status,
            "idempotent_replay": candidate_replayed and not vendor_product_created,
        }

    def catalog_categories_public(self):
        self.cur.execute(
            """
            SELECT c.id, c.name_fa, c.slug, c.icon_url, c.display_order,
                   COALESCE(json_agg(json_build_object('id', sc.id, 'name_fa', sc.name_fa, 'slug', sc.slug, 'display_order', sc.display_order)
                                      ORDER BY sc.display_order, sc.name_fa) FILTER (WHERE sc.id IS NOT NULL), '[]'::json) AS subcategories
            FROM categories c
            LEFT JOIN subcategories sc ON sc.category_id=c.id
            GROUP BY c.id, c.name_fa, c.slug, c.icon_url, c.display_order
            ORDER BY c.display_order, c.name_fa
            """
        )
        return self.cur.fetchall()

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
            WHERE pm.product_id = %s::uuid
              AND ma.status = 'READY'
              AND ma.provenance IN ('VENDOR_UPLOADED', 'MANUFACTURER_PROVIDED', 'POL_OWNED')
              AND pm.approval_status = 'APPROVED'
              AND pm.approval_status <> 'PRIVATE_REFERENCE'
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

    def vendor_inventory_continuous_scan(
        self,
        *,
        product_id: str,
        vendor_sku: str,
        packaging_unit: str,
        pack_quantity: int,
        physical_quantity: int,
        unit_price_toman: int,
        consumer_price_per_unit_toman: int | None,
        session_id: str,
    ):
        if not self.context.organization_id:
            raise PermissionError("Inventory scan requires an active organization context.")
        if pack_quantity < 1 or physical_quantity < 0 or unit_price_toman <= 0:
            raise ValueError("Invalid pack quantity, physical quantity, or unit price.")
        vendor = self._current_vendor_for_context()
        if not vendor:
            raise PermissionError("Active vendor membership required.")

        self.cur.execute(
            "SELECT id FROM products WHERE id=%s::uuid AND is_active=TRUE",
            (product_id,),
        )
        if not self.cur.fetchone():
            raise KeyError("Master product not found or inactive.")

        self.cur.execute(
            """
            SELECT id, product_id, packaging_unit, pack_quantity, listing_status
            FROM vendor_products
            WHERE vendor_id=%s AND vendor_sku=%s
            FOR UPDATE
            """,
            (vendor["id"], vendor_sku.strip()),
        )
        vp = self.cur.fetchone()
        if vp:
            if str(vp["product_id"]) != str(product_id):
                raise ValueError("vendor_sku is already bound to another master product.")
            if vp["packaging_unit"] != packaging_unit or int(vp["pack_quantity"]) != int(pack_quantity):
                raise ValueError("Existing vendor SKU packaging does not match the scan contract.")
            vendor_product_id = str(vp["id"])
            if vp["listing_status"] == "SUSPENDED":
                raise ValueError("Suspended vendor product cannot be updated by scan.")
        else:
            vendor_product_id = str(uuid4())
            self.cur.execute(
                """
                INSERT INTO vendor_products
                    (id,vendor_id,product_id,vendor_sku,packaging_unit,pack_quantity,sales_unit,is_active,listing_status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,TRUE,'DRAFT_PENDING_CATALOG')
                RETURNING id
                """,
                (vendor_product_id, vendor["id"], product_id, vendor_sku.strip(),
                 packaging_unit, int(pack_quantity), packaging_unit),
            )

        self.cur.execute(
            """
            INSERT INTO inventory_scan_sessions
                (vendor_id,external_session_id,created_by_user_id,status)
            VALUES (%s,%s,%s,'DRAFT')
            ON CONFLICT (vendor_id,external_session_id)
            DO UPDATE SET created_by_user_id=EXCLUDED.created_by_user_id
            RETURNING id,status
            """,
            (vendor["id"], session_id.strip(), self.context.user_id),
        )
        session = self.cur.fetchone()
        if session["status"] != "DRAFT":
            raise ValueError("Inventory scan session is already closed.")

        self.cur.execute(
            """
            INSERT INTO inventory_scan_session_items
                (session_id,vendor_product_id,physical_quantity,unit_price_toman,consumer_price_per_unit_toman)
            VALUES (%s,%s,%s,%s,%s)
            ON CONFLICT (session_id,vendor_product_id)
            DO UPDATE SET
                physical_quantity=EXCLUDED.physical_quantity,
                unit_price_toman=EXCLUDED.unit_price_toman,
                consumer_price_per_unit_toman=EXCLUDED.consumer_price_per_unit_toman,
                updated_at=now()
            RETURNING id
            """,
            (session["id"], vendor_product_id, physical_quantity, unit_price_toman,
             consumer_price_per_unit_toman),
        )

        self.cur.execute(
            """
            SELECT physical_quantity, reserved_quantity
            FROM vendor_inventory
            WHERE vendor_product_id=%s
            FOR UPDATE
            """,
            (vendor_product_id,),
        )
        inv = self.cur.fetchone()
        old_qty = int(inv["physical_quantity"]) if inv else 0
        reserved = int(inv["reserved_quantity"]) if inv else 0
        if inv and physical_quantity < reserved:
            raise ValueError("Physical quantity cannot be below currently reserved quantity.")

        if inv:
            self.cur.execute(
                """
                UPDATE vendor_inventory
                SET physical_quantity=%s, updated_at=now(),
                    freshness_status='FRESH',
                    inventory_confidence='CONFIRMED_TODAY',
                    verification_source='CONTINUOUS_SCAN',
                    last_confirmed_at=now()
                WHERE vendor_product_id=%s
                """,
                (physical_quantity, vendor_product_id),
            )
        else:
            self.cur.execute(
                """
                INSERT INTO vendor_inventory
                    (vendor_product_id,inventory_unit,physical_quantity,reserved_quantity,freshness_status,
                     inventory_confidence,verification_source,last_confirmed_at)
                VALUES (%s,%s,%s,0,'FRESH','CONFIRMED_TODAY','CONTINUOUS_SCAN',now())
                """,
                (vendor_product_id, packaging_unit, physical_quantity),
            )

        self.cur.execute(
            """
            UPDATE vendor_prices
            SET is_current=FALSE,effective_to=now()
            WHERE vendor_product_id=%s AND is_current=TRUE
            """,
            (vendor_product_id,),
        )
        self.cur.execute(
            """
            INSERT INTO vendor_prices
                (vendor_product_id,price_toman,consumer_price_per_unit_toman,is_current,effective_from)
            VALUES (%s,%s,%s,TRUE,now())
            """,
            (vendor_product_id, unit_price_toman, consumer_price_per_unit_toman),
        )
        self.cur.execute(
            """
            INSERT INTO inventory_audit_log
                (vendor_id,vendor_product_id,old_quantity,new_quantity,old_price_toman,new_price_toman,
                 source_trigger,reference_id,actor_user_id)
            VALUES (%s,%s,%s,%s,
                    (SELECT price_toman FROM vendor_prices WHERE vendor_product_id=%s AND is_current=FALSE ORDER BY effective_to DESC NULLS LAST LIMIT 1),
                    %s,'BARCODE_SCAN',%s,%s)
            """,
            (vendor["id"],vendor_product_id,old_qty,physical_quantity,vendor_product_id,
             unit_price_toman,session_id.strip(),self.context.user_id),
        )
        return {
            "vendor_product_id": vendor_product_id,
            "available_quantity": physical_quantity - reserved,
            "inventory_unit": packaging_unit,
            "unit_price_toman": unit_price_toman,
            "freshness_status": "FRESH",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id.strip(),
            "listing_status": "DRAFT_PENDING_CATALOG",
        }

    def vendor_inventory_publish(self, *, session_id: str):
        if not self.context.organization_id:
            raise PermissionError("Inventory publish requires an active organization context.")
        vendor = self._current_vendor_for_context()
        if not vendor:
            raise PermissionError("Active vendor membership required.")

        self.cur.execute(
            """
            SELECT id,status
            FROM inventory_scan_sessions
            WHERE vendor_id=%s AND external_session_id=%s
            FOR UPDATE
            """,
            (vendor["id"], session_id.strip()),
        )
        session = self.cur.fetchone()
        if not session:
            raise KeyError("Inventory scan session not found.")
        if session["status"] == "PUBLISHED":
            self.cur.execute(
                "SELECT COUNT(*)::INT AS count FROM inventory_scan_session_items WHERE session_id=%s",
                (session["id"],),
            )
            return {"session_id": session_id.strip(), "status": "PUBLISHED",
                    "published_count": int(self.cur.fetchone()["count"]), "idempotent_replay": True}
        if session["status"] != "DRAFT":
            raise ValueError("Inventory scan session cannot be published from its current state.")

        self.cur.execute(
            "SELECT vendor_product_id,physical_quantity,unit_price_toman FROM inventory_scan_session_items WHERE session_id=%s FOR UPDATE",
            (session["id"],),
        )
        items = self.cur.fetchall()
        if not items:
            raise ValueError("Inventory scan session contains no items.")

        published = 0
        for item in items:
            self.cur.execute(
                """
                UPDATE vendor_products
                SET listing_status='ACTIVE', is_active=TRUE, updated_at=now()
                WHERE id=%s
                  AND vendor_id=%s
                  AND listing_status='DRAFT_PENDING_CATALOG'
                RETURNING id
                """,
                (item["vendor_product_id"],vendor["id"]),
            )
            if self.cur.fetchone():
                published += 1
            self.cur.execute(
                """
                INSERT INTO inventory_audit_log
                    (vendor_id,vendor_product_id,old_quantity,new_quantity,new_price_toman,source_trigger,reference_id,actor_user_id)
                SELECT %s,vi.vendor_product_id,vi.physical_quantity,vi.physical_quantity,%s,'SESSION_PUBLISH',%s,%s
                FROM vendor_inventory vi
                WHERE vi.vendor_product_id=%s
                """,
                (vendor["id"],item["vendor_product_id"],session_id.strip(),self.context.user_id,item["vendor_product_id"]),
            )

        self.cur.execute(
            """
            UPDATE inventory_scan_sessions
            SET status='PUBLISHED',published_at=now()
            WHERE id=%s
            RETURNING status,published_at
            """,
            (session["id"],),
        )
        done = self.cur.fetchone()
        return {
            "session_id": session_id.strip(),
            "status": done["status"],
            "published_count": published,
            "published_at": done["published_at"].isoformat(),
            "idempotent_replay": False,
        }

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

    def referral_create(self, *, referral_code=None, max_redemptions=None, expires_at=None):
        """Create a vendor referral through the canonical D-016 service."""
        if not self.context.organization_id:
            raise PermissionError("Referral creation requires an organization context.")

        self.cur.execute(
            """
            SELECT v.id
            FROM vendors v
            JOIN organizations o ON o.id = v.organization_id
            JOIN organization_memberships om
              ON om.organization_id = v.organization_id
             AND om.user_id = %s
             AND om.status = 'ACTIVE'
             AND om.role IN ('VENDOR_OWNER','VENDOR_STAFF')
            WHERE v.organization_id = %s
              AND v.status = 'ACTIVE'
              AND o.org_type = 'VENDOR'
              AND o.status = 'ACTIVE'
            ORDER BY v.id
            LIMIT 1
            """,
            (self.context.user_id, self.context.organization_id),
        )
        vendor = self.cur.fetchone()
        if not vendor:
            raise PermissionError("Only active vendor members may create referrals.")

        return VendorReferralService.create_referral(
            self.cur,
            self.context.user_id,
            str(vendor["id"]),
            referral_code=referral_code,
            max_redemptions=max_redemptions,
            expires_at=expires_at,
        )

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
        """Redeem a vendor referral as first-touch attribution for the current retailer."""
        if not self.context.organization_id:
            raise PermissionError("Referral redemption requires an organization context.")

        self.cur.execute(
            """
            SELECT r.id AS retailer_id
            FROM retailers r
            JOIN organizations o ON o.id=r.organization_id
            JOIN organization_memberships om
              ON om.organization_id=r.organization_id
             AND om.user_id=%s
             AND om.status='ACTIVE'
             AND om.role IN ('RETAILER_OWNER','RETAILER_STAFF')
            WHERE r.organization_id=%s
              AND o.status='ACTIVE'
            ORDER BY r.id
            LIMIT 1
            """,
            (self.context.user_id, self.context.organization_id),
        )
        retailer = self.cur.fetchone()
        if not retailer:
            raise PermissionError("Referral redemption requires an active retailer membership.")

        self.cur.execute(
            """
            SELECT vr.id, vr.vendor_id, vr.referral_code, vr.status
            FROM vendor_referrals vr
            JOIN vendors v ON v.id=vr.vendor_id
            JOIN organizations o ON o.id=v.organization_id
            WHERE vr.id=%s
              AND o.status='ACTIVE'
            FOR UPDATE
            """,
            (referral_id,),
        )
        referral = self.cur.fetchone()
        if not referral:
            raise KeyError("Referral not found.")

        request_key = (
            f"HTTP_REFERRAL_REDEEM:{str(referral_id)}:"
            f"{str(retailer['retailer_id'])}"
        )
        return VendorReferralService.redeem_referral(
            self.cur,
            self.context.user_id,
            str(retailer["retailer_id"]),
            referral["referral_code"],
            request_key,
        )

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
            allowed_next = FIELD_TASK_TRANSITIONS.get(task["status"], set())
            if status != task["status"] and status not in allowed_next:
                raise ValueError(
                    f"Invalid field task transition: {task['status']} -> {status}."
                )
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

    def field_task_create(
        self,
        *,
        task_type,
        assigned_to_user_id,
        retailer_id=None,
        vendor_id=None,
        target_organization_id=None,
        notes=None,
    ):
        """Create a field task (admin/operator only) with an explicit target entity."""
        self._require_ops_context()

        if retailer_id and vendor_id:
            raise ValueError("A field task cannot target both a retailer and a vendor.")
        if target_organization_id and (retailer_id or vendor_id):
            raise ValueError("Use retailer_id/vendor_id or target_organization_id, not both.")

        self.cur.execute(
            "SELECT id, is_active FROM users WHERE id = %s",
            (assigned_to_user_id,),
        )
        assigned = self.cur.fetchone()
        if not assigned:
            raise ValueError("Assigned user not found.")
        if not assigned["is_active"]:
            raise ValueError("Assigned user is inactive.")

        resolved_target_organization_id = target_organization_id
        if retailer_id:
            self.cur.execute(
                """
                SELECT r.organization_id
                FROM retailers r
                JOIN organizations o ON o.id = r.organization_id
                WHERE r.id = %s
                  AND o.status = 'ACTIVE'
                """,
                (retailer_id,),
            )
            target = self.cur.fetchone()
            if not target:
                raise KeyError("Target retailer not found or inactive.")
            resolved_target_organization_id = str(target["organization_id"])

        if vendor_id:
            self.cur.execute(
                """
                SELECT v.organization_id
                FROM vendors v
                JOIN organizations o ON o.id = v.organization_id
                WHERE v.id = %s
                  AND v.status = 'ACTIVE'
                  AND o.status = 'ACTIVE'
                """,
                (vendor_id,),
            )
            target = self.cur.fetchone()
            if not target:
                raise KeyError("Target vendor not found or inactive.")
            resolved_target_organization_id = str(target["organization_id"])

        if resolved_target_organization_id:
            self.cur.execute(
                "SELECT id FROM organizations WHERE id=%s AND status='ACTIVE'",
                (resolved_target_organization_id,),
            )
            if not self.cur.fetchone():
                raise KeyError("Target organization not found or inactive.")

        self.cur.execute(
            """
            INSERT INTO field_tasks (task_type, assigned_to_user_id, target_organization_id, notes)
            VALUES (%s, %s, %s, %s)
            RETURNING id, task_type, target_organization_id, assigned_to_user_id,
                      status, due_date, completed_at, notes, created_at, updated_at
            """,
            (task_type, assigned_to_user_id, resolved_target_organization_id, notes),
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

    # ── Catalog Administration (Stage 41) ───────────────────────────

    def admin_category_create(self, *, name_fa, slug, icon_url=None, display_order=0):
        self._require_catalog_admin()
        if not name_fa or not name_fa.strip():
            raise ValueError("Category name is required.")
        if not slug or not slug.strip():
            raise ValueError("Category slug is required.")
        if int(display_order) < 0:
            raise ValueError("display_order cannot be negative.")
        self.cur.execute(
            """
            INSERT INTO categories (id,name_fa,slug,icon_url,display_order)
            VALUES (%s,%s,%s,%s,%s)
            RETURNING id,name_fa,slug,icon_url,display_order,created_at
            """,
            (str(uuid4()), name_fa.strip(), slug.strip(), icon_url, int(display_order)),
        )
        row = dict(self.cur.fetchone())
        row["id"] = str(row["id"])
        row["created_at"] = row["created_at"].isoformat()
        return row

    def admin_category_update(self, *, category_id, name_fa=None, slug=None, icon_url=None, display_order=None):
        self._require_catalog_admin()
        updates = []
        params = []
        if name_fa is not None:
            if not name_fa.strip():
                raise ValueError("Category name cannot be empty.")
            updates.append("name_fa=%s")
            params.append(name_fa.strip())
        if slug is not None:
            if not slug.strip():
                raise ValueError("Category slug cannot be empty.")
            updates.append("slug=%s")
            params.append(slug.strip())
        if icon_url is not None:
            updates.append("icon_url=%s")
            params.append(icon_url)
        if display_order is not None:
            if int(display_order) < 0:
                raise ValueError("display_order cannot be negative.")
            updates.append("display_order=%s")
            params.append(int(display_order))
        if not updates:
            raise ValueError("No category fields to update.")
        params.append(category_id)
        self.cur.execute(
            "UPDATE categories SET " + ", ".join(updates) +
            " WHERE id=%s RETURNING id,name_fa,slug,icon_url,display_order,created_at",
            tuple(params),
        )
        row = self.cur.fetchone()
        if not row:
            raise KeyError("Category not found.")
        result = dict(row)
        result["id"] = str(result["id"])
        result["created_at"] = result["created_at"].isoformat()
        return result

    # ── Ops Analytics (Stage 38) ───────────────────────────────────

    def ops_analytics(self, *, start_date, end_date):
        self._require_ops_context()
        if start_date > end_date:
            raise ValueError("start_date must be on or before end_date.")
        from scripts.pilot_kpis import compute_all_kpis

        kpis = compute_all_kpis(self.cur, start_date, end_date)
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "kpis": kpis,
        }

    def ops_analytics_week(self, *, snapshot_date):
        self._require_ops_context()
        from scripts.pilot_kpis import weekly_snapshot

        return weekly_snapshot(self.cur, snapshot_date)

    # ── Management / IAM Read & Mutation Surface ───────────────────

    def _require_vendor_management(self):
        if not self.context.organization_id:
            raise PermissionError("Vendor management requires an active organization context.")
        self.cur.execute(
            """
            SELECT om.role, o.org_type, o.status AS org_status
            FROM organization_memberships om
            JOIN organizations o ON o.id = om.organization_id
            WHERE om.user_id = %s
              AND om.organization_id = %s
              AND om.status = 'ACTIVE'
              AND o.org_type = 'VENDOR'
              AND o.status = 'ACTIVE'
            LIMIT 1
            """,
            (self.context.user_id, self.context.organization_id),
        )
        row = self.cur.fetchone()
        if not row or row["role"] not in ("VENDOR_OWNER", "VENDOR_STAFF"):
            raise PermissionError("Access denied: vendor membership required.")
        return row

    def _require_vendor_owner(self):
        row = self._require_vendor_management()
        if row["role"] != "VENDOR_OWNER":
            raise PermissionError("Only VENDOR_OWNER may manage staff.")
        return row

    def _require_admin_management(self):
        self._require_ops_context()
        self.cur.execute(
            """
            SELECT role
            FROM organization_memberships
            WHERE user_id = %s
              AND organization_id = %s
              AND status = 'ACTIVE'
            LIMIT 1
            """,
            (self.context.user_id, self.context.organization_id),
        )
        row = self.cur.fetchone()
        if not row or row["role"] not in ("SUPER_ADMIN", "OPS_ADMIN", "ADMIN_SUPER", "OPS_AGENT"):
            raise PermissionError("Administrative membership required.")
        return row

    def _require_super_admin(self):
        row = self._require_admin_management()
        if row["role"] not in ("SUPER_ADMIN", "ADMIN_SUPER"):
            raise PermissionError("SUPER_ADMIN authority required.")
        return row


    def _require_dispute_resolution_context(self):
        self._require_ops_context()
        self.cur.execute(
            """
            SELECT om.role
            FROM organization_memberships om
            JOIN organizations o ON o.id=om.organization_id
            WHERE om.user_id=%s
              AND om.organization_id=%s
              AND om.status='ACTIVE'
              AND o.org_type='OPERATOR'
              AND o.status='ACTIVE'
              AND om.role IN ('OPS_ADMIN','SUPER_ADMIN','ADMIN_SUPER')
            LIMIT 1
            """,
            (self.context.user_id, self.context.organization_id),
        )
        row = self.cur.fetchone()
        if not row:
            raise PermissionError("Dispute resolution requires OPS_ADMIN authority.")

    def _require_catalog_admin(self):
        row = self._require_admin_management()
        if row["role"] not in ("SUPER_ADMIN", "ADMIN_SUPER", "OPS_ADMIN"):
            raise PermissionError("Catalog administration requires SUPER_ADMIN or OPS_ADMIN.")
        return row

    def _require_broadcast_admin(self):
        row = self._require_admin_management()
        if row["role"] not in ("SUPER_ADMIN", "ADMIN_SUPER", "OPS_ADMIN"):
            raise PermissionError("Broadcast administration requires SUPER_ADMIN or OPS_ADMIN.")
        return row

    def vendor_customers_list(self, *, query=None, offset=0, limit=50):
        self._require_vendor_management()
        params: list = [self.context.organization_id]
        clauses = ["v.organization_id = %s", "o.order_status <> 'CANCELLED'"]
        if query:
            clauses.append("(r.store_name ILIKE %s OR u.full_name ILIKE %s OR u.phone_number ILIKE %s)")
            needle = f"%{query.strip()}%"
            params.extend([needle, needle, needle])
        where_sql = " AND ".join(clauses)
        params.extend([limit, offset])
        self.cur.execute(
            f"""
            SELECT
                r.id AS retailer_id,
                r.store_name,
                r.city,
                r.neighborhood,
                u.id AS user_id,
                u.full_name,
                u.phone_number,
                COUNT(o.id)::INT AS order_count,
                MAX(o.created_at) AS last_order_at
            FROM orders o
            JOIN vendors v ON v.id = o.vendor_id
            JOIN retailers r ON r.id = o.retailer_id
            JOIN users u ON u.id = r.user_id
            WHERE {where_sql}
            GROUP BY r.id, r.store_name, r.city, r.neighborhood, u.id, u.full_name, u.phone_number
            ORDER BY MAX(o.created_at) DESC, r.id
            LIMIT %s OFFSET %s
            """,
            tuple(params),
        )
        rows = [dict(x) for x in self.cur.fetchall()]
        return {"customers": rows, "limit": limit, "offset": offset}

    def vendor_staff_list(self, *, offset=0, limit=100):
        self._require_vendor_management()
        self.cur.execute(
            """
            SELECT
                m.id AS membership_id,
                m.user_id,
                u.phone_number,
                u.full_name,
                m.role,
                m.status,
                m.is_primary,
                m.created_at,
                m.updated_at
            FROM organization_memberships m
            JOIN users u ON u.id = m.user_id
            WHERE m.organization_id = %s
            ORDER BY
                CASE m.role WHEN 'VENDOR_OWNER' THEN 0 ELSE 1 END,
                m.created_at ASC
            LIMIT %s OFFSET %s
            """,
            (self.context.organization_id, limit, offset),
        )
        return {"members": [dict(x) for x in self.cur.fetchall()], "limit": limit, "offset": offset}

    def vendor_staff_invite(self, *, phone_number, full_name):
        self._require_vendor_owner()
        self.cur.execute(
            "SELECT id, is_active FROM users WHERE phone_number = %s LIMIT 1",
            (phone_number,),
        )
        user = self.cur.fetchone()
        if user and not user["is_active"]:
            raise ValueError("The target user account is inactive.")
        if not user:
            user_id = str(uuid4())
            self.cur.execute(
                """
                INSERT INTO users (id, phone_number, role, full_name, is_active)
                VALUES (%s, %s, 'VENDOR_STAFF', %s, TRUE)
                RETURNING id
                """,
                (user_id, phone_number, full_name),
            )
        else:
            user_id = str(user["id"])
            if full_name.strip():
                self.cur.execute(
                    "UPDATE users SET full_name=%s, updated_at=now() WHERE id=%s",
                    (full_name.strip(), user_id),
                )
        self.cur.execute(
            """
            SELECT id, status, role
            FROM organization_memberships
            WHERE organization_id=%s AND user_id=%s
            """,
            (self.context.organization_id, user_id),
        )
        existing = self.cur.fetchone()
        if existing:
            raise ValueError(f"User already has membership in this vendor organization ({existing['status']}).")
        membership_id = str(uuid4())
        self.cur.execute(
            """
            INSERT INTO organization_memberships
                (id, organization_id, user_id, role, status, is_primary)
            VALUES (%s, %s, %s, 'VENDOR_STAFF', 'INVITED', FALSE)
            RETURNING id, organization_id, user_id, role, status, created_at
            """,
            (membership_id, self.context.organization_id, user_id),
        )
        row = dict(self.cur.fetchone())
        self.cur.execute(
            """
            INSERT INTO admin_audit_logs
                (actor_user_id, action, target_entity_type, target_entity_id, state_after, reason, correlation_id)
            VALUES (%s, 'VENDOR_STAFF_INVITED', 'ORGANIZATION_MEMBERSHIP', %s, %s, %s, %s)
            """,
            (
                self.context.user_id,
                membership_id,
                Json(row),
                "vendor staff invitation",
                self.context.correlation_id,
            ),
        )
        return row

    def vendor_staff_update(self, *, membership_id, role=None, status=None):
        self._require_vendor_owner()
        allowed_roles = {"VENDOR_OWNER", "VENDOR_STAFF"}
        allowed_statuses = {"INVITED", "ACTIVE", "SUSPENDED", "REVOKED"}
        if role is not None and role not in allowed_roles:
            raise ValueError("Invalid vendor membership role.")
        if status is not None and status not in allowed_statuses:
            raise ValueError("Invalid membership status.")
        self.cur.execute(
            """
            SELECT id, user_id, role, status
            FROM organization_memberships
            WHERE id=%s AND organization_id=%s
            FOR UPDATE
            """,
            (membership_id, self.context.organization_id),
        )
        before = self.cur.fetchone()
        if not before:
            raise KeyError("Vendor membership not found.")
        if before["role"] == "VENDOR_OWNER" and (role == "VENDOR_STAFF" or status in {"SUSPENDED", "REVOKED"}):
            self.cur.execute(
                """
                SELECT COUNT(*) AS owners
                FROM organization_memberships
                WHERE organization_id=%s
                  AND role='VENDOR_OWNER'
                  AND status='ACTIVE'
                  AND id<>%s
                """,
                (self.context.organization_id, membership_id),
            )
            if int(self.cur.fetchone()["owners"]) == 0:
                raise ValueError("Cannot remove the last active vendor owner.")
        updates = []
        params: list = []
        if role is not None:
            updates.append("role=%s")
            params.append(role)
        if status is not None:
            updates.append("status=%s")
            params.append(status)
        if not updates:
            raise ValueError("No staff fields to update.")
        updates.append("updated_at=now()")
        params.extend([membership_id, self.context.organization_id])
        self.cur.execute(
            f"""
            UPDATE organization_memberships
            SET {", ".join(updates)}
            WHERE id=%s AND organization_id=%s
            RETURNING id, organization_id, user_id, role, status, is_primary, updated_at
            """,
            tuple(params),
        )
        after = dict(self.cur.fetchone())
        self.cur.execute(
            """
            INSERT INTO admin_audit_logs
                (actor_user_id, action, target_entity_type, target_entity_id, state_before, state_after, reason, correlation_id)
            VALUES (%s, 'VENDOR_STAFF_UPDATED', 'ORGANIZATION_MEMBERSHIP', %s, %s, %s, %s, %s)
            """,
            (
                self.context.user_id,
                membership_id,
                Json(dict(before)),
                Json(after),
                "vendor staff membership update",
                self.context.correlation_id,
            ),
        )
        return after

    def delegated_permissions_list(self, *, membership_id):
        if not self.context.organization_id:
            raise PermissionError("Delegated permissions require an active organization context.")
        return membership_permissions(
            self.cur,
            self.context.user_id,
            self.context.organization_id,
            str(membership_id),
        )

    def delegated_permission_grant(
        self,
        *,
        membership_id,
        permission_key,
        reason,
        client=None,
    ):
        if not self.context.organization_id:
            raise PermissionError("Delegated permissions require an active organization context.")
        return grant_permission(
            self.cur,
            self.context.user_id,
            self.context.organization_id,
            str(membership_id),
            permission_key,
            reason,
            client=client,
            target_role="VENDOR_STAFF",
        )

    def delegated_permission_revoke(
        self,
        *,
        membership_id,
        permission_key,
        reason,
        client=None,
    ):
        if not self.context.organization_id:
            raise PermissionError("Delegated permissions require an active organization context.")
        return revoke_permission(
            self.cur,
            self.context.user_id,
            self.context.organization_id,
            str(membership_id),
            permission_key,
            reason,
            client=client,
            target_role="VENDOR_STAFF",
        )

    def delegated_permission_audit(self, *, membership_id=None, limit=100):
        if not self.context.organization_id:
            raise PermissionError("Delegated permissions require an active organization context.")
        return {
            "items": permission_audit(
                self.cur,
                self.context.user_id,
                self.context.organization_id,
                target_membership_id=str(membership_id) if membership_id else None,
                limit=limit,
            ),
            "limit": limit,
        }

    def admin_users_list(self, *, query=None, offset=0, limit=50):
        self._require_admin_management()
        params: list = []
        clauses = ["1=1"]
        if query:
            clauses.append("(u.phone_number ILIKE %s OR u.full_name ILIKE %s OR u.role ILIKE %s)")
            needle = f"%{query.strip()}%"
            params.extend([needle, needle, needle])
        where_sql = " AND ".join(clauses)
        params.extend([limit, offset])
        self.cur.execute(
            f"""
            SELECT
                u.id, u.phone_number, u.full_name, u.role, u.is_active,
                u.last_login_at, u.created_at,
                COUNT(DISTINCT m.id)::INT AS membership_count
            FROM users u
            LEFT JOIN organization_memberships m ON m.user_id=u.id
            WHERE {where_sql}
            GROUP BY u.id
            ORDER BY u.created_at DESC
            LIMIT %s OFFSET %s
            """,
            tuple(params),
        )
        return {"users": [dict(x) for x in self.cur.fetchall()], "limit": limit, "offset": offset}

    def admin_user_update(self, *, user_id, is_active):
        self._require_super_admin()
        self.cur.execute(
            "SELECT id, is_active, role FROM users WHERE id=%s FOR UPDATE",
            (user_id,),
        )
        before = self.cur.fetchone()
        if not before:
            raise KeyError("User not found.")
        if str(before["id"]) == str(self.context.user_id) and not is_active:
            raise ValueError("Administrator cannot deactivate the current account.")
        self.cur.execute(
            "UPDATE users SET is_active=%s, updated_at=now() WHERE id=%s RETURNING id, phone_number, full_name, role, is_active, updated_at",
            (is_active, user_id),
        )
        after = dict(self.cur.fetchone())
        if not is_active:
            self.cur.execute(
                "UPDATE user_sessions SET status='REVOKED', revoked_at=now() WHERE user_id=%s AND status='ACTIVE'",
                (user_id,),
            )
        self.cur.execute(
            """
            INSERT INTO admin_audit_logs
                (actor_user_id, action, target_entity_type, target_entity_id, state_before, state_after, reason, correlation_id)
            VALUES (%s, 'ADMIN_USER_STATUS_UPDATED', 'USER', %s, %s, %s, %s, %s)
            """,
            (self.context.user_id, user_id, Json(dict(before)), Json(after), "admin user status update", self.context.correlation_id),
        )
        return after

    def admin_organizations_list(self, *, query=None, org_type=None, offset=0, limit=50):
        self._require_admin_management()
        params: list = []
        clauses = ["1=1"]
        if query:
            clauses.append("(o.name ILIKE %s OR COALESCE(o.national_id,'') ILIKE %s)")
            needle = f"%{query.strip()}%"
            params.extend([needle, needle])
        if org_type:
            clauses.append("o.org_type=%s")
            params.append(org_type)
        where_sql = " AND ".join(clauses)
        params.extend([limit, offset])
        self.cur.execute(
            f"""
            SELECT
                o.id, o.name, o.org_type, o.status, o.national_id,
                o.created_at, o.updated_at,
                COUNT(DISTINCT m.id)::INT AS membership_count
            FROM organizations o
            LEFT JOIN organization_memberships m ON m.organization_id=o.id
            WHERE {where_sql}
            GROUP BY o.id
            ORDER BY o.created_at DESC
            LIMIT %s OFFSET %s
            """,
            tuple(params),
        )
        return {"organizations": [dict(x) for x in self.cur.fetchall()], "limit": limit, "offset": offset}

    def admin_organization_update(self, *, organization_id, status):
        self._require_super_admin()
        allowed = {"LEAD", "DOCUMENTS_PENDING", "UNDER_REVIEW", "VERIFICATION_PENDING", "APPROVED", "ACTIVE", "REJECTED", "SUSPENDED"}
        if status not in allowed:
            raise ValueError("Invalid organization status.")
        self.cur.execute(
            "SELECT id, name, org_type, status FROM organizations WHERE id=%s FOR UPDATE",
            (organization_id,),
        )
        before = self.cur.fetchone()
        if not before:
            raise KeyError("Organization not found.")
        self.cur.execute(
            "UPDATE organizations SET status=%s, updated_at=now() WHERE id=%s RETURNING id, name, org_type, status, updated_at",
            (status, organization_id),
        )
        after = dict(self.cur.fetchone())
        if status in ("SUSPENDED", "REJECTED"):
            self.cur.execute(
                """
                UPDATE user_sessions
                SET status='REVOKED', revoked_at=now()
                WHERE active_organization_id=%s AND status='ACTIVE'
                """,
                (organization_id,),
            )
        self.cur.execute(
            """
            INSERT INTO admin_audit_logs
                (actor_user_id, action, target_entity_type, target_entity_id, state_before, state_after, reason, correlation_id)
            VALUES (%s, 'ADMIN_ORG_STATUS_UPDATED', 'ORGANIZATION', %s, %s, %s, %s, %s)
            """,
            (self.context.user_id, organization_id, Json(dict(before)), Json(after), "admin organization status update", self.context.correlation_id),
        )
        return after

    def permission_catalog(self):
        self._require_ops_context()
        return {
            "roles": {
                "RETAILER_OWNER": ["invite_staff", "manage_store_profile", "place_orders", "confirm_delivery", "submit_payment_evidence", "open_disputes", "view_invoices"],
                "RETAILER_STAFF": ["view_orders", "confirm_delivery"],
                "VENDOR_OWNER": ["manage_catalog", "set_prices", "update_inventory", "accept_reject_orders", "assign_drivers", "view_settlements", "manage_staff"],
                "VENDOR_STAFF": ["review_orders", "mark_preparing", "mark_ready", "dispatch", "confirm_inventory"],
                "FIELD_ACTIVATOR": ["register_retailer_lead", "verify_coordinates", "complete_onboarding", "log_field_visits"],
                "OPS_ADMIN": ["resolve_support", "catalog_operations", "review_candidates", "monitor_vendor_sla"],
                "SUPER_ADMIN": ["manage_users", "manage_organizations", "broadcasts", "dispute_resolution", "financial_adjustments", "feature_flags"],
            },
            "delegatable_permissions": sorted(CANONICAL_PERMISSIONS),
            "delegation_rules": {
                "manager_permission": "membership.manage",
                "tenant_scope": "active_organization",
                "privilege_ceiling": "actor_can_only_delegate_permissions_in_actor_effective_set",
                "audit": "permission_audit_events_append_only",
            },
            "source": "MASTER_SYSTEM_ARCHITECTURE.md §4 + Master Tree VD-15",
        }
    
    def global_returns_list(self, *, status=None, offset=0, limit=50):
        self._require_ops_context()
        params: list = []
        clauses = ["1=1"]
        if status:
            clauses.append("r.status=%s")
            params.append(status)
        params.extend([limit, offset])
        where_sql = " AND ".join(clauses)
        self.cur.execute(
            f"""
            SELECT
                r.id AS return_id,
                r.order_id,
                r.status,
                r.reason,
                r.claimed_refund_amount_toman,
                r.approved_refund_amount_toman,
                r.created_at,
                o.order_number,
                o.order_status,
                ret.store_name AS retailer_name,
                v.business_name AS vendor_name
            FROM returns r
            JOIN orders o ON o.id=r.order_id
            JOIN retailers ret ON ret.id=o.retailer_id
            JOIN vendors v ON v.id=o.vendor_id
            WHERE {where_sql}
            ORDER BY r.created_at DESC
            LIMIT %s OFFSET %s
            """,
            tuple(params),
        )
        return {"returns": [dict(x) for x in self.cur.fetchall()], "limit": limit, "offset": offset}


    # ── Admin SLA Override (Stage 39) ──────────────────────────────

    def admin_sla_override(self, *, order_id, extension_minutes, reason):
        self._require_admin_management()
        if not 1 <= int(extension_minutes) <= 24 * 60:
            raise ValueError("extension_minutes must be between 1 and 1440.")
        if not reason or not reason.strip():
            raise ValueError("reason is required for an SLA override.")

        self.cur.execute(
            """
            SELECT id, order_number, order_status, vendor_acceptance_deadline_at
            FROM orders
            WHERE id=%s
            FOR UPDATE
            """,
            (order_id,),
        )
        before = self.cur.fetchone()
        if not before:
            raise KeyError("Order not found.")
        if before["order_status"] != "SUBMITTED":
            raise ValueError("SLA override is only valid for SUBMITTED orders.")
        if before["vendor_acceptance_deadline_at"] is None:
            raise ValueError("Order has no vendor acceptance SLA deadline.")

        self.cur.execute(
            """
            UPDATE orders
            SET vendor_acceptance_deadline_at = vendor_acceptance_deadline_at + (%s * interval '1 minute'),
                updated_at = now()
            WHERE id=%s
            RETURNING id, order_number, order_status, vendor_acceptance_deadline_at, updated_at
            """,
            (int(extension_minutes), order_id),
        )
        after = dict(self.cur.fetchone())
        self.cur.execute(
            """
            INSERT INTO admin_audit_logs
                (actor_user_id, action, target_entity_type, target_entity_id,
                 state_before, state_after, reason, correlation_id)
            VALUES (%s, 'ORDER_SLA_OVERRIDE', 'ORDER', %s, %s, %s, %s, %s)
            """,
            (
                self.context.user_id,
                order_id,
                Json({
                    "vendor_acceptance_deadline_at":
                        before["vendor_acceptance_deadline_at"].isoformat()
                        if before["vendor_acceptance_deadline_at"] else None
                }),
                Json({
                    "vendor_acceptance_deadline_at":
                        after["vendor_acceptance_deadline_at"].isoformat()
                        if after["vendor_acceptance_deadline_at"] else None,
                    "extension_minutes": int(extension_minutes),
                }),
                reason.strip(),
                self.context.correlation_id,
            ),
        )
        return after


    # ── Admin Broadcast HTTP Boundary (Stage 40) ────────────────────

    @staticmethod
    def _broadcast_criteria_where(criteria: dict, alias: str = "u"):
        allowed = {"org_type", "status", "city", "role"}
        unknown = set(criteria) - allowed
        if unknown:
            raise ValueError("Unsupported broadcast targeting criteria: " + ", ".join(sorted(unknown)))

        clauses = []
        params = []
        if "role" in criteria:
            role = str(criteria["role"])
            if role not in {
                "RETAILER_OWNER", "RETAILER_STAFF",
                "VENDOR_OWNER", "VENDOR_STAFF",
                "FIELD_ACTIVATOR", "OPS_ADMIN", "SUPER_ADMIN",
            }:
                raise ValueError("Unsupported broadcast role criterion.")
            clauses.append("m.role = %s")
            params.append(role)
        if "org_type" in criteria:
            org_type = str(criteria["org_type"]).upper()
            if org_type not in {"RETAILER", "VENDOR", "OPERATOR"}:
                raise ValueError("Unsupported organization type criterion.")
            clauses.append("o.org_type = %s")
            params.append(org_type)
        if "status" in criteria:
            org_status = str(criteria["status"]).upper()
            if org_status not in {"ACTIVE", "SUSPENDED", "REJECTED", "APPROVED", "UNDER_REVIEW", "DOCUMENTS_PENDING", "VERIFICATION_PENDING", "LEAD"}:
                raise ValueError("Unsupported organization status criterion.")
            clauses.append("o.status = %s")
            params.append(org_status)
        if "city" in criteria:
            clauses.append("r.city = %s")
            params.append(str(criteria["city"]).strip())
        return clauses, params

    def admin_broadcast_create(self, *, title, body, target_criteria, channel="IN_APP", priority="NORMAL", scheduled_at=None):
        self._require_broadcast_admin()
        if not title or not title.strip():
            raise ValueError("Broadcast title is required.")
        if not body or not body.strip():
            raise ValueError("Broadcast body is required.")
        if channel not in {"IN_APP", "SMS", "PUSH", "INBOX_AND_SMS", "ALL"}:
            raise ValueError("Unsupported broadcast channel.")
        if priority not in {"LOW", "NORMAL", "HIGH", "URGENT"}:
            raise ValueError("Unsupported broadcast priority.")
        if channel != "IN_APP":
            raise ValueError("Only IN_APP broadcast dispatch is enabled in the current MVP notification runtime.")

        criteria = dict(target_criteria or {})
        clauses, params = self._broadcast_criteria_where(criteria)
        where = " AND ".join(["m.status = 'ACTIVE'", "u.is_active = TRUE"] + clauses)

        if "city" in criteria:
            query = f"""
                SELECT COUNT(DISTINCT u.id)::INT AS count
                FROM users u
                JOIN organization_memberships m ON m.user_id=u.id AND m.status='ACTIVE'
                JOIN organizations o ON o.id=m.organization_id
                JOIN retailers r ON r.organization_id=o.id
                WHERE {where}
            """
        else:
            query = f"""
                SELECT COUNT(DISTINCT u.id)::INT AS count
                FROM users u
                JOIN organization_memberships m ON m.user_id=u.id AND m.status='ACTIVE'
                JOIN organizations o ON o.id=m.organization_id
                WHERE {where}
            """
        self.cur.execute(query, tuple(params))
        estimated = int(self.cur.fetchone()["count"])

        bid = str(uuid4())
        self.cur.execute(
            """
            INSERT INTO broadcast_messages
                (id, admin_user_id, title, body, target_criteria, channel,
                 priority, status, estimated_recipient_count, scheduled_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,'DRAFT',%s,%s)
            RETURNING id, title, body, target_criteria, channel, priority,
                      status, recipient_count, estimated_recipient_count,
                      scheduled_at, created_at
            """,
            (
                bid,
                self.context.user_id,
                title.strip(),
                body.strip(),
                Json(criteria),
                channel,
                priority,
                estimated,
                scheduled_at,
            ),
        )
        row = dict(self.cur.fetchone())
        for key in ("id",):
            row[key] = str(row[key])
        for key in ("scheduled_at", "created_at"):
            if row[key]:
                row[key] = row[key].isoformat()
        return row

    def admin_broadcast_dispatch(self, *, broadcast_id, approve=True):
        self._require_broadcast_admin()
        if not approve:
            raise ValueError("Broadcast dispatch requires explicit approval.")

        self.cur.execute(
            """
            SELECT *
            FROM broadcast_messages
            WHERE id=%s
            FOR UPDATE
            """,
            (broadcast_id,),
        )
        broadcast = self.cur.fetchone()
        if not broadcast:
            raise KeyError("Broadcast not found.")
        if broadcast["status"] == "COMPLETED":
            self.cur.execute(
                "SELECT COUNT(*)::INT AS count FROM broadcast_recipients WHERE broadcast_id=%s AND status='SENT'",
                (broadcast_id,),
            )
            return {
                "id": str(broadcast["id"]),
                "status": "COMPLETED",
                "recipient_count": int(self.cur.fetchone()["count"]),
                "idempotent_replay": True,
            }
        if broadcast["status"] not in {"DRAFT", "SCHEDULED"}:
            raise ValueError(f"Broadcast cannot be dispatched from {broadcast['status']}.")

        criteria = dict(broadcast["target_criteria"] or {})
        clauses, params = self._broadcast_criteria_where(criteria)
        where = " AND ".join(["m.status='ACTIVE'", "u.is_active=TRUE"] + clauses)

        if "city" in criteria:
            recipient_sql = f"""
                SELECT DISTINCT u.id AS user_id, o.id AS organization_id
                FROM users u
                JOIN organization_memberships m ON m.user_id=u.id AND m.status='ACTIVE'
                JOIN organizations o ON o.id=m.organization_id
                JOIN retailers r ON r.organization_id=o.id
                WHERE {where}
                ORDER BY u.id, o.id
            """
        else:
            recipient_sql = f"""
                SELECT DISTINCT u.id AS user_id, o.id AS organization_id
                FROM users u
                JOIN organization_memberships m ON m.user_id=u.id AND m.status='ACTIVE'
                JOIN organizations o ON o.id=m.organization_id
                WHERE {where}
                ORDER BY u.id, o.id
            """
        self.cur.execute(recipient_sql, tuple(params))
        recipients = self.cur.fetchall()

        # Frozen recipient snapshot. The unique constraint makes retries safe.
        self.cur.execute(
            """
            UPDATE broadcast_messages
            SET status='PROCESSING', approved_by=%s, dispatched_at=now()
            WHERE id=%s
            """,
            (self.context.user_id, broadcast_id),
        )

        sent = 0
        for recipient in recipients:
            self.cur.execute(
                """
                INSERT INTO broadcast_recipients
                    (id,broadcast_id,user_id,organization_id,status)
                VALUES (%s,%s,%s,%s,'PENDING')
                ON CONFLICT (broadcast_id,user_id) DO NOTHING
                RETURNING id
                """,
                (str(uuid4()), broadcast_id, recipient["user_id"], recipient["organization_id"]),
            )
            snap = self.cur.fetchone()
            if not snap:
                continue

            self.cur.execute(
                """
                INSERT INTO notifications
                    (id,user_id,organization_id,event_name,title,body,priority)
                VALUES (%s,%s,%s,'ADMIN_BROADCAST_MESSAGE',%s,%s,%s)
                RETURNING id
                """,
                (
                    str(uuid4()),
                    recipient["user_id"],
                    recipient["organization_id"],
                    broadcast["title"],
                    broadcast["body"],
                    broadcast["priority"],
                ),
            )
            notification_id = self.cur.fetchone()["id"]

            self.cur.execute(
                """
                INSERT INTO user_inbox_items
                    (id,user_id,notification_id,title,body,category,is_read)
                VALUES (%s,%s,%s,%s,%s,'SYSTEM',FALSE)
                """,
                (
                    str(uuid4()),
                    recipient["user_id"],
                    notification_id,
                    broadcast["title"],
                    broadcast["body"],
                ),
            )
            self.cur.execute(
                """
                UPDATE broadcast_recipients
                SET notification_id=%s, status='SENT'
                WHERE id=%s
                """,
                (notification_id, snap["id"]),
            )
            sent += 1

        self.cur.execute(
            """
            UPDATE broadcast_messages
            SET recipient_count=%s, status='COMPLETED', completed_at=now()
            WHERE id=%s
            RETURNING id,status,recipient_count,estimated_recipient_count,completed_at
            """,
            (sent, broadcast_id),
        )
        row = dict(self.cur.fetchone())
        return {
            "id": str(row["id"]),
            "status": row["status"],
            "recipient_count": int(row["recipient_count"]),
            "estimated_recipient_count": int(row["estimated_recipient_count"]),
            "completed_at": row["completed_at"].isoformat() if row["completed_at"] else None,
            "idempotent_replay": False,
        }
