# Visual QA Execution Ledger — 2026-10-06 (POL-2.4 master execution run)

Runtime: Windows host, Android Emulator `POL_API_Emulator` (Pixel 6, API 35, x86_64), adb 37.0.1.
Builds: canonical `build_android_variant.mjs` (arm64-v8a, per `withAndroidSizeOptimization`) + QA-only
`build_qa_x86.mjs` (arm64+x86_64) for emulator runtime QA. API target: `http://85.198.50.29` (staging),
`EXPO_PUBLIC_DATA_MODE=live`, `POL_RELEASE=0` (QA gate; release gate requires HTTPS which the VPS does
not yet serve — see blockers).

## Captured evidence (real runtime screenshots)

| Item | State | File |
|---|---|---|
| VQA-M-001 | Login / phone — LIGHT | `captures/VQA-M-001_login_phone_light.png` |
| VQA-M-001 | Login / phone — NIGHT (follows system dark) | `captures/VQA-M-001_login_phone_night.png` |
| VQA-M-002 | Login / phone validation error (client-side, no SMS sent) | `captures/VQA-M-002_login_phone_validation_error.png` |
| VQA-M-031 (pre-auth) | Vendor app launch / shared SH-AUTH-01, package `ir.pol.vendor` verified in foreground | `captures/VQA-M-031_vendor_login_light.png` |
| VQA-M-059 (partial) | Offline attempt: network disabled, tap on `دریافت کد` with valid-format number — banner unchanged | `captures/VQA-M-059_offline_banner_error.png` |

## Runtime test results

| Check | Result |
|---|---|
| Retailer `ir.pol.market` install + launch | PASS (no crash, 0 FATAL in crash buffer) |
| Vendor `ir.pol.vendor` install + launch | PASS (no crash; foreground verified via dumpsys) |
| Login screen render (RTL, Persian numerals, Precision Commerce light) | PASS |
| Night theme at runtime (system dark mode) | PASS — app follows system; brand blue preserved |
| Phone validation error state | PASS (client-side validation before any API/SMS call) |
| OTP request / verify / authenticated workspace | BLOCKED_AUTH — real SMS OTP required (SMSIR live provider, no dev bypass) |
| Offline OTP-request feedback on login screen | FINDING VQA-F-003 (P3): valid-format number + network off → banner unchanged; needs code triage |

## Findings update

| Finding | Status |
|---|---|
| VQA-F-001 (`app.json` declares `com.anonymous.polmobile`) | RESOLVED_BY_VARIANT_CONFIG — variant builds use `app.config.js`; `aapt dump badging` proves `ir.pol.market` / `ir.pol.vendor` on the produced APKs |
| VQA-F-002 (Support reachability) | UNCHANGED — authenticated reachability still unproven (OTP) |
| VQA-F-003 (new) | OPEN/P3 — offline OTP-request feedback on LoginScreen (see above) |

## Note on the x86_64 emulator and the canonical APK

The canonical APKs are arm64-v8a-only by design (`reactNativeArchitectures=arm64-v8a`, size optimization).
An earlier launch attempt on this x86_64 emulator crashed with
`couldn't find DSO to load: libreactnative.so` — that is an **ABI mismatch of the QA environment, not a
repository defect**; the same APK must be runtime-verified on arm64 hardware for release sign-off.
`POL-Market-qa-x86_64.apk` / `POL-Vendor-qa-x86_64.apk` are QA-only builds (not release candidates).

## Remaining BLOCKED items

- All AUTHENTICATED captures (VQA-M-006…058, VQA-M-060): require a real SMS OTP login.
- Release APK gate (`POL_RELEASE=1`): requires an HTTPS API endpoint; VPS currently serves HTTP only.
