# Comprehensive Cartona APK Extraction & Evidence Program

Use this prompt for the next major REA investigation. The objective is to extract and document **as much technically recoverable information as possible** from the authorized Cartona APK/XAPK and its splits, then compare evidence with POL. This is a research and product-analysis task, not a POL code-change task.

## Critical expectation management

- Do not promise recovery of the original Dart source line-for-line. A Flutter release APK normally contains Dart AOT code rather than the original source tree. REA's AOT inspection returns snapshot/build metadata and a bounded string-pool projection; typed class/function recovery requires a parser matched to the target snapshot layout. Record what each tool can actually recover and its coverage.
- Do not confuse strings, route names, endpoint-looking strings, SQL identifiers, or class-like tokens with proof that a feature executes at runtime.
- **Maximize extraction locally, but do not commit the complete proprietary APK, split packages, DEX files, Dart AOT snapshot, native libraries, reconstructed database contents, bulk decompiled code/pseudocode, or the full set of proprietary app assets to GitHub.** Keep the raw analysis corpus outside the Git repository (or in a clearly local-only, ignored location); commit sanitized indexes, hashes, evidence metadata, proportionate excerpts, screenshots chosen for analysis, findings, and independent product requirements. Do not copy Cartona code into POL.
- Do not extract, publish, or reuse live credentials, API secrets, session tokens, customer data, or private business records.
- No anti-fraud bypass, license-check bypass, access-control bypass, certificate-pinning bypass, or unauthorized production API probing. For runtime UI work, use an authorized test account and normal application flows; if that is unavailable, mark runtime checks BLOCKED rather than circumventing controls.

## Mandatory repository workflow

Read these first:

- `analysis/rea/README.md`
- `analysis/rea/SYNC_PROTOCOL.md`
- `analysis/rea/AGENT_PROMPT.md`
- `analysis/rea/LATEST.md`
- `analysis/rea/sync-manifest.json`

Before changing files, record:
- `git rev-parse --show-toplevel`
- `git status --short`
- `git branch --show-current`
- `git rev-parse HEAD`
- `git remote -v`
- current upstream status and local/remote divergence after fetch

Preserve all user changes. Never reset hard or force-push. Do not modify POL application code during this extraction phase. Use a new dated run folder under `analysis/rea/runs/`; do not overwrite prior audits.

## Phase 0 — Find and freeze every authorized input artifact

1. Locate the exact base APK and all available related files, including XAPK/APKS archives, ABI splits, language/density splits, manifest JSON, previously decoded manifest/resource directories, and any legally available test installation package.
2. Do not assume that the base APK alone contains the complete Flutter payload. Enumerate every split and ABI.
3. Compute SHA-256 for every input artifact; record path, byte size, timestamps, package/version, source and whether it is an original or derived file.
4. Treat originals as read-only. Copy inputs to a local-only analysis directory outside the repository before unpacking.
5. Create a local-only inventory that maps every extracted item back to its parent artifact and archive path. Never put raw extracted files in a Git staging area.

## Phase 1 — Package, signing, Android and build provenance

Inspect and record:
- APK/XAPK/APKS identity, package ID, label, version name/code, min/target/compile SDK, supported ABIs and split relationships
- APK signing schemes and signer/certificate fingerprints using supported tools
- all DEX files, native libraries, asset directories, manifests, resources and archive entries
- decoded AndroidManifest.xml: application class, activities, services, providers, receivers, exported flags, intent filters, deep links, permissions, queries, network-security config, cleartext policy, backup and data-extraction settings
- Flutter framework evidence, Dart snapshot hash/header layout, per-ABI `libapp.so` hashes and ELF build IDs for `libflutter.so`
- bundled third-party SDKs and their exact evidence/namespace
- App Links, deferred links, messaging, mapping, image/file picker, payment/credit integrations and analytics clues

Distinguish confirmed metadata from interpretations. A manifest permission is not proof that an operation executes.

## Phase 2 — Exhaustive local asset and resource inventory

On the local-only copy:
1. Enumerate all archive entries and group them by file type, directory, package and likely purpose.
2. Inventory every Flutter asset, locale/translation file, JSON/config file, font, SVG, raster image, animation, icon, audio/video resource and bundled notice/license.
3. Record path, size, SHA-256, dimensions/duration where relevant, format, likely usage and evidence confidence.
4. Preview/classify image assets locally so the report identifies logos, category icons, product imagery, onboarding illustrations, campaigns, banners and placeholders where those categories are actually evident.
5. Inspect string/ARB/JSON localization sources. The absence of visible Arabic strings in the Dart snapshot does not prove the UI lacks translations; localization may be in assets or server-delivered content.
6. Do not commit extracted proprietary assets in bulk. Publish an inventory and selected, proportionate evidence only.

Deliver locally: complete asset table, archive inventory, extracted resources and a contact sheet if supported. Commit only the sanitized catalog and summary.

## Phase 3 — Maximal Flutter/Dart AOT investigation

Use the exact installed REA tool schemas and current official documentation.

1. Run `identify-flutter-build` and `inspect-dart-aot` for every available ABI split, not just the base APK or one ABI.
2. Preserve complete structural metadata and bounded string-pool output locally. Page through supported collections such as package URIs, Dart SDK URIs and class-like tokens until the provider's actual reported boundary, recording whether counts are exact or lower bounds.
3. Determine the probable Dart snapshot generation from the hash and reliable evidence. Do not infer an exact Dart SDK release without a supporting source.
4. Research SDK-matched, legally usable tooling that can recover additional typed class/function structure from this specific AOT layout. Compare candidates by:
   - supported snapshot/version
   - platform and architecture support
   - parser/code quality and validation method
   - licensing and install footprint
   - evidence that the candidate works on a known compatible sample
5. Trial a candidate on a benign compatible sample before applying it to the target. Keep original binaries unchanged, use copies, record commands and outputs, and retain explicit error/coverage data.
6. Where a compatible parser or licensed analysis engine exists, recover the maximum useful typed structure locally: class/function names when present, method boundaries, call/reference relationships, constants, type clues, pseudocode and assembly as supported. Never present reconstruction as original source unless it demonstrably is.
7. If typed recovery fails or is incomplete, proceed with static string and resource analysis, and mark that phase PARTIAL. Do not manufacture a Dart widget tree or source code from isolated tokens.
8. Keep the complete raw decompilation/pseudocode local. GitHub may contain a symbol index, coverage report, selected minimal evidence excerpts, findings and stable local references, not a bulk source dump.

## Phase 4 — Product API and domain model map

Create a local master catalog of endpoint-like strings, named routes, deep links, database identifiers, event names, state/status strings and product-domain terms.

For each API-like item, record only what evidence supports:
- raw path/string and source file/snapshot offset or evidence ID
- probable HTTP method only when directly observed; otherwise UNKNOWN
- probable product domain and linked route/symbols
- observed parameters and models only when recovered
- authentication assumptions as hypotheses unless proven
- environment/base URL status
- confidence: VERIFIED STRING / STRONG LINK / HYPOTHESIS / UNRESOLVED
- whether the item is merely present in the artifact or actual runtime use has been demonstrated

Never call production endpoints or attempt to enumerate private data. Do not use discovered credentials. Avoid committing a full proprietary string dump; publish a curated endpoint/route catalog relevant to product analysis.

Investigate these domains when evidence leads there:
- authentication, OTP, session refresh and guest browsing
- service area and business/branch management
- suppliers, categories, products, sponsored listings, pricing, discount, MOV/MOP filters and favorites
- cart persistence, cart validation, quantity/stock rules, checkout and order creation
- order lifecycle, reorder, tracking, delivery, cancellation, returns, support/disputes
- wallet, installment/credit/BNPL, consent and webview message contracts
- notifications, campaigns, cashback, loyalty/GMV targets and customer support
- analytics, attribution, app links, integrity and anti-fraud signals

## Phase 5 — UI/UX and runtime screen capture

This phase requires a compatible emulator or Android device and must be evidence-based.

1. Check whether `adb`, Android SDK platform tools, emulator/device, Flutter/Android inspection tooling and screenshot capture are actually available. Report exact versions and connected device details without exposing personal information.
2. Do not silently install a very large emulator/system image. If no compatible runtime exists, finish static work and mark runtime capture BLOCKED with the exact prerequisite.
3. If a device exists, install only the authorized package/split set as required. Use a safe test account and ordinary in-app behavior. Do not bypass OTP, licensing, anti-fraud, or other protections. Do not place a real order, incur a charge, or affect a real merchant without explicit authorization.
4. Walk through every accessible named route and journey, including:
   - launch, onboarding, registration/login and guest mode
   - home/landing and service-area states
   - categories, search, supplier listing/detail, product detail
   - filters, favorite/unfavorite and pagination
   - cart, validation, minimum order, stock/price changed states, checkout prerequisites
   - orders, lifecycle states, reorder and tracking
   - branch/user management
   - wallet/credit/BNPL consent surfaces, without submitting financial applications
   - notifications, promotions/campaigns, support, profile and settings
5. For each screen capture:
   - full-screen screenshot and dimensions
   - route/screen identification and path taken
   - locale, RTL/LTR, device density and Android version
   - visible text transcribed when feasible, but respect the boundary between observed screen text and inferred behavior
   - loading, empty, success, validation error, network error, permission denied and offline states that can be produced safely
   - scroll position and the state/data prerequisite
6. Use at least one normal device size and note any responsive variations. Test accessibility tree/semantics where available, but record that Flutter's painted widget hierarchy may not be fully represented by Android's accessibility tree.
7. Build a screen atlas, journey diagrams, screen-to-route map, interaction specification and a UX pattern inventory. Measure layout/tokens from captures but mark pixel-derived measurements as estimates.
8. Do not commit bulk extracted source imagery or the full app asset library. Save sanitized screen evidence and selected representative screenshots only where needed for the research record.

## Phase 6 — Data, persistence and behavior clues

1. Inspect only database schema and structure that can be lawfully obtained from the supplied package or normal test installation. Do not collect actual user records.
2. For any SQLite file, determine whether it is a schema/template, a bundled seed database, or runtime-generated storage. Inventory tables/columns/indexes/version metadata; redact row contents unless they are clearly benign non-user test fixtures.
3. Cross-link fields such as reorder origins, abandoned cart timestamps, search history and branch/order relationships to API and UI evidence.
4. Reconstruct a domain model and entity relationship diagram as a hypothesis map, distinguishing directly observed schema from inferred server entities.
5. Infer state transitions only where evidence supports them. Keep runtime and server-side behavior marked unresolved unless observed through authorized tests or documentation.

## Phase 7 — Security, privacy and integrity posture

Perform a non-invasive static configuration review:
- cleartext/TLS and network security config
- permission minimization and exported components
- app-link trust and configuration
- storage of local state and sensitive information indicators
- integrity/license/fake-location checks
- logging and analytics SDK signals
- backup and data-extraction settings
- cryptographic/provider references when evident

Report potential risks with evidence and confidence. Do not exploit the app, bypass protections, harvest secrets, or try to defeat anti-fraud controls. Separate a declared signal/check from proof of how enforcement behaves.

## Phase 8 — Re-audit POL against its actual current source

Before marking a gap:
1. Record the exact POL branch and commit being analyzed.
2. Inspect real screen files, routes, state stores, API contracts, models, migration/schema definitions, tests, and build variants.
3. For every product capability, provide exact POL source/test paths and the observed Cartona evidence reference.
4. Use only these statuses: `PRESENT`, `PARTIAL`, `MISSING`, `UNVERIFIED`. Use `UNVERIFIED` when the target or POL evidence is insufficient.
5. Prioritize by MVP necessity, revenue/retention value, engineering effort, operational cost, data dependencies and risk. Do not treat a competitor's presence of a feature as proof it belongs in POL.
6. Make no application source changes during this investigation.

## Local raw corpus vs GitHub deliverables

Create a local-only root outside the Git working tree, for example:

`C:/Star/pol-2.4-private-analysis/cartona/<APK-SHA256>/`

Suggested local folders:
- `originals-index/` — metadata only, keep original APK/splits at their existing location
- `archive-inventory/`
- `decoded-manifest-resources/`
- `flutter-assets/`
- `strings-and-snapshot/`
- `decompilation-or-pseudocode/`
- `ui-captures-full/`
- `database-schema/`
- `scratch/`

Keep bulk raw code, full string dumps, complete proprietary assets, database row data and extracted binaries outside Git. If a raw file is required to reproduce a finding, record its local path, SHA-256, extraction method and parent artifact in the private manifest. Do not put credentials or user data in that manifest.

## Required GitHub run deliverables

Create a new immutable run folder:
`analysis/rea/runs/YYYY-MM-DD-cartona-comprehensive-extraction/`

Include as applicable:
1. `executive-summary.md`
2. `artifact-inventory.json`
3. `archive-and-split-inventory.csv`
4. `manifest-components.csv`
5. `flutter-assets-inventory.csv`
6. `flutter-snapshot-and-code-recovery.md`
7. `symbol-and-class-index.csv` (curated index; no bulk source dump)
8. `api-endpoint-catalog.csv`
9. `route-feature-map.csv`
10. `ui-screen-catalog.csv`
11. `ui-ux-design-system.md`
12. `user-journey-maps.md`
13. `domain-data-model.md`
14. `security-and-integrity-review.md`
15. `pol-feature-gap-matrix.csv`
16. `implementation-priorities.md`
17. `coverage-and-limitations.md`
18. `validation.json`
19. `run-log.md`

For unavailable categories, say `NOT AVAILABLE` or `BLOCKED` and explain why; do not fabricate an artifact merely to fill the list. Do not upload the APK, XAPK/split packages, full DEX/Dart/native binaries, full recovered proprietary source, full asset dump, or raw database contents.

## Validation and evidence rules

- JSON files must pass a standard JSON parser. CSV files must pass a real CSV parser with uniform row widths.
- Every factual claim should point to an artifact hash and operation/evidence ID, or a runtime capture identifier.
- Record tool name/version, exact command or operation, exit/status, limits, and coverage.
- Compare each artifact hash against the source as available.
- Count files and coverage by ABI, DEX, resources, Flutter assets and screens actually inspected.
- Separate static fact, runtime observation, hypothesis, and unknown.
- Do not claim all code has been extracted unless a defensible completeness criterion exists. Prefer explicit coverage matrices and lower-bound counts.
- Run `git diff --check`; inspect the staged diff before committing.

## Synchronization and final status

1. Update `analysis/rea/LATEST.md` and `sync-manifest.json`.
2. Stage only the sanitized intended `analysis/rea/` files.
3. Commit and push to the intended branch, respecting the repository's branch/PR workflow.
4. Never force-push, discard user changes, or silently overwrite old run folders.
5. Read every expected output back from GitHub and verify the final commit SHA.
6. Update the index with exact sync status and commit details; push and read back the index update too.

Final response must report exact:
- input artifacts and SHA-256 values
- tool versions and commands actually executed
- extraction/coverage figures, per category
- all deliverables and links
- tests and parser validations
- local-only corpus location and file inventory/hash manifest
- what could not be recovered and why
- highest-confidence findings for POL
- commit SHA, branch, remote read-back result

Final status must be one of:
- `PASS / SYNCED` — checks that were in scope completed, deliverables pushed and read back; note any explicit static-analysis limitations.
- `PARTIAL` — useful evidence exists but some extraction/validation/capture tasks remain incomplete.
- `BLOCKED` — input, tools, access, or execution blockers prevent reliable progress.

Start now and perform the work, not just plan it.
