#!/usr/bin/env python3
"""build_asset_inventory.py — CP5 tool.

Read-only rebuild of the Cartona Flutter asset inventory directly from the APK,
with per-file dimensions (PIL), SHA-256, kind, and role classification.
Also produces asset-color-analysis.csv (dominant colors via PIL quantization)
for bitmap assets. No asset bytes are published; only metadata.

Counting rules (each output field documents its rule):
  rows              : one row per ZIP entry under assets/flutter_assets/ (files only)
  declared          : path appears as a key (or list member) in AssetManifest.json
  kind              : extension-based; 'other' for unknown
  role              : path-pattern classification (icons / images / fonts / data / fa-icons / misc)

Usage: python build_asset_inventory.py <repo_root>
"""
import csv, hashlib, io, json, os, re, sys, zipfile
from collections import Counter

REPO = sys.argv[1] if len(sys.argv) > 1 else "."
APK = os.path.join(REPO, "cartona app", "cartona.apk")
OUT = os.path.dirname(os.path.abspath(__file__)) + "/.."
OUT = os.path.abspath(OUT)

from PIL import Image

def dimensions(data, name):
    try:
        if name.lower().endswith((".png", ".webp", ".jpg", ".jpeg")):
            im = Image.open(io.BytesIO(data))
            return im.size, im.mode
        if name.lower().endswith(".svg"):
            m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', data.decode("utf-8", "ignore"))
            if m:
                return (int(float(m.group(1))), int(float(m.group(2)))), "vector"
    except Exception:
        pass
    return (None, None), None

def classify_role(path):
    p = path.lower()
    if "fontawesome" in p or re.search(r"fa[-_]?(solid|brands|regular)", p):
        return "fa-icons"
    if "/fonts/" in p or p.endswith((".ttf", ".otf")):
        return "fonts"
    if re.search(r"(icon|ic_)", p):
        return "icons"
    if re.search(r"(image|illustration|logo|banner|onboard|placeholder|empty|error|success)", p):
        return "images"
    if p.endswith((".json", ".txt", ".xml", ".properties", ".gradle")):
        return "data"
    return "misc"

with zipfile.ZipFile(APK) as z:
    names = [n for n in z.namelist() if n.startswith("assets/flutter_assets/") and not n.endswith("/")]
    manifest_raw = z.read("assets/flutter_assets/AssetManifest.json").decode("utf-8", "ignore")
    manifest = json.loads(manifest_raw)
    # Rule: AssetManifest keys are pubspec-relative ("assets/images/Logo.png") and
    # map to ZIP paths "assets/flutter_assets/<key-or-variant>". Values are variant lists.
    declared_paths = set()
    manifest_keys = set(manifest.keys())
    for k, v in manifest.items():
        candidates = [k] + (v if isinstance(v, list) else [])
        for c in candidates:
            declared_paths.add("flutter_assets/" + c)
    rows = []
    color_rows = []
    for n in names:
        rel = n[len("assets/"):]
        data = z.read(n)
        h = hashlib.sha256(data).hexdigest()
        (w, hh), mode = dimensions(data, rel)
        kind = rel.rsplit(".", 1)[-1].lower() if "." in rel else "none"
        role = classify_role(rel)
        row = {
            "archive_path": rel,
            "bytes": len(data),
            "sha256": h,
            "kind": kind,
            "role": role,
            "declared_in_assetmanifest": "yes" if rel in declared_paths else "no",
            "width_px": w or "",
            "height_px": hh or "",
            "color_mode": mode or "",
            "license_status": "cartona-proprietary-unknown",
            "publication": "metadata-only",
        }
        rows.append(row)
        if kind in ("png", "webp", "jpg", "jpeg") and w and role in ("icons", "images", "misc"):
            try:
                rgba = Image.open(io.BytesIO(data)).convert("RGBA")
                # composite on white so transparent backgrounds do not skew colors
                bg = Image.new("RGB", rgba.size, (255, 255, 255))
                bg.paste(rgba, mask=rgba.split()[3])
                im = bg.resize((min(64, w or 64), min(64, hh or 64)))
                q = im.quantize(colors=5, method=Image.Quantize.MEDIANCUT)
                pal = q.getpalette()
                counts = sorted(q.getcolors(), reverse=True)[:3]
                top = ["#%02x%02x%02x" % tuple(pal[i * 3:i * 3 + 3]) for _, i in counts]
                color_rows.append({"archive_path": rel, "width_px": w, "height_px": hh, "top_colors": "|".join(top)})
            except Exception:
                pass

rows.sort(key=lambda r: r["archive_path"])
cols = ["archive_path", "bytes", "sha256", "kind", "role", "declared_in_assetmanifest", "width_px", "height_px", "color_mode", "license_status", "publication"]
with open(os.path.join(OUT, "flutter-assets-inventory.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)
with open(os.path.join(OUT, "asset-color-analysis.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["archive_path", "width_px", "height_px", "top_colors"])
    w.writeheader()
    w.writerows(color_rows)

declared = sum(1 for r in rows if r["declared_in_assetmanifest"] == "yes")
summary = {
    "rule": "one row per ZIP file entry under assets/flutter_assets/",
    "total_rows": len(rows),
    "declared": declared,
    "undeclared": len(rows) - declared,
    "kind_distribution": dict(Counter(r["kind"] for r in rows)),
    "role_distribution": dict(Counter(r["role"] for r in rows)),
    "color_analyzed": len(color_rows),
    "manifest_keys": len(manifest),
}
with open(os.path.join(OUT, "asset-count-reconciliation-phase2.json"), "w", encoding="utf-8") as fh:
    json.dump(summary, fh, ensure_ascii=False, indent=2)
print(json.dumps(summary, indent=2))
