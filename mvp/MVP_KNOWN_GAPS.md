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
- **Evidence:** HTTP notification tests cover listing, unread count, deep links, tenant-scoped mark-read, idempotent mark-all-read, and read-state projection. Historical CI evidence exists for an earlier verified commit; fresh remediation CI is currently blocked before useful job-step execution.
- **Status:** RESOLVED for source + historical automated evidence; fresh post-remediation CI remains blocked.

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

Vendor staff list/invite/update is implemented with owner-only mutations, tenant scoping, last-owner protection and audit logs. D-026/VD-15 is now source-implemented with tenant-scoped delegated grant/revoke, effective-permission evaluation, privilege ceiling, append-only permission audit, and Web + Android Permission Editor surfaces.


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

## G-033 — Deterministic OTP outside explicit test environment (SECURITY GAP — REMEDIATED)

- **Finding (2026-09-25):** AuthService.request_otp previously selected deterministic `1234` for every non-production environment, so an unset/unknown environment could silently inherit the test credential.
- **Resolution:** deterministic OTP is now allowed only when `ENVIRONMENT=test` and production-mode detection is false. All other environments use cryptographically random 4-digit OTPs. The `test_code` response field is exposed only in the explicit test environment.
- **Regression proof:** scripts/test_auth_contract.py::test_static_otp_is_strictly_test_only covers explicit test mode plus development, unknown and unset environment cases.
- **CI status:** source and test remediation committed; fresh GitHub Actions certification remains blocked by the current runner/check execution failure before useful job steps.
- **Status:** SOURCE REMEDIATED / CI PENDING

## G-034 — Delivery exception notification routing (RESOLVED — 2026-09-25)

- Finding: delivery exception outbox events were emitted without explicit user/organization targets, while the canonical integration worker requires explicit routing.
- Resolution: report events route to active vendor members, resolved events to active retailer members, escalation events to active operator/admin members; per-recipient dedupe keys and INBOX channel hints are persisted.
- Additional hardening: report/get/list/resolve/escalate paths now enforce tenant and actor boundaries at the service layer.
- Notification templates added in migration 042.
- Status: RESOLVED in source; fresh CI certification remains separate.

## G-035 — Fulfillment lifecycle notification template coverage (RESOLVED — 2026-09-25)

- Finding: lifecycle events emitted by fulfillment/timeout workers included PREPARING, READY, DISPATCHED, DELIVERY_OTP_GENERATED, DELIVERED and CANCELLED, but the notification template registry did not cover all emitted events.
- Resolution: migration 045 adds active INBOX templates for all six events. ORDER_DELIVERED and ORDER_CANCELLED now route to both commercial parties where the canonical notification matrix requires it.
- Status: RESOLVED in source; fresh CI certification remains separate.
## G-036 — Barcode-only candidate concurrency (RESOLVED — 2026-09-25)

- Finding: application-level replay checks did not by themselves guarantee uniqueness when two barcode-only candidate submissions raced concurrently.
- Resolution: migration 046 adds a partial unique index on (vendor_id, barcode) for PENDING_REVIEW candidates; the application insert uses the same conflict target and re-reads the canonical candidate on conflict.
- Status: RESOLVED in source; fresh CI certification remains separate.
## G-037 — Notification worker inactive-user delivery (RESOLVED — 2026-09-25)

- Finding: canonical integration validated active organization membership but did not also require users.is_active.
- Resolution: worker now verifies active user + active membership + active organization; membership-isolation regression coverage adds an inactive-user case.
- Status: RESOLVED in source; fresh CI certification remains separate.
## G-038 — Duplicate payment verification HTTP route (RESOLVED — 2026-09-25)

- Finding: POST /api/v1/orders/{order_id}/payments/verify was registered twice in the same router.
- Resolution: retained the canonical implementation and removed the duplicate registration; route uniqueness regression now covers this class automatically.
- Status: RESOLVED in source; fresh CI certification remains separate.
## G-039 — Boundary role resolution trusted inactive users/orgs (RESOLVED — 2026-09-25)

- Finding: the central application-boundary role resolver accepted ACTIVE memberships without independently checking users.is_active and organizations.status.
- Resolution: role resolution now requires active user, active membership and active organization; batch contract regression covers inactive-user and suspended-organization contexts.
- Status: RESOLVED in source; fresh CI certification remains separate.
## G-040 — Payment evidence tenant isolation and retry idempotency (RESOLVED — 2026-09-25)

- Finding: evidence reads were order-ID based without explicit tenant authorization, and duplicate submissions using the globally unique external reference could surface as a raw database conflict.
- Resolution: reads require active retailer/vendor tenant membership; submissions require an active user; repeated external references return the existing evidence for the same payment with idempotent_replay=true, while cross-payment reuse is rejected.
- Regression coverage: wrong-tenant read plus same-reference replay HTTP tests.
- Status: RESOLVED in source; fresh CI certification remains separate.


## G-041 — Bearer/refresh token validity after principal deactivation (SECURITY GAP — REMEDIATED — 2026-09-26)

- **Finding:** access-token validation trusted an ACTIVE session + ACTIVE membership without independently checking `users.is_active` and `organizations.status`; refresh-token validation had the same omission.
- **Resolution:** `validate_access_token` now requires active user + active organization + active membership. `AuthService.refresh_access_token` enforces the same principal checks before issuing a new access token or rotating the refresh token.
- **Regression proof:** `scripts/test_auth_contract.py` now covers inactive-user and inactive-organization rejection for both bearer access tokens and refresh tokens.
- **Status:** SOURCE REMEDIATED / FRESH CI PENDING


## G-042 — Payment evidence / verification role drift (SECURITY GAP — REMEDIATED — 2026-09-26)

- **Finding:** payment evidence submission previously allowed `RETAILER_STAFF`; payment verification previously allowed `VENDOR_STAFF`, exceeding the current payment responsibility boundary.
- **Resolution:** retailer-side payment evidence now requires `RETAILER_OWNER`; verification now requires `VENDOR_OWNER` or authorized ops/admin roles. Vendor-side evidence collection remains available for the evidence types already defined by the API contract.
- **Regression proof:** `scripts/test_http_payment_evidence.py` adds explicit Retailer Staff submission rejection and Vendor Staff verification rejection.
- **Status:** SOURCE REMEDIATED / FRESH CI PENDING


## G-043 — Presigned media upload target retargeting (SECURITY GAP — REMEDIATED — 2026-09-26)

- **Finding:** the presign request authorized one target, but confirm-upload accepted a caller-supplied target independently; an upload could therefore be rebound to another object accessible to the same actor.
- **Resolution:** migration `048_bind_media_upload_target.sql` binds `upload_target_type` + `upload_target_id` to the presigned asset. Confirmation rejects any target mismatch before storage finalization.
- **Regression proof:** `scripts/test_media_service.py::test_presigned_upload_target_cannot_be_retargeted` plus schema assertions for migration 048.
- **Status:** SOURCE REMEDIATED / FRESH CI PENDING


## G-044 — Authentication OTP purpose / organization binding (SECURITY GAP — REMEDIATED — 2026-09-26)

- **Finding:** authentication OTP verification selected the latest pending challenge by phone without restricting its purpose to LOGIN/REGISTER, and it did not require the selected organization itself to be ACTIVE.
- **Resolution:** auth verification now accepts only LOGIN/REGISTER challenges and requires an ACTIVE user, ACTIVE membership, and ACTIVE organization before session creation.
- **Regression proof:** `scripts/test_auth_contract.py` covers suspended-organization rejection and prevents ORDER_CONFIRMATION challenges from being consumed by authentication verification.
- **Status:** SOURCE REMEDIATED / FRESH CI PENDING


## G-045 — Organization switch valid-target regression (SECURITY / CORRECTNESS — REMEDIATED — 2026-09-26)

- **Finding:** `AuthService.switch_organization` performed an additional `cur.fetchone()` after validating the target membership. No query preceded that fetch, so the cursor returned no row and every otherwise-valid organization switch was rejected.
- **Resolution:** removed the stray cursor fetch. Target user/session ownership, session state, target membership, user state and organization state remain explicitly validated before the session context is updated.
- **Regression proof:** `scripts/test_auth_contract.py::test_p0_switch_organization_valid_target_succeeds` now verifies successful tenant switching, persisted active organization, and the newly issued JWT role/org/session claims.
- **Status:** SOURCE REMEDIATED / FRESH CI PENDING


## G-046 — Retailer staff commerce-command overreach (SECURITY / RBAC — REMEDIATED — 2026-09-26)

- **Finding:** basket creation/modification/allocation and checkout were reachable from an active RETAILER_STAFF membership even though the approved role matrix reserves basket creation/checkout authority to RETAILER_OWNER (with field-assisted execution handled separately).
- **Resolution:** canonical basket/allocation mutations now explicitly require RETAILER_OWNER; checkout-from-allocation-plan now resolves only an active RETAILER_OWNER membership.
- **Regression proof:** scripts/test_basket_allocation_application.py covers staff rejection for basket create/add/allocation; checkout source authorization is owner-only.
- **Status:** SOURCE REMEDIATED / FRESH CI PENDING

## G-047 — Retailer staff partial-acceptance decision overreach (SECURITY / RBAC — REMEDIATED — 2026-09-26)

- **Finding:** partial-acceptance approve/decline queries accepted both RETAILER_OWNER and RETAILER_STAFF, allowing a staff member to make a quantity/financial order decision.
- **Resolution:** canonical partial-acceptance approve/decline now require an active RETAILER_OWNER; vendor-side proposal creation remains governed by the vendor acceptance permission.
- **Regression proof:** scripts/test_partial_acceptance.py::test_retailer_staff_cannot_decide_partial_acceptance verifies the decision is rejected and the proposal remains PENDING.
- **Status:** SOURCE REMEDIATED / FRESH CI PENDING

## G-048 — Vendor staff order-acceptance permission drift (SECURITY / RBAC — REMEDIATED — 2026-09-26)

- **Finding:** VENDOR_STAFF still carried the generic order.accept permission even though the approved role matrix assigns order acceptance/rejection to VENDOR_OWNER.
- **Resolution:** order.accept was removed from the VENDOR_STAFF baseline permission set; vendor owner retains it.
- **Regression proof:** scripts/test_delegated_permissions.py::test_vendor_staff_role_does_not_receive_order_accept_permission.
- **Status:** SOURCE REMEDIATED / FRESH CI PENDING


## G-049 — Retailer staff formal-dispute opening overreach (SECURITY / RBAC — REMEDIATED — 2026-09-26)

- **Finding:** the formal dispute-open path enforced retailer tenancy but did not independently restrict the actor to RETAILER_OWNER, allowing a retailer staff membership to invoke the client-facing dispute command.
- **Resolution:** both the HTTP route and the application boundary now require an active RETAILER_OWNER membership in an active retailer organization.
- **Regression proof:** scripts/test_http_returns_disputes.py::TestDisputeOpen::test_retailer_staff_cannot_open_formal_dispute.
- **Status:** SOURCE REMEDIATED / FRESH CI PENDING


## G-050 — Expo SDK 57 CI Node-runtime mismatch (TOOLCHAIN — REMEDIATED — 2026-09-26)

- **Finding:** the mobile verification workflow used Node 20 while the repository's Expo SDK 57 stack requires Node 22.13.x or newer.
- **Resolution:** mobile CI now uses Node 22.23.1; mvp/package.json and the lockfile declare Node >=22.13.0.
- **Evidence:** Expo's current SDK reference lists 22.13.x as the minimum Node.js version for SDK 57.
- **Status:** SOURCE REMEDIATED / FRESH CI EXECUTION BLOCKED BEFORE STEPS


## G-051 — Delegated permission could reintroduce owner-only capabilities (SECURITY / RBAC — REMEDIATED — 2026-09-26)

- **Finding:** removing an owner-only capability from a staff role's baseline permission set did not by itself prevent an owner from re-granting that capability through delegated permissions.
- **Resolution:** role-aware delegation ceilings now explicitly block owner-only capabilities such as VENDOR_STAFF order acceptance and membership management.
- **Regression proof:** scripts/test_delegated_permissions.py::test_owner_only_permissions_cannot_be_delegated_to_vendor_staff.
- **Status:** SOURCE REMEDIATED / FRESH CI PENDING


## G-052 — Delegated Permission Ceiling Must Hold at Evaluation Time
**Class:** Security / RBAC / Defense-in-Depth  
**Finding:** Earlier hardening blocked new grants of owner-only permissions to restricted roles, but a legacy or directly seeded GRANTED row could still be added to effective_permissions() and become active.  
**Remediation:** Effective-permission evaluation now filters delegated grants through the canonical role delegation-deny ceiling and ignores unknown/non-canonical delegated permission keys. The membership-management response exposes the same target-role-aware delegation ceiling.  
**Regression:** `scripts/test_delegated_permissions.py` covers both the direct legacy-grant path and the exposed delegatable-permission catalog.  
**Status:** **SOURCE REMEDIATED / FRESH CI PENDING**

## G-053 — Product Media Authorization Must Be Vendor-Product Scoped
**Class:** Security / Multi-Tenancy / Media Provenance  
**Finding:** Product media authorization previously checked only that the actor belonged to a vendor/operator organization. A vendor member could therefore attempt to attach media to an unrelated Master Product outside that vendor's active product relationship. Operator uploads also inherited VENDOR_UPLOADED provenance.  
**Remediation:** Vendor product-media authorization now requires an active `vendor_products` relationship for the target Master Product in the actor's organization. Operator-authorized product media is recorded with `POL_OWNED` provenance; canonical OPS and legacy aliases are accepted consistently.  
**Regression:** `scripts/test_media_service.py` covers vendor ownership, unrelated-tenant rejection and operator provenance.  
**Status:** **SOURCE REMEDIATED / FRESH CI PENDING**

## G-054 — Legacy In-Flight Media Uploads Must Fail Closed
**Class:** Security / Upload Integrity / Migration Safety  
**Finding:** Migration 048 introduced upload target binding, but pre-migration `UPLOADING` rows with a null target could otherwise reach confirmation because the runtime validator treated a missing binding as implicitly acceptable.  
**Remediation:** Confirm-upload now rejects any `UPLOADING` asset without an immutable target binding. Migration 048 invalidates legacy unbound `UPLOADING` rows as `DELETED` and adds a PostgreSQL CHECK invariant requiring both target fields for every in-flight upload.  
**Regression:** `scripts/test_media_service.py` covers missing-binding rejection.  
**Status:** **SOURCE REMEDIATED / FRESH CI PENDING**


## G-055 — Field Task HTTP/Boundary Contract Alignment
**Class:** Runtime Contract / API Integration / Field Operations  
**Finding:** `/api/v1/field/tasks` passed `retailer_id`/`vendor_id`, while the application boundary previously accepted only `target_organization_id`, creating a transport-to-domain signature mismatch.  
**Remediation:** `field_task_create()` now accepts the route contract, resolves retailer/vendor targets to their active organization, rejects ambiguous target combinations, and validates the target organization and assigned user state before insertion.  
**Regression:** `scripts/test_http_field_tasks.py` now creates a real retailer target and verifies the resolved target organization through the HTTP endpoint.  
**Status:** **SOURCE REMEDIATED / FRESH CI PENDING**

## G-056 — Support Case Related Order Must Be Tenant-Bound
**Class:** Security / Multi-Tenancy / Referential Integrity  
**Finding:** Support case creation checked the active support organization but did not independently verify that an optional `related_order_id` belonged to that same retailer/vendor organization. A guessed order UUID could therefore be persisted as a cross-tenant support reference.  
**Remediation:** `CanonicalSupportService.create_case()` now verifies active membership and requires the related order to resolve through its retailer or vendor organization to the active support tenant before insertion.  
**Regression:** `scripts/test_http_support.py` creates an order under another retailer organization and verifies support creation is rejected with HTTP 403.  
**Status:** **SOURCE REMEDIATED / FRESH CI PENDING**


## G-057 — HTTP Referral Redemption Must Materialize Attribution
**Class:** Functional Correctness / Referral Lifecycle / API-Domain Contract  
**Finding:** The HTTP `POST /api/v1/referrals/{referral_id}/redeem` boundary previously treated redemption as a vendor-side counter increment and did not execute the canonical retailer first-touch attribution flow required by D-016.  
**Remediation:** The boundary now resolves the active retailer from the authenticated organization, loads the canonical referral independently of vendor tenant, and delegates redemption to `VendorReferralService.redeem_referral()` using a deterministic HTTP idempotency key. This persists `vendor_referral_attributions` and emits the canonical analytics outbox event while keeping retailer first-touch uniqueness.  
**Regression:** New `scripts/test_http_referrals.py` verifies first redemption creates an attribution and a repeated HTTP redemption replays without incrementing the quota twice.  
**Status:** **SOURCE REMEDIATED / FRESH CI PENDING**
