# Execution Plan — Cartona UI/UX Deep Extraction Phase 2

Approved plan (2026-10-27). Sources of authority, in order:
1. Mission doc `CARTONA_UIUX_DEEP_EXTRACTION_PHASE2_COMPLETE.md`
2. Mandatory Execution Addendum A–G
3. User refinements (branch/PR strategy, device-first runtime, absolute product-freeze)

## Checkpoint sequence and exit criteria

| CP | Scope | Exit criterion (testable) |
|---|---|---|
| CP0 | Sync, branch, baseline | Remote branch SHA == local HEAD, verified by `git ls-remote`; baseline/TODO/progress-log committed |
| CP1 | Prior-research audit | Every prior claim has a verdict (CONFIRMED / REVISED / UNVERIFIABLE / WRONG) + method; string & endpoint metrics recounted with documented rules (Addendum F) |
| CP2 | APK inventory, environment, tooling | apk-inventory.csv complete with recomputed hashes; environment matrix lists installed system images; tooling research has source register; split-compat metadata captured (Addendum A prep) |
| CP3 | Runtime attempt | Either successful validated `adb install-multiple` on device (or viable emulator per Addendum B), OR complete failure evidence with root causes + alternatives tried |
| CP4 | Runtime observation | Screenshot manifest with hashes/metadata for every captured state; catalog upgrades backed by evidence; auth-gated areas labeled BLOCKED_AUTH |
| CP5 | Assets | Asset inventory complete with per-file license classification; publication decisions recorded (Addendum D) |
| CP6 | Static analysis | Snapshot facts re-verified with tool/provenance; runtime-vs-static reconciliation rows for every catalog screen |
| CP7 | Complementary apps | Capability matrix with per-finding confidence; legal-access status explicit |
| CP8 | Mapping & recommendations | Mapping rows cite evidence + exact POL paths; every recommendation risk-classified; Persian text with correct ی/ک; nothing implemented |
| CP9 | QA + publish | Validation scripts PASS with recorded exit codes; product-freeze diff = zero; remote SHAs verified per checkpoint; PR step attempted (BLOCKED_AUTH documented if applicable) |

## Git guard (every commit, Addendum E + refinement #3)

1. `git status` review
2. staged + unstaged diff review
3. path allowlist: only `analysis/rea/runs/2026-10-27-cartona-uiux-phase2/**`
4. `git diff --check`
5. secret/prohibited-artifact scan
6. explicit file staging; out-of-scope change → stop, preserve, investigate

After every push: record local HEAD + remote SHA + verification command in progress-log.md.

## Runtime strategy (Addendum A/B + refinement #2)

Device-first. Before any install: per-APK metadata (package, versions, split, ABI, density, locale) + device query (ABIs, Android version, density, dims, locale) → select compatible split set → validate same package/version → `adb install-multiple` with full logging. Emulator fallback chosen by verified native-library compatibility (Android 11 x86/x86_64 ARM-translation caveats), never API number alone; historical x86_64 failure reproduced only as supplementary, non-blocking test. ARTEMIS optional (Addendum C): isolated clone, no global config changes, no paid services, independent validation; if hard, continue with ADB + uiautomator/screencap.

## Publication policy (Addendum D)

Screenshots and contact sheets = potentially proprietary until classified. Local-only artifacts get evidence ID + hash + reason (no sensitive paths). Nothing claimed "on GitHub" without remote verification.
