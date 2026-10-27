# APK Integrity Report — CP2

**Method:** SHA-256 recomputed from file bytes; `aapt dump badging` for identity; `apksigner verify --print-certs` for signing; `zipfile` enumeration for structure. Raw data: `apk-inventory.csv` (8 rows) + `apk-inventory-raw.json`. Generator: `tools/build_apk_inventory.py`.

## Cartona bundle (com.cartona)

| File | Bytes | SHA-256 | Role | Signer cert | SourceStamp |
|---|---|---|---|---|---|
| `cartona app\cartona.apk` | 41,963,460 | `e4a0f4d1…df808c` | standalone base copy | `83891e0a…d653ee` | yes |
| `xapk_extracted\com.cartona.apk` | 41,963,460 | `e4a0f4d1…df808c` (byte-identical to above) | XAPK base split | same | yes |
| `xapk_extracted\config.armeabi_v7a.apk` | 18,993,995 | `d232c761…00f3fb1c8` | ABI split (armeabi-v7a; contains libapp.so + libflutter.so) | same | yes |
| `xapk_extracted\config.en.apk` | 61,849 | `da962ee2…746749c34` | locale split (en-AU/CA/GB/IN/XC; densities 160) | same | yes |
| `xapk_extracted\config.mdpi.apk` | 139,457 | `5c76dd24…c684300670` | density split (160/240/65534) | same | yes |

**Integrity findings:**

1. **Single coherent version set.** All five files: package `com.cartona`, versionCode `70000083` (versionName 8.4.6 on the base; splits carry empty versionName as expected for splits). Identical signer certificate SHA-256 `83891e0a1243f16db19d3fd0b9e836148ce455f943d2a2808632565aa4d653ee` (Play App Signing, CN=Android/O=Google Inc.) + SourceStamp on every file → the four splits are mutually compatible and installable as one `adb install-multiple` set (pending per-device Addendum A selection: on any device, base + armeabi_v7a are mandatory; config.en optional per locale; config.mdpi optional per density — a non-mdpi device should receive the closest available density split or none).
2. **Base-only install is non-functional.** Base APK contains **zero `lib/` entries**; all native code lives in the armeabi_v7a split (6 libs incl. libapp.so 10,945,116 B / `e150ce501b87d3c0…`, libflutter.so). Installing base alone on any device cannot produce a working app. Confirms CP1 root-cause of the historical runtime blocker.
3. **Structure counts (recomputed):** base = 1,445 ZIP entries (119 under `assets/`), armeabi split = 11 entries (6 under `lib/armeabi-v7a/`), en split = 6 entries (resources.arsc only), mdpi split = 86 entries.
4. minSdk 24, targetSdk 36 (compileSdk 36 / platform 16).

## POL test builds (context only — not part of Cartona analysis)

| File | Package | ABIs | Signer cert |
|---|---|---|---|
| `POL-Retailer-Test.apk` | `com.pol.retailer.test` | arm64-v8a;armeabi-v7a;x86;x86_64 (universal) | `fac61745…` (local build) |
| `POL-Wholesaler-Test.apk` | `com.pol.wholesaler.test` | universal | same |
| `POL-Field-Test.apk` | `com.pol.field.test` | universal | same |

POL test APKs are universal-ABI local builds — installable on any emulator/device; relevant only if POL-side visual comparison is needed in CP8, and for CP3 as a device sanity check.

## Publication decision (Addendum D)

No APK binaries are published. `apk-inventory.csv` publishes hashes + metadata only. Raw JSON sidecar contains the same metadata (no binaries).

## CP2 exit status

- [x] apk-inventory.csv (8 rows, hashes recomputed)
- [x] apk-integrity-report.md
- [x] android-environment-matrix.md + environment-matrix.json (incl. installed-system-image inventory for Addendum B)
- [x] tooling-research.md (ARTEMIS assessed, not activated) + research-source-register.csv
- [x] Addendum A pre-install metadata pass complete (per-device selection deferred to CP3 device query)
