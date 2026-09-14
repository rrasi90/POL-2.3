"""
Repository Consistency & Architectural Integrity Verification Script for POL (پُل)
Comprehensive Independent Verification Suite (Checks 1 through 11).
"""

import os
import re
import sys
import json

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def run_checks():
    passed = 0
    failed = 0
    errors = []

    print("=" * 80)
    print("POL REPOSITORY CONSISTENCY & ARCHITECTURAL INTEGRITY AUDIT")
    print(f"Repository Root: {REPO_ROOT}")
    print("=" * 80)

    migration_file_1 = os.path.join(REPO_ROOT, "migrations", "001_initial_schema.sql")
    migration_file_2 = os.path.join(REPO_ROOT, "migrations", "002_platform_core_schema.sql")
    migration_file_3 = os.path.join(REPO_ROOT, "migrations", "003_contract_reconciliation.sql")
    if not os.path.exists(migration_file_1) or not os.path.exists(migration_file_2) or not os.path.exists(migration_file_3):
        errors.append(f"Missing migration files")
        print(f"  [FAIL] Missing migration file: {migration_file_1}, {migration_file_2}, or {migration_file_3}")
        return False

    with open(migration_file_1, "r", encoding="utf-8") as f:
        ddl_001 = f.read()
    with open(migration_file_2, "r", encoding="utf-8") as f:
        ddl_002 = f.read()
    with open(migration_file_3, "r", encoding="utf-8") as f:
        ddl_003 = f.read()
    ddl_content = ddl_001 + "\n" + ddl_002 + "\n" + ddl_003

    # -------------------------------------------------------------
    # CHECK 1: Database Migration Schema Table Integrity (56 Tables)
    # -------------------------------------------------------------
    print("\n[CHECK 1] Verifying Complete Database Migration Chain (001 + 002 + 003)...")
    required_tables = [
        "users", "retailers", "vendors", "brands", "categories",
        "subcategories", "products", "product_reference_metadata",
        "product_identifiers", "media_assets", "product_media",
        "product_candidates", "product_merge_history", "vendor_products",
        "vendor_inventory", "vendor_prices", "inventory_audit_log",
        "baskets", "basket_items", "allocation_plans", "allocation_items",
        "order_groups", "orders", "order_items", "deliveries",
        "delivery_attempts", "proof_of_delivery", "disputes", "payments",
        "payment_attempts", "settlements", "settlement_adjustments",
        "refunds", "reputations", "reputation_snapshots", "outbox_events",
        "domain_events_log",
        "organizations", "organization_memberships", "user_devices",
        "user_sessions", "otp_challenges", "notifications",
        "notification_deliveries", "user_inbox_items", "notification_preferences",
        "broadcast_messages", "broadcast_recipients", "support_cases",
        "support_case_messages", "support_case_assignments", "field_tasks",
        "inventory_reservations", "invoices", "invoice_items", "admin_audit_logs"
    ]

    missing_tables = []
    for tbl in required_tables:
        pattern = rf"CREATE\s+TABLE\s+(IF\s+NOT\s+EXISTS\s+)?{tbl}\b"
        if not re.search(pattern, ddl_content, re.IGNORECASE):
            missing_tables.append(tbl)

    if missing_tables:
        errors.append(f"Missing DDL tables in migration: {missing_tables}")
        failed += 1
        print(f"  [FAIL] Missing tables: {missing_tables}")
    else:
        print(f"  [PASS] All {len(required_tables)} canonical tables verified in DDL.")
        passed += 1

    # -------------------------------------------------------------
    # CHECK 2: Orthogonal Dispute Architecture Separation
    # -------------------------------------------------------------
    print("\n[CHECK 2] Verifying Orthogonal Separation of Orders vs Disputes...")
    orders_match = re.search(r"CREATE\s+TABLE\s+(IF\s+NOT\s+EXISTS\s+)?orders\s*\((.*?)\n\);", ddl_content, re.DOTALL | re.IGNORECASE)
    if not orders_match:
        errors.append("Could not isolate CREATE TABLE orders block in DDL")
        failed += 1
    else:
        orders_block = orders_match.group(2)
        status_match = re.search(r"order_status\s+VARCHAR\(\d+\).*?CHECK\s*\((.*?)\)", orders_block, re.DOTALL | re.IGNORECASE)
        if status_match:
            status_check = status_match.group(1)
            if "DISPUTED" in status_check.upper():
                errors.append("Violation: 'DISPUTED' is present in orders.order_status check constraint!")
                failed += 1
                print("  [FAIL] 'DISPUTED' found in orders.order_status constraint.")
            else:
                print("  [PASS] orders.order_status constraint correctly excludes 'DISPUTED'.")
                passed += 1
        else:
            errors.append("Could not find order_status CHECK constraint in orders table")
            failed += 1

    disputes_match = re.search(r"CREATE\s+TABLE\s+(IF\s+NOT\s+EXISTS\s+)?disputes\s*\((.*?)\);", ddl_content, re.DOTALL | re.IGNORECASE)
    if disputes_match and "dispute_status" in disputes_match.group(2):
        print("  [PASS] Independent 'disputes' table verified with dispute_status column.")
        passed += 1
    else:
        errors.append("Missing or invalid 'disputes' table definition")
        failed += 1

    # -------------------------------------------------------------
    # CHECK 3: Master SKU Dataset Profiling & Record Count
    # -------------------------------------------------------------
    print("\n[CHECK 3] Verifying Master SKU Dataset (Master SKU/backup_no_images.json)...")
    dataset_file = os.path.join(REPO_ROOT, "Master SKU", "backup_no_images.json")
    if not os.path.exists(dataset_file):
        errors.append(f"Master SKU dataset missing: {dataset_file}")
        failed += 1
        print(f"  [FAIL] Dataset file not found at {dataset_file}")
    else:
        try:
            with open(dataset_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            total_records = len(data)
            if total_records == 68707:
                print(f"  [PASS] Exact record count verified ({total_records:,} items).")
                passed += 1
            else:
                errors.append(f"Master SKU record count discrepancy: expected 68707, found {total_records}")
                failed += 1
        except Exception as e:
            errors.append(f"Error reading Master SKU dataset: {e}")
            failed += 1

    # -------------------------------------------------------------
    # CHECK 4: Canonical Decisions (D-001 through D-014)
    # -------------------------------------------------------------
    print("\n[CHECK 4] Verifying Canonical Decisions D-001 through D-014 and MVP Multi-Vendor Direction...")
    assumptions_file = os.path.join(REPO_ROOT, "01_RESEARCH", "Assumptions_and_Hypotheses.md")
    dec_reg_file = os.path.join(REPO_ROOT, "POL_00_PROJECT_CONTROL", "DECISION_REGISTER.md")
    
    if not os.path.exists(assumptions_file):
        errors.append(f"Missing assumptions file: {assumptions_file}")
        failed += 1
    else:
        with open(assumptions_file, "r", encoding="utf-8") as f:
            content = f.read()

        missing_decisions = []
        for i in range(1, 15):
            dec_id = f"D-{i:03d}"
            if dec_id not in content:
                missing_decisions.append(dec_id)

        if missing_decisions:
            errors.append(f"Missing Canonical Decisions in {assumptions_file}: {missing_decisions}")
            failed += 1
            print(f"  [FAIL] Missing decisions in {assumptions_file}: {missing_decisions}")
        else:
            print(f"  [PASS] All 14 canonical decisions (D-001 to D-014) verified in Assumptions_and_Hypotheses.md.")
            passed += 1

    # Verify DECISION_REGISTER.md consistency
    if os.path.exists(dec_reg_file):
        with open(dec_reg_file, "r", encoding="utf-8") as f:
            reg_content = f.read()
        if "D-001 through D-014" in reg_content and "D-014" in reg_content:
            print("  [PASS] DECISION_REGISTER.md correctly registers D-001 through D-014.")
            passed += 1
        else:
            errors.append("DECISION_REGISTER.md missing D-001 through D-014 header or D-014 entry")
            failed += 1
        
        if "SUPERSEDED by D-014" in reg_content:
            print("  [PASS] D-003 correctly documented as superseded by D-014.")
            passed += 1
        else:
            errors.append("D-003 not marked as superseded by D-014 in DECISION_REGISTER.md")
            failed += 1

    # -------------------------------------------------------------
    # CHECK 5: Canonical Documents Existence & Minimum Size
    # -------------------------------------------------------------
    print("\n[CHECK 5] Verifying Existence and Non-Emptiness of Canonical Documents...")
    canonical_files = [
        ("POL_00_PROJECT_CONTROL/REPOSITORY_INVENTORY.md", 1000),
        ("POL_00_PROJECT_CONTROL/SYSTEM_CONSISTENCY_MATRIX.md", 1000),
        ("POL_00_PROJECT_CONTROL/FINAL_TRACEABILITY_MATRIX.md", 1000),
        ("POL_00_PROJECT_CONTROL/FINAL_CONTRADICTION_REGISTER.md", 1000),
        ("01_RESEARCH/Assumptions_and_Hypotheses.md", 2000),
        ("01_RESEARCH/Evidence_Register.md", 1000),
        ("06_PRODUCT/PRD.md", 5000),
        ("06_PRODUCT/Order_Lifecycle.md", 3000),
        ("06_PRODUCT/API_Contracts.md", 5000),
        ("06_PRODUCT/Technical_Architecture_Spec.md", 5000),
        ("06_PRODUCT/SCHEMA_API_VERIFICATION.md", 1000),
        ("08_DATA/DOMAIN_MODEL.md", 5000),
        ("08_DATA/Data_Schema.md", 5000),
        ("08_DATA/CATALOG_DATA_DICTIONARY.md", 1000),
        ("08_DATA/INVENTORY_DATA_DICTIONARY.md", 1000),
        ("08_DATA/CATALOG_PRODUCT_MASTER.md", 3000),
        ("08_DATA/INVENTORY_MODEL.md", 3000),
        ("08_DATA/Event_Architecture.md", 4000),
        ("08_DATA/Master_SKU_Import_Audit.md", 2000),
        ("08_DATA/Master_SKU_Ground_Truth.json", 1000),
        ("09_OPERATIONS/Payments_and_Settlement.md", 4000),
        ("11_PILOT/KPIs.md", 2000),
        ("11_PILOT/Success_Criteria.md", 2000),
        ("migrations/001_initial_schema.sql", 5000),
        ("POL_00_PROJECT_CONTROL/MVP_MULTI_VENDOR_DECISION.md", 1000),
        ("07_ALGORITHMS/MVP_MULTI_VENDOR_ALLOCATION.md", 2000),
        ("08_DATA/MULTI_VENDOR_ORDERING_MODEL.md", 2000),
        ("POL_00_PROJECT_CONTROL/RUNTIME_SCENARIO_VALIDATION.md", 2000),
        ("POL_00_PROJECT_CONTROL/MULTI_VENDOR_MVP_READINESS_REPORT.md", 2000),
        ("POL_00_PROJECT_CONTROL/CANONICAL_CONTRACT_MATRIX.md", 1000),
        ("POL_00_PROJECT_CONTROL/DATABASE_SCHEMA_MANIFEST.md", 1000),
        ("migrations/002_platform_core_schema.sql", 5000),
    ]

    all_docs_valid = True
    for rel_path, min_bytes in canonical_files:
        full_path = os.path.join(REPO_ROOT, rel_path.replace("/", os.sep))
        if not os.path.exists(full_path):
            errors.append(f"Canonical document missing: {rel_path}")
            all_docs_valid = False
        else:
            size = os.path.getsize(full_path)
            if size < min_bytes:
                errors.append(f"Canonical document too small ({size} < {min_bytes} bytes): {rel_path}")
                all_docs_valid = False

    if all_docs_valid:
        print(f"  [PASS] All {len(canonical_files)} canonical documents exist and meet size thresholds.")
        passed += 1
    else:
        print("  [FAIL] Some canonical documents are missing or below size thresholds.")
        failed += 1

    # -------------------------------------------------------------
    # CHECK 6: Contradiction & Deprecated Keyword Scan
    # -------------------------------------------------------------
    print("\n[CHECK 6] Scanning for Contradictions & Deprecated Keywords...")
    contradiction_checks = [
        {
            "name": "Invalid assignment order_status = DISPUTED",
            "pattern": r"(?:order_status\s*=\s*['\"]DISPUTED['\"]|'DISPUTED'\s*in\s*order_status|status_in_order_status.*DISPUTED)",
            "allowed_in": ["scripts/verify_repository_consistency.py", "scripts/test_verification_mutations.py"],
            "description": "Invalid DISPUTED status assigned to order_status"
        },
        {
            "name": "Ambiguous Fastify / NestJS Slash",
            "pattern": r"Fastify\s*/\s*NestJS",
            "allowed_in": ["scripts/verify_repository_consistency.py", "scripts/test_verification_mutations.py"],
            "description": "Slash ambiguity Fastify / NestJS"
        }
    ]

    scan_errors = []
    scan_dirs = ["00_PROJECT_OVERVIEW", "01_RESEARCH", "06_PRODUCT", "08_DATA", "09_OPERATIONS", "11_PILOT", "POL_00_PROJECT_CONTROL"]
    for sdir in scan_dirs:
        dir_path = os.path.join(REPO_ROOT, sdir)
        if not os.path.exists(dir_path):
            continue
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".md"):
                    fpath = os.path.join(root, file)
                    rel_fpath = os.path.relpath(fpath, REPO_ROOT).replace("\\", "/")
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                    for idx, line in enumerate(lines, 1):
                        for c in contradiction_checks:
                            if re.search(c["pattern"], line, re.IGNORECASE):
                                if rel_fpath not in c["allowed_in"]:
                                    scan_errors.append(f"{rel_fpath}:{idx} -> {c['name']}")

    if scan_errors:
        errors.extend(scan_errors)
        failed += 1
        print(f"  [FAIL] Found {len(scan_errors)} contradiction occurrences:")
        for err in scan_errors[:5]:
            print(f"     - {err}")
    else:
        print("  [PASS] Zero contradiction keywords found across documentation.")
        passed += 1

    # -------------------------------------------------------------
    # CHECK 7: Advanced Schema Constraints & Referential Integrity
    # -------------------------------------------------------------
    print("\n[CHECK 7] Verifying Advanced Schema Constraints & Foreign Keys...")
    schema_checks_passed = True

    # 7.1: vendor_products: UNIQUE(vendor_id, vendor_sku) present; UNIQUE(vendor_id, product_id) removed
    if "uq_vendor_product_sku UNIQUE (vendor_id, vendor_sku)" not in ddl_content:
        errors.append("Missing uq_vendor_product_sku constraint in vendor_products")
        schema_checks_passed = False
    if "UNIQUE (vendor_id, product_id)" in ddl_content:
        errors.append("Constraint violation: Restrictive UNIQUE(vendor_id, product_id) is present in vendor_products")
        schema_checks_passed = False

    # 7.2: vendor_prices: partial unique index on is_current = TRUE
    if "uq_vendor_product_current_price" not in ddl_content or "WHERE is_current = TRUE" not in ddl_content:
        errors.append("Missing uq_vendor_product_current_price partial unique index on vendor_prices")
        schema_checks_passed = False

    # 7.3: settlement_adjustments has REFERENCES disputes(id)
    if not re.search(r"dispute_id\s+UUID\s+REFERENCES\s+disputes\(id\)", ddl_content, re.IGNORECASE):
        errors.append("Missing explicit FOREIGN KEY (dispute_id) REFERENCES disputes(id) in settlement_adjustments")
        schema_checks_passed = False

    # 7.4: refunds has REFERENCES disputes(id)
    refunds_match = re.search(r"CREATE\s+TABLE\s+(IF\s+NOT\s+EXISTS\s+)?refunds\s*\((.*?)\);", ddl_content, re.DOTALL | re.IGNORECASE)
    if not refunds_match or "REFERENCES disputes(id)" not in refunds_match.group(2):
        errors.append("Missing explicit FOREIGN KEY (dispute_id) REFERENCES disputes(id) in refunds")
        schema_checks_passed = False

    # 7.5: allocation_items supports UNFULFILLED with NULL vendor_id
    if "status = 'UNFULFILLED' AND vendor_id IS NULL" not in ddl_content:
        errors.append("Missing UNFULFILLED check constraint allowing NULL vendor_id in allocation_items")
        schema_checks_passed = False

    # 7.6: vendor_inventory has generic quantity fields
    if "inventory_unit" not in ddl_content or "physical_quantity" not in ddl_content:
        errors.append("vendor_inventory lacks generic inventory_unit or physical_quantity fields")
        schema_checks_passed = False

    # 7.7: product_identifiers has vendor-scoped index
    if "uq_vendor_product_identifier" not in ddl_content:
        errors.append("Missing uq_vendor_product_identifier for vendor-scoped internal barcodes")
        schema_checks_passed = False

    # 7.8: reputation_snapshots table exists
    if "reputation_snapshots" not in ddl_content:
        errors.append("Missing reputation_snapshots table in DDL")
        schema_checks_passed = False

    # 7.9: basket_items multi-packaging uniqueness
    if "uq_basket_product_packaging" not in ddl_content:
        errors.append("Missing uq_basket_product_packaging constraint in basket_items")
        schema_checks_passed = False

    if schema_checks_passed:
        print("  [PASS] All advanced schema constraints, partial unique indices, and FKs verified.")
        passed += 1
    else:
        print("  [FAIL] Advanced schema constraint verification failed.")
        failed += 1

    # -------------------------------------------------------------
    # CHECK 8: 100% Column-Level Parity between DDL and Data_Schema.md
    # -------------------------------------------------------------
    print("\n[CHECK 8] Verifying Column-Level Parity between DDL and Data_Schema.md...")
    doc_file = os.path.join(REPO_ROOT, "08_DATA", "Data_Schema.md")
    if not os.path.exists(doc_file):
        errors.append(f"Missing Data_Schema.md file: {doc_file}")
        failed += 1
    else:
        with open(doc_file, "r", encoding="utf-8") as f:
            doc_content = f.read()

        def extract_table_columns(content):
            pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z0-9_]+)\s*\((.*?)\);'
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            tbls = {}
            for tbl, body in matches:
                cols = []
                for line in body.split('\n'):
                    line = line.strip()
                    if not line or line.startswith('--') or line.startswith('CONSTRAINT') or line.startswith('PRIMARY') or line.startswith('FOREIGN') or line.startswith('CHECK'):
                        continue
                    m = re.match(r'^([a-zA-Z0-9_]+)\s+', line)
                    if m:
                        cols.append(m.group(1).lower())
                tbls[tbl.lower()] = cols
            return tbls

        ddl_tbls = extract_table_columns(ddl_content)
        doc_tbls = extract_table_columns(doc_content)

        parity_mismatches = []
        for tbl in required_tables:
            if tbl not in ddl_tbls:
                parity_mismatches.append(f"Table {tbl} missing in DDL")
            elif tbl not in doc_tbls:
                parity_mismatches.append(f"Table {tbl} missing in Data_Schema.md")
            elif ddl_tbls[tbl] != doc_tbls[tbl]:
                parity_mismatches.append(f"Column mismatch in {tbl}: DDL={ddl_tbls[tbl]} vs DOC={doc_tbls[tbl]}")

        if parity_mismatches:
            errors.extend(parity_mismatches)
            failed += 1
            print(f"  [FAIL] Column parity mismatches found ({len(parity_mismatches)}):")
            for m in parity_mismatches[:3]:
                print(f"     - {m}")
        else:
            print(f"  [PASS] All {len(required_tables)} tables have 100% identical column definitions between DDL and Data_Schema.md.")
            passed += 1

    # -------------------------------------------------------------
    # CHECK 9: Generic Unit Abstraction in DDL and API Contracts
    # -------------------------------------------------------------
    print("\n[CHECK 9] Verifying Generic Unit Abstraction in DDL and API Contracts...")
    unit_checks_passed = True

    # 9.1: order_items in DDL must not contain carton-only fields
    if "quantity_cartons_requested" in ddl_content or "price_per_carton_toman" in ddl_content:
        errors.append("DDL order_items contains legacy carton-only columns (quantity_cartons_requested or price_per_carton_toman)")
        unit_checks_passed = False

    # 9.2: API_Contracts.md must not contain carton-only fields
    api_file = os.path.join(REPO_ROOT, "06_PRODUCT", "API_Contracts.md")
    if os.path.exists(api_file):
        with open(api_file, "r", encoding="utf-8") as f:
            api_content = f.read()
        legacy_api_patterns = [r'"available_cartons"', r'"requested_cartons"', r'"price_per_carton_toman"']
        for p in legacy_api_patterns:
            if re.search(p, api_content):
                errors.append(f"API_Contracts.md contains legacy carton-only payload property matching {p}")
                unit_checks_passed = False
    else:
        errors.append("API_Contracts.md missing")
        unit_checks_passed = False

    if unit_checks_passed:
        print("  [PASS] Generic unit abstraction verified in DDL and API contracts (Zero legacy carton-only columns/fields).")
        passed += 1
    else:
        print("  [FAIL] Generic unit abstraction verification failed.")
        failed += 1

    # -------------------------------------------------------------
    # SUMMARY REPORT
    # -------------------------------------------------------------
    print("\n" + "=" * 80)
    print("AUDIT SUMMARY REPORT")
    print(f"Total Checks: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if errors:
        print("\nErrors / Warnings:")
        for err in errors:
            print(f"  - {err}")
        print("\nVERDICT: AUDIT FAILED [FAIL]")
        return False
    else:
        print("\nVERDICT: ALL CONSISTENCY & HARD GATE CHECKS PASSED! [PASS]")
        return True

if __name__ == "__main__":
    success = run_checks()
    sys.exit(0 if success else 1)
