# Coverage and Limitations — Comprehensive Extraction Run

## Coverage matrix (what was actually examined)
| Category | Examined | Boundary |
|---|---|---|
| Input artifacts | 7/7 hashed and role-mapped | all originals read-only |
| Archive entries (base) | 1,445/1,445 listed and categorized | per-entry CSV in private corpus |
| DEX files | 6 counted (names/sizes) | not decompiled (Flutter host; app logic in Dart) |
| Native libs | 6/6 listed with sizes; libapp/libflutter hashed + ELF metadata | .so bodies not disassembled |
| Manifest | 100% components extracted (56), permissions (19), queries, intent-filters, cleartext/backup configs | signing certs not verified (Play-signed; not in scope) |
| Flutter assets | 106/106 inventory entries; fonts + icons classified | image pixels not individually analyzed |
| Dart snapshot | sections located (4 symbols); 15,407 ASCII + 1,966 UTF-16LE runs mined; REA projections pulled (package_uris 6/6 exact; tokens 2,000 of >=4,000) | typed class/function recovery BLOCKED (no compatible parser) |
| Routes/endpoints | 24 routes, 70 endpoint strings cataloged | presence ≠ runtime proof |
| Arabic UI strings | 1,494 recovered; domain-counted; curated samples committed | full dump stays local (proprietary) |
| POL source | branch/commit pinned; api-client (78 lines, generic), 9 mobile screens, mock-driven data, fa.ts i18n | no POL code changes; tests not re-run |
| Runtime UI | 0 screens observed | BLOCKED: INSTALL_FAILED_NO_MATCHING_ABIS on API 35 x86_64 (Google APIs, no ARM translation); prerequisites documented |

## Phase status
- Phase 0-2 (inputs/inventory): PASS
- Phase 3-4 (AOT/API/domain map): PASS (string-level; typed recovery BLOCKED with exact error)
- Phase 5 (UI/UX): PARTIAL — static atlas complete; runtime capture BLOCKED (ABI + OTP prerequisites)
- Phase 6 (data/persistence): PASS (schema from snapshot; server model hypothesis-tagged)
- Phase 7 (security): PASS (static config review; enforcement behavior UNVERIFIED)
- Phase 8 (POL re-audit): PASS (statuses grounded in actual file reads)

## Corrections to prior runs
1. Arabic UI strings WERE in the snapshot (UTF-16LE) — revision-2 recorded them absent.
2. Cleartext traffic is restricted to the emulator loopback by network-security-config — production HTTPS-enforced.
3. config.en/mdpi splits verified to carry no AOT (completes the split matrix).

## What could not be recovered, and why
- Typed Dart classes/functions: snapshot is kind-3 (Dart 2.14-era); no PyPI parser supports it (Doldrums rejects the hash — exact error recorded); blutter needs a matched Dart SDK + C++ toolchain (future option).
- SERVER_BASE_URL value: not stored as a plain string; likely assembled or config-delivered.
- Payment provider names: not embedded; server-driven.
- Colors/spacing/widget tree: require runtime capture (blocked).
- assetlinks.json verification: server-side, not contacted.

## Local-only corpus
C:/Star/pol-2.4-private-analysis/cartona/e4a0f4d1.../ — originals-index, archive-inventory, decoded-manifest-resources (pointer to existing apktool tree), flutter-assets, strings-and-snapshot (libapp copy + string dumps), decompilation-or-pseudocode (Doldrums output attempt), ui-captures-full (empty — capture blocked), database-schema (from snapshot strings), scratch (tools + generator scripts). No credentials or user data stored.
