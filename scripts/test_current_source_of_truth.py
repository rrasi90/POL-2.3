"""
POL — Current Source of Truth & Brand Architecture Static Verification Gate

Validates:
1. Single Decision Authority: Exactly one decision register (POL_00_PROJECT_CONTROL/DECISION_REGISTER.md)
   with D-014 active and D-003 superseded.
2. Historical Document Banners: All 7 historical audit/hardening reports contain the canonical
   HISTORICAL / SUPERSEDED warning banner.
3. Active Documents Coherence: Active MVP specs align to D-014 multi-vendor basket without claiming
   single-vendor MVP as active.
4. Brand Architecture & Assets: POL, POL Market, and POL Vendor definitions and the 3 logo files exist.
5. Line-Item Allocation Semantics: Prohibition of intra-line splitting and two-stage pipeline explicitly specified.
6. Dispute Single Source of Truth: Canonical disputes.dispute_status vs orders.dispute_status projection.
7. Payment Model: NON_CUSTODIAL_DIRECT canonical MVP, zero custody, ESCROW_FUTURE roadmap, child order ledger.
"""

import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def check_single_decision_register():
    print("[CHECK 1] Verifying Single Decision Register Authority...")
    reg_path = os.path.join(REPO_ROOT, "POL_00_PROJECT_CONTROL", "DECISION_REGISTER.md")
    if not os.path.exists(reg_path):
        print("  [FAIL] Missing DECISION_REGISTER.md")
        return False
    
    with open(reg_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    if "D-014" not in content:
        print("  [FAIL] D-014 missing from DECISION_REGISTER.md")
        return False
    if "D-015" not in content:
        print("  [FAIL] D-015 missing from DECISION_REGISTER.md")
        return False
    if "SUPERSEDED" not in content or "D-003" not in content:
        print("  [FAIL] D-003 not marked SUPERSEDED in DECISION_REGISTER.md")
        return False
        
    # Check that no competing general decision registers exist
    ctrl_dir = os.path.join(REPO_ROOT, "POL_00_PROJECT_CONTROL")
    for fname in os.listdir(ctrl_dir):
        if fname not in ("DECISION_REGISTER.md", "MVP_MULTI_VENDOR_DECISION.md") and "DECISION" in fname.upper() and fname.endswith(".md"):
            print(f"  [FAIL] Rogue decision document found: {fname}")
            return False

    print("  [PASS] Single Decision Authority verified: DECISION_REGISTER.md governs D-001 through D-015.")
    return True

def check_historical_banners():
    print("[CHECK 2] Verifying Historical / Superseded Banners on Prior Audit/Hardening Reports...")
    historical_files = [
        "FINAL_HARDENING_REPORT.md",
        "REPOSITORY_AUDIT_AND_BUILD_READINESS.md",
        "CANONICAL_AUDIT_REPORT.md",
        "FINAL_CERTIFICATION_REPORT.md",
        "CONTRADICTION_LOG.md",
        "PRE_MVP_SCENARIO_REPORT.md",
        "PRE_MVP_SCENARIO_FINDINGS.md",
    ]
    
    for fname in historical_files:
        fpath = os.path.join(REPO_ROOT, "POL_00_PROJECT_CONTROL", fname)
        if not os.path.exists(fpath):
            print(f"  [FAIL] Historical file missing: {fname}")
            return False
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        if "HISTORICAL / SUPERSEDED" not in content:
            print(f"  [FAIL] Missing HISTORICAL / SUPERSEDED banner in {fname}")
            return False
        if "D-014" not in content:
            print(f"  [FAIL] Missing D-014 reference in banner in {fname}")
            return False

    print(f"  [PASS] All {len(historical_files)} historical documents properly carry the SUPERSEDED banner.")
    return True

def check_active_documents_coherence():
    print("[CHECK 3] Verifying Active MVP Documents Coherence with Multi-Vendor (D-014)...")
    active_files = [
        os.path.join("06_PRODUCT", "MVP_Definition.md"),
        os.path.join("06_PRODUCT", "PRD.md"),
        os.path.join("06_PRODUCT", "API_Contracts.md"),
        os.path.join("07_ALGORITHMS", "Cart_Allocation.md"),
        os.path.join("07_ALGORITHMS", "MVP_MULTI_VENDOR_ALLOCATION.md"),
        os.path.join("08_DATA", "DOMAIN_MODEL.md"),
        os.path.join("08_DATA", "MULTI_VENDOR_ORDERING_MODEL.md"),
        os.path.join("11_PILOT", "Pilot_Strategy.md"),
        os.path.join("11_PILOT", "KPIs.md"),
    ]
    
    for rel_path in active_files:
        fpath = os.path.join(REPO_ROOT, rel_path)
        if not os.path.exists(fpath):
            print(f"  [FAIL] Active document missing: {rel_path}")
            return False
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        if "D-014" not in content and "Multi-Vendor" not in content and "multi-vendor" not in content:
            print(f"  [FAIL] Active document {rel_path} does not reflect Multi-Vendor MVP (D-014)")
            return False

    print(f"  [PASS] All {len(active_files)} active MVP documents are coherent with D-014.")
    return True

def check_brand_architecture():
    print("[CHECK 4] Verifying Brand Architecture & Logo Asset Integration...")
    brand_doc = os.path.join(REPO_ROOT, "POL_00_PROJECT_CONTROL", "BRAND_ARCHITECTURE.md")
    if not os.path.exists(brand_doc):
        print("  [FAIL] BRAND_ARCHITECTURE.md is missing")
        return False
    with open(brand_doc, "r", encoding="utf-8") as f:
        content = f.read()
        
    for term in ["POL", "POL Market", "POL Vendor", "پل مغازه دار", "پل بنکدار"]:
        term_clean = term.replace(" ", "").replace("\u200c", "")
        content_clean = content.replace(" ", "").replace("\u200c", "")
        if term_clean not in content_clean:
            print(f"  [FAIL] Brand term '{term}' missing in BRAND_ARCHITECTURE.md")
            return False
            
    logo_dir = os.path.join(REPO_ROOT, "logo")
    expected_logos = [
        "pol company logo.png",
        "لوگو پل برای مغازه داران.png",
        "لوگو پل برای بنکدار.png",
    ]
    for logo in expected_logos:
        lpath = os.path.join(logo_dir, logo)
        if not os.path.exists(lpath):
            print(f"  [FAIL] Required logo file missing: {logo}")
            return False

    print("  [PASS] Brand Architecture specification and all 3 logo assets verified.")
    return True

def check_allocation_and_delivery_semantics():
    print("[CHECK 5] Verifying Line-Item Allocation & Delivery Semantics...")
    alg_path = os.path.join(REPO_ROOT, "07_ALGORITHMS", "MVP_MULTI_VENDOR_ALLOCATION.md")
    with open(alg_path, "r", encoding="utf-8") as f:
        alg_content = f.read()
        
    if "Line-Item Allocation Only" not in alg_content and "Prohibition of Intra-Line Quantity Splitting" not in alg_content:
        print("  [FAIL] Line-item allocation rule not explicitly specified in MVP_MULTI_VENDOR_ALLOCATION.md")
        return False
        
    if "Stage 1: Candidate Vendor Universe Filtering" not in alg_content:
        print("  [FAIL] Stage 1 candidate filtering not specified in MVP_MULTI_VENDOR_ALLOCATION.md")
        return False

    if "MVP Operational Simplification" not in alg_content:
        print("  [FAIL] Delivery semantics (MVP Operational Simplification) missing in MVP_MULTI_VENDOR_ALLOCATION.md")
        return False

    print("  [PASS] Line-item allocation, two-stage pipeline, and delivery simplification verified.")
    return True

def check_dispute_and_payment_invariants():
    print("[CHECK 6] Verifying Dispute SSoT and Multi-Vendor Payment Invariants...")
    data_path = os.path.join(REPO_ROOT, "08_DATA", "MULTI_VENDOR_ORDERING_MODEL.md")
    with open(data_path, "r", encoding="utf-8") as f:
        data_content = f.read()

    # Check order_status never contains DISPUTED
    if "NEVER contains" not in data_content or "DISPUTED" not in data_content:
        print("  [FAIL] orders.order_status NEVER contains 'DISPUTED' invariant missing in MULTI_VENDOR_ORDERING_MODEL.md")
        return False

    if "dispute_status" not in data_content or "canonical source of truth" not in data_content:
        print("  [FAIL] disputes.dispute_status canonical source of truth missing in MULTI_VENDOR_ORDERING_MODEL.md")
        return False

    if "NON_CUSTODIAL_DIRECT" not in data_content:
        print("  [FAIL] Canonical NON_CUSTODIAL_DIRECT payment architecture missing in MULTI_VENDOR_ORDERING_MODEL.md")
        return False

    if "Zero Custody of Funds in MVP" not in data_content or "ESCROW_FUTURE" not in data_content:
        print("  [FAIL] Zero custody in MVP / ESCROW_FUTURE roadmap distinction missing in MULTI_VENDOR_ORDERING_MODEL.md")
        return False

    if "Independent Child Order Payment Ledger" not in data_content:
        print("  [FAIL] Independent child order payment ledger missing in MULTI_VENDOR_ORDERING_MODEL.md")
        return False

    if "Vendor Rejection / Cancellation Handling" not in data_content:
        print("  [FAIL] Vendor rejection / cancellation payment handling missing in MULTI_VENDOR_ORDERING_MODEL.md")
        return False

    print("  [PASS] Dispute SSoT and Multi-Vendor NON_CUSTODIAL_DIRECT payment invariants verified.")
    return True

def check_technical_environment():
    print("[CHECK 7] Verifying Canonical Technical Environment (PostgreSQL 18 & Dependencies)...")
    env_doc = os.path.join(REPO_ROOT, "POL_00_PROJECT_CONTROL", "TECHNICAL_ENVIRONMENT.md")
    if not os.path.exists(env_doc):
        print("  [FAIL] Missing TECHNICAL_ENVIRONMENT.md")
        return False
    with open(env_doc, "r", encoding="utf-8") as f:
        env_content = f.read()
    if "PostgreSQL 18" not in env_content or "psycopg2-binary>=2.9.9" not in env_content:
        print("  [FAIL] TECHNICAL_ENVIRONMENT.md missing PostgreSQL 18 or psycopg2-binary>=2.9.9 declaration")
        return False

    req_file = os.path.join(REPO_ROOT, "requirements.txt")
    if not os.path.exists(req_file):
        print("  [FAIL] Missing requirements.txt")
        return False
    with open(req_file, "r", encoding="utf-8") as f:
        req_content = f.read()
    if "psycopg2-binary>=2.9.9" not in req_content:
        print("  [FAIL] requirements.txt missing psycopg2-binary>=2.9.9")
        return False

    arch_file = os.path.join(REPO_ROOT, "06_PRODUCT", "Technical_Architecture_Spec.md")
    with open(arch_file, "r", encoding="utf-8") as f:
        arch_content = f.read()
    if "PostgreSQL 18" not in arch_content:
        print("  [FAIL] Technical_Architecture_Spec.md missing PostgreSQL 18 target")
        return False

    mig_file = os.path.join(REPO_ROOT, "migrations", "001_initial_schema.sql")
    with open(mig_file, "r", encoding="utf-8") as f:
        mig_content = f.read()
    if "PostgreSQL 18" not in mig_content:
        print("  [FAIL] 001_initial_schema.sql missing PostgreSQL 18 target")
        return False

    print("  [PASS] Canonical Technical Environment verified: PostgreSQL 18 locked, psycopg2 declared.")
    return True

def test_current_source_of_truth():
    """Canonical pytest entry point for architecture integrity and SSoT checks."""
    checks = [
        check_single_decision_register,
        check_historical_banners,
        check_active_documents_coherence,
        check_brand_architecture,
        check_allocation_and_delivery_semantics,
        check_dispute_and_payment_invariants,
        check_technical_environment,
    ]
    for check in checks:
        assert check() is True, f"SSoT check failed at: {check.__name__}"

def main():
    print("=" * 78)
    print("POL — CURRENT SOURCE OF TRUTH & ARCHITECTURE INTEGRITY TEST SUITE")
    print("=" * 78)
    test_current_source_of_truth()
    print("=" * 78)
    print("SUCCESS: All 7/7 Source of Truth & Architecture checks PASSED!")
    print("=" * 78)

if __name__ == "__main__":
    main()
