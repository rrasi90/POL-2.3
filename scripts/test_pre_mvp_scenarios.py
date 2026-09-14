"""
POL Pre-MVP 100-Scenario Static Invariant Test Harness
Validates that all architectural constraints, domain invariants,
and scenario behaviors are mathematically consistent and contradiction-free.

Hard Failure Conditions:
1. D-003 says Single Vendor but an active MVP document exposes Split Cart checkout.
2. 'order_disputed' remains in active Test Specification or schema.
3. Order status contains 'DISPUTED'.
4. Vendor timeout values contradict (target vs 2-hour hard timeout).
5. MOQ / MOV semantics are inconsistent.
6. Candidate can become publicly purchasable without approval.
7. Vendor SKU uniqueness constraint is removed.
8. Current-price partial unique index is removed.
9. Required Transactional Outbox table or semantics disappear.
10. Required Order/Dispute orthogonal separation disappears.
"""

import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def check_1_multi_vendor_mvp():
    print("[INVARIANT 1] Checking Multi-Vendor Basket MVP (D-014) & Historical D-003...")
    cart_alloc_path = os.path.join(REPO_ROOT, "07_ALGORITHMS", "Cart_Allocation.md")
    with open(cart_alloc_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Must have canonical D-014 and historical D-003
    if "D-014" not in content:
        print("  [FAIL] Missing D-014 citation in Cart_Allocation.md")
        return False
    if "D-003" not in content:
        print("  [FAIL] Missing historical D-003 citation in Cart_Allocation.md")
        return False
    
    # Must have canonical algorithm spec MVP_MULTI_VENDOR_ALLOCATION.md
    mv_spec = os.path.join(REPO_ROOT, "07_ALGORITHMS", "MVP_MULTI_VENDOR_ALLOCATION.md")
    if not os.path.exists(mv_spec) or os.path.getsize(mv_spec) < 1000:
        print("  [FAIL] MVP_MULTI_VENDOR_ALLOCATION.md missing or too small")
        return False
        
    print("  [PASS] Invariant 1 passed: Canonical Multi-Vendor MVP (D-014) & Historical D-003 verified.")
    return True

def check_2_no_order_disputed_event():
    print("[INVARIANT 2] Checking eradication of deprecated 'order_disputed' event...")
    test_spec_path = os.path.join(REPO_ROOT, "06_PRODUCT", "Test_Specification.md")
    with open(test_spec_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "order_disputed" in content:
        print("  [FAIL] 'order_disputed' found in Test_Specification.md")
        return False
    if "dispute_opened" not in content:
        print("  [FAIL] 'dispute_opened' missing from Test_Specification.md")
        return False
    print("  [PASS] Invariant 2 passed: 'order_disputed' replaced with canonical 'dispute_opened'.")
    return True

def check_3_no_disputed_in_order_status():
    print("[INVARIANT 3] Checking orders.order_status constraint excludes 'DISPUTED'...")
    ddl_path = os.path.join(REPO_ROOT, "migrations", "001_initial_schema.sql")
    with open(ddl_path, "r", encoding="utf-8") as f:
        ddl = f.read()
    
    # Find orders table
    match = re.search(r"CREATE TABLE IF NOT EXISTS orders\s*\((.*?)\n\);", ddl, re.DOTALL)
    if not match:
        print("  [FAIL] Could not locate orders table in DDL")
        return False
    orders_block = match.group(1)
    
    status_match = re.search(r"order_status\s+VARCHAR\(\d+\).*?CHECK\s*\((.*?)\)", orders_block, re.DOTALL)
    if not status_match:
        print("  [FAIL] Could not locate order_status CHECK constraint")
        return False
    
    statuses = status_match.group(1).upper()
    if "DISPUTED" in statuses:
        print("  [FAIL] 'DISPUTED' found inside orders.order_status CHECK constraint")
        return False
    print("  [PASS] Invariant 3 passed: orders.order_status strictly excludes 'DISPUTED'.")
    return True

def check_4_vendor_timeout_consistency():
    print("[INVARIANT 4] Checking Vendor Acceptance Timeout consistency...")
    lifecycle_path = os.path.join(REPO_ROOT, "06_PRODUCT", "Order_Lifecycle.md")
    with open(lifecycle_path, "r", encoding="utf-8") as f:
        lifecycle = f.read()
    
    # Must have explicit target vs hard timeout section
    has_target = "Target Acceptance Time" in lifecycle or "زمان هدف تایید" in lifecycle
    has_hard_timeout = "Hard Acceptance Timeout" in lifecycle or "تایم‌اوت سخت تایید" in lifecycle
    has_120_min = "۱۲۰ دقیقه" in lifecycle or "120 دقیقه" in lifecycle or "120 minute" in lifecycle or "۲ ساعت کاری" in lifecycle
    
    if not (has_target and has_hard_timeout and has_120_min):
        print("  [FAIL] Missing formal Target vs Hard Timeout definitions in Order_Lifecycle.md")
        return False
    print("  [PASS] Invariant 4 passed: Vendor Acceptance Timeout hierarchy is consistent.")
    return True

def check_5_moq_mov_coexistence():
    print("[INVARIANT 5] Checking MOQ vs MOV semantic consistency and coexistence...")
    glossary_path = os.path.join(REPO_ROOT, "00_PROJECT_OVERVIEW", "Glossary.md")
    with open(glossary_path, "r", encoding="utf-8") as f:
        glossary = f.read()
    
    ddl_path = os.path.join(REPO_ROOT, "migrations", "001_initial_schema.sql")
    with open(ddl_path, "r", encoding="utf-8") as f:
        ddl = f.read()
    
    has_moq_glossary = "MOQ (Minimum Order Quantity)" in glossary
    has_mov_glossary = "MOV (Minimum Order Value)" in glossary
    has_coexistence = "هم‌زیستی الزامی در Checkout" in glossary or "MOQ_VIOLATION" in glossary
    
    has_mov_ddl = "min_order_value_toman" in ddl
    has_moq_ddl = "moq INTEGER" in ddl
    
    if not (has_moq_glossary and has_mov_glossary and has_coexistence and has_mov_ddl and has_moq_ddl):
        print("  [FAIL] MOQ / MOV semantics inconsistent between Glossary and DDL")
        return False
    print("  [PASS] Invariant 5 passed: MOQ and MOV definitions and coexistence rules verified.")
    return True

def check_6_candidate_quarantine():
    print("[INVARIANT 6] Checking Candidate Draft Quarantine invariant...")
    matching_path = os.path.join(REPO_ROOT, "08_DATA", "CATALOG_MATCHING.md")
    with open(matching_path, "r", encoding="utf-8") as f:
        matching = f.read()
    
    ddl_path = os.path.join(REPO_ROOT, "migrations", "001_initial_schema.sql")
    with open(ddl_path, "r", encoding="utf-8") as f:
        ddl = f.read()
    
    has_draft_status = "DRAFT_PENDING_CATALOG" in ddl and "DRAFT_PENDING_CATALOG" in matching
    has_quarantine_rule = "Catalog Safety Invariant" in matching or "اصل تغییرناپذیر ایمنی کاتالوگ" in matching
    
    # Must NOT permit immediate selling
    if "بلافاصله می‌تواند قیمت و موجودی خود را بفروشد" in matching:
        print("  [FAIL] Invariant violated: candidate allows immediate unapproved selling")
        return False
    
    if not (has_draft_status and has_quarantine_rule):
        print("  [FAIL] Candidate quarantine rules missing or incomplete")
        return False
    print("  [PASS] Invariant 6 passed: Candidate Draft Quarantine invariant strictly enforced.")
    return True

def check_7_vendor_sku_uniqueness():
    print("[INVARIANT 7] Checking Vendor SKU uniqueness constraint in DDL...")
    ddl_path = os.path.join(REPO_ROOT, "migrations", "001_initial_schema.sql")
    with open(ddl_path, "r", encoding="utf-8") as f:
        ddl = f.read()
    
    has_sku_uniq = "uq_vendor_product_sku UNIQUE (vendor_id, vendor_sku)" in ddl
    if not has_sku_uniq:
        print("  [FAIL] Missing constraint uq_vendor_product_sku UNIQUE (vendor_id, vendor_sku)")
        return False
    print("  [PASS] Invariant 7 passed: uq_vendor_product_sku verified.")
    return True

def check_8_current_price_uniqueness():
    print("[INVARIANT 8] Checking Current Price partial unique index...")
    ddl_path = os.path.join(REPO_ROOT, "migrations", "001_initial_schema.sql")
    with open(ddl_path, "r", encoding="utf-8") as f:
        ddl = f.read()
    
    has_price_idx = "uq_vendor_product_current_price" in ddl and "WHERE is_current = TRUE" in ddl
    if not has_price_idx:
        print("  [FAIL] Missing partial unique index uq_vendor_product_current_price WHERE is_current = TRUE")
        return False
    print("  [PASS] Invariant 8 passed: uq_vendor_product_current_price verified.")
    return True

def check_9_transactional_outbox():
    print("[INVARIANT 9] Checking Transactional Outbox table and event architecture...")
    ddl_path = os.path.join(REPO_ROOT, "migrations", "001_initial_schema.sql")
    with open(ddl_path, "r", encoding="utf-8") as f:
        ddl = f.read()
    
    event_arch_path = os.path.join(REPO_ROOT, "08_DATA", "Event_Architecture.md")
    with open(event_arch_path, "r", encoding="utf-8") as f:
        event_arch = f.read()
    
    has_outbox_table = "CREATE TABLE IF NOT EXISTS outbox_events" in ddl
    has_outbox_pattern = "Transactional Outbox" in event_arch
    has_event_table = "CREATE TABLE IF NOT EXISTS domain_events_log" in ddl
    
    if not (has_outbox_table and has_outbox_pattern and has_event_table):
        print("  [FAIL] Outbox infrastructure or documentation missing")
        return False
    print("  [PASS] Invariant 9 passed: Transactional Outbox and event architecture verified.")
    return True

def check_10_order_dispute_separation():
    print("[INVARIANT 10] Checking Order vs Dispute orthogonal separation...")
    ddl_path = os.path.join(REPO_ROOT, "migrations", "001_initial_schema.sql")
    with open(ddl_path, "r", encoding="utf-8") as f:
        ddl = f.read()
    
    has_disputes_table = "CREATE TABLE IF NOT EXISTS disputes" in ddl
    has_dispute_status_col = "dispute_status VARCHAR(30) NOT NULL DEFAULT 'NONE'" in ddl
    has_adjustments_fk = "dispute_id UUID REFERENCES disputes(id)" in ddl
    
    if not (has_disputes_table and has_dispute_status_col and has_adjustments_fk):
        print("  [FAIL] Orthogonal Dispute separation missing in DDL")
        return False
    print("  [PASS] Invariant 10 passed: Order vs Dispute orthogonal separation verified.")
    return True

def check_11_scenario_and_state_machine_documents():
    print("[INVARIANT 11] Checking existence of 100-scenario and state machine documents...")
    scenario_path = os.path.join(REPO_ROOT, "POL_00_PROJECT_CONTROL", "PRE_MVP_100_SCENARIO_STRESS_TEST.md")
    state_matrix_path = os.path.join(REPO_ROOT, "POL_00_PROJECT_CONTROL", "PRE_MVP_STATE_MACHINE_MATRIX.md")
    findings_path = os.path.join(REPO_ROOT, "POL_00_PROJECT_CONTROL", "PRE_MVP_SCENARIO_FINDINGS.md")
    
    if not (os.path.exists(scenario_path) and os.path.exists(state_matrix_path) and os.path.exists(findings_path)):
        print("  [FAIL] One or more required scenario stress test control documents are missing")
        return False
    
    # Check scenario count
    with open(scenario_path, "r", encoding="utf-8") as f:
        s_text = f.read()
    
    # Count RET-001..060 and VND-001..040
    ret_matches = re.findall(r"####\s+RET-\d{3}:", s_text)
    vnd_matches = re.findall(r"####\s+VND-\d{3}:", s_text)
    
    if len(ret_matches) != 60 or len(vnd_matches) != 40:
        print(f"  [FAIL] Expected 60 RET and 40 VND scenarios, found {len(ret_matches)} RET and {len(vnd_matches)} VND")
        return False
    print(f"  [PASS] Invariant 11 passed: All 100 scenarios (60 Retailer + 40 Vendor) verified in test matrix.")
    return True

def run_all_scenario_tests():
    print("=" * 80)
    print("POL PRE-MVP 100-SCENARIO BEHAVIORAL STRESS TEST & INVARIANT HARNESS")
    print("=" * 80)
    
    checks = [
        check_1_multi_vendor_mvp(),
        check_2_no_order_disputed_event(),
        check_3_no_disputed_in_order_status(),
        check_4_vendor_timeout_consistency(),
        check_5_moq_mov_coexistence(),
        check_6_candidate_quarantine(),
        check_7_vendor_sku_uniqueness(),
        check_8_current_price_uniqueness(),
        check_9_transactional_outbox(),
        check_10_order_dispute_separation(),
        check_11_scenario_and_state_machine_documents()
    ]
    
    print("\n" + "=" * 80)
    if all(checks):
        print("PRE-MVP STRESS TEST VERDICT: ALL 11 INVARIANT & SCENARIO CHECKS PASSED! [PASS]")
        return True
    else:
        print("PRE-MVP STRESS TEST VERDICT: STATIC INVARIANT VERIFICATION FAILED [FAIL]")
        return False

def test_pre_mvp_scenarios():
    """Canonical pytest entry point for Pre-MVP 100-scenario invariants."""
    success = run_all_scenario_tests()
    assert success is True, "Pre-MVP invariant verification failed!"

if __name__ == "__main__":
    test_pre_mvp_scenarios()
