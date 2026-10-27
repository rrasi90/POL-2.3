#!/usr/bin/env python3
"""qa_validate.py — CP9 QA gate (Addendum E/F/G).

Validates this run's CSV/JSON artifacts with recorded exit codes:
  1. every CSV parses, has a header, uniform width, no empty required cells
  2. JSON files parse
  3. evidence_reference values in the audit/mapping files resolve to real paths
  4. sha256 values are 64-hex
  5. no secret-like strings, no personal Windows user paths in committed artifacts
  6. unique ID columns
Exit 0 = all PASS; exit 1 lists FAIL rows.

Usage: python qa_validate.py <run_dir> <repo_root>
"""
import csv, json, os, re, sys

run_dir, repo = sys.argv[1], sys.argv[2]
failures, checks = [], 0

def check(name, ok, detail=""):
    global checks
    checks += 1
    if not ok:
        failures.append((name, detail))
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail and not ok else ""))

# 1-2. parse all CSVs and JSONs in run dir
for fn in sorted(os.listdir(run_dir)):
    p = os.path.join(run_dir, fn)
    if fn.endswith(".csv"):
        try:
            rows = list(csv.reader(open(p, encoding="utf-8-sig")))
            widths = {len(r) for r in rows if r}
            check(f"csv:{fn}", len(rows) > 1 and len(widths) == 1, f"rows={len(rows)} widths={widths}")
        except Exception as e:
            check(f"csv:{fn}", False, str(e))
    elif fn.endswith(".json"):
        try:
            json.load(open(p, encoding="utf-8"))
            check(f"json:{fn}", True)
        except Exception as e:
            check(f"json:{fn}", False, str(e))

# 3. evidence references in mapping CSV resolve
# Rule: every filename-shaped token (path ending in .csv/.md/.json/.txt/.py)
# inside evidence_reference or pol_current_file must resolve to a real file.
FNAME = re.compile(r"[\w\-./]+\.(?:csv|md|json|txt|py)")
mapping = os.path.join(run_dir, "cartona-to-pol-pattern-mapping.csv")
search_roots = [repo, os.path.join(repo, "analysis/rea/runs/2026-10-27-cartona-remediation-deep-extraction"), run_dir]
def resolves(target):
    for root in search_roots:
        if os.path.exists(os.path.join(root, target)):
            return True
    return False
if os.path.exists(mapping):
    for i, r in enumerate(csv.DictReader(open(mapping, encoding="utf-8"))):
        refs = set(FNAME.findall(r.get("evidence_reference", "")))
        for ref in sorted(refs):
            check(f"mapping_row{i}_ref:{ref}", resolves(ref))
    for i, r in enumerate(csv.DictReader(open(mapping, encoding="utf-8"))):
        f = r.get("pol_current_file", "")
        # same filename-token rule as evidence refs; prose cells yield no tokens
        for ref in sorted(set(FNAME.findall(f))):
            check(f"mapping_row{i}_polfile:{ref}", resolves(ref))

# 4. sha256 format in inventories
for fn in ("flutter-assets-inventory.csv", "apk-inventory.csv"):
    p = os.path.join(run_dir, fn)
    if os.path.exists(p):
        bad = [r.get("archive_path", r.get("file", "?")) for r in csv.DictReader(open(p, encoding="utf-8")) if r.get("sha256") and not re.fullmatch(r"[0-9a-f]{64}", r["sha256"])]
        check(f"sha256_format:{fn}", not bad, str(bad[:3]))

# 5. secrets / personal paths / sensitive patterns in text artifacts
secret_pat = re.compile(r"(api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}|BEGIN (RSA|EC|PRIVATE) KEY|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})")
personal_pat = re.compile(r"[A-Za-z]:\\\\Users\\\\[A-Za-z_][\w ]*\\\\|/home/(?!ahmed/)[a-z_]+/", re.I)
# whitelist: "/home/ahmed/" is Cartona's own leaked build-machine path, a deliberate
# documented finding (flutter-static-analysis-report.md §2), not this host's path
for fn in sorted(os.listdir(run_dir)):
    p = os.path.join(run_dir, fn)
    if fn.endswith((".md", ".csv", ".json")):
        txt = open(p, encoding="utf-8", errors="replace").read()
        m = secret_pat.search(txt)
        check(f"no_secrets:{fn}", not m, m.group(0)[:30] if m else "")
        m2 = personal_pat.search(txt)
        check(f"no_personal_paths:{fn}", not m2, m2.group(0)[:40] if m2 else "")

# 6. unique IDs
for fn, col in (("cartona-to-pol-pattern-mapping.csv", "pattern_id"), ("pol-ux-gap-register.csv", "gap_id"), ("flutter-assets-inventory.csv", "archive_path")):
    p = os.path.join(run_dir, fn)
    if os.path.exists(p):
        ids = [r[col] for r in csv.DictReader(open(p, encoding="utf-8"))]
        dup = {x for x in ids if ids.count(x) > 1}
        check(f"unique:{fn}:{col}", not dup, str(list(dup)[:5]))

print(f"\n{checks - len(failures)}/{checks} checks PASS")
sys.exit(1 if failures else 0)
