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

## 6. Status

- Physical device: **BLOCKED (not connected)** — will be retried; user indicated availability.
- Emulator (google_apis API 35): **BLOCKED_TECHNICAL** — `INSTALL_FAILED_NO_MATCHING_ABIS`, evidence above.
- Emulator (google_apis_playstore API 34): **IN PROGRESS** — image downloading via official sdkmanager; AVD creation + validated install attempt to follow.
