# POL MVP — KNOWN GAPS / CONFLICTS / BLOCKED

**Rule (Master Instruction §3):** higher authority wins; log here; unresolved = screen status `GAP` + minimal stub; do not guess; do not stop build unless critical dependency.

**Status values in this file:** `CONFLICT` | `GAP` | `BLOCKED_EXTERNAL` | `PROPOSED`

---

## G-001 — OTP digit count (CONFLICT — RESOLVED)

- **Sources:** `frontend_route_contract_map.md` “OTP 6-digit” vs **D-018** + `scripts/operational_config.py` `OTP_CODE_LENGTH = 4`
- **Resolution:** D-018 wins → **4-digit**. Route map note is stale.
- **Action:** implement 4-digit; no further guess.

## G-002 — Master Tree filename / legacy reference (CONFLICT — RESOLVED)

- **Legacy reference:** an older governance document used a superseded tool-specific Master Tree filename; the active file is `50_POL_MASTER_PRODUCT_EXPERIENCE_DELIVERY_CONTROL_TREE_SPEC_…` v4.3.0.
- **Resolution:** the active file + v4.3.0 is canonical; execution tooling is not product authority.

## G-003 — Catalog list/search contract path (RESOLVED)

- **Canonical contract:** GET `/api/v1/products/search`
- **Current implementation:** `catalog_products_search` behind `/api/v1/products/search`, with `q`, optional `category_id`, `page`, `limit`, contract envelope, pagination, current lowest vendor price and available-vendor count.
- **Compatibility:** existing `/api/v1/catalog/search` remains available for current screens; it is no longer the only real path.
- **Evidence:** catalog HTTP contract test added to the verification suite.
- **Status:** RESOLVED for source/path parity; public deployed performance and media URL configuration remain deployment evidence.

## G-004 — Notifications inbox path (RESOLVED)

- **Contract:** `/api/v1/inbox/items*`
- **Current implementation:** `GET /api/v1/inbox/items`, `PATCH /api/v1/inbox/items/{item_id}/read`, and `PATCH /api/v1/inbox/items/read-all`, alongside `/api/v1/notifications` and preferences.
- **Evidence:** HTTP notification tests cover listing, unread count, deep links, tenant-scoped mark-read, idempotent mark-all-read, and read-state projection; current verification CI is green.
- **Status:** RESOLVED for source + automated CI evidence.

## G-005 — Notification read/deep-link projection (RESOLVED)

- **Current canonical wire field:** `is_read`, with `deep_link` on durable inbox items.
- **Current implementation:** `/api/v1/inbox/items*` exposes unread filtering/counts and mark-one/mark-all read operations; `/api/v1/notifications` projects read state and deep link.
- **Evidence:** current notification HTTP tests pass for projection, tenant-scoped read, and idempotent read-all; verification CI run #805 is green.
- **Status:** RESOLVED for source + automated CI evidence.

## G-006 — Corporate routes absent from route map (GAP)

- Spec 22 C-01…C-08 + Master Tree CP-* exist; `frontend_route_contract_map.md` has **no corporate routes**.
- **Build:** propose routes `/`, `/retailers`, `/vendors`, `/how`, `/pilot-ahvaz`, `/about`, `/contact`, `/legal` as `PROPOSED` in matrix with source = screen IDs only; record here.
- **Status:** GAP → screens implemented as static marketing under proposed routes; mark route source `PROPOSED-G006`.

## G-007 — Admin dedicated screen family underspecified (GAP)

- Spec 22 folds admin into O-10; route map has `/admin/users`, `/admin/orgs` with **no API source** (not in 50-endpoint or REAL list except audit/exceptions).
- **Build:** implement O-10 admin/context using REAL `/admin/audit-logs` + `/admin/exceptions/dashboard`; users/orgs screens = stub list UI without fake CRUD success → **GAP** rows.
- **Status:** GAP

## G-008 — No HTTP for pilot analytics O-09 (GAP)

- No analytics endpoints in inventory.
- **Build:** screen with empty/loading + explicit “data unavailable” or mock aggregate **without** inventing metrics API paths; prefer GAP UI shell.
- **Status:** GAP

## G-009 — Vendor customers V-09 list API missing (GAP)

- No `GET /customers` in inventory or routes.
- **Build:** stub + GAP; optional derive from retailer-facing orders only if documented (not documented → no derive).
- **Status:** GAP

## G-010 — Staff/access management V-11 / permission APIs (GAP)

- No membership admin HTTP beyond profile/membership self-serve.
- **Build:** read-only stub or GAP; no fake invite success.
- **Status:** GAP

## G-011 — Admin broadcasts / SLA overrides / category admin (CONTRACT)

- Contract-only endpoints; mock allowed with same contract if screens need them in Phase 2 Ops.
- **Status:** GAP until mock or backend HTTP

## G-012 — Basket GET list not in routes (GAP)

- Only POST create/items/preview; no GET basket.
- Screens that reload basket need client persistence **or** GAP; checkout uses allocation-preview + POST orders.
- **Status:** GAP (client basket cache is presentation, not business rule)

## G-013 — Returns list all-orders (GAP)

- Only `GET /orders/{order_id}/returns` — no global returns list.
- R-11 entry via order → returns; global RMA queue for ops may need GAP.
- **Status:** GAP for global list

## G-014 — Design contradictions register (PROPOSED / multi)

Prior research noted: brand blue vs tokens, type scale variants, radius, motion bands, density labels, WCAG version wording, Latin fallback font, breakpoints, focus ring details, golden-screen set.
- **Resolution:** doc 56 (Precision Commerce) wins for visual tokens; motion bands 120–160 / 160–240 / 200–280 / ≤400ms; WCAG 2.2 where doc 21/22 adopt it.
- Anything still undefined at implement time → new `G-0xx` + `PROPOSED` token marked in code.
- **Status:** PROPOSED (rolling)

## G-015 — OP-06 / OP-09 missing from Master Tree §9 listing (CONFLICT)

- Spec 22 has O-06, O-09; Master Tree tree listing gaps numbering.
- **Resolution:** implement per spec 22 (higher for screen detail after decisions); tree is navigation aid.
- **Status:** CONFLICT (resolved for build)

## G-016 — Phase C dead routes (historical)

- `/admin/users`, `/admin/orgs`, `/ops/finance`, `/ops/reconciliation` were nav-only.
- **Build:** only routes in SCREEN_MATRIX with sources; no dead links.

## G-017 — Backend HTTP coverage 21/50 at inventory snapshot (BLOCKED_EXTERNAL for non-mock)

- Many CONTRACT endpoints not yet on FastAPI at Stage 07 snapshot; research-hardening added many REAL routes (orders list, support, field, etc.) beyond that snapshot.
- **Build:** prefer REAL map in API_MAP §3; remaining CONTRACT → MOCK same-contract.
- **Status:** BLOCKED_EXTERNAL for true e2e against missing HTTP; not a stop — continue with mocks.

## G-018 — Android readiness RED in design audit 60 (BLOCKED_EXTERNAL sequencing)

- Dual-client mandated (D-026) but audit marks Android RED pre-build.
- **Build:** Phase 3 still required by contract; not a Phase 0 blocker.
- **Status:** informational

## G-019 — Working tree lacks many canonical files (CONFLICT — tooling)

- Docs on `origin/product-architecture-evolution-2026-09-20` / research-hardening; working tree `main` has partial 50/56 staged.
- **Resolution:** `git show <ref>:<path>` for reads (§2.8); do not switch branches unless necessary.
- **Status:** CONFLICT (tooling)

## G-020 — Corporate `PUBLIC_ANON` not a backend role (GAP — expected)

- Marketing screens need no auth; no API required for C-01…08 static content.
- **Status:** GAP (by design — static)

## G-021 — No GET list for partial-acceptance proposals (GAP)

- **Sources:** `orders.py` has POST create + approve/decline only; no `GET .../partial-acceptance-proposals`.
- **Build:** R-09C derives open proposals from `GET /orders/{id}/timeline` `event_data.proposal_id` on `ORDER_PARTIAL_ACCEPTANCE_PROPOSED`, closed on later APPROVED/DECLINED events. If backend later adds a list GET, switch to it.
- **Status:** GAP (documented workaround; no invented endpoint)

## G-022 — Delivery OTP schema vs D-018 (CONFLICT)

- **Sources:** `DeliveryConfirmRequest.otp_code` pattern was `^\d{6}$` vs **D-018** 4-digit OTP (`OTP_CODE_LENGTH = 4`).
- **Resolution:** **RESOLVED (2026-09-23).** Backend aligned end-to-end: schema pattern `^\d{4}$`; `fulfillment_service.dispatch_order` generates via `OTP_CODE_LENGTH` and **persists** `delivery_otp` (was generated-but-not-saved); web R-09E OTP input `maxLength={4}`; POD tests use 4-digit codes. Migration `030` column stays `VARCHAR(6)` for historical rows; comment updated to D-018 4-digit.
- **Status:** RESOLVED

---

## How to add

```
## G-0xx — Title (TYPE)
- Sources: …
- Resolution / Build action: …
- Status: …
```

Update SCREEN_MATRIX status + API_MAP when an entry changes.

## Phase 3 / live-e2e execution notes — 2026-09-23

- Mobile retailer/vendor/ops foundations are implemented but remain `IMPLEMENTED` until mobile CI + three QA cycles provide evidence; do not promote to `VERIFIED` yet.
- D-028 barcode matching remains contract-only because the authoritative request/response schema and runtime camera adapter are not yet available; no invented payload or success behavior is allowed.
- Mobile Night theme tokens exist, but screen-by-screen visual verification is still pending; no claim of full visual parity is made.
- Live basket → allocation → checkout e2e remains pending in the local environment because the current catalog seed/search path and orderability criteria still need live verification. This is an execution task, not a reason to stop other work.


## G-023 — Field assisted catalog empty-query request (RESOLVED)

- Finding: F-03 AssistedOrderScreen previously issued GET /api/v1/catalog/search?limit=40 when the query was empty, while the authoritative route requires q with min_length=1.
- Source remediation (2026-09-24): Mobile now short-circuits an empty query locally and never calls the route without q; the explicit search action reports that the query is required.
- Status: RESOLVED — post-remediation device retest PASS (2026-09-24).

## G-024 — Field assisted catalog product field mapping (RESOLVED)

- Finding: F-03 catalog rows could fall back to — because the API canonical fields are canonical_name_fa and master_sku, while the mobile adapter primarily expected name / sku.
- Source remediation (2026-09-24): Mobile now prefers canonical_name_fa for display and master_sku for SKU fallback, while retaining compatibility fallbacks.
- Status: RESOLVED — post-remediation device retest PASS (2026-09-24).

## G-025 — Mobile Night theme runtime wiring (RESOLVED)

- Finding: Night palette existed but runtime styles were created statically and there was no user-facing Light/Night control; changing system UI mode therefore did not update the rendered app.
- Source remediation (2026-09-24): Added centralized runtime theme context, dynamic themed style factories for mobile screens/shared components, system-aware initial mode, and explicit Light/Night controls in Account. app.json now uses automatic interface style.
- Status: RESOLVED for runtime wiring — post-remediation Night-theme device retest PASS (2026-09-24); broader screen-by-screen visual coverage remains a separate QA scope if required.

## G-026 — Mobile phone input vs E.164 contract (RESOLVED)

- Finding: Authentication storage/test fixtures use E.164 (+...), while the mobile login UI accepted/displayed local 09... input without normalization.
- Source remediation (2026-09-24): Mobile normalizes Iranian local numbers to E.164 before auth and backend OTP request/verification schemas now enforce the E.164 pattern.
- Status: RESOLVED — local authentication/device retest PASS (2026-09-24).

## G-029 — Web token persistence uses localStorage (SECURITY GAP — SOURCE REMEDIATED)

- **Historical source finding (2026-09-24):** the web auth store persisted access/refresh bearer credentials in browser localStorage.
- **Current source remediation:** mvp/apps/web/src/lib/auth/store.ts now persists profile metadata only; accessToken remains in memory. Browser refresh uses the server-managed `pol_refresh` HttpOnly/Secure/SameSite cookie.
- **Transport hardening:** web verify/refresh endpoints do not expose the refresh credential in JSON when the cookie-backed flow is used; refresh tests assert this behavior.
- **Residual verification:** browser-runtime/XSS and production-cookie deployment evidence remain separate release evidence.
- **Status:** SOURCE REMEDIATED / CI VERIFICATION IN PROGRESS.

## G-030 — Browser-to-API CORS policy was not previously explicit (SOURCE REMEDIATED)

- **Finding:** web API client uses a separate API base origin while FastAPI had no explicit CORS policy in the audited transport source.
- **Source remediation (2026-09-24):** FastAPI now applies environment-scoped CORS with explicit local development origins, requires POL_CORS_ORIGINS in production, forbids wildcard production CORS, and has a transport test for allowed/blocked origins.
- **Status:** SOURCE REMEDIATED / CI VERIFICATION REQUIRED.
