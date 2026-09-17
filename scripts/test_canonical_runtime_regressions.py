"""Regression contracts for the 2026-09-16 repository-wide bug audit."""

import ast
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import verify_repository_consistency as verifier

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_checkout_persists_order_items_and_groups_by_vendor():
    src = read("scripts/revalidation_checkout.py")
    assert "allocations_by_vendor" in src
    assert "INSERT INTO order_items" in src
    assert "vendor_total = sum(a[\"amount_toman\"] for a in vendor_allocs)" in src
    assert "f\"res-{idempotency_key}-{alloc['vendor_product_id']}\"" in src


def test_checkout_idempotency_key_is_bound_to_request_fingerprint():
    gateway = read("scripts/checkout_gateway.py")
    migration = read("migrations/024_runtime_bug_fixes_and_audit_guards.sql")
    assert "def _fingerprint" in gateway
    assert "checkout_request_fingerprint" in gateway
    assert "different checkout request payload" in gateway
    assert "checkout_request_fingerprint VARCHAR(64)" in migration


def test_rma_aggregates_duplicate_order_item_lines():
    src = read("scripts/returns_rma.py")
    assert "requested_by_item = {}" in src
    assert "requested_by_item[item_key] = requested_by_item.get(item_key, 0) + quantity" in src
    assert "Aggregated return quantity exceeds delivered/ordered quantity." in src
    assert "uq_return_items_return_order_item" in read("migrations/024_runtime_bug_fixes_and_audit_guards.sql")


def test_refund_requires_operational_actor_and_two_person_control():
    src = read("scripts/returns_rma.py")
    assert "OPS_ROLES" in src
    assert "allowed = ops_ok" in src
    assert "completed_by_user_id=%s" in src
    assert "must be performed by a different actor than the approver" in src


def test_unknown_outbox_events_leave_pending_queue_and_enter_failed_quarantine():
    src = read("scripts/canonical_integration_worker.py")
    assert "_quarantine_unsupported" in src
    assert "status='FAILED'" in src
    migration = read("migrations/024_runtime_bug_fixes_and_audit_guards.sql")
    assert "outbox_events_status_canonical_check" in migration
    assert "'FAILED'" in migration


def test_payment_reconciliation_rejects_conflicting_trusted_evidence():
    src = read("scripts/payment_reconciliation_worker.py")
    assert "conflicting = len(distinct_values) > 1" in src
    assert "conflicting_match = conflicting and matches_expected" in src
    assert "if conflicting_match:" in src
    assert "status='MISMATCH'" in src


def test_repository_verifier_is_dynamic_not_legacy_56_table_audit():
    src = read("scripts/verify_repository_consistency.py")
    assert "glob(\"[0-9][0-9][0-9]_*.sql\")" in src
    assert "Current migration chain is contiguous" in src
    assert "56 Tables" not in src
    assert "migration_file_1" not in src


def test_canonical_e2e_entrypoints_exist_without_legacy_domain_service_import():
    checkout_gateway = read("scripts/checkout_gateway.py")
    boundary = read("scripts/application_boundary.py")
    master_e2e = read("scripts/test_e2e_mvp_platform.py")
    assert "CanonicalCheckoutGateway" in checkout_gateway
    assert "revalidation_checkout" in checkout_gateway
    assert "CanonicalCheckoutGateway" in boundary
    for path in (
        "scripts/test_e2e_mvp_platform.py", "scripts/application_boundary.py",
        "scripts/checkout_gateway.py", "scripts/revalidation_checkout.py",
    ):
        assert legacy_imports(read(path)) == [], path
    tree = ast.parse(master_e2e)
    assert any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "checkout"
        and isinstance(node.func.value, ast.Call)
        and isinstance(node.func.value.func, ast.Name)
        and node.func.value.func.id == "POLApplicationBoundary"
        for node in ast.walk(tree)
    )


def legacy_imports(source):
    offenders = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                module = "scripts" + ("." + module if module else "")
            names = [module] + [f"{module}.{alias.name}" for alias in node.names]
        else:
            continue
        if any(name == "scripts.domain_services" or name.startswith("scripts.domain_services.") for name in names):
            offenders.append(node.lineno)
    return offenders


@pytest.mark.parametrize("source", [
    "from scripts.domain_services import CheckoutService",
    "import scripts.domain_services as legacy",
    "from scripts import domain_services as legacy",
    "from .domain_services import CheckoutService",
    "from . import domain_services",
])
def test_legacy_import_detector_rejects_real_imports(source):
    assert legacy_imports(source) == [1]


def test_legacy_import_detector_ignores_literals_and_comments():
    source = '\"\"\"from scripts.domain_services import CheckoutService\"\"\"\n'
    source += '# import scripts.domain_services\n'
    source += 'message = "from scripts.domain_services import CheckoutService"\n'
    source += 'from scripts.checkout_gateway import CanonicalCheckoutGateway\n'
    assert legacy_imports(source) == []


@pytest.mark.parametrize("filenames", [
    [], ["002_second.sql"], ["001_first.sql", "003_third.sql"],
    ["001_first.sql", "001_duplicate.sql"],
])
def test_verifier_migration_chain_errors_are_counted(tmp_path, monkeypatch, capsys, filenames):
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    for filename in filenames:
        (migrations / filename).write_text("SELECT 1;", encoding="utf-8")
    monkeypatch.setattr(verifier, "REPO_ROOT", tmp_path)
    assert verifier.run_checks() is False
    output = capsys.readouterr().out
    assert "No canonical migrations found" in output or "Migration chain has gaps" in output
    assert "FAIL: 0" not in output


def test_verifier_accepts_new_contiguous_migrations(tmp_path):
    for number in range(1, 28):
        (tmp_path / f"{number:03d}_migration.sql").write_text("SELECT 1;", encoding="utf-8")
    files, errors = verifier.check_migration_chain(tmp_path)
    assert len(files) == 27
    assert errors == []


def test_verifier_reports_unreadable_migration(tmp_path, monkeypatch, capsys):
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    (migrations / "001_bad.sql").write_bytes(b"\xff")
    monkeypatch.setattr(verifier, "REPO_ROOT", tmp_path)
    assert verifier.run_checks() is False
    assert "Cannot read migrations/001_bad.sql" in capsys.readouterr().out


def hierarchy_doc(tmp_path):
    doc = tmp_path / "POL_00_PROJECT_CONTROL" / "CURRENT_SOURCE_OF_TRUTH.md"
    doc.parent.mkdir(parents=True)
    return doc


def verifier_repo(tmp_path):
    (tmp_path / "migrations").mkdir()
    (tmp_path / "migrations" / "001_init.sql").write_text("SELECT 1;", encoding="utf-8")
    return tmp_path


@pytest.mark.parametrize("removed_entity", ["Basket", "AllocationPlan", "OrderGroup", "Order", "OrderItem"])
def test_verifier_requires_all_five_hierarchy_entities_in_every_canonical_doc(
    tmp_path, monkeypatch, capsys, removed_entity,
):
    doc = hierarchy_doc(tmp_path)
    entities = [entity for entity in verifier.HIERARCHY_ENTITIES if entity != removed_entity]
    doc.write_text(" -> ".join(entities), encoding="utf-8")
    monkeypatch.setattr(verifier, "REPO_ROOT", verifier_repo(tmp_path))
    monkeypatch.setattr(verifier, "HIERARCHY_FILES", [doc])
    assert verifier.run_checks() is False
    assert "Canonical order hierarchy documentation is incomplete" in capsys.readouterr().out


def test_verifier_accepts_plural_entity_forms_as_in_real_canonical_docs(tmp_path, monkeypatch, capsys):
    doc = hierarchy_doc(tmp_path)
    doc.write_text(" -> ".join(f"{entity}s" for entity in verifier.HIERARCHY_ENTITIES), encoding="utf-8")
    monkeypatch.setattr(verifier, "REPO_ROOT", verifier_repo(tmp_path))
    monkeypatch.setattr(verifier, "HIERARCHY_FILES", [doc])
    verifier.run_checks()
    assert "Canonical order hierarchy documentation is incomplete" not in capsys.readouterr().out


def test_verifier_accepts_documents_with_full_hierarchy(tmp_path, monkeypatch, capsys):
    (tmp_path / "migrations").mkdir()
    (tmp_path / "migrations" / "001_init.sql").write_text("SELECT 1;", encoding="utf-8")
    doc = tmp_path / "POL_00_PROJECT_CONTROL" / "CURRENT_SOURCE_OF_TRUTH.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("Basket -> AllocationPlan -> OrderGroup -> Order -> OrderItem", encoding="utf-8")
    monkeypatch.setattr(verifier, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(verifier, "HIERARCHY_FILES", [doc])
    verifier.run_checks()
    assert "Canonical order hierarchy documentation is incomplete" not in capsys.readouterr().out


def test_verifier_cli_returns_nonzero_for_failed_checks(tmp_path):
    command = (
        "from pathlib import Path; "
        "from scripts import verify_repository_consistency as v; "
        f"v.REPO_ROOT = Path({str(tmp_path)!r}); "
        "raise SystemExit(0 if v.run_checks() else 1)"
    )
    result = subprocess.run([sys.executable, "-c", command], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 1
    assert "No canonical migrations found" in result.stdout
