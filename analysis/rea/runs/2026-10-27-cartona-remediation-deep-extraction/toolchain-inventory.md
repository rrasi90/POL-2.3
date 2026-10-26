# Toolchain Inventory & Decision Log — Run 2026-10-27

## toolchain-inventory

| Tool | Detected version | Source / path | Install required? | Result | Actual test performed |
|---|---|---|---|---|---|
| python | 3.11.15 (this shell's PATH resolution) | system | no | usable | validator + generators executed (exit 0) |
| git | Git-bash bundled | system | no | usable | sync/commit/push operations |
| java | OpenJDK 21.0.9 | C:/Program Files/Android/Android Studio/jbr | no | usable | not directly invoked this run (JADX MCP used its own bridge in prior runs) |
| adb | 1.0.41 | SDK platform-tools | no | usable | emulator install attempt (INSTALL_FAILED_NO_MATCHING_ABIS) |
| JADX headless | 0.7.1 (pinned JAR 6e5eacf5…) | ~/.local/share/rea/android | no | usable (prior runs); this run reused verified Oct-5 decoded tree with provenance note | — |
| apksigner | build-tools 36.0.0 | Android SDK | no | usable | `apksigner verify --verbose --print-certs` on base APK → Verifies (v2+v3+SourceStamp) |
| docker | 28.5.2 | system | started Desktop | usable | r2flutter container build/run |
| r2/r2flutter | r2: git master (≥6.2.2); r2flutter: trufae/r2flutter git HEAD | cloned from official GitHub inside ubuntu:24.04 container | **yes** (built in container) | **BUILD OK, header parse OK** | `-H` header probe → Dart 3.9.2 exact-hash match |
| apktool | NOT on PATH | — | no (Oct-5 decoded tree reused with provenance) | reused tree | manifest/configs re-read from tree |
| MobSF | NOT INSTALLED | — | deferred | — | not needed yet; static security review done via decoded manifest + apksigner |
| adb-mcp | NOT INSTALLED | iksnerd/adb-mcp candidate | no | ADB CLI suffices; MCP not required by plan §3.3 | — |
| reverse-skill | NOT INSTALLED | zhaoxuya520/reverse-skill candidate | no | NOT INSTALLED per plan §16.2 (router scope unclear; not needed) | — |
| Ghidra | NOT INSTALLED | — | no | no specific native question requiring it this run | — |

## toolchain-decision-log

1. **r2flutter — INSTALLED (container-isolated).** Rationale: plan §4.4 priority tool for Dart snapshot structure; the support matrix maps our exact snapshot hash to Dart 3.9.2, making it the only tool able to authoritatively version the snapshot. Official sources: https://github.com/radareorg/r2flutter + https://github.com/trufae/r2flutter (README's clone target) + doc/support.md (fetched 2026-10-27: profiles Dart 2.10→3.14; hash 97ff04a7… → Dart 3.9.2; AArch64 primary; ARMv7 instruction analysis unsupported). License checked: r2flutter is BSD-3 (repo), radare2 LGPL — analysis-only use. Install method: `git clone --depth 1` + `sys/install.sh` (radare2) + `make` (r2flutter) inside **ubuntu:24.04 container** (plan §4.4 prefers isolated Linux env) — no host pollution. Build result: `R2FLUTTER_BUILD_OK`; CLI confirms documented options (-H/-jH/-c/-f/-z/-S/-T/-i/-A/-n/-D…). Known limitation honored: instruction analysis is AArch64-only → for our ARMv7 payload only header/metadata/string/pool phases are meaningful; instruction-level results (if any) must be tagged NOT_APPLICABLE_ARM64_ONLY.
2. **Blutter — NOT RUN.** Official docs: ARM64-only for Android libapp.so. Our artifact is armeabi-v7a-only → `NOT COMPATIBLE: ARMv7 input; tool expects arm64`. Recorded per plan §4.5; no attempt to fake architecture.
3. **Doldrums — previously rejected** (run 2026-10-26): `Unsupported Dart SDK, snapshot hash: 97ff04a7…`. Root cause now understood: Doldrums predates the 3.9.2 profile; r2flutter supersedes it.
4. **MobSF — DEFERRED.** Docker available; image pull ≈1–2 GB with 22 GB free disk. Static security posture already covered by decoded manifest + apksigner + snapshot review this run; MobSF adds automated scans but no new decisive evidence for the POL handoff. Revisit if runtime analysis is authorized.
5. **adb-mcp / reverse-skill — NOT INSTALLED.** Plan allows ADB CLI fallback (§3.3 step 5: "MCP شرط اجرای پروژه نیست"); reverse-skill's scope/security unclear per §16.2 → kept as reference only.
6. **Emulator images — NOT downloaded.** INSTALL_FAILED_NO_MATCHING_ABIS root cause = missing ARM translation on Google APIs x86_64. Fix would require a Google-Play-API-level image (~multi-GB) or an ARMv7 device. Per plan §4.7 step 3, no silent heavy downloads; runtime capture stays BLOCKED with prerequisites documented.
7. **JADX full re-run — SKIPPED with provenance.** The Oct-5 apktool/jadx decode tree is reused; its AndroidManifest.xml matches the current base APK's XAPK descriptor (min 24/target 36 cross-checked in run 2026-10-26), and the base APK hash is unchanged (re-verified this run). A full fresh decompile of 6 DEX (~27.4 MB code) adds time without changing known findings; targeted verification (DEX names/sizes, apksigner) was performed instead.
