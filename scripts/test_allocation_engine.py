"""
Unit & Regression Test Suite for POL Multi-Vendor Allocation Engine
Tests 15 mission-critical allocation behaviors and invariants.
"""

import sys
import os

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

from scripts.allocation_engine import (
    MasterProduct,
    Vendor,
    VendorSKU,
    BasketItem,
    MultiVendorAllocationEngine
)


def run_tests():
    passed = 0
    failed = 0
    test_results = []

    print("=" * 80)
    print("POL MULTI-VENDOR ALLOCATION ENGINE TEST SUITE (15 INVARIANTS)")
    print("=" * 80)

    # -------------------------------------------------------------
    # TEST 1: Section 7 Canonical Benchmark (A..E across Vendors A, B, C)
    # -------------------------------------------------------------
    print("\n[TEST 1] Testing Section 7 Canonical Benchmark...")
    try:
        vendors = {
            "vnd_a": Vendor(id="vnd_a", name="Wholesaler A", mov_toman=5_000_000, reputation_score=4.8),
            "vnd_b": Vendor(id="vnd_b", name="Wholesaler B", mov_toman=4_000_000, reputation_score=4.6),
            "vnd_c": Vendor(id="vnd_c", name="Wholesaler C", mov_toman=10_000_000, reputation_score=4.9),
        }
        skus = [
            # Vendor A: A, B, C
            VendorSKU("sku_a_a", "vnd_a", "prod_a", "CARTON", 1_000_000, 100, 0, moq=1),
            VendorSKU("sku_a_b", "vnd_a", "prod_b", "CARTON", 800_000, 100, 0, moq=1),
            VendorSKU("sku_a_c", "vnd_a", "prod_c", "CARTON", 1_200_000, 100, 0, moq=1),
            # Vendor B: C, D, E
            VendorSKU("sku_b_c", "vnd_b", "prod_c", "CARTON", 1_100_000, 100, 0, moq=1),
            VendorSKU("sku_b_d", "vnd_b", "prod_d", "CARTON", 500_000, 100, 0, moq=1),
            VendorSKU("sku_b_e", "vnd_b", "prod_e", "CARTON", 3_000_000, 100, 0, moq=1),
            # Vendor C: A, E
            VendorSKU("sku_c_a", "vnd_c", "prod_a", "CARTON", 950_000, 100, 0, moq=1),
            VendorSKU("sku_c_e", "vnd_c", "prod_e", "CARTON", 2_800_000, 100, 0, moq=1),
        ]
        engine = MultiVendorAllocationEngine(vendors, skus)
        basket = [
            BasketItem("b_1", "prod_a", 2, "CARTON"),
            BasketItem("b_2", "prod_b", 5, "CARTON"),
            BasketItem("b_3", "prod_c", 3, "CARTON"),
            BasketItem("b_4", "prod_d", 10, "CARTON"),
            BasketItem("b_5", "prod_e", 1, "CARTON"),
        ]
        plan = engine.allocate("ret_1", "Ahvaz", basket)
        assert plan.is_fully_fulfilled, "Plan should be fully fulfilled"
        assert plan.vendor_count == 2, f"Expected 2 vendors, got {plan.vendor_count}"
        assert set(plan.vendor_subtotals.keys()) == {"vnd_a", "vnd_b"}, f"Expected vendors A and B, got {plan.vendor_subtotals.keys()}"
        assert plan.vendor_subtotals["vnd_a"] == 6_000_000, f"Vendor A subtotal should be 6M, got {plan.vendor_subtotals['vnd_a']}"
        assert plan.vendor_subtotals["vnd_b"] == 11_300_000, f"Vendor B subtotal should be 11.3M, got {plan.vendor_subtotals['vnd_b']}"
        assert plan.total_amount_toman == 17_300_000, f"Total should be 17.3M, got {plan.total_amount_toman}"
        print("  [PASS] Test 1: Section 7 Canonical Benchmark verified perfectly.")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Test 1 failed: {e}")
        failed += 1

    # -------------------------------------------------------------
    # TEST 2: Single-Vendor Complete Fulfillment (K=1 Priority)
    # -------------------------------------------------------------
    print("\n[TEST 2] Testing Single-Vendor Priority (K=1 Preferred over K=2)...")
    try:
        vendors = {
            "vnd_1": Vendor(id="vnd_1", name="Mega Wholesaler", mov_toman=1_000_000),
            "vnd_2": Vendor(id="vnd_2", name="Small Wholesaler", mov_toman=500_000),
        }
        skus = [
            VendorSKU("s1", "vnd_1", "prod_a", "CARTON", 100_000, 50, 0),
            VendorSKU("s2", "vnd_1", "prod_b", "CARTON", 200_000, 50, 0),
            VendorSKU("s3", "vnd_2", "prod_b", "CARTON", 190_000, 50, 0),  # slightly cheaper but requires 2 vendors
        ]
        engine = MultiVendorAllocationEngine(vendors, skus)
        basket = [
            BasketItem("b_1", "prod_a", 10, "CARTON"),  # 1M
            BasketItem("b_2", "prod_b", 5, "CARTON"),   # 1M
        ]
        plan = engine.allocate("ret_1", "Ahvaz", basket)
        assert plan.is_fully_fulfilled
        assert plan.vendor_count == 1, f"Expected 1 vendor, got {plan.vendor_count}"
        assert "vnd_1" in plan.vendor_subtotals
        print("  [PASS] Test 2: Single-Vendor Priority (K=1) verified.")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Test 2 failed: {e}")
        failed += 1

    # -------------------------------------------------------------
    # TEST 3: Cheaper Vendor Selected When Both Can Fulfill
    # -------------------------------------------------------------
    print("\n[TEST 3] Testing Cheaper Vendor Selected (Price Optimization)...")
    try:
        vendors = {
            "vnd_cheap": Vendor(id="vnd_cheap", name="Cheap Wholesaler", mov_toman=1_000_000),
            "vnd_expensive": Vendor(id="vnd_expensive", name="Expensive Wholesaler", mov_toman=1_000_000),
        }
        skus = [
            VendorSKU("s_c1", "vnd_cheap", "prod_a", "CARTON", 90_000, 50, 0),
            VendorSKU("s_e1", "vnd_expensive", "prod_a", "CARTON", 100_000, 50, 0),
        ]
        engine = MultiVendorAllocationEngine(vendors, skus)
        basket = [BasketItem("b_1", "prod_a", 20, "CARTON")]
        plan = engine.allocate("ret_1", "Ahvaz", basket)
        assert plan.vendor_count == 1
        assert "vnd_cheap" in plan.vendor_subtotals
        assert plan.total_amount_toman == 1_800_000
        print("  [PASS] Test 3: Price Optimization verified.")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Test 3 failed: {e}")
        failed += 1

    # -------------------------------------------------------------
    # TEST 4: Independent MOV Failure Prunes Vendor
    # -------------------------------------------------------------
    print("\n[TEST 4] Testing Independent MOV Failure Prunes Vendor...")
    try:
        vendors = {
            "vnd_high_mov": Vendor(id="vnd_high_mov", name="High MOV Wholesaler", mov_toman=10_000_000),
        }
        skus = [
            VendorSKU("s1", "vnd_high_mov", "prod_a", "CARTON", 500_000, 50, 0),
        ]
        engine = MultiVendorAllocationEngine(vendors, skus)
        basket = [BasketItem("b_1", "prod_a", 2, "CARTON")]  # 1,000,000 Toman < 10,000,000 MOV
        plan = engine.allocate("ret_1", "Ahvaz", basket)
        assert plan.vendor_count == 0
        assert not plan.is_fully_fulfilled
        assert len(plan.unfulfilled_items) == 1
        assert plan.unfulfilled_items[0].reason_code == "VENDOR_MOV_NOT_MET"
        print("  [PASS] Test 4: MOV Failure Pruning and reason code verified.")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Test 4 failed: {e}")
        failed += 1

    # -------------------------------------------------------------
    # TEST 5: SKU MOQ Not Met Prevents Allocation
    # -------------------------------------------------------------
    print("\n[TEST 5] Testing SKU MOQ Not Met...")
    try:
        vendors = {
            "vnd_1": Vendor(id="vnd_1", name="Wholesaler 1", mov_toman=100_000),
        }
        skus = [
            VendorSKU("s1", "vnd_1", "prod_a", "CARTON", 50_000, 50, 0, moq=10),
        ]
        engine = MultiVendorAllocationEngine(vendors, skus)
        basket = [BasketItem("b_1", "prod_a", 5, "CARTON")]  # 5 < MOQ 10
        plan = engine.allocate("ret_1", "Ahvaz", basket)
        assert plan.vendor_count == 0
        assert len(plan.unfulfilled_items) == 1
        assert plan.unfulfilled_items[0].reason_code == "SKU_MOQ_NOT_MET"
        print("  [PASS] Test 5: SKU MOQ check verified.")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Test 5 failed: {e}")
        failed += 1

    # -------------------------------------------------------------
    # TEST 6: Out of Stock Prevents Allocation
    # -------------------------------------------------------------
    print("\n[TEST 6] Testing Out of Stock Detection...")
    try:
        vendors = {
            "vnd_1": Vendor(id="vnd_1", name="Wholesaler 1", mov_toman=100_000),
        }
        skus = [
            VendorSKU("s1", "vnd_1", "prod_a", "CARTON", 50_000, 10, 8),  # net available = 2
        ]
        engine = MultiVendorAllocationEngine(vendors, skus)
        basket = [BasketItem("b_1", "prod_a", 5, "CARTON")]  # requested 5 > net 2
        plan = engine.allocate("ret_1", "Ahvaz", basket)
        assert plan.vendor_count == 0
        assert plan.unfulfilled_items[0].reason_code == "OUT_OF_STOCK"
        print("  [PASS] Test 6: Out of Stock check verified.")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Test 6 failed: {e}")
        failed += 1

    # -------------------------------------------------------------
    # TEST 7: Three-Vendor Open Allocation (D-005 Open Vendor Count)
    # -------------------------------------------------------------
    print("\n[TEST 7] Testing Three-Vendor Allocation (D-005 Open Count)...")
    try:
        vendors = {
            "v1": Vendor(id="v1", name="Vendor 1", mov_toman=1_000_000),
            "v2": Vendor(id="v2", name="Vendor 2", mov_toman=1_000_000),
            "v3": Vendor(id="v3", name="Vendor 3", mov_toman=1_000_000),
        }
        skus = [
            VendorSKU("s1", "v1", "prod_1", "CARTON", 1_000_000, 10, 0),
            VendorSKU("s2", "v2", "prod_2", "CARTON", 1_000_000, 10, 0),
            VendorSKU("s3", "v3", "prod_3", "CARTON", 1_000_000, 10, 0),
        ]
        engine = MultiVendorAllocationEngine(vendors, skus)
        basket = [
            BasketItem("b1", "prod_1", 1, "CARTON"),
            BasketItem("b2", "prod_2", 1, "CARTON"),
            BasketItem("b3", "prod_3", 1, "CARTON"),
        ]
        plan = engine.allocate("ret_1", "Ahvaz", basket)
        assert plan.is_fully_fulfilled
        assert plan.vendor_count == 3, f"Expected 3 vendors, got {plan.vendor_count}"
        assert set(plan.vendor_subtotals.keys()) == {"v1", "v2", "v3"}
        print("  [PASS] Test 7: Three-Vendor Allocation verified.")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Test 7 failed: {e}")
        failed += 1

    # -------------------------------------------------------------
    # TEST 8: Compensatory Rebalancing between Two Vendors
    # -------------------------------------------------------------
    print("\n[TEST 8] Testing Compensatory Rebalancing...")
    try:
        vendors = {
            "v1": Vendor(id="v1", name="Vendor 1", mov_toman=2_000_000),
            "v2": Vendor(id="v2", name="Vendor 2", mov_toman=2_000_000),
        }
        skus = [
            VendorSKU("s1", "v1", "prod_only_v1", "CARTON", 1_000_000, 10, 0),
            VendorSKU("s2", "v2", "prod_only_v2", "CARTON", 5_000_000, 10, 0),
            # Shared item: cheaper at v2, but v1 needs it to clear MOV (1M + 1M = 2M)
            VendorSKU("s3_v1", "v1", "prod_shared", "CARTON", 1_000_000, 10, 0),
            VendorSKU("s3_v2", "v2", "prod_shared", "CARTON", 950_000, 10, 0),
        ]
        engine = MultiVendorAllocationEngine(vendors, skus)
        basket = [
            BasketItem("b1", "prod_only_v1", 1, "CARTON"),
            BasketItem("b2", "prod_only_v2", 1, "CARTON"),
            BasketItem("b3", "prod_shared", 1, "CARTON"),
        ]
        plan = engine.allocate("ret_1", "Ahvaz", basket)
        assert plan.is_fully_fulfilled
        assert plan.vendor_count == 2
        assert plan.vendor_subtotals["v1"] >= 2_000_000
        assert plan.vendor_subtotals["v2"] >= 2_000_000
        print("  [PASS] Test 8: Compensatory Rebalancing verified.")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Test 8 failed: {e}")
        failed += 1

    # -------------------------------------------------------------
    # TEST 9: Unfulfilled Items Preserve Demand
    # -------------------------------------------------------------
    print("\n[TEST 9] Testing Unfulfilled Items Demand Preservation...")
    try:
        vendors = {
            "v1": Vendor(id="v1", name="Vendor 1", mov_toman=1_000_000),
        }
        skus = [
            VendorSKU("s1", "v1", "prod_1", "CARTON", 1_000_000, 10, 0),
        ]
        engine = MultiVendorAllocationEngine(vendors, skus)
        basket = [
            BasketItem("b1", "prod_1", 1, "CARTON"),
            BasketItem("b2", "prod_nonexistent", 1, "CARTON"),
        ]
        plan = engine.allocate("ret_1", "Ahvaz", basket)
        assert not plan.is_fully_fulfilled
        assert len(plan.allocated_items) == 1
        assert len(plan.unfulfilled_items) == 1
        assert plan.unfulfilled_items[0].vendor_id is None
        assert plan.unfulfilled_items[0].reason_code == "NO_VENDOR_AVAILABLE"
        print("  [PASS] Test 9: Unfulfilled Demand Preservation verified.")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Test 9 failed: {e}")
        failed += 1

    # -------------------------------------------------------------
    # TEST 10: Deterministic Reproducibility (100 Iterations)
    # -------------------------------------------------------------
    print("\n[TEST 10] Testing Deterministic Reproducibility...")
    try:
        vendors = {
            "va": Vendor(id="va", name="Vendor A", mov_toman=1_000_000),
            "vb": Vendor(id="vb", name="Vendor B", mov_toman=1_000_000),
        }
        skus = [
            VendorSKU("sa", "va", "prod_1", "CARTON", 1_000_000, 10, 0),
            VendorSKU("sb", "vb", "prod_1", "CARTON", 1_000_000, 10, 0),
        ]
        engine = MultiVendorAllocationEngine(vendors, skus)
        basket = [BasketItem("b1", "prod_1", 1, "CARTON")]
        first_plan = engine.allocate("ret_1", "Ahvaz", basket)
        selected_v = list(first_plan.vendor_subtotals.keys())[0]

        for _ in range(100):
            p = engine.allocate("ret_1", "Ahvaz", basket)
            assert list(p.vendor_subtotals.keys())[0] == selected_v
        print("  [PASS] Test 10: 100% Deterministic Reproducibility verified.")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Test 10 failed: {e}")
        failed += 1

    # -------------------------------------------------------------
    # TEST 11: Inactive Vendor Excluded
    # -------------------------------------------------------------
    print("\n[TEST 11] Testing Inactive Vendor Exclusion...")
    try:
        vendors = {
            "v_inactive": Vendor(id="v_inactive", name="Suspended Vendor", active=False, mov_toman=100_000),
            "v_active": Vendor(id="v_active", name="Active Vendor", active=True, mov_toman=100_000),
        }
        skus = [
            VendorSKU("s1", "v_inactive", "prod_1", "CARTON", 50_000, 10, 0),
            VendorSKU("s2", "v_active", "prod_1", "CARTON", 100_000, 10, 0),
        ]
        engine = MultiVendorAllocationEngine(vendors, skus)
        basket = [BasketItem("b1", "prod_1", 2, "CARTON")]
        plan = engine.allocate("ret_1", "Ahvaz", basket)
        assert plan.vendor_count == 1
        assert "v_active" in plan.vendor_subtotals
        print("  [PASS] Test 11: Inactive Vendor Exclusion verified.")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Test 11 failed: {e}")
        failed += 1

    # -------------------------------------------------------------
    # TEST 12: Out of Zone Vendor Excluded
    # -------------------------------------------------------------
    print("\n[TEST 12] Testing Geographic Out of Bounds...")
    try:
        vendors = {
            "v_tehran": Vendor(id="v_tehran", name="Tehran Vendor", delivery_zones=("Tehran",), mov_toman=100_000),
            "v_ahvaz": Vendor(id="v_ahvaz", name="Ahvaz Vendor", delivery_zones=("Ahvaz",), mov_toman=100_000),
        }
        skus = [
            VendorSKU("s1", "v_tehran", "prod_1", "CARTON", 50_000, 10, 0),
            VendorSKU("s2", "v_ahvaz", "prod_1", "CARTON", 100_000, 10, 0),
        ]
        engine = MultiVendorAllocationEngine(vendors, skus)
        basket = [BasketItem("b1", "prod_1", 2, "CARTON")]
        plan = engine.allocate("ret_1", "Ahvaz", basket)
        assert plan.vendor_count == 1
        assert "v_ahvaz" in plan.vendor_subtotals
        print("  [PASS] Test 12: Geographic Zone Filtering verified.")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Test 12 failed: {e}")
        failed += 1

    # -------------------------------------------------------------
    # TEST 13: Multi-Packaging Exact Match
    # -------------------------------------------------------------
    print("\n[TEST 13] Testing Packaging Unit Precision...")
    try:
        vendors = {
            "v1": Vendor(id="v1", name="Vendor 1", mov_toman=100_000),
        }
        skus = [
            VendorSKU("s_box", "v1", "prod_1", "BOX", 100_000, 10, 0),
            VendorSKU("s_carton", "v1", "prod_1", "CARTON", 500_000, 10, 0),
        ]
        engine = MultiVendorAllocationEngine(vendors, skus)
        basket = [BasketItem("b1", "prod_1", 1, "CARTON")]
        plan = engine.allocate("ret_1", "Ahvaz", basket)
        assert plan.allocated_items[0].vendor_sku_id == "s_carton"
        assert plan.allocated_items[0].total_price_toman == 500_000
        print("  [PASS] Test 13: Packaging Unit Precision verified.")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Test 13 failed: {e}")
        failed += 1

    # -------------------------------------------------------------
    # TEST 14: Empty Basket Handled Gracefully
    # -------------------------------------------------------------
    print("\n[TEST 14] Testing Empty Basket Handling...")
    try:
        vendors = {
            "v1": Vendor(id="v1", name="Vendor 1", mov_toman=100_000),
        }
        engine = MultiVendorAllocationEngine(vendors, [])
        plan = engine.allocate("ret_1", "Ahvaz", [])
        assert plan.vendor_count == 0
        assert plan.total_amount_toman == 0
        assert plan.is_fully_fulfilled
        print("  [PASS] Test 14: Empty Basket Handling verified.")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Test 14 failed: {e}")
        failed += 1

    # -------------------------------------------------------------
    # TEST 15: All Items Unfulfillable Handled Gracefully
    # -------------------------------------------------------------
    print("\n[TEST 15] Testing Complete Allocation Failure (All Out of Stock)...")
    try:
        vendors = {
            "v1": Vendor(id="v1", name="Vendor 1", mov_toman=100_000),
        }
        skus = [
            VendorSKU("s1", "v1", "prod_1", "CARTON", 100_000, 0, 0),
        ]
        engine = MultiVendorAllocationEngine(vendors, skus)
        basket = [BasketItem("b1", "prod_1", 1, "CARTON")]
        plan = engine.allocate("ret_1", "Ahvaz", basket)
        assert not plan.is_fully_fulfilled
        assert plan.vendor_count == 0
        assert len(plan.unfulfilled_items) == 1
        assert plan.unfulfilled_items[0].reason_code == "OUT_OF_STOCK"
        print("  [PASS] Test 15: Complete Allocation Failure Handling verified.")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Test 15 failed: {e}")
        failed += 1

    print("\n" + "=" * 80)
    print("ALLOCATION ENGINE TEST SUMMARY REPORT")
    print(f"Total Tests: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if failed == 0:
        print("VERDICT: ALL 15 ALLOCATION ENGINE INVARIANT TESTS PASSED! [PASS]")
        return True
    else:
        print("VERDICT: SOME TESTS FAILED [FAIL]")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
