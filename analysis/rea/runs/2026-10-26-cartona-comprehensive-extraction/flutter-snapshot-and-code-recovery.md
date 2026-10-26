# Flutter Snapshot and Code Recovery — Cartona v8.4.6

## Snapshot facts (VERIFIED)
- Payload: libapp.so in config.armeabi_v7a.apk only; 10,945,116 bytes; SHA-256 e150ce501b87d3c0ff8b45548b05be151733e839ea00a0b3947620cd0f8f3df2
- ELF symbols: _kDartVmSnapshotInstructions (27,800 B), _kDartIsolateSnapshotInstructions (7,689,160 B), _kDartVmSnapshotData (29,192 B), _kDartIsolateSnapshotData (3,168,720 B) — evidence ev_fff3465f... (revision-2), reconfirmed ev_18ae4731...
- Snapshot kind 3 (Dart 2.14 FullAOT layout); hash 97ff04a728735e6b6b098bdf983faaba (2 sources); engine build-id deaf7120f4bf65f07ea2c5505bcf74436d4efd1e, clang 18.0.1 (r522817); no labeled Dart version (release build)
- en/mdpi splits: no AOT payload (ev_bf9eb76f..., ev_b6eed37b...) — single-ABI app

## REA bounded projections (exact where reported)
| Collection | Returned | Boundary |
|---|---|---|
| package_uris | 6 (exhausted, exact) | firebase_messaging_platform_interface, flutter_local_notifications, flutter internals, stack_trace |
| dart_uris | 7 (lower bound) | capped |
| class_like_tokens | 2,000 of >=4,000 (capped) | identifier-shaped runs; incidental matches included |
| printable runs | 17,001 (lower bound) | ASCII sweep: 15,407; UTF-16LE sweep: 1,966 runs (1,494 Arabic) |

Evidence: ev_a4d04d70... (class-token page), ev_18ae4731... (package URIs).

## Typed recovery candidates (researched + trialled)
| Candidate | Version support | Result |
|---|---|---|
| Doldrums (rscloura/Doldrums) | Dart 2.10 releases only (README) | BLOCKED — installed (pyelftools 0.33), executed on a working copy, failed: Exception: Unsupported Dart SDK, snapshot hash: 97ff04a728735e6b6b098bdf983faaba. Original untouched. |
| blutter | Requires exact-matching Dart SDK + C++ build | NOT ATTEMPTED — recorded as future option |
| REA inspect_dart_aot | kind-3 string-pool projection | PASS within bounds (primary evidence) |

## What string-level analysis DID recover (VERIFIED strings, not runtime proof)
- 70 endpoint-path strings (43 base paths + regex variants) — api-endpoint-catalog.csv
- 24 named routes — route-feature-map.csv
- Local SQLite schema: cartona_v0016.sqlite carts table (reorder/abandonment columns) — revision-2
- 1,494 Arabic UI strings (UTF-16LE) — private corpus; curated samples in reports
- ~30 state/feature flags + registration form fields — symbol-and-class-index.csv
- Config identifiers: ABANDONED_CART_TIMEOUT_DURATION_HOURS, SERVER_BASE_URL (value unresolved), CARTONA_FINANCE_WEB_APP_BASE_URL
- gen-l10n localization evidence; Segment analytics event names

## Explicit non-claims
No Dart class tree, function bodies, widget hierarchy, or source code recovered. Route/endpoint/flag strings do not prove runtime execution. Raw corpus (working copy, Doldrums clone, string dumps) is local-only.
