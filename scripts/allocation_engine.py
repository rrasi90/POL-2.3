"""
POL Deterministic Heuristic Multi-Vendor Allocation Engine
Implements Decision D-014 (Multi-Vendor Basket in MVP), D-005 (Open Vendor Count),
and D-010 (Order Entity Separation).

Core Invariants:
1. Deterministic and reproducible (zero randomness).
2. Minimum fragmentation by default (favors 1 vendor, then 2, then N).
3. Independent MOV enforcement per vendor sub-basket.
4. Independent SKU MOQ enforcement.
5. Preserves unfulfilled items with explainability reason codes.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
import hashlib
import itertools
import json
import uuid


@dataclass(frozen=True)
class MasterProduct:
    id: str
    name: str
    category_id: str
    barcode: Optional[str] = None


@dataclass(frozen=True)
class Vendor:
    id: str
    name: str
    active: bool = True
    delivery_zones: Tuple[str, ...] = ("Ahvaz",)
    mov_toman: int = 0
    reputation_score: float = 5.0


@dataclass(frozen=True)
class VendorSKU:
    id: str
    vendor_id: str
    master_product_id: str
    packaging_unit: str  # e.g., "CARTON", "BOX", "BUNDLE"
    price_toman: int
    physical_quantity: int
    reserved_quantity: int
    moq: int = 1
    pack_quantity: int = 1

    @property
    def available_quantity(self) -> int:
        return max(0, self.physical_quantity - self.reserved_quantity)


@dataclass(frozen=True)
class BasketItem:
    id: str
    master_product_id: str
    requested_quantity: int
    packaging_unit: str = "CARTON"
    pack_quantity: int = 1


@dataclass
class AllocationResultItem:
    basket_item_id: str
    master_product_id: str
    requested_quantity: int
    packaging_unit: str
    status: str  # 'ALLOCATED' or 'UNFULFILLED'
    vendor_id: Optional[str] = None
    vendor_sku_id: Optional[str] = None
    unit_price_toman: Optional[int] = None
    total_price_toman: Optional[int] = None
    reason_code: str = "ALLOCATED"


@dataclass
class AllocationPlan:
    plan_id: str
    retailer_id: str
    vendor_count: int
    vendor_subtotals: Dict[str, int]
    total_amount_toman: int
    is_fully_fulfilled: bool
    items: List[AllocationResultItem]
    decision_hash: str = ""

    @property
    def allocated_items(self) -> List[AllocationResultItem]:
        return [it for it in self.items if it.status == "ALLOCATED"]

    @property
    def unfulfilled_items(self) -> List[AllocationResultItem]:
        return [it for it in self.items if it.status == "UNFULFILLED"]


class MultiVendorAllocationEngine:
    def __init__(
        self,
        vendors: Dict[str, Vendor],
        vendor_skus: List[VendorSKU]
    ):
        self.vendors = vendors
        # Index SKUs by product + sell unit + exact pack size.
        self.sku_catalog: Dict[Tuple[str, str, int], List[VendorSKU]] = {}
        for sku in vendor_skus:
            key = (sku.master_product_id, sku.packaging_unit, sku.pack_quantity)
            if key not in self.sku_catalog:
                self.sku_catalog[key] = []
            self.sku_catalog[key].append(sku)

    def allocate(
        self,
        retailer_id: str,
        retailer_zone: str,
        basket_items: List[BasketItem]
    ) -> AllocationPlan:
        """
        Executes deterministic multi-vendor allocation following the 9-step pipeline:
        1. Evaluates feasibility per line item.
        2. Evaluates K=1 candidate plans.
        3. Evaluates K=2 candidate plans.
        4. Evaluates K=N candidate plans with MOV pruning.
        5. Selects best plan based on lexicographical objective hierarchy.
        """
        plan_id = str(uuid.uuid4())
        if not basket_items:
            return AllocationPlan(
                plan_id=plan_id,
                retailer_id=retailer_id,
                vendor_count=0,
                vendor_subtotals={},
                total_amount_toman=0,
                is_fully_fulfilled=True,
                items=[]
            )

        # Step 1: Pre-filter candidate SKUs per basket item
        item_candidates: Dict[str, List[VendorSKU]] = {}
        item_diagnostics: Dict[str, str] = {}

        for b_item in basket_items:
            key = (b_item.master_product_id, b_item.packaging_unit, b_item.pack_quantity)
            skus = self.sku_catalog.get(key, [])
            valid_skus = []
            has_vendor = False
            has_stock = False
            has_moq = False

            for sku in skus:
                vendor = self.vendors.get(sku.vendor_id)
                if not vendor or not vendor.active or retailer_zone not in vendor.delivery_zones:
                    continue
                has_vendor = True

                if sku.available_quantity < b_item.requested_quantity:
                    continue
                has_stock = True

                if b_item.requested_quantity < sku.moq:
                    continue
                has_moq = True

                valid_skus.append(sku)

            item_candidates[b_item.id] = valid_skus
            if not has_vendor:
                item_diagnostics[b_item.id] = "NO_VENDOR_AVAILABLE"
            elif not has_stock:
                item_diagnostics[b_item.id] = "OUT_OF_STOCK"
            elif not has_moq:
                item_diagnostics[b_item.id] = "SKU_MOQ_NOT_MET"
            else:
                item_diagnostics[b_item.id] = "OUT_OF_STOCK" if not valid_skus else "FEASIBLE"

        # Collect candidate vendors across all feasible items
        candidate_vendor_ids: Set[str] = set()
        for skus in item_candidates.values():
            for sku in skus:
                candidate_vendor_ids.add(sku.vendor_id)
        sorted_vendor_ids = sorted(list(candidate_vendor_ids))

        # Generate candidate plans across K = 1, 2, ... N
        candidate_plans: List[AllocationPlan] = []

        # --- PHASE 1: K = 1 Evaluation (Single Vendor) ---
        for v_id in sorted_vendor_ids:
            plan = self._build_vendor_subset_plan(
                retailer_id, basket_items, item_candidates, item_diagnostics, [v_id]
            )
            if plan and plan.vendor_count == 1:
                candidate_plans.append(plan)

        # Check if we have complete 1-vendor plans
        complete_k1_plans = [p for p in candidate_plans if p.vendor_count == 1 and p.is_fully_fulfilled]
        if complete_k1_plans:
            # Sort by price, then vendor reputation, then vendor_id
            complete_k1_plans.sort(
                key=lambda p: (
                    p.total_amount_toman,
                    -self.vendors[list(p.vendor_subtotals.keys())[0]].reputation_score,
                    list(p.vendor_subtotals.keys())[0]
                )
            )
            return self._with_decision_hash(complete_k1_plans[0], basket_items)

        # --- PHASE 2: K = 2 Evaluation (Vendor Pairs) ---
        if len(sorted_vendor_ids) >= 2:
            for pair in itertools.combinations(sorted_vendor_ids, 2):
                plan = self._build_vendor_subset_plan(
                    retailer_id, basket_items, item_candidates, item_diagnostics, list(pair)
                )
                if plan and plan.vendor_count == 2:
                    candidate_plans.append(plan)

        complete_k2_plans = [p for p in candidate_plans if p.vendor_count == 2 and p.is_fully_fulfilled]
        if complete_k2_plans:
            complete_k2_plans.sort(
                key=lambda p: (
                    p.total_amount_toman,
                    -sum(self.vendors[v].reputation_score for v in p.vendor_subtotals) / p.vendor_count,
                    sorted(list(p.vendor_subtotals.keys()))
                )
            )
            return self._with_decision_hash(complete_k2_plans[0], basket_items)

        # --- PHASE 3: K >= 3 and Greedy Fallback with MOV Pruning ---
        greedy_plan = self._build_greedy_residual_plan(
            retailer_id, basket_items, item_candidates, item_diagnostics, sorted_vendor_ids
        )
        if greedy_plan:
            candidate_plans.append(greedy_plan)

        if not candidate_plans:
            # Entire basket unfulfilled
            return self._with_decision_hash(self._build_all_unfulfilled_plan(retailer_id, basket_items, item_diagnostics), basket_items)

        # Sort all candidate plans according to canonical objective hierarchy:
        # 1. Fulfilled line item count (descending)
        # 2. Total fulfilled value (descending)
        # 3. Vendor count K (ascending - minimize fragmentation!)
        # 4. Total cost to retailer (ascending)
        # 5. Average reputation score (descending)
        # 6. Sorted vendor IDs tuple (deterministic tie-break)
        candidate_plans.sort(
            key=lambda p: (
                -len(p.allocated_items),
                -p.total_amount_toman,
                p.vendor_count,
                p.total_amount_toman,
                -(sum(self.vendors[v].reputation_score for v in p.vendor_subtotals) / max(1, p.vendor_count)),
                sorted(list(p.vendor_subtotals.keys()))
            )
        )

        return self._with_decision_hash(candidate_plans[0], basket_items)


    def _with_decision_hash(self, plan: AllocationPlan, basket_items: List[BasketItem]) -> AllocationPlan:
        canonical = {
            "retailer_id": plan.retailer_id,
            "basket": [
                {
                    "id": x.id,
                    "product": x.master_product_id,
                    "qty": x.requested_quantity,
                    "unit": x.packaging_unit,
                    "pack_quantity": x.pack_quantity,
                }
                for x in sorted(basket_items, key=lambda z: z.id)
            ],
            "decision": [
                {
                    "basket_item_id": x.basket_item_id,
                    "status": x.status,
                    "vendor_id": x.vendor_id,
                    "vendor_sku_id": x.vendor_sku_id,
                    "qty": x.requested_quantity,
                    "unit": x.packaging_unit,
                    "unit_price": x.unit_price_toman,
                    "total": x.total_price_toman,
                    "reason": x.reason_code,
                }
                for x in sorted(plan.items, key=lambda z: z.basket_item_id)
            ],
            "vendor_subtotals": dict(sorted(plan.vendor_subtotals.items())),
            "total_amount_toman": plan.total_amount_toman,
            "vendor_count": plan.vendor_count,
        }
        plan.decision_hash = hashlib.sha256(
            json.dumps(canonical, sort_keys=True, separators=(",", ":"), default=str).encode()
        ).hexdigest()
        return plan

    def _build_vendor_subset_plan(
        self,
        retailer_id: str,
        basket_items: List[BasketItem],
        item_candidates: Dict[str, List[VendorSKU]],
        item_diagnostics: Dict[str, str],
        subset_vendor_ids: List[str]
    ) -> Optional[AllocationPlan]:
        """
        Attempts to fulfill basket using strictly the provided subset of vendors.
        Enforces that EVERY utilized vendor in the subset MUST meet their MOV.
        If a vendor in the subset cannot meet their MOV, that vendor is pruned.
        """
        subset_set = set(subset_vendor_ids)
        assignment: Dict[str, VendorSKU] = {}

        # 1. Greedy assignment to cheapest vendor within subset
        for b_item in basket_items:
            skus = [s for s in item_candidates.get(b_item.id, []) if s.vendor_id in subset_set]
            if skus:
                # Sort by price, then vendor reputation
                skus.sort(key=lambda s: (s.price_toman, -self.vendors[s.vendor_id].reputation_score, s.vendor_id, s.id))
                assignment[b_item.id] = skus[0]

        # 2. Calculate subtotals per vendor
        vendor_subtotals: Dict[str, int] = {v: 0 for v in subset_vendor_ids}
        for b_item in basket_items:
            if b_item.id in assignment:
                sku = assignment[b_item.id]
                vendor_subtotals[sku.vendor_id] += b_item.requested_quantity * sku.price_toman

        # 3. Check for MOV compensatory rebalancing if K=2
        # If one vendor is just below MOV, check if moving a multi-sourced item helps both clear MOV
        if len(subset_vendor_ids) == 2:
            v1, v2 = subset_vendor_ids[0], subset_vendor_ids[1]
            mov1, mov2 = self.vendors[v1].mov_toman, self.vendors[v2].mov_toman
            sub1, sub2 = vendor_subtotals[v1], vendor_subtotals[v2]

            # If v1 below MOV but v2 has surplus, try moving shared items from v2 to v1
            if sub1 > 0 and sub1 < mov1 and sub2 > mov2:
                for b_item in basket_items:
                    if b_item.id in assignment and assignment[b_item.id].vendor_id == v2:
                        skus = [s for s in item_candidates.get(b_item.id, []) if s.vendor_id == v1]
                        if skus:
                            transfer_val_v2 = b_item.requested_quantity * assignment[b_item.id].price_toman
                            transfer_val_v1 = b_item.requested_quantity * skus[0].price_toman
                            if (sub2 - transfer_val_v2) >= mov2:
                                # Safe to transfer!
                                assignment[b_item.id] = skus[0]
                                sub1 += transfer_val_v1
                                sub2 -= transfer_val_v2
                                vendor_subtotals[v1] = sub1
                                vendor_subtotals[v2] = sub2
                                if sub1 >= mov1:
                                    break

            # Symmetrically if v2 below MOV but v1 has surplus
            elif sub2 > 0 and sub2 < mov2 and sub1 > mov1:
                for b_item in basket_items:
                    if b_item.id in assignment and assignment[b_item.id].vendor_id == v1:
                        skus = [s for s in item_candidates.get(b_item.id, []) if s.vendor_id == v2]
                        if skus:
                            transfer_val_v1 = b_item.requested_quantity * assignment[b_item.id].price_toman
                            transfer_val_v2 = b_item.requested_quantity * skus[0].price_toman
                            if (sub1 - transfer_val_v1) >= mov1:
                                assignment[b_item.id] = skus[0]
                                sub2 += transfer_val_v2
                                sub1 -= transfer_val_v1
                                vendor_subtotals[v1] = sub1
                                vendor_subtotals[v2] = sub2
                                if sub2 >= mov2:
                                    break

        # 4. Strict MOV Feasibility Gate:
        # Every vendor with items assigned MUST meet MOV. If not, prune that vendor's items.
        valid_vendors = set()
        for v in subset_vendor_ids:
            if vendor_subtotals[v] >= self.vendors[v].mov_toman and vendor_subtotals[v] > 0:
                valid_vendors.add(v)

        # If a vendor was assigned items but failed MOV, those items become unfulfilled (or reassigned)
        final_items: List[AllocationResultItem] = []
        final_subtotals: Dict[str, int] = {v: 0 for v in valid_vendors}
        total_amount = 0

        for b_item in basket_items:
            if b_item.id in assignment and assignment[b_item.id].vendor_id in valid_vendors:
                sku = assignment[b_item.id]
                item_total = b_item.requested_quantity * sku.price_toman
                final_subtotals[sku.vendor_id] += item_total
                total_amount += item_total
                final_items.append(
                    AllocationResultItem(
                        basket_item_id=b_item.id,
                        master_product_id=b_item.master_product_id,
                        requested_quantity=b_item.requested_quantity,
                        packaging_unit=b_item.packaging_unit,
                        status="ALLOCATED",
                        vendor_id=sku.vendor_id,
                        vendor_sku_id=sku.id,
                        unit_price_toman=sku.price_toman,
                        total_price_toman=item_total,
                        reason_code="ALLOCATED"
                    )
                )
            else:
                # Check if item had candidate that failed MOV
                failed_mov = False
                if b_item.id in assignment and assignment[b_item.id].vendor_id not in valid_vendors:
                    failed_mov = True
                reason = "VENDOR_MOV_NOT_MET" if failed_mov else item_diagnostics.get(b_item.id, "OUT_OF_STOCK")
                final_items.append(
                    AllocationResultItem(
                        basket_item_id=b_item.id,
                        master_product_id=b_item.master_product_id,
                        requested_quantity=b_item.requested_quantity,
                        packaging_unit=b_item.packaging_unit,
                        status="UNFULFILLED",
                        vendor_id=None,
                        vendor_sku_id=None,
                        unit_price_toman=None,
                        total_price_toman=None,
                        reason_code=reason
                    )
                )

        if not valid_vendors:
            return None

        # Clean zero-subtotal vendors
        active_subtotals = {v: amt for v, amt in final_subtotals.items() if amt > 0}
        is_full = all(it.status == "ALLOCATED" for it in final_items)

        return AllocationPlan(
            plan_id=str(uuid.uuid4()),
            retailer_id=retailer_id,
            vendor_count=len(active_subtotals),
            vendor_subtotals=active_subtotals,
            total_amount_toman=total_amount,
            is_fully_fulfilled=is_full,
            items=final_items
        )

    def _build_greedy_residual_plan(
        self,
        retailer_id: str,
        basket_items: List[BasketItem],
        item_candidates: Dict[str, List[VendorSKU]],
        item_diagnostics: Dict[str, str],
        all_vendor_ids: List[str]
    ) -> Optional[AllocationPlan]:
        """
        Greedy multi-vendor assignment with iterative pruning of sub-MOV vendors.
        """
        # Copy candidates
        available_vendors = set(all_vendor_ids)

        while available_vendors:
            # Assign each item to cheapest eligible vendor in available_vendors
            assignment: Dict[str, VendorSKU] = {}
            for b_item in basket_items:
                skus = [s for s in item_candidates.get(b_item.id, []) if s.vendor_id in available_vendors]
                if skus:
                    skus.sort(key=lambda s: (s.price_toman, -self.vendors[s.vendor_id].reputation_score, s.vendor_id))
                    assignment[b_item.id] = skus[0]

            # Calculate subtotals
            vendor_subtotals: Dict[str, int] = {v: 0 for v in available_vendors}
            for b_item in basket_items:
                if b_item.id in assignment:
                    sku = assignment[b_item.id]
                    vendor_subtotals[sku.vendor_id] += b_item.requested_quantity * sku.price_toman

            # Find vendors failing MOV
            failing_vendors = [
                v for v, sub in vendor_subtotals.items()
                if 0 < sub < self.vendors[v].mov_toman
            ]

            if not failing_vendors:
                # All utilized vendors meet MOV!
                utilized_vendors = {v: sub for v, sub in vendor_subtotals.items() if sub > 0}
                final_items = []
                total_amount = 0
                for b_item in basket_items:
                    if b_item.id in assignment and assignment[b_item.id].vendor_id in utilized_vendors:
                        sku = assignment[b_item.id]
                        item_total = b_item.requested_quantity * sku.price_toman
                        total_amount += item_total
                        final_items.append(
                            AllocationResultItem(
                                basket_item_id=b_item.id,
                                master_product_id=b_item.master_product_id,
                                requested_quantity=b_item.requested_quantity,
                                packaging_unit=b_item.packaging_unit,
                                status="ALLOCATED",
                                vendor_id=sku.vendor_id,
                                vendor_sku_id=sku.id,
                                unit_price_toman=sku.price_toman,
                                total_price_toman=item_total,
                                reason_code="ALLOCATED"
                            )
                        )
                    else:
                        final_items.append(
                            AllocationResultItem(
                                basket_item_id=b_item.id,
                                master_product_id=b_item.master_product_id,
                                requested_quantity=b_item.requested_quantity,
                                packaging_unit=b_item.packaging_unit,
                                status="UNFULFILLED",
                                vendor_id=None,
                                vendor_sku_id=None,
                                unit_price_toman=None,
                                total_price_toman=None,
                                reason_code=item_diagnostics.get(b_item.id, "OUT_OF_STOCK")
                            )
                        )

                if not utilized_vendors:
                    return None

                return AllocationPlan(
                    plan_id=str(uuid.uuid4()),
                    retailer_id=retailer_id,
                    vendor_count=len(utilized_vendors),
                    vendor_subtotals=utilized_vendors,
                    total_amount_toman=total_amount,
                    is_fully_fulfilled=all(it.status == "ALLOCATED" for it in final_items),
                    items=final_items
                )

            # Prune the failing vendor with the largest MOV deficit
            failing_vendors.sort(key=lambda v: (self.vendors[v].mov_toman - vendor_subtotals[v], v), reverse=True)
            worst_failing = failing_vendors[0]
            available_vendors.remove(worst_failing)

        return None

    def _build_all_unfulfilled_plan(
        self,
        retailer_id: str,
        basket_items: List[BasketItem],
        item_diagnostics: Dict[str, str]
    ) -> AllocationPlan:
        items = []
        for b_item in basket_items:
            diag = item_diagnostics.get(b_item.id, "OUT_OF_STOCK")
            reason = "VENDOR_MOV_NOT_MET" if diag == "FEASIBLE" else diag
            items.append(
                AllocationResultItem(
                    basket_item_id=b_item.id,
                    master_product_id=b_item.master_product_id,
                    requested_quantity=b_item.requested_quantity,
                    packaging_unit=b_item.packaging_unit,
                    status="UNFULFILLED",
                    vendor_id=None,
                    vendor_sku_id=None,
                    unit_price_toman=None,
                    total_price_toman=None,
                    reason_code=reason
                )
            )
        return AllocationPlan(
            plan_id=str(uuid.uuid4()),
            retailer_id=retailer_id,
            vendor_count=0,
            vendor_subtotals={},
            total_amount_toman=0,
            is_fully_fulfilled=False,
            items=items
        )
