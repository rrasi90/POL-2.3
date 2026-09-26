"""Canonical basket and allocation application service for the HTTP transport."""

from __future__ import annotations

import hashlib
import json

from scripts.allocation_engine import (
    BasketItem,
    MultiVendorAllocationEngine,
    Vendor,
    VendorSKU,
)
from scripts.domain_services import AllocationService, BasketService


class CanonicalBasketAllocationService:
    """Own tenant-scoped basket commands and allocation-plan materialization."""

    @staticmethod
    def _retailer_for_context(cur, user_id: str, organization_id: str):
        if not organization_id:
            raise PermissionError("Retailer operations require an active organization context.")

        cur.execute(
            """
            SELECT r.id AS retailer_id,
                   r.organization_id,
                   r.city,
                   r.store_name,
                   om.role
            FROM retailers r
            JOIN organizations o ON o.id = r.organization_id
            JOIN organization_memberships om
              ON om.organization_id = r.organization_id
            WHERE om.user_id = %s
              AND om.organization_id = %s
              AND om.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
              AND om.role IN ('RETAILER_OWNER', 'RETAILER_STAFF')
            ORDER BY r.id
            LIMIT 1
            """,
            (user_id, organization_id),
        )
        retailer = cur.fetchone()
        if not retailer:
            raise PermissionError(
                "Actor is not an active retailer member of the selected organization."
            )
        return retailer

    @classmethod
    def _basket_for_context(cls, cur, user_id: str, organization_id: str, basket_id: str):
        retailer = cls._retailer_for_context(cur, user_id, organization_id)
        cur.execute(
            """
            SELECT b.id, b.retailer_id, b.version, b.status
            FROM baskets b
            WHERE b.id = %s
              AND b.retailer_id = %s
            FOR UPDATE
            """,
            (basket_id, retailer["retailer_id"]),
        )
        basket = cur.fetchone()
        if not basket:
            raise KeyError("Basket not found in the active retailer organization.")
        return retailer, basket

    @staticmethod
    def _assert_owner(retailer):
        if retailer["role"] != "RETAILER_OWNER":
            raise PermissionError(
                "Basket modification and allocation require RETAILER_OWNER authority."
            )

    @classmethod
    def create_basket(cls, cur, user_id: str, organization_id: str):
        retailer = cls._retailer_for_context(cur, user_id, organization_id)
        cls._assert_owner(retailer)
        basket_id = BasketService.create_basket(cur, str(retailer["retailer_id"]))
        return {
            "basket_id": str(basket_id),
            "version": 1,
            "status": "OPEN",
        }

    @classmethod
    def add_item(
        cls,
        cur,
        user_id: str,
        organization_id: str,
        basket_id: str,
        product_id: str,
        quantity: int,
        pack_quantity: int,
        expected_version: int,
    ):
        retailer, basket = cls._basket_for_context(cur, user_id, organization_id, basket_id)
        cls._assert_owner(retailer)
        if basket["status"] != "OPEN":
            raise ValueError("Only OPEN baskets can be modified.")
        if quantity <= 0:
            raise ValueError("requested_quantity must be greater than zero.")
        if pack_quantity <= 0:
            raise ValueError("pack_quantity must be greater than zero.")
        if expected_version < 1:
            raise ValueError("expected_version must be a positive integer.")

        cur.execute(
            """
            SELECT id
            FROM products
            WHERE id = %s
              AND is_active = TRUE
            """,
            (product_id,),
        )
        if not cur.fetchone():
            raise KeyError("Active product not found.")

        new_version = BasketService.add_item_optimistic(
            cur,
            basket_id,
            product_id,
            quantity,
            pack_quantity,
            expected_version,
        )
        return {
            "basket_id": str(basket_id),
            "version": int(new_version),
            "status": "OPEN",
        }

    @classmethod
    def allocation_preview(
        cls,
        cur,
        user_id: str,
        organization_id: str,
        basket_id: str,
    ):
        retailer, basket = cls._basket_for_context(
            cur, user_id, organization_id, basket_id
        )
        cls._assert_owner(retailer)
        if basket["status"] != "OPEN":
            raise ValueError("Allocation preview requires an OPEN basket.")

        cur.execute(
            """
            SELECT id, product_id, requested_quantity, requested_unit, pack_quantity
            FROM basket_items
            WHERE basket_id = %s
            ORDER BY created_at, id
            """,
            (basket_id,),
        )
        basket_rows = cur.fetchall()
        if not basket_rows:
            raise ValueError("Allocation preview requires at least one basket item.")

        basket_items = [
            BasketItem(
                id=str(row["id"]),
                master_product_id=str(row["product_id"]),
                requested_quantity=int(row["requested_quantity"]),
                packaging_unit=str(row["requested_unit"]),
                pack_quantity=int(row["pack_quantity"]),
            )
            for row in basket_rows
        ]

        cur.execute(
            """
            SELECT v.id, v.business_name, v.min_order_value_toman
            FROM vendors v
            JOIN organizations o ON o.id = v.organization_id
            WHERE v.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
            ORDER BY v.id
            """
        )
        vendor_rows = cur.fetchall()
        vendors = {
            str(row["id"]): Vendor(
                id=str(row["id"]),
                name=row["business_name"],
                active=True,
                delivery_zones=("Ahvaz",),
                mov_toman=int(row["min_order_value_toman"]),
                reputation_score=5.0,
            )
            for row in vendor_rows
        }

        cur.execute(
            """
            SELECT vp.id,
                   vp.vendor_id,
                   vp.product_id,
                   vp.packaging_unit,
                   vp_price.price_toman,
                   vi.physical_quantity,
                   vi.reserved_quantity,
                   vi.moq
            FROM vendor_products vp
            JOIN vendors v ON v.id = vp.vendor_id
            JOIN organizations o ON o.id = v.organization_id
            JOIN vendor_inventory vi ON vi.vendor_product_id = vp.id
            JOIN vendor_prices vp_price
              ON vp_price.vendor_product_id = vp.id
             AND vp_price.is_current = TRUE
            JOIN products p ON p.id = vp.product_id
            WHERE v.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
              AND vp.is_active = TRUE
              AND vp.listing_status = 'ACTIVE'
              AND p.is_active = TRUE
            ORDER BY vp.vendor_id, vp.id
            """
        )
        sku_rows = cur.fetchall()
        vendor_skus = [
            VendorSKU(
                id=str(row["id"]),
                vendor_id=str(row["vendor_id"]),
                master_product_id=str(row["product_id"]),
                packaging_unit=str(row["packaging_unit"]),
                pack_quantity=int(row["pack_quantity"]),
                price_toman=int(row["price_toman"]),
                physical_quantity=int(row["physical_quantity"]),
                reserved_quantity=int(row["reserved_quantity"]),
                moq=int(row["moq"]),
            )
            for row in sku_rows
            if str(row["vendor_id"]) in vendors
        ]

        retailer_zone = str(retailer["city"] or "Ahvaz")
        engine = MultiVendorAllocationEngine(vendors, vendor_skus)
        plan = engine.allocate(
            retailer_id=str(retailer["retailer_id"]),
            retailer_zone=retailer_zone,
            basket_items=basket_items,
        )

        if plan.vendor_count < 1:
            raise ValueError(
                "No orderable vendor allocation is currently available for this basket."
            )

        canonical_input = {
            "basket_id": str(basket_id),
            "basket_version": int(basket["version"]),
            "items": [
                {
                    "basket_item_id": str(row["id"]),
                    "product_id": str(row["product_id"]),
                    "requested_quantity": int(row["requested_quantity"]),
                    "requested_unit": str(row["requested_unit"]),
                    "pack_quantity": int(row["pack_quantity"]),
                }
                for row in basket_rows
            ],
            "vendors": [
                {"id": str(v), "name": vendors[v].name, "mov_toman": vendors[v].mov_toman,
                 "reputation_score": vendors[v].reputation_score}
                for v in sorted(vendors)
            ],
            "vendor_skus": [
                {
                    "id": str(s.id), "vendor_id": str(s.vendor_id), "product_id": str(s.master_product_id),
                    "packaging_unit": str(s.packaging_unit), "pack_quantity": int(s.pack_quantity),
                    "price_toman": int(s.price_toman), "physical_quantity": int(s.physical_quantity),
                    "reserved_quantity": int(s.reserved_quantity), "moq": int(s.moq),
                }
                for s in sorted(vendor_skus, key=lambda x: (x.vendor_id, x.master_product_id, x.packaging_unit, x.pack_quantity, x.id))
            ],
            "decision_hash": plan.decision_hash,
            "algorithm_version": "v1.1",
        }
        input_hash = hashlib.sha256(
            json.dumps(canonical_input, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        plan_row = AllocationService.create_plan(
            cur,
            str(basket_id),
            int(basket["version"]),
            int(plan.vendor_count),
            int(plan.total_amount_toman),
            input_hash=input_hash,
        )
        plan_id = str(plan_row["id"])

        for item in plan.items:
            if item.status == "UNFULFILLED":
                cur.execute(
                    """
                    INSERT INTO allocation_items (
                        id, allocation_plan_id, basket_item_id,
                        vendor_id, vendor_product_id, allocated_quantity,
                        allocated_unit, unit_price_snapshot_toman,
                        line_total_toman, status
                    )
                    VALUES (
                        gen_random_uuid(), %s, %s,
                        NULL, NULL, 0,
                        %s, 0, 0, 'UNFULFILLED'
                    )
                    """,
                    (plan_id, item.basket_item_id, item.packaging_unit),
                )
                continue

            cur.execute(
                """
                INSERT INTO allocation_items (
                    id, allocation_plan_id, basket_item_id,
                    vendor_id, vendor_product_id, allocated_quantity,
                    allocated_unit, unit_price_snapshot_toman,
                    line_total_toman, status
                )
                VALUES (
                    gen_random_uuid(), %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s
                )
                """,
                (
                    plan_id,
                    item.basket_item_id,
                    item.vendor_id,
                    item.vendor_sku_id,
                    int(item.requested_quantity),
                    item.packaging_unit,
                    int(item.unit_price_toman),
                    int(item.total_price_toman),
                    item.status,
                ),
            )

        allocated_vendors = []
        for vendor_id, subtotal in sorted(plan.vendor_subtotals.items()):
            vendor = vendors[vendor_id]
            allocated_vendors.append(
                {
                    "vendor_id": vendor_id,
                    "business_name": vendor.name,
                    "subtotal_toman": int(subtotal),
                    "min_order_value_toman": int(vendor.mov_toman),
                    "mov_satisfied": int(subtotal) >= int(vendor.mov_toman),
                    "allocated_items_count": sum(
                        1
                        for item in plan.allocated_items
                        if item.vendor_id == vendor_id
                    ),
                }
            )

        unfulfilled_items = [
            {
                "product_id": item.master_product_id,
                "requested_quantity": int(item.requested_quantity),
                "unit": item.packaging_unit,
                "reason_code": item.reason_code,
            }
            for item in plan.unfulfilled_items
        ]

        return {
            "allocation_plan_id": plan_id,
            "basket_version": int(basket["version"]),
            "strategy": "MULTI_VENDOR_MIN_FRAGMENTATION",
            "vendor_count": int(plan.vendor_count),
            "allocated_vendors": allocated_vendors,
            "summary": {
                "total_items_requested": sum(
                    int(item.requested_quantity) for item in plan.items
                ),
                "total_items_allocated": sum(
                    int(item.requested_quantity) for item in plan.allocated_items
                ),
                "total_items_unfulfilled": sum(
                    int(item.requested_quantity) for item in plan.unfulfilled_items
                ),
                "total_amount_toman": int(plan.total_amount_toman),
                "estimated_delivery_cost_toman": 0,
            },
            "unfulfilled_items": unfulfilled_items,
        }
