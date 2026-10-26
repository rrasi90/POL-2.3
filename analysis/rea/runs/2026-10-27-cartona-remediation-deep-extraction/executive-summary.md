# Executive Summary — Remediation Deep Extraction (Run 2026-10-27)

**Extends** (does not replace) run 2026-10-26-cartona-comprehensive-extraction. Mission: fix every known defect, deepen extraction, research all three Cartona products, audit the real POL repository, and produce a build-ready handoff for پل بازار، پل بنکدار، پل راننده.

## Defects fixed (quality-audit.md, all with proof-of-fix)

1. `archive-and-split-inventory.csv` was JSON → regenerated as a true CSV (20 rows × 5 cols).
2. `size_bytes` corruption → root-caused (AssetManifest values are variant-path lists, no sizes) → regenerated from real ZIP bytes with per-asset SHA-256 (113 rows).
3. 113/106 asset-count discrepancy → path-level reconciliation (7 infra files + 3 URL-encoded Font Awesome twins; validator enforces 103 declared matches).
4. API catalog depth → per-endpoint source-line, input hash, evidence ID, adjacent context, dedup rule, honest UNKNOWN methods.
5. UI catalog → explicit `observation_status` vocabulary; all 21 screens STATIC_INFERRED (none observed — none can be).
6. Validator → semantic (types, SHAs, uniqueness, reconciliation, secrets, binaries, P0-criteria) with 6 negative fixtures — all rejected (validator-self-test.json: 16/16 + 6/6).
7. Prior recovery/UI statuses re-derived honestly: typed recovery and UI capture were re-attempted with real tools, not relabeled.

## Major new evidence

- **Dart snapshot versioned authoritatively: 3.9.2** — r2flutter (built in isolated container from official repos) parsed the ARMv7 libapp.so header with `version_source: exact-hash`; corrects the earlier Dart-2.14-era inference. 6,426 function addresses + 312 VM-internal classes recovered; **zero app-level classes** (AArch64-only analysis; honest STATIC_METADATA_PARTIAL).
- **Signing verified:** Play App Signing, schemes v2+v3+SourceStamp, signer cert SHA-256 `83891e0a…`.
- **Three-product research** (public-product-research.md): supplier console = orders/catalog/pricing/offers/receivables (10K+ installs); Express driver app = daily-assignment→routing→POD→earnings loop (500+ installs, POD mechanics undisclosed); Cartona = asset-light marketplace + BNPL (AMAN) + Enterprise sourcing arm; comparators Gumla (own fleet) and MaxAB (fintech pivot; site currently unofficial demo). All claims citation-tagged.
- **POL reality audit** (pol-repository-reality-audit.md, all file-path grounded): FastAPI backend ~120 real routes; two-variant mobile build (`ir.pol.market`/`ir.pol.vendor`); **no DRIVER role anywhere**; strong backend RBAC (JWT org-binding, delegation ceiling + deny-lists, DB role invariants); 77 migrations, 92 tables; mock transport is vendor-only (retailer cannot run in mock); admin route shadowing defect; docs drift catalog.

## The handoff (implementation-handoff.md)

- **بازار+بنکدار are real and share a clean shell/API core** — most vendor flows REUSE_AS_IS; retailer needs mock coverage (B-03) + reorder/timeline UI (B-05/B-06) + push (B-07).
- **راننده has no backend substrate** — the P0 chain is B-09 (role+org model) → B-10 (delivery ownership) → B-11 (idempotent delivery) → B-12 (third app variant), all documented with acceptance criteria and negative tests; gated on one product decision (driver org model, D-01).
- 46 capabilities assessed across 5 roles; 25 fast-path decisions (single primary path each); 22 workflow transitions; 15 risks; golden E2E G1–G5 backed by real endpoints/tests, G6 documented as failing-gap.

## Honest gates

`EXTRACTION_COMPLETE`: PASS (all accessible sources; not full-source-recovery). `BUILD_HANDOFF_READY`: **PASS** — conditional note: driver items gated on D-01 decision. `RUNTIME_PARITY_VERIFIED`: **NOT CLAIMED** — no runtime observation (ABI blocker persists; prerequisites documented).
