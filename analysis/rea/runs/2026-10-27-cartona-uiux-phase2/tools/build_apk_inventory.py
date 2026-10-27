#!/usr/bin/env python3
"""build_apk_inventory.py — CP2 tool (Addendum A metadata pass).

Read-only. For each APK: SHA-256, bytes, aapt badging fields, native ABIs,
ZIP entry counts, and (for signing-capable files) apksigner cert digest.
Writes apk-inventory.csv + raw JSON sidecar next to it.

Usage: python build_apk_inventory.py <repo_root>
"""
import csv, hashlib, json, os, re, subprocess, sys, zipfile

REPO = sys.argv[1] if len(sys.argv) > 1 else "."
BT = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Android", "Sdk", "build-tools", "36.0.0")
AAPT = os.path.join(BT, "aapt.exe")
APKSIGNER = os.path.join(BT, "apksigner.bat")

APKS = [
    ("cartona app/cartona.apk", "cartona-base-standalone", "Cartona retail base (standalone copy; byte-identical to XAPK base split)"),
    ("cartona app/xapk_extracted/com.cartona.apk", "cartona-base-split", "Cartona XAPK base split"),
    ("cartona app/xapk_extracted/config.armeabi_v7a.apk", "cartona-split-abi", "ABI split: armeabi-v7a native libs"),
    ("cartona app/xapk_extracted/config.en.apk", "cartona-split-locale", "Locale split: en"),
    ("cartona app/xapk_extracted/config.mdpi.apk", "cartona-split-density", "Density split: mdpi"),
    ("artifacts/android/POL-Retailer-Test.apk", "pol-retailer-test", "POL retailer test build (context only)"),
    ("artifacts/android/POL-Wholesaler-Test.apk", "pol-wholesaler-test", "POL wholesaler test build (context only)"),
    ("artifacts/android/POL-Field-Test.apk", "pol-field-test", "POL field ops test build (context only)"),
]

def run(cmd, timeout=120):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.stdout, p.stderr, p.returncode
    except Exception as e:
        return "", str(e), -1

def badging(path):
    out, err, rc = run([AAPT, "dump", "badging", path])
    f = {}
    for key in ("package", "sdkVersion", "targetSdkVersion", "native-code", "split", "application-label:", "application-label-ar:", "densities", "locales"):
        m = re.search(rf"^{re.escape(key)}:(.*)$", out, re.M)
        if m:
            f[key.rstrip(":")] = m.group(1).strip()
    return f, rc

rows = []
for rel, label, role in APKS:
    path = os.path.join(REPO, rel)
    r = {"file": rel, "label": label, "role": role}
    if not os.path.exists(path):
        r["status"] = "NOT_FOUND"
        rows.append(r)
        continue
    r["bytes"] = os.path.getsize(path)
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    r["sha256"] = h.hexdigest()
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        r["zip_entries_total"] = len(names)
        r["zip_assets_entries"] = sum(1 for n in names if n.startswith("assets/"))
        abis = sorted({n.split("/")[1] for n in names if n.startswith("lib/") and len(n.split("/")) > 2})
        r["zip_lib_abis"] = ";".join(abis) if abis else ""
    b, rc = badging(path)
    r.update({k: b.get(k, "") for k in ("package", "sdkVersion", "targetSdkVersion", "native-code", "split", "application-label", "application-label-ar", "densities", "locales")})
    r["aapt_exit_code"] = rc
    so, se, src = run([APKSIGNER, "verify", "--print-certs", path], timeout=180)
    m = re.search(r"Signer #1 certificate SHA-256 digest: ([0-9a-f]+)", so)
    r["signer_cert_sha256"] = m.group(1) if m else ""
    r["source_stamp"] = "yes" if "Source Stamp Signer certificate" in so else ("unknown" if src != 0 else "no")
    r["status"] = "OK"
    rows.append(r)

outdir = os.path.dirname(os.path.abspath(__file__)) + "/.."
outdir = os.path.abspath(outdir)
cols = ["file", "label", "role", "status", "bytes", "sha256", "package", "version_from_package_field", "sdkVersion", "targetSdkVersion", "native-code", "split", "application-label", "application-label-ar", "densities", "locales", "zip_entries_total", "zip_assets_entries", "zip_lib_abis", "signer_cert_sha256", "source_stamp", "aapt_exit_code"]
# extract versionName/Code from package field for CSV clarity
for r in rows:
    m = re.search(r"versionCode='([^']+)' versionName='([^']+)'", r.get("package", "") or "")
    r["version_from_package_field"] = f"code={m.group(1)} name={m.group(2)}" if m else ""
with open(os.path.join(outdir, "apk-inventory.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in cols})
with open(os.path.join(outdir, "apk-inventory-raw.json"), "w", encoding="utf-8") as fh:
    json.dump(rows, fh, ensure_ascii=False, indent=2)
print("wrote apk-inventory.csv with", len(rows), "rows")
for r in rows:
    print(r["file"], "|", r.get("status"), "|", r.get("package", "")[:60], "| abis:", r.get("zip_lib_abis", ""))
