# Limitations & Unknowns — Revision 2

## Phase classification

| Phase | Status | Basis |
|---|---|---|
| 1 Preserve & repair evidence | **PASS** | 7 originals preserved at `pol-2.4/` root; JSONs parse; evidence reconciled (v1 calls preserved with real evidence IDs; no fabricated outputs) |
| 2 Architecture | **PASS** | Flutter proven by libapp.so ELF symbols + flutter_assets + identify_flutter_build on split APK; manifest fully decoded; all 56 components enumerated |
| 3 Class & resource analysis | **PARTIAL** | Base-APK Java classes inventoried (12,338) and vendor-namespace-classified; Dart snapshot analyzed at string level (15,407 runs) but **not** decompiled to typed Dart classes/functions — no SDK-matched snapshot parser available in this environment |
| 4 User journeys | **PASS** (with labeled confidence) | 7 journeys reconstructed; every claim tagged V/H/U; no runtime proof claimed |
| 5 POL re-audit | **PASS** | Branch/commit pinned; framework verified (Expo 57/RN 0.86.3); 9 screens + i18n + variants recorded with paths; gap statuses use UNVERIFIED where POL evidence is absent |
| 6 Deliverables & validation | **PASS** | 8 files; JSON+CSV parse; evidence IDs resolvable to retained REA evidence; local paths exist; coverage summary below |

## What static analysis cannot prove (unchanged constraints)
- No APK execution; no runtime behavior claims. No API calls; endpoints are observed strings only, and `SERVER_BASE_URL`'s value was not resolved (not embedded as a plain string).
- Dart snapshot: kind-3 FullAOT string projection is bounded (lower bounds; 6 package URIs / 4000+ class tokens returned of ≥17,001 printable runs). Typed Dart recovery (classes, functions, widget tree) requires an SDK-matched snapshot parser — recorded as the main open unknown.
- Arabic UI strings are absent from the snapshot; localization source (arb/json asset or server) unresolved.
- Payment provider names not found statically — likely server-driven; unknown, not proven absent.
- Manifest decoded from a pre-existing apktool output (Oct 5) of the same base APK, cross-checked against the XAPK `manifest.json` (min 24 / target 36 agreement); original APK bytes untouched.

## Coverage summary (what was actually examined)
- **DEX/classes**: 12,338 base-APK classes counted; top-level `com.cartona` (3 classes) inspected; vendor namespaces enumerated from decompiled `sources/` tree. Not every class decompiled.
- **Manifest**: 100% of declared components extracted (1 app activity + 23 vendor activities, 14 services, 9 receivers, 9 providers, all intent-filters, 19 permissions).
- **Resources**: 1,445 base resources counted; flutter_assets itemized (106 entries, 5 bundled packages); fonts/images categorized. Not every XML/asset opened.
- **Native libs**: 6 .so files in ABI split itemized with digests; libapp.so sections located (4 symbols) and string-mined; libflutter build-id extracted. No disassembly of .so bodies.
- **Bundles**: no JS bundle (not a RN app); Dart AOT snapshot analyzed as above.
- **Journeys**: 7 journeys, 30+ sub-claims, each tagged V/H/U.

## Residual unknowns (ranked)
1. Typed Dart class/function recovery from libapp.so (needs Dart 2.14-matched tooling) — would confirm screen-level UI flows.
2. `SERVER_BASE_URL` actual value and any API base variants (staging/prod).
3. Payment provider integration details (server-driven).
4. Wallet API surface (route exists; endpoints not observed).
5. Enforcement details of fake-GPS detection and PairIP license flow.
6. Localization source of Arabic strings.
