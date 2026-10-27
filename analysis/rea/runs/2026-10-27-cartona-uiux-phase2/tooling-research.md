# Tooling Research — CP2

**Date:** 2026-10-27 · Sources in `research-source-register.csv` · Addendum C compliance noted per tool.

## 1. ARTEMIS (github.com/google/artemis) — researched, NOT activated

| Aspect | Finding (source: official repo README, fetched 2026-10-27) |
|---|---|
| Purpose | Natural-language → Android automation; AndroidWorld benchmark claims; end-to-end workflows, logcat, screenshots, bug reproduction |
| License | Apache-2.0 (free) |
| Windows | Supported (`start.bat` for CMD/PowerShell) |
| Requirements | Python via `uv`; connected device/emulator; auto-installs ADB, scrcpy, FFmpeg; installs an on-device accessibility helper (removable via `uv run artemis helper uninstall`) |
| Execution profiles | Flash (3–5 s/step, reactive) and Pro (15–40 s/step, planner/operator/checker graph) |
| **LLM dependency** | Configures model providers via `.env` / `config/artemis.jsonc`; README references Gemini/Google AI — **requires a provider API key** |
| Interfaces | CLI (`uv run artemis run …`), MCP server (`artemis mcp --install …`), Web UI, Python SDK |

**Addendum C assessment (why not activated now):**
1. **Paid/external API**: driving ARTEMIS requires an LLM provider API key (e.g., Gemini) → per-inference cost not authorized in this mission. Not activated.
2. **Data handling**: ARTEMIS sends screenshots/UI observations to the configured external model. Cartona screen captures are potentially proprietary evidence (Addendum D); transmitting them to an external service without explicit authorization is excluded by this run's publication policy.
3. **Device modification**: first run installs an accessibility service on the target device. Permitted only with user consent; not needed while ADB covers evidence capture.
4. **Isolation plan if later authorized**: clone into `analysis/rea/runs/2026-10-27-cartona-uiux-phase2/` sibling scratch (outside repo tracking) or a separate directory, project-local `.venv` via `uv`, **no global MCP install** (`artemis mcp --install` NOT to be run), no repo files modified.

**Verdict: `OPTIONAL — NOT ACTIVATED (requires user authorization for model API + external data handling)`. Not a prerequisite (Addendum C).**

## 2. Local ADB + UI automation baseline (chosen primary path)

Fully local, zero cost, available now (verified in android-environment-matrix.md):
- `adb exec-out screencap -p` — PNG screen capture with device-side PNG encoding.
- `adb shell uiautomator dump` — XML accessibility hierarchy (works for Flutter apps' platform views; Flutter's own widgets may expose limited semantics unless accessibility is enabled — a known limitation to record during CP4, not an assumption).
- `adb shell input tap/swipe/text/keyevent` — interaction.
- `adb shell wm size / wm density` — device geometry for screenshot metadata.
- `adb logcat` — session logs (PII-filtered before any publication).
- `adb install-multiple` — validated multi-split install (Addendum A).
- `adb shell monkey -p com.cartona 1` — safe cold-start launcher invocation (no UI stress).

## 3. Emulator ARM-translation compatibility (Addendum B research)

| Question | Finding (official blog + docs; see register) |
|---|---|
| Which images run ARM apps on x86_64? | Android 11 (API 30)+ **Google Play** x86_64 system images translate ARM→x86 on the fly (native bridge: libndk on newer images; libhoudini on older) |
| ARMv7 caveat | 32-bit ARM (`armeabi-v7a`) apps are **less reliable** under translation than arm64-v8a; some apps fail to load native libs or refuse to run |
| Locally installed | Only `android-35/google_apis/x86_64` (no Play variant, no translation) → historical install failure is consistent with this |
| Policy for this run | Device-first (physical ARM device). Emulator fallback only if device unavailable: download official `google_apis_playstore` x86_64 API 30+ image via SDK manager (free/official), then **validate by actual install attempt**; a passing image test is the only acceptable evidence of viability |
| Historical failure replay | Supplementary only (CP3, non-blocking): document the exact `INSTALL_FAILED_NO_MATCHING_ABIS`-class error on the existing google_apis image |

## 4. Tooling decisions

| Need | Decision |
|---|---|
| Runtime evidence capture | ADB + screencap + uiautomator dump (local) |
| Install | `adb install-multiple` after Addendum A validation |
| ARTEMIS | Not activated (see §1) |
| Static analysis | Existing prior decompile + direct APK reads (zipfile/aapt/apksigner) — no new tool installs required for CP2/CP6 scope |
