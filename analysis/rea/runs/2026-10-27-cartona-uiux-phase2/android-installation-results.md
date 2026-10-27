# Android Installation Results — CP3 (continuation run)

**All commands executed on the host; outputs captured verbatim. No APK was modified; no security control bypassed.**

## 1. Device connectivity (Addendum A step 1)

| When | Command | Result |
|---|---|---|
| CP3 start (continuation) | `adb version` | Android Debug Bridge 1.0.41 (37.0.1-15733141) |
| CP3 start | `adb devices -l` | **empty — no physical device connected** |
| after booting existing AVD | `adb devices -l` | `emulator-5554 device product:sdk_gphone64_x86_64` |

**Physical device status: NOT CONNECTED → recorded, not assumed.** Emulator fallback path (continuation mission §5, Addendum B) activated.

## 2. Device/environment facts (verified via adb getprop / wm)

Existing AVD `POL_API_Emulator` (the only installed image: `android-35/google_apis/x86_64`):

| Property | Value | Source |
|---|---|---|
| Android version | 15 (API 35) | `ro.build.version.release` |
| ABIs | `x86_64,arm64-v8a` — **no `armeabi-v7a`** | `ro.product.cpu.abilist` |
| Display | 1080x2400 @ 420dpi | `wm size`, `wm density` |
| Play Store | not enabled (google_apis variant) | AVD config `PlayStore.enabled = no` |

## 3. Split re-verification (Addendum A step 2)

All 4 files re-hashed this session — identical to `apk-inventory.csv` (base `e4a0f4d1…`, abi `d232c761…`, en `da962ee2…`, mdpi `5c76dd24…`). Same package `com.cartona` versionCode `70000083`, same signer cert `83891e0a…` (verified in CP2). **Coherent set confirmed.**

## 4. Install attempts (exact commands, exit codes, results)

### Attempt 1 — Addendum A selected set (base + armeabi_v7a + en; mdpi omitted: device 420dpi, split is mdpi)

```
adb install-multiple -r com.cartona.apk config.armeabi_v7a.apk config.en.apk
```
- exit code: 1
- stderr: `adb: failed to finalize session` / `Failure [INSTALL_FAILED_MISSING_SPLIT: Missing split for com.cartona]`
- Finding: the base declares split config requiring a density split → the density split is mandatory in this bundle even on non-mdpi devices.

### Attempt 2 — full 4-split set

```
adb install-multiple -r com.cartona.apk config.armeabi_v7a.apk config.en.apk config.mdpi.apk
```
- exit code: 1
- stderr: `adb: failed to finalize session` / `Failure [INSTALL_FAILED_NO_MATCHING_ABIS: INSTALL_FAILED_NO_MATCHING_ABIS: Failed to extract native libraries, res=-113]`
- **Finding: the historical x86_64 failure is reproduced exactly and root-caused** — the google_apis API 35 image has no ARMv7 native bridge (abilist lacks `armeabi-v7a`); all Cartona native code is armeabi-v7a-only.

**This reproduction is supplementary evidence (continuation mission §5); it does not end the runtime work.** Fallback in progress: official `system-images;android-34;google_apis_playstore;x86_64` (Google Play images on Android 11+ carry the ARM→x86 native bridge per official Android Emulator documentation; per-binary success is NOT assumed — validated by actual install attempt).

## 5. Package state after attempts

`com.cartona` NOT installed (both sessions failed before commit). Verified via install failure output; no partial install state.
## 6. Attempt 3 — official Google Play image (API 34, libndk ARM translation)

Preparation (all verified):
- `sdkmanager` downloads failed twice mid-transfer (`Connection reset` / `connection aborted` at 22% and 17% — session logs retained).
- Recovered via resumable `curl -C -` of the **official** zip `https://dl.google.com/android/repository/sys-img/google_apis_playstore/x86_64-34_r14.zip`; final size **1,510,752,654 B == server Content-Length**; `unzip -t` -> `No errors detected`.
- Extracted to `system-images/android-34/google_apis_playstore/x86_64/` (source.properties: x86_64 with Google Play, API 34).
- AVD `CP4_Play34` created (manual `config.ini` with `image.sysdir.1`; an initial `printf` escape corruption of the path was caught by an emulator FATAL and fixed; `disk.dataPartition.size` reduced 8G->4G for host disk limits — both documented).
- Boot: `sys.boot_completed=1`.

Device facts (getprop):
| Property | Value |
|---|---|
| Android | 14 (API 34) |
| `ro.product.cpu.abilist` | `x86_64,arm64-v8a` — **no `armeabi-v7a`** |
| `ro.dalvik.vm.native.bridge` | `libndk_translation.so` (enabled) — **arm64 translation only; `ro.product.cpu.abilist32` empty** |

Install attempt (all 4 splits — attempt-1 lesson applied):
```
adb install-multiple -r com.cartona.apk config.armeabi_v7a.apk config.en.apk config.mdpi.apk
```
- exit code: 1 — `Failure [INSTALL_FAILED_NO_MATCHING_ABIS ... res=-113]`
- **Root cause: libndk translates arm64-v8a only; Cartona ships armeabi-v7a-only native code.**

## 7. Attempt 4 — legacy x86 + houdini hypothesis (API 25)

Hypothesis: pre-API-26 x86 google_apis images shipped houdini ARMv7 translation (historically documented).
- Highest image compatible with minSdk 24: `system-images;android-25;google_apis;x86` (rev 18).
- sdkmanager download failed again (connection aborted at 15%); recovered via resumable curl from the official URL `sys-img/google_apis/x86-25_r18.zip` — size 1,013,657,090 B == Content-Length; `unzip -t` OK; extracted.
- **Hypothesis DISPROVEN by image inspection:** `build.prop` `ro.product.cpu.abilist=x86` (no ARM); binary grep of `system.img`/`ramdisk.img` -> **houdini: 0 occurrences**. AVD `CP4_API25` created but boot not attempted — the image contains no ARM translator, so an install could only repeat attempts 1-3 identically.

## 8. Conclusion — runtime paths exhausted with evidence

| Path | Result | Evidence |
|---|---|---|
| Physical ARM device | **NOT CONNECTED** (user-indicated availability never materialized during this run window) | `adb devices -l` empty at every check |
| google_apis API 35 x86_64 | `INSTALL_FAILED_NO_MATCHING_ABIS` (no native bridge) | attempt 2 log |
| google_apis_playstore API 34 x86_64 (libndk) | `INSTALL_FAILED_NO_MATCHING_ABIS` (arm64-only translation) | attempt 3 log |
| google_apis API 25 x86 (houdini hypothesis) | **no translator in image** (build.prop + binary grep) | attempt 4 inspection |

**Runtime UI observation is `BLOCKED_TECHNICAL` for this run** on all available environments. The one viable untried path remains a physical `armeabi-v7a` device (or an arm64 build of the app from the vendor — out of scope). The AVDs `CP4_Play34` and `CP4_API25` remain installed for future retry. `com.cartona` was never installed on any environment; no partial install state exists.
