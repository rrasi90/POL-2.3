from pathlib import Path
import base64, hashlib

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "parts"
OUT = ROOT / "New File 1.penpot.zip"
EXPECTED_SHA256 = "b27dab72381f4e4551b684090f8caff3198f6b113a460c61a484d68e3d7ecbda"

files = sorted(PARTS.glob("part_*.b64"))
if not files:
    raise SystemExit("No Penpot chunks found")

with OUT.open("wb") as dst:
    for part in files:
        dst.write(base64.b64decode(part.read_text(encoding="ascii")))

digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
if digest != EXPECTED_SHA256:
    raise SystemExit(f"Checksum mismatch: {digest} != {EXPECTED_SHA256}")
print(f"Rebuilt {OUT} ({OUT.stat().st_size} bytes), SHA-256={digest}")
