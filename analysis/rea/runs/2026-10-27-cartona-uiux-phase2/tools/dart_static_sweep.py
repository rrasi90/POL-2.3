#!/usr/bin/env python3
"""dart_static_sweep.py — CP6 tool.

Independent sweep of libapp.so (from the armeabi split) for printable string
runs, used to re-verify prior static-analysis claims from raw bytes:

  ascii_runs_ge6   : count of printable-ASCII runs >= 6 chars (rule from prior run)
  utf16le_runs     : printable UTF-16LE runs >= 4 chars; arabic subset flagged by
                     presence of Arabic block code points
  endpoint_check   : how many of the prior 70 API path literals appear verbatim
  route_check      : how many of the prior route-feature-map routes appear
  strings_diff     : runs NOT already explained (sample) — new facts only

Usage: python dart_static_sweep.py <repo_root>
"""
import csv, json, os, re, sys, zipfile, hashlib
from collections import Counter

REPO = sys.argv[1] if len(sys.argv) > 1 else "."
SPLIT = os.path.join(REPO, "cartona app", "xapk_extracted", "config.armeabi_v7a.apk")
PRIOR = os.path.join(REPO, "analysis", "rea", "runs", "2026-10-27-cartona-remediation-deep-extraction")
OUT = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/..")

with zipfile.ZipFile(SPLIT) as z:
    data = z.read("lib/armeabi-v7a/libapp.so")
payload_sha = hashlib.sha256(data).hexdigest()

# ASCII printable runs >= 6 (decoded to str for downstream comparisons)
ascii_runs = {m.group(0).decode("ascii") for m in re.finditer(rb"[\x20-\x7e]{6,}", data)}
# UTF-16LE runs: sequences of (printable-ascii-or-arabic byte, 0x00); require >= 4 units
u16 = set()
for m in re.finditer(rb"(?:[\x20-\x7e][\x00]|[\x01-\xff][\x06]){4,}", data):
    try:
        s = m.group(0).decode("utf-16-le")
    except Exception:
        continue
    if all(ch.isprintable() for ch in s):
        u16.add(s)
arabic = [s for s in u16 if any("\u0600" <= c <= "\u06ff" for c in s)]

# endpoint check
api_rows = list(csv.DictReader(open(os.path.join(PRIOR, "api-endpoint-catalog.csv"), encoding="utf-8")))
ep_found = [r["path"] for r in api_rows if r["path"] in ascii_runs]
ep_missing = [r["path"] for r in api_rows if r["path"] not in ascii_runs]

# route check
routes = [r["route"] for r in csv.DictReader(open(os.path.join(PRIOR, "route-feature-map.csv"), encoding="utf-8"))]
rt_found = [r for r in routes if r in ascii_runs]
rt_missing = [r for r in routes if r not in ascii_runs]

# flag/config-like and interesting new literals not in prior catalogs (sample)
known = {r["path"] for r in api_rows} | set(routes)
interesting = sorted(s for s in ascii_runs if s.startswith("/") and len(s) > 4 and s not in known)[:40]

result = {
    "libapp_sha256": payload_sha,
    "ascii_runs_ge6": len(ascii_runs),
    "utf16le_runs_ge4": len(u16),
    "utf16le_arabic_runs": len(arabic),
    "endpoints_verbatim_found": len(ep_found),
    "endpoints_verbatim_missing": ep_missing,
    "routes_verbatim_found": len(rt_found),
    "routes_verbatim_missing": rt_missing,
    "sample_new_path_literals": interesting,
    "arabic_sample_10": arabic[:10],
}
with open(os.path.join(OUT, "dart-static-sweep.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(json.dumps({k: v for k, v in result.items() if not k.startswith("sample")}, ensure_ascii=False, indent=2))
