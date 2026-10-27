#!/usr/bin/env python3
"""capture_screen.py — CP4 screenshot capture with manifest metadata.

Captures a real device screenshot via `adb exec-out screencap -p`, stores it
under <run_dir>/screens/, and appends a metadata row to screenshot-manifest.csv.

Usage:
  python capture_screen.py <run_dir> <serial> <screen_id> <state_id> <session_id> <app_version> <login_state> <interaction_path> [evidence_status]

Rules:
  - capture method recorded as 'adb exec-out screencap -p'
  - sha256 + PNG dimensions computed from actual bytes
  - evidence_status defaults to OBSERVED
  - publication defaults to local-only (Addendum D; publication is a later explicit decision)
"""
import csv, hashlib, os, struct, subprocess, sys, time

run_dir, serial, screen_id, state_id, session_id, app_version, login_state, interaction_path = sys.argv[1:9]
evidence_status = sys.argv[9] if len(sys.argv) > 9 else "OBSERVED"

adb = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Android", "Sdk", "platform-tools", "adb.exe")
png = subprocess.run([adb, "-s", serial, "exec-out", "screencap", "-p"], capture_output=True, timeout=60)
if png.returncode != 0 or not png.stdout.startswith(b"\x89PNG"):
    print("CAPTURE_FAILED", png.returncode, png.stderr[:200])
    sys.exit(1)

data = png.stdout
sha = hashlib.sha256(data).hexdigest()
# PNG IHDR dimensions (bytes 16-24)
w, h = struct.unpack(">II", data[16:24])

screens_dir = os.path.join(run_dir, "screens")
os.makedirs(screens_dir, exist_ok=True)
ts = time.strftime("%Y%m%d-%H%M%S")
fname = f"{screen_id}__{state_id}__{ts}.png"
with open(os.path.join(screens_dir, fname), "wb") as f:
    f.write(data)

# device metadata
def prop(name):
    p = subprocess.run([adb, "-s", serial, "shell", "getprop", name], capture_output=True, text=True, timeout=20)
    return p.stdout.strip()
android_version = prop("ro.build.version.release")
device_model = prop("ro.product.model")

manifest = os.path.join(run_dir, "screenshot-manifest.csv")
new = not os.path.exists(manifest)
with open(manifest, "a", encoding="utf-8", newline="") as f:
    wcsv = csv.writer(f)
    if new:
        wcsv.writerow(["evidence_id", "file", "screen_id", "state_id", "session_id", "app_version", "device_model", "android_version", "width_px", "height_px", "login_state", "interaction_path", "captured_at", "capture_method", "sha256", "evidence_status", "publication"])
    eid = f"scr_{sha[:16]}"
    wcsv.writerow([eid, f"screens/{fname}", screen_id, state_id, session_id, app_version, device_model, android_version, w, h, login_state, interaction_path, time.strftime("%Y-%m-%dT%H:%M:%S"), "adb exec-out screencap -p", sha, evidence_status, "local-only"])
print(f"OK {fname} {w}x{h} sha={sha[:16]} eid={eid}")
