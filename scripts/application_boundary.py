"""Framework-agnostic POL application boundary.

HTTP/GraphQL/RPC adapters should translate transport payloads into these command
methods. Domain tables must not be written directly by client-facing code.
"""

from __future__ import annotations

from dataclasses import dataclass

from scripts.checkout_gateway import CanonicalCheckoutGateway
from scripts.canonical_feedback import CanonicalFeedbackService
from scripts.canonical_basket_allocation import CanonicalBasketAllocationService
from scripts.canonical_partial_acceptance import CanonicalPartialAcceptanceService
from scripts.canonical_vendor_order import CanonicalVendorOrderService
from scripts.canonical_support import CanonicalSupportService
from scripts.payment_reconciliation_worker import PaymentReconciliationWorker
from scripts.provider_delivery_worker import ProviderDeliveryWorker
from scripts.returns_rma import CanonicalReturnService
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

    def process_vendor_acceptance_timeouts(self, *, limit=100):
        self._require_ops_context()
        return VendorAcceptanceTimeoutWorker.process_expired(self.cur, limit=limit)

    def reconcile_payments(self, *, limit=50):
        self._require_ops_context()
        return PaymentReconciliationWorker.process_pending(self.cur, limit=limit)

    def deliver_external_notifications(self, *, limit=100):
        self._require_ops_context()
        return ProviderDeliveryWorker.process_pending(self.cur, limit=limit)

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
