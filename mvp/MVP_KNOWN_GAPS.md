# POL MVP — KNOWN GAPS / CONFLICTS / BLOCKED

**Rule (Master Instruction §3):** higher authority wins; log here; unresolved = screen status `GAP` + minimal stub; do not guess; do not stop build unless critical dependency.

**Status values in this file:** `RESOLVED` | `CONFLICT` | `GAP` | `BLOCKED_EXTERNAL` | `PROPOSED`

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
- **Evidence:** current notification HTTP tests pass for projection, tenant-scoped read, and idempotent read-all; earlier verification CI green is historical evidence; fresh post-remediation CI is currently blocked before useful step execution.
- **Status:** RESOLVED for source + automated CI evidence.

## G-006 — Corporate routes absent from legacy route map (RESOLVED)

- Spec 22 C-01…C-08 + Master Tree CP-* are implemented as public static pages.
- Current canonical paths are `/`, `/retailers`, `/vendors`, `/how`, `/pilot`, `/about`, `/contact`, `/legal`, matching the current `MVP_SCREEN_MATRIX.md`.
- **Status:** RESOLVED. The older route-map omission is historical documentation drift, not a runtime gap.

## G-007 — Admin users / organizations screen family (RESOLVED)

Admin user and organization list/status APIs now exist behind the canonical administrative boundary, with audit logging and session invalidation on deactivation/suspension. Web screens are connected to live data.


## G-008 — Pilot analytics O-09 HTTP (RESOLVED)

Authenticated /api/v1/ops/analytics and /api/v1/ops/analytics/weekly routes now expose the existing KPI calculation service through POLApplicationBoundary. The /ops/analytics screen consumes the live API; KPI source-of-truth remains scripts/pilot_kpis.py + scripts/analytics_lineage.py.


## G-009 — Vendor customers V-09 list API (RESOLVED)

/api/v1/vendors/customers now returns tenant-scoped retailers derived from real vendor orders, with search and pagination. /vendor/customers consumes the API and does not fabricate rows.


## G-010 — Staff/access management V-11 / permission APIs (RESOLVED)

Vendor staff list/invite/update is implemented with owner-only mutations, tenant scoping, last-owner protection and audit logs. /api/v1/ops/permissions exposes the canonical RBAC catalog, and vendor staff UI is live.


## G-011 — Admin broadcasts / SLA overrides / category admin (RESOLVED)

- `POST /admin/sla-overrides`, `POST/PATCH /admin/categories`, and `POST /admin/broadcasts` + dispatch are REAL and audited.
- **Status:** RESOLVED.

## G-012 — Basket current GET (RESOLVED)

- `GET /api/v1/baskets/current` exists and the application boundary owns current-basket retrieval.
- **Status:** RESOLVED

## G-013 — Returns list all-orders (RESOLVED)

Ops now has /api/v1/ops/returns for a tenant-independent operational workbench over all returns, and /ops/rma consumes it directly.


## G-014 — Design contradictions register (RESOLVED)

Prior research noted: brand blue vs tokens, type scale variants, radius, motion bands, density labels, WCAG version wording, Latin fallback font, breakpoints, focus ring details, golden-screen set.
- **Resolution:** doc 56 (Precision Commerce) wins for visual tokens; motion bands 120–160 / 160–240 / 200–280 / ≤400ms; WCAG 2.2 where doc 21/22 adopt it.
- Anything still undefined at implement time → new `G-0xx` + `PROPOSED` token marked in code.
- **Status:** RESOLVED. The canonical visual design system defines the active token hierarchy, typography, spacing, radius, motion, density, WCAG reference, RTL, responsive and golden-screen requirements. New material changes must be registered as explicit decisions rather than treated as inherited contradictions.

## G-015 — OP-06 / OP-09 missing from Master Tree §9 listing (CONFLICT — RESOLVED)

- Spec 22 has O-06, O-09; Master Tree tree listing gaps numbering.
- **Resolution:** implement per spec 22 (higher for screen detail after decisions); tree is navigation aid.
- **Status:** RESOLVED for current build/source mappings; historical section numbering remains evidence only.

## G-016 — Phase C dead routes (HISTORICAL — RESOLVED)

- `/admin/users`, `/admin/orgs`, `/ops/finance`, `/ops/reconciliation` were nav-only.
- **Build:** only routes in SCREEN_MATRIX with sources; no dead links.

## G-017 — Backend HTTP coverage 21/50 at inventory snapshot (HISTORICAL — RESOLVED)

- Many CONTRACT endpoints not yet on FastAPI at Stage 07 snapshot; research-hardening added many REAL routes (orders list, support, field, etc.) beyond that snapshot.
- **Build:** prefer REAL map in API_MAP §3; remaining CONTRACT → MOCK same-contract.
- **Status:** RESOLVED on the current remediation branch: canonical ledger is now 50/50 HTTP_IMPLEMENTED; runtime CI evidence remains the release gate.

## G-018 — Android readiness RED in design audit 60 (HISTORICAL)

- Dual-client mandated (D-026) but audit marks Android RED pre-build.
- **Build:** Phase 3 still required by contract; not a Phase 0 blocker.
- **Status:** HISTORICAL / RESOLVED. Mobile implementation and prior local/device verification exist on the current project line; final CI runner evidence remains separate.

## G-019 — Working tree lacks many canonical files (HISTORICAL — RESOLVED)

- Docs on `origin/product-architecture-evolution-2026-09-20` / research-hardening; working tree `main` has partial 50/56 staged.
- **Resolution:** `git show <ref>:<path>` for reads (§2.8); do not switch branches unless necessary.
- **Status:** HISTORICAL / RESOLVED. The active source-of-truth references now point only to files present on the current remediation branch; missing historical documents are not treated as active authority.

## G-020 — Corporate `PUBLIC_ANON` not a backend role (RESOLVED — BY DESIGN)

- Marketing screens need no auth; no API required for C-01…08 static content.
- **Status:** RESOLVED (by design). Corporate surfaces are static public pages and intentionally do not require an authenticated backend role.

## G-021 — Partial-acceptance proposal list (RESOLVED)

- `GET /api/v1/orders/{order_id}/partial-acceptance-proposals` now returns the canonical proposal rows and item reductions, with vendor/retailer tenant scoping.
- **Status:** RESOLVED

## G-022 — Delivery OTP schema vs D-018 (RESOLVED)

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

- Historical mobile CI cycles remain evidence, but the current remediation branch must not inherit their green certification automatically because fresh GitHub runs currently fail before useful step execution.
- D-028 barcode matching is implemented at the canonical API boundary, with legacy and extended request compatibility; camera/device transport remains a client/runtime concern.
- Mobile Night theme verification and live checkout/idempotency are now recorded as LOCAL-01…04 PASS in the execution tracker; deployment/runtime evidence remains separate.
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

## G-029 — Web token persistence uses localStorage (SECURITY GAP — RESOLVED)

- **Historical source finding (2026-09-24):** the web auth store persisted access/refresh bearer credentials in browser localStorage.
- **Current source remediation:** mvp/apps/web/src/lib/auth/store.ts now persists profile metadata only; accessToken remains in memory. Browser refresh uses the server-managed `pol_refresh` HttpOnly/Secure/SameSite cookie.
- **Transport hardening:** web verify/refresh endpoints do not expose the refresh credential in JSON when the cookie-backed flow is used; refresh tests assert this behavior.
- **Residual verification:** browser-runtime/XSS and production-cookie deployment evidence remain separate release evidence.
- **Status:** SOURCE REMEDIATED; final release gate is CI/runtime evidence.

## G-030 — Browser-to-API CORS policy was not previously explicit (RESOLVED)

- **Finding:** web API client uses a separate API base origin while FastAPI had no explicit CORS policy in the audited transport source.
- **Source remediation (2026-09-24):** FastAPI now applies environment-scoped CORS with explicit local development origins, requires POL_CORS_ORIGINS in production, forbids wildcard production CORS, and has a transport test for allowed/blocked origins.
- **Status:** SOURCE REMEDIATED; final release gate is CI/runtime evidence.

## G-031 — Duplicate barcode route / schema collision (RESOLVED — 2026-09-25)

- Finding: two route modules registered the same POST /api/v1/products/match-barcode path with incompatible request models.
- Resolution: one canonical route now serves both legacy and extended request shapes; duplicate registration was removed; route uniqueness regression coverage was added.
- Status: RESOLVED in source; fresh CI certification remains separate.

## G-032 — Direct candidate idempotency / notification targeting (RESOLVED — 2026-09-25)

- Finding: direct candidate creation could create a new candidate and overwrite an existing vendor-SKU association, and candidate-created outbox events lacked recipient targets.
- Resolution: advisory-lock serialization, existing-association replay, rejection protection, tenant-aware authorization, targeted outbox fields and dedupe key, plus HTTP regression coverage were added.
- Status: RESOLVED in source; fresh CI certification remains separate.
