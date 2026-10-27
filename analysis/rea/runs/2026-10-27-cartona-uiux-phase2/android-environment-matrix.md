# Android Environment Matrix — CP2

**Captured:** 2026-10-27 · All rows OBSERVED unless marked otherwise. Companion data: `environment-matrix.json`.

## 1. SDK & core tools

| Component | Status | Detail |
|---|---|---|
| Android SDK root | PRESENT | `%LOCALAPPDATA%\Android\Sdk` (ANDROID_HOME/ANDROID_SDK_ROOT set) |
| platform-tools (adb) | PRESENT | version 1.0.41 (37.0.1-15733141) |
| build-tools | PRESENT | 36.0.0 (aapt, aapt2, apksigner, zipalign, d8, dexdump), 35.0.0 |
| cmdline-tools | PRESENT | latest (apkanalyzer.bat usable) |
| emulator | PRESENT | `emulator.exe` working (`-list-avds` returned the AVD) |
| Java | PRESENT | OpenJDK 21.0.9 (Android Studio JBR) via JAVA_HOME |
| keytool | PRESENT | JBR bin |
| Python | PRESENT | 3.11.15 (venv) and 3.14.2 on PATH |
| unzip | PRESENT | Info-ZIP 6.00 (Git Bash) |
| Secondary SDK copy | PRESENT | `C:\Star\android_sdk\` (+ setup scripts) — not used by this run |
| frida | ABSENT | not on PATH, no pip module |
| jadx (binary) | ABSENT | prior decompile output exists at `cartona app\decompiled\` |
| apktool | ABSENT | — |
| scrcpy | ABSENT | — |
| 7z | ABSENT | Info-ZIP unzip suffices for reads |

## 2. Installed system images (Addendum B input)

| API | Variant | ABI | Notes |
|---|---|---|---|
| 35 | google_apis | x86_64 | **the only installed image**; PlayStore.enabled = no on the AVD using it |

No Play Store (google_apis_playstore) image, no API 30 image, and no ARM-translation-capable image is installed locally. If an emulator fallback becomes necessary, an official `google_apis_playstore` x86_64 image (Android 11+ carries ARM-to-x86 translation via libndk/native-bridge; per official Android Emulator documentation, ARM app support exists on Android 11+ x86_64 images with known per-binary limitations) would need to be downloaded via the official SDK manager — free, official channel; decision deferred to CP3 and only if the physical device is unavailable. **Emulator viability must be validated by an actual install attempt, never assumed.**

## 3. AVDs

| Name | Device | API | Image | Play Store | Disk |
|---|---|---|---|---|---|
| POL_API_Emulator | pixel_6 | 35 | google_apis/x86_64 | no | 6 GB data, 512 MB sdcard |

## 4. Devices

| State at capture | Detail |
|---|---|
| 0 devices attached | `adb devices -l` empty (server freshly started by query) |

**Physical ARM device:** user confirmed one will be connected for CP3. Device query (ABIs, Android version, density, dimensions, locale) will be run at CP3 start per Addendum A.

## 5. Automation options assessed (details in tooling-research.md)

| Option | Assessment |
|---|---|
| ADB + screencap/uiautomator dump | AVAILABLE NOW; sufficient for screenshots, hierarchy dumps, tap/input via `adb shell input` |
| ARTEMIS | RESEARCHED (see tooling-research.md); optional, isolated-env only, no prerequisite status |
| UI Automator (instrumentation-based) | possible via adb shell uiautomator; no extra install needed |
| scrcpy | ABSENT; not required for evidence capture |

## 6. Constraints carried into CP3

- Install only after Addendum A split-compatibility validation (per-device ABI/locale/density selection; same package+versionCode across chosen splits).
- Full command/exit/stdout/stderr/device-state logging for every install attempt.
- No APK modification; no security-control bypass.
