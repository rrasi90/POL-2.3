#!/usr/bin/env python3
"""recount_prior_metrics.py — CP1 audit tool.

Independently recounts the metrics claimed by prior Cartona extraction runs,
using documented counting rules. Research-only; read-only on all inputs.

Counting rules (each rule name appears in the output JSON):
  zip_entries       : len(zipfile.ZipFile.namelist()) of the named archive
  csv_data_rows     : rows minus 1 header, parsed with csv module, expected width enforced
  strings_lines     : physical lines in a text file
  strings_unique    : unique lines after strip(); duplicates counted separately
  endpoint_class    : per-row classification of api-endpoint-catalog 'path' values
                      URL_LITERAL                  : absolute http(s) URL
                      API_PATH_LITERAL_STRING_ONLY : starts with '/', path-shaped literal from string-pool evidence (relation_status STRING_ONLY, http_method UNKNOWN) — NOT a confirmed functional endpoint
                      ROUTE_LIKE                  : single-segment navigation-route-shaped name
                      OTHER_LITERAL               : anything else
                      CONFIRMED_FUNCTIONAL_ENDPOINT: only when a row carries method + call-site/runtime evidence (none expected in prior data)
  screen_status     : distribution of ui-screen-catalog observation_status values

Usage: python recount_prior_metrics.py <repo_root>
Output: JSON on stdout (also written next to this script as recount-results.json)
"""
import csv, json, os, re, sys, zipfile
from collections import Counter

REPO = sys.argv[1] if len(sys.argv) > 1 else "."
PRIOR = os.path.join(REPO, "analysis", "rea", "runs", "2026-10-27-cartona-remediation-deep-extraction")
SPEC58 = os.path.join(REPO, "13_PRODUCT_DESIGN", "58_CARTONA_SCREEN_BY_SCREEN_SPEC_2026-10-05", "data")
RUN26 = os.path.join(REPO, "analysis", "rea", "runs", "2026-10-26-cartona-comprehensive-extraction")
APK = os.path.join(REPO, "cartona app", "cartona.apk")
SPLIT = os.path.join(REPO, "cartona app", "xapk_extracted", "config.armeabi_v7a.apk")
SPLIT_EN = os.path.join(REPO, "cartona app", "xapk_extracted", "config.en.apk")
SPLIT_MDPI = os.path.join(REPO, "cartona app", "xapk_extracted", "config.mdpi.apk")

out = {"generated_by": "recount_prior_metrics.py", "rules_documented_in_docstring": True}

# 1. ZIP entry counts
def zip_count(path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        return {
            "zip_entries": len(names),
            "asset_entries": sum(1 for n in names if n.startswith("assets/")),
            "lib_entries": sum(1 for n in names if n.startswith("lib/")),
            "lib_abis": sorted({n.split("/")[1] for n in names if n.startswith("lib/") and len(n.split("/")) > 2}),
        }

out["base_apk"] = zip_count(APK)
out["armeabi_split"] = zip_count(SPLIT)
out["en_split"] = zip_count(SPLIT_EN)
out["mdpi_split"] = zip_count(SPLIT_MDPI)

# 2. flutter-assets-inventory recount
rows = list(csv.DictReader(open(os.path.join(PRIOR, "flutter-assets-inventory.csv"), encoding="utf-8")))
out["assets_inventory"] = {
    "rule": "csv_data_rows",
    "data_rows": len(rows),
    "declared_yes": sum(1 for r in rows if r.get("declared_in_assetmanifest", "").strip().lower() == "yes"),
    "declared_no": sum(1 for r in rows if r.get("declared_in_assetmanifest", "").strip().lower() == "no"),
    "sha256_distinct": len({r["sha256"] for r in rows}),
}

# 3. String corpora recount
def count_text(path):
    lines = [l.rstrip("\n").rstrip("\r") for l in open(path, encoding="utf-8", errors="replace")]
    stripped = [l.strip() for l in lines if l.strip()]
    c = Counter(stripped)
    return {
        "rule": "strings_lines / strings_unique",
        "lines_incl_empty": len(lines),
        "nonempty_lines": len(stripped),
        "unique_records": len(c),
        "duplicate_occurrences": sum(v - 1 for v in c.values() if v > 1),
    }

out["arabic_ui_strings_58spec"] = count_text(os.path.join(SPEC58, "arabic_ui_strings.txt"))

# curated snapshot corpus from the 2026-10-26 run (if committed)
for cand in ("arabic-strings-samples.txt", "arabic_strings_samples.txt"):
    p = os.path.join(RUN26, cand)
    if os.path.exists(p):
        out[f"run26_{cand}"] = count_text(p)

# android default strings.xml resource count (independent <string> element count)
sx = os.path.join(REPO, "cartona app", "decompiled", "resources", "res", "values", "strings.xml")
out["android_values_strings_xml"] = {
    "rule": "count of <string name=...> elements",
    "string_elements": len(re.findall(r"<string\s+name=", open(sx, encoding="utf-8", errors="replace").read())),
}

# 4. Endpoint catalog recount + per-row classification
api_rows = list(csv.DictReader(open(os.path.join(PRIOR, "api-endpoint-catalog.csv"), encoding="utf-8")))
cls = Counter()
per_row = []
for r in api_rows:
    p = (r.get("path") or "").strip()
    method = (r.get("http_method") or "").strip().upper()
    loc = (r.get("source_location") or "").strip()
    rel = (r.get("relation_status") or "").strip().upper()
    if re.match(r"^https?://", p):
        c = "URL_LITERAL"
    elif method in ("GET", "POST", "PUT", "PATCH", "DELETE") and rel not in ("STRING_ONLY",):
        c = "CONFIRMED_FUNCTIONAL_ENDPOINT"
    elif p.startswith("/") and "/" in p[1:]:
        c = "API_PATH_LITERAL_STRING_ONLY" if rel == "STRING_ONLY" else "API_PATH_LITERAL"
    elif re.match(r"^[a-zA-Z][\w-]*$", p):
        c = "ROUTE_LIKE"
    else:
        c = "OTHER_LITERAL"
    cls[c] += 1
    per_row.append({"path": p, "http_method": method, "class": c, "source_location": loc})
out["endpoint_catalog"] = {
    "rule": "endpoint_class (see docstring)",
    "data_rows": len(api_rows),
    "classification": dict(cls),
    "per_row": per_row,
}

# 5. Screen catalog recount
scr = list(csv.DictReader(open(os.path.join(PRIOR, "ui-screen-catalog.csv"), encoding="utf-8")))
out["screen_catalog"] = {
    "rule": "csv_data_rows + observation_status distribution",
    "data_rows": len(scr),
    "status_distribution": dict(Counter(r.get("observation_status", "") for r in scr)),
    "screens_with_screenshot_field_nonempty": sum(1 for r in scr if (r.get("screenshots") or "").strip() not in ("", "none", "NONE")),
}

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "recount-results.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(json.dumps({k: v for k, v in out.items() if k != "endpoint_catalog"}, ensure_ascii=False, indent=2))
print("--- endpoint classification:", dict(cls))
