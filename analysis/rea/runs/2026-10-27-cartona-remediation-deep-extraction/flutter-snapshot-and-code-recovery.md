# Flutter Snapshot and Code Recovery — Cartona v8.4.6 (Run 2026-10-27)

Supersedes the recovery section of run 2026-10-26; extends evidence with r2flutter. Toolchain decisions: `toolchain-inventory.md`.

## 1. Snapshot identity — now AUTHORITATIVE

| Field | Value | Source |
|---|---|---|
| Payload | libapp.so in config.armeabi_v7a.apk only; 10,945,116 B; SHA-256 `e150ce501b87d3c0ff8b45548b05be151733e839ea00a0b3947620cd0f8f3df2` | ZIP entry hash (re-verified) |
| **Dart version** | **3.9.2** (`version_source: exact-hash`) | **r2flutter -H** (built from official repos in isolated container this run) |
| Tag style | OBJECT_HEADER (v3.4+), cws 8, alignment 16 | r2flutter -H |
| Snapshot kind | 3 (both VM and isolate headers) | r2flutter -H + REA inspect_dart_aot (agree) |
| Flags | product, no-code_comments, dwarf_stack_traces_mode, dedup_instructions, no-tsan, no-msan, no-shared_data, **arm**, android, **no-compressed-pointers** | r2flutter -H (VM snapshot flags) |
| Header internals | base_objects 99, objects 1176, clusters 5 (VM); header_fields 5, it_capacity 20000 | r2flutter -H |
| Engine | libflutter.so build-id `deaf7120f4bf65f07ea2c5505bcf74436d4efd1e`, clang 18.0.1 (r522817) | ELF PT_NOTE (prior run, unchanged) |
| **Correction of record** | REA's earlier "kind 3 = Dart 2.14 FullAOT" inference was a **layout-kind reading, not a version determination**. The exact-hash match to **Dart 3.9.2** (Flutter ~3.35.x era per r2flutter support matrix) is authoritative. Doldrums' rejection is explained: it predates this profile. | — |

## 2. What r2flutter actually recovered on the ARMv7 payload

Tool is AArch64-primary (official docs); ARMv7 instruction analysis unsupported. Staged per plan §15:

| Probe | Result | App-level value |
|---|---|---|
| `-H` header | **PASS** — full header incl. exact-hash Dart version | HIGH — definitive snapshot identity |
| `-jH` JSON header | PASS (saved) | structured record |
| `-c` classes | 312 class names — **all snapshot-internal/VM types** (`_Uint16List`, `FutureOr`, `Script`, `UnlinkedCall2`, …); **zero app-level classes** (`grep -i "cartona|retailer|order|product|supplier|wallet"` = 0) | LOW — structural sanity only |
| `-f` functions | **6,426 function entry addresses** (e.g. `0x316cc0 method.fn_0`), sequentially named, **no semantic names** | MEDIUM — a callable-address map; names NOT recovered (naming relies on AArch64 code analysis; `-n` heuristic is explicitly unreliable per docs) |
| `-S` SBOM | 28 components, all `dart:*` libraries at confidence 50 | LOW-MEDIUM — confirms dart: core libs only |
| `-z` ObjectPool strings | **EMPTY** — PP-walk is AArch64-assumptive → NOT PRODUCED on ARMv7 | — |
| `-i` instruction table | 27 lines (limit-20 sample) | structural sample only |
| `-T` type names | same 312 internal classes | LOW |

**Verdict: `STATIC_METADATA_PARTIAL`** — authoritative versioning + header + function-address map achieved; app-level typed class/function recovery NOT achieved on ARMv7 with any available tool (Doldrums: rejects hash; r2flutter: AArch64-only analysis; Blutter: ARM64-only).

## 3. String-level corpus (unchanged evidence, re-confirmed)

- ASCII runs (≥6 chars): 15,407 → endpoint paths, routes, flags, config identifiers (this run's `api-endpoint-catalog.csv` adds per-endpoint source-line provenance).
- **UTF-16LE runs: 1,966 (1,494 Arabic UI strings)** — the UI localization corpus (gen-l10n), recovered in run 2026-10-26, re-verified present.
- These remain STRING_ONLY evidence: presence ≠ runtime execution.

## 4. Raw outputs (local-only corpus)

`C:/Star/pol-2.4-private-analysis/cartona/e4a0f4d1…/r2flutter/` — json-header.json, classes.txt (312), functions.txt (6,426), sbom.txt, type-names.txt, instr-table.txt, pool-strings.txt (empty). Build logs: `…/scratch/r2flutter-run.log`, `r2flutter-probe.log`. libapp working copy: `…/strings-and-snapshot/libapp-copy.so` (SHA-256 matches payload).

## 5. Explicit non-claims

- No Dart source code, widget tree, or app-level class structure was recovered.
- Function addresses are entry points without semantic names; linking them to endpoints/routes would require caller evidence that is not producible on ARMv7 with current tools.
- The 6,426 function count is an address-map count, not a business-logic inventory.
- Committing policy honored: only the curated `symbol-and-class-index.csv` (config identifiers/flags) is published; full outputs stay local.
