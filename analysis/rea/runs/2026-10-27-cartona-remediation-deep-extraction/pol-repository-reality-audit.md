# POL Repository Reality Audit

**Repo:** `C:\Star\pol\2.4` — branch `ui/visual-qa-screen-completion-20261025`, commit `e68d2e45`
**Audit date:** 2026-10-26. Read-only audit; no files modified.
**Evidence tags:** `[CODE_VERIFIED]` (read in source), `[TEST_VERIFIED]` (test file exists asserting it), `[DOC_ONLY]` (documented, not found/verified in code), `[NOT_FOUND]` (searched, absent).

---

## 1. Backend Reality

### 1.1 What the backend actually is

The runtime backend is a **FastAPI service at `scripts/api/`** (NOT under `mvp/`). Entrypoint: `C:\Star\pol\2.4\scripts\api\main.py` (`create_app()`, line 78). Architecture is intentionally thin: HTTP → auth/session → `ApplicationContext` → `POLApplicationBoundary` (`scripts/application_boundary.py`, ~5,400+ lines, holds all business logic) → PostgreSQL. All 77 SQL migrations live in `C:\Star\pol\2.4\migrations\`. `mvp/apps/web` is a **Next.js frontend only** (no `app/api` server routes — `find mvp/apps/web/src/app -name route.ts` returns nothing); the `frontend/` dir at repo root contains only `node_modules` (dead). `db.sqlite3` at repo root is **0 bytes** (dead artifact) `[CODE_VERIFIED]`. Deployment: `docker-compose.vps.yml` (postgres + migrate + web/api + worker via `python -m scripts.worker_runtime` at line 97 + nginx) and `deploy/vps_deploy.sh`.

### 1.2 REAL route registrations (method + path), from `scripts/api/routes/*.py` decorators, all mounted with prefix `/api/v1` at `scripts/api/main.py:149-185`

All paths verified by reading decorator lines. Counts: ~120 real endpoints.

**Auth — `scripts/api/routes/auth.py` (`/auth`)**
- POST `/auth/request-otp` (:38), POST `/auth/verify-otp` (:56), POST `/auth/refresh` (:71), POST `/auth/switch-organization` (:86), DELETE `/auth/sessions/current` (:100), DELETE `/auth/sessions/{session_id}` (:113), POST `/auth/logout-all` (:123) `[CODE_VERIFIED]`

**Profile/Membership — `profile.py`**: GET/PUT `/profile` (:15,:30), GET `/profile/completion` (:20), GET `/profile/context` (:25), GET/PUT `/membership/profile` (:40,:46)

**Privacy — `privacy.py`**: POST `/privacy/deletion` (:25). NOTE: **`POST /privacy/export` is NOT registered** (doc-claimed in `mvp/MVP_API_MAP.md:77`) — see 1.4.

**Baskets — `baskets.py`**: POST `/baskets` (:16), GET `/baskets/current` (:21), POST `/baskets/{id}/items` (:25), POST `/baskets/{id}/allocation-preview` (:42)

**Catalog (auth'd) — `catalog.py`**: GET `/catalog/search` (:14), `/catalog/categories`, `/catalog/products/{id}`, `.../vendors`, `.../compare-prices`, `.../compare-inventory` (:30-59)
**Public catalog — `products.py`** GET `/products/search` (:15); `categories.py` GET `/categories` (:12); `catalog_matching.py` POST `/products/match-barcode` (:30), GET `/catalog/barcode/lookup` (:16); `catalog_identifiers.py` POST `/product-candidates` (:15); `catalog_search.py` GET `/search` (:13)

**Vendor catalog — `vendor_catalog.py`** (`/catalog/vendors`): GET/POST `/products` (:22,:27), PATCH `/products/{id}` (:47), GET/POST `/products/{id}/prices` (:66,:82), GET `.../prices/current` (:74), GET/PATCH `/products/{id}/inventory` (:97,:105)

**Daily inventory — `daily_inventory.py`** (`/inventory/daily`): GET `/{confirmation_date}` (route at :14-25 area), POST `/{date}/confirm` (:25), POST `/{date}/confirm-with-changes` (:33)

**Orders — `orders.py`** (`/orders`, 541 lines — the largest route file):
POST `/orders` (checkout, :41), POST `/{id}/cancel` (:58), POST `/{id}/accept` (:69), POST `/{id}/reject` (:80), GET+POST `/{id}/partial-acceptance-proposals` (:96,:114), POST `/{id}/partial-acceptance-proposals/{proposal_id}/approve|decline` (:138,:153), GET `/orders` list (:173), GET `/{id}` (:185), GET `/{id}/items` (:195), GET `/{id}/timeline` (:205), GET `/group/{order_group_id}` (:215) + `/group/{id}/orders` (:225), POST `/{id}/preparing|ready` (:238,:249), POST `/{id}/dispatch` (:260), POST `/{id}/delivery/picked-up|in-transit|arrived|failed` (:288-318), POST `/{id}/deliver` (:330), GET `/{id}/delivery` (:363), GET `/{id}/delivery/proof` (:373), POST+GET `/{id}/delivery-exceptions` (:385,:401), GET/PATCH `/orders/delivery-exceptions/{id}` + `/resolve` + `/escalate` (:419-445), POST+GET `/{id}/payments/evidence` (:463,:502), POST `/{id}/payments/direct-transfer` (:483), POST `/{id}/payments/verify` (:512), POST `/{id}/payments/{payment_id}/verify` (:527)

**Returns — `returns.py`**: POST+GET `/orders/{id}/returns` (:28,:54), GET `/returns/{id}` (:64), POST `/returns/{id}/refund/approve` (:74), PATCH `/returns/{id}` (:89)
**Disputes — `disputes.py`**: POST+GET `/orders/{id}/disputes` (:24-36 area, :35), POST `/disputes/{id}/investigate` (:46), GET `/disputes/{id}` (:58), PATCH `/disputes/{id}/resolve` (:69), POST `/disputes/{id}/close` (:87)

**Support — `support.py`**: POST/GET `/support/cases` (:22,:38), GET `/{id}` (:45), GET+POST `/{id}/messages` (:55,:65), POST `/{id}/assign` (:79), PATCH `/{id}/status` (:92), PATCH `/{id}` (:107)

**Finance — `finance.py`**: GET `/invoices` + `/invoices/{id}` (:20,:31), GET `/orders/{id}/invoice` (:41), GET `/vendors/settlements` (:51), GET `/settlements/{id}` (:62), POST `/finance/refunds/issue` (:76), GET `/finance/refunds` + `/{refund_id}` (:94,:104), POST `/finance/refunds/{id}/approve|complete` (:113,:123)
**Reconciliation — `reconciliation.py`**: GET `/finance/reconciliation` + `/{case_id}` + PATCH `/{case_id}/resolve` (:17,:31,:41)

**Admin — `admin.py`**: GET `/admin/audit-logs` (:17), GET `/admin/exceptions/dashboard` (:28), POST `/admin/broadcasts` (:39), POST `/admin/broadcasts/{id}/dispatch` (:57), POST `/admin/categories` (:72), PATCH `/admin/categories/{id}` (:79)
**Management — `management.py`** (three routers): vendor_router `/vendors`: GET `/customers` (:31), GET `/staff` (:43), POST `/staff/invite` (:52), GET/POST `/staff/{id}/permissions` (:65,:75), POST `/staff/{id}/permissions/{key}/revoke` (:91), PATCH `/staff/{id}` (:108); admin_router `/admin`: GET `/users` (:123), PATCH `/users/{id}/status` (:135), POST `/sla-overrides` (:149), POST `/broadcasts`+`dispatch` (:163,:180), POST+PATCH `/categories` (:194,:209), GET+PATCH `/product-candidates` (:227,:245), GET `/organizations` (:265), PATCH `/organizations/{id}/status` (:280); ops_router `/ops`: GET `/permissions/audit` (:294), GET `/permissions` (:308), GET `/returns` (:313)
**Analytics — `analytics.py`**: GET `/ops/analytics` + `/weekly` (:15,:26)

**Notifications — `notifications.py`**: GET `/notifications` (mounted router), GET/PUT `/notifications/preferences` (in router), GET `/inbox/items` (:51), PATCH `/inbox/items/{id}/read` (:64), PATCH `/inbox/items/read-all` (:69)
**Field — `field.py`**: GET+POST `/field/tasks` (:29 area, :54), GET+PATCH `/field/tasks/{task_id}`
**Media — `media.py`**: POST `/media/presigned-url` (:19), POST `/media/resumable/init` (:42), POST `/media/resumable/complete` (:61), POST `/media/confirm-upload` (:80)
**Vendor storefront — `vendor_storefront.py`** (explicitly public, `context=None`, line 4 comment): GET `/storefront/vendors` (:21), GET `/storefront/vendors/{id}` (:48), GET `/{id}/products` (:60)
**Vendor inventory scan — `vendor_inventory.py`**: POST `/vendors/inventory/continuous-scan` (:19), POST `/vendors/inventory/publish` (:39)
**Ops health**: GET `/healthz`, GET `/readyz` (`main.py:132-147`)

### 1.3 Route registration collision (real defect candidate)

`admin.py` and `management.py` **both** register POST `/admin/broadcasts`, POST `/admin/broadcasts/{id}/dispatch`, POST/PATCH `/admin/categories*` `[CODE_VERIFIED]` (`admin.py:39,57,72,79` vs `management.py:163,180,194,209`). `main.py:172` mounts `admin.py`'s router **before** `management.py`'s (:183), so FastAPI dispatches to `admin.py` handlers; the management.py duplicates are shadowed dead routes. Behavior is equivalent today (both call the same boundary methods), but this is a live routing hazard. Related: `mvp/MVP_KNOWN_GAPS.md` G-038 records a prior duplicate payment-verify route fix, so this class of bug has precedent.

### 1.4 Documented-vs-runtime reconciliation

**DOCUMENTED_NOT_FOUND_IN_RUNTIME:**
- `POST /privacy/export` — documented in `mvp/MVP_API_MAP.md:77`; `scripts/api/routes/privacy.py` (27 lines) registers only `/privacy/deletion`. `[CODE_VERIFIED]` NOT_FOUND in runtime.
- `POST /orders/{id}/partial-accept` — documented in `06_PRODUCT/SCHEMA_API_VERIFICATION.md` §1 (row "`/orders/:id/partial-accept`"); runtime implements `partial-acceptance-proposals` (two-party protocol) instead. `[DOC_ONLY]`.
- `POST /media/presigned-url` IS documented and IS real (`API_Contracts.md:586`, `media.py:19`) — verified, no gap.
- Dispute state vocabulary in docs (`NONE/OPEN/UNDER_REVIEW/RESOLVED_ADJUSTED/RESOLVED_REJECTED/CLOSED` in `06_PRODUCT/Order_Lifecycle.md` §3 and `SCHEMA_API_VERIFICATION.md` §3.2) does not match the canonical runtime chain `OPEN → INVESTIGATING → RESOLVED → CLOSED` (`migrations/001_initial_schema.sql:505-507` disputes CHECK; `migrations/072_orders_dispute_status_projection.sql` explicitly labels the doc vocabulary "legacy" and keeps old values only for historical rows). `[CODE_VERIFIED]` — code wins.

**CODED_NOT_IN_CONTRACT (real routes absent from `06_PRODUCT/API_Contracts.md` and/or `mvp/MVP_API_MAP.md`):**
- Whole refund admin surface: POST/GET `/finance/refunds*` (`finance.py:73-123`) — absent from MVP_API_MAP §3.11.
- Delivery stage endpoints `POST /orders/{id}/delivery/picked-up|in-transit|arrived|failed` (`orders.py:288-318`) — not in MVP_API_MAP §3.8.
- GET `/{id}/partial-acceptance-proposals` (`orders.py:96`) — MVP_API_MAP:146 says "no GET list → G-021"; G-021 is marked RESOLVED in MVP_KNOWN_GAPS but the map table was never updated.
- POST `/orders/{id}/payments/direct-transfer` and GET `/orders/{id}/payments/evidence` (`orders.py:483,:502`) — direct-transfer IS in API_Contracts §5.7 but neither appears in MVP_API_MAP §3.8; `payments/{payment_id}/verify` variant (`orders.py:527`) also missing from the map.
- Delivery-exceptions endpoints (`orders.py:385-445`) — in neither contract doc.
- GET `/orders/{id}/invoice` (`finance.py:41`) — map §3.11 says "GET `/orders/{order_id}/invoices`" (plural); actual path is singular `/invoice`. Minor drift.
- `GET /search` unified (`catalog_search.py:13`) is in map §3.5 but not in API_Contracts.md.
- Ops/analytics and `/ops/returns`, `/ops/permissions` are in MVP_API_MAP §6 table but have no sections in API_Contracts.md.

---

## 2. Mobile App Reality

### 2.1 (a) Shared shell / API core and variant boundaries

- **Shared shell:** `mvp/apps/mobile/AppShell.tsx` is the generic root for ALL variants: fonts (Vazirmatn, :29-33), session restore (`restoreSession`, :41-57), role gating via `allowedRoles` prop (:43, :66-75), routing between login/workspace/order-detail/account (:34-37, :96-104), RTL layout (:112), OfflineBanner. It accepts `orderMode: "retailer" | "vendor"` (:19) — there is **no "driver" order mode**.
- **Variants:** `AppRetailer.tsx` wraps `AppShell` with `allowedRoles=["RETAILER_OWNER","RETAILER_STAFF"]`, workspace = `RetailerMobileScreen`, appName `"پل بازار"` (:12). `AppVendor.tsx` wraps with `["VENDOR_OWNER","VENDOR_STAFF"]`, workspace = `VendorMobileScreen`, appName `"پل بنکدار"` (:12). Boundaries are clean: roles, workspace screen, order detail mode.
- **Shared API core:** `mvp/apps/mobile/src/api.ts` — single fetch client with envelope handling (`{success,data/error}` matching backend `scripts/api/errors.py`), SecureStore token persistence (:58-82), silent 401 refresh against `POST /api/v1/auth/refresh` (:84-113), online/offline listeners, and a mock-mode switch driven by `EXPO_PUBLIC_DATA_MODE` (:34-35, :147-160). Base URL default `http://10.0.2.2:8000` (:40). `src/types.ts` defines the `Role` union — 7 roles, **no DRIVER role** (:1-8). `src/i18n/fa.ts` is not a string catalog but Persian digit/number/date formatters (`toAsciiDigits`, `formatFaNumber`, `formatTehranDateTime`, `todayTehranIso`); all UI strings are inline Persian literals in screens.
- **Entry points:** `index.ts` and `index.retailer.ts` are **identical** — both mount `AppRetailer` (`index.ts:1-3`, `index.retailer.ts:1-3`); `index.vendor.ts` mounts `AppVendor`. The build script temporarily overwrites `index.ts` with the variant entry (`build_android_variant.mjs:42,71`) so Metro bundles only one product.

### 2.2 (b) What `scripts/build_android_variant.mjs` produces

`mvp/apps/mobile/scripts/build_android_variant.mjs` (72 lines):
- Args: `retailer|vendor` + `apk|aab` (:5-9). Runs `scripts/pre_apk_qa.mjs <variant>` release gate first (:38).
- Overwrites `index.ts` with `index.retailer.ts` or `index.vendor.ts` source (:42), sets `POL_APP_VARIANT` env (:20), runs `expo prebuild --clean --platform android` (:44) then `gradlew assembleRelease|bundleRelease` (:50-54), copies output to `dist/<variant>/POL-Market.apk|aab` or `POL-Vendor.apk|aab` (:64-68), restores `index.ts` in `finally` (:71).
- Package IDs and labels come from `app.config.js` (reads `app.json` base): retailer = name **"پل بازار"**, slug `pol-market`, package **`ir.pol.market`**; vendor = name **"پل بنکدار"**, slug `pol-vendor`, package **`ir.pol.vendor`**, versionCode 100 (`app.config.js:10-11,29,31`). Base `app.json` package is legacy `com.anonymous.polmobile` (overridden by app.config.js). Data mode env `EXPO_PUBLIC_DATA_MODE` is baked into `extra.dataMode` (:15).
- **Naming note for the three-app handoff:** the retailer app is branded "پل بازار" (`pol-market`), not "پل خرده‌فروش". A third driver variant would need a third entry file + a third branch in `app.config.js` and `build_android_variant.mjs:7` (both hardcode a two-value enum today) `[CODE_VERIFIED]`.

### 2.3 (c) Screens: real vs placeholder/shell (10 files in `src/screens/`, not 9)

| Screen | Lines | Verdict |
|---|---|---|
| `VendorMobileScreen.tsx` | 1536 | **Real.** Tabbed app (home/orders/inventory/finance/more/support, :11-14); ~40 live API calls (orders list/actions, partial acceptance, catalog prices/inventory, daily confirm, invoices/settlements, referrals, customers, staff invite/permissions, storefront, barcode, continuous-scan/publish, product-candidates) |
| `RetailerMobileScreen.tsx` | 879 | **Real.** Search, basket CRUD + allocation preview + checkout with `Idempotency-Key` (:171-178), orders list, invoices, storefront browse |
| `OrderDetailMobileScreen.tsx` | 573 | **Real.** Detail+items+timeline, vendor actions (accept/reject/preparing/ready/dispatch with driver name/phone/plate fields :185-195, :402-404), delivery stage transitions (:209), delivery confirm with 6-digit OTP (:230), returns list |
| `LoginScreen.tsx` | 226 | **Real.** request-otp/verify-otp with E.164 + 6-digit OTP |
| `AccountMobileScreen.tsx` | 294 | **Real.** profile, profile/context, notifications, preferences (PUT per channel), logout (`DELETE /auth/sessions/current`) |
| `SupportMobileScreen.tsx` | 190 | **Real.** case list/create/detail/messages |
| `OpsMobileScreen.tsx` | 372 | **Real code, ORPHANED.** Uses admin/ops APIs incl. ADMIN_SUPER-gated audit surface — but **no App root mounts it** (only referenced by QA grep scripts) |
| `FieldTaskListScreen.tsx` / `FieldTaskDetailScreen.tsx` | 125/136 | **Real code, ORPHANED.** Same: not imported by any App root since the variants were split |
| `AssistedOrderScreen.tsx` | 140 | **Real code, ORPHANED** (field-assisted order flow) |

Orphan evidence: `grep "import.*OpsMobileScreen|FieldTask|AssistedOrder"` across `mvp/apps/mobile/*.tsx` returns nothing; `AppShell` still supports any `Role` (`AppShell.tsx:13`), and `src/types.ts:36-43` still defines `field`/`task`/`assisted` routes that nothing reaches. These ops/field screens are shipped-in-source dead weight for the two Android products; they remain reachable only via QA source-greps (`scripts/mobile_regression_qa.mjs:70,114,153,211-227`).

### 2.4 (d) Driver app / driver role — anywhere?

**No driver app, no driver role, no driver session exists** `[NOT_FOUND]` after repo-wide search:
- Role enums: `mvp/apps/mobile/src/types.ts:1-8` (7 roles), `scripts/permissions.py:38-118` (same 7 + legacy aliases), DB `users.role` CHECK (`migrations/001_initial_schema.sql:19-22`) — same 7 + `MANUFACTURER_ANALYST`. **No DRIVER anywhere.**
- `mvp/apps/mobile/src/utils/statusLabels.ts:172` contains `DRIVER: "راننده"` — display-label map entry only; no backend role emits it.
- Docs: `mvp/apps/mobile/src/__tests__/parity.md:20` — "No Driver App (D-023)". `mvp/BUILD_PLAN.md:113` — "Full Driver App (D-023 — handoff link only)" explicitly out of scope.
- What DOES exist for the driver concept: delivery `driver_name`/`driver_phone`/`vehicle_plate` columns (`migrations/001_initial_schema.sql:454-455`, `002_platform_core_schema.sql:310-312`), vendor-side dispatch collecting them (`scripts/fulfillment_service.py:192-239`, requires all three, :226), delivery OTP + POD (`scripts/api/routes/orders.py:330-373`, `migrations/030_delivery_otp_column.sql`, `077_delivery_otp_six_digit_format.sql`), and delivery stage transitions (picked-up/in-transit/arrived/failed, `orders.py:288-318`). All are vendor/retailer/ops-actor driven; the "راننده" is data, never an authenticated actor.

---

## 3. RBAC / Authorization

**Backend enforcement is real and layered** `[CODE_VERIFIED]`:

1. **Token claims:** `scripts/auth_boundary.py` — JWT access tokens carry `sub`, `sid`, `org_id`, `role` (`encode_access_token` :70-89; `decode_access_token` requires all claims :99). `validate_access_token` (:103-166) checks: session exists/active, user active, **`jwt.org_id == session.active_organization_id`** (:141-142), active membership in that org. So the org/tenant context is server-resolved from the token+DB, not client-supplied.
2. **FastAPI dependencies:** `scripts/api/dependencies.py` — `require_permission(key)` (:50-70) and `require_roles(*roles)` (:73-92), both resolving through `AuthApplicationService.authorize_action` / `scripts/permissions.py`.
3. **Permission engine:** `scripts/permissions.py` — canonical 17 permission keys (:16-34), role ceilings `BASE_ROLE_PERMISSIONS` (:38-118), delegated grants via `delegated_permission_grants` table with **privilege ceiling** (grantor must hold the permission, :233-234), **delegation deny-lists** for staff roles (`ROLE_DELEGATION_DENY` :127-134: staff can never get `order.accept`, `membership.manage`, `payment.record`), and append-only `permission_audit_events` (:308-315).
4. **Tenant ownership checks in services:** e.g., retailer cancel requires actor membership in the order's retailer org (`scripts/canonical_retailer_order.py:10-34`); order actor must be member of the order's retailer OR vendor tenant (`scripts/application_boundary.py:1522`); payment evidence read is tenant-gated (:1668); vendor-scoped role lists in SQL (:1741, :2118).
5. **Boundary-level admin gate:** `scripts/application_boundary.py:4862-4882` `_require_admin_management` (ADMIN_SUPER/OPS_ADMIN/OPS_AGENT, with ADMIN_SUPER-only branches). Used by `management.py` admin routes which have **no route-level guard** — enforcement lives in the boundary instead (`management.py:123-294` has zero `require_*` deps; verified by grep count).
6. **DB-enforced role invariants:** trigger `trg_enforce_org_membership_role_invariant` (`migrations/003_contract_reconciliation.sql:91-94`) — RETAILER_* roles only in RETAILER orgs, VENDOR_* only in VENDOR, platform roles only in OPERATOR (documented in `06_PRODUCT/Roles_and_Permissions.md` §2.4, verified in SQL) `[CODE_VERIFIED]`.
7. **Idempotency:** UUIDv4 `Idempotency-Key` header enforced at checkout (`orders.py:31-38,44`), fingerprint-based in DB (migration `061_idempotency_fingerprints.sql`; `[TEST_VERIFIED]` via `scripts/test_checkout_fingerprint.py`).

**Frontend-only enforcement (gates, not security):**
- Web Next.js middleware `mvp/apps/web/src/middleware.ts` — cookie-based role→route gate, self-described in code as "UX route gate only — cookies for SSR shell; API remains authoritative" (:26). Roles per prefix at :13-21.
- Mobile `AppShell.tsx:43,66-75` — `allowedRoles` filtering + `clearSession()` on mismatch (frontend gate; the API would reject anyway).
- Public/unauthenticated surfaces (by design): `/storefront/vendors*` (`vendor_storefront.py:4` "no authentication required"), `/healthz`, `/readyz`.
- Routes with **no route-level guard and boundary-internal checks** (still backend-enforced, weaker visibility): `management.py` (admin via `_require_admin_management`), `profile.py`, `notifications.py`, `support.py`, `referrals.py`, `field.py`, `reconciliation.py` (0 `require_*` occurrences each — verified by grep). These rely on org scoping inside `POLApplicationBoundary`; sensitivity varies (reconciliation resolve and field task PATCH are mutations worth double-checking in a security pass).

**State per sensitive operation:**
| Operation | Enforcement |
|---|---|
| Order checkout (POST /orders) | Backend route `require_roles(RETAILER_*)` + tenant-scoped checkout `[CODE_VERIFIED]` |
| Vendor accept/reject/partial | Backend `require_permission("order.accept")` (`orders.py:73,85,120`); staff deny-list blocks delegation `[CODE_VERIFIED]` |
| Dispatch/deliver/delivery stages | Boundary tenant + role checks (`application_boundary.py` vendor/ops role SQL :1741; fulfillment_service) `[CODE_VERIFIED]` |
| Refund issue/approve/complete | Backend `require_roles(OPS_*/ADMIN_*)` (`finance.py:81-128`) `[CODE_VERIFIED]` |
| Admin users/orgs/SLA/broadcasts | Boundary `_require_admin_management` only (no route dep) `[CODE_VERIFIED]` |
| Permission grant/revoke | `membership.manage` + privilege ceiling + deny-list + audit `[CODE_VERIFIED]` |
| Web page access | Frontend cookie gate only; API authoritative `[CODE_VERIFIED]` |
| Mobile role scoping | Frontend `allowedRoles`; API authoritative `[CODE_VERIFIED]` |

---

## 4. Data Model

**Canonical schema = 77 ordered SQL migrations** in `C:\Star\pol\2.4\migrations\` (001…077), applied by `scripts/migration_runner.py`; there is **no ORM** (no Prisma/Drizzle/SQLAlchemy) — raw `psycopg` cursors against PostgreSQL. 92 core tables `[CODE_VERIFIED]` via CREATE TABLE scan. Key entities and sources:

| Entity | Source |
|---|---|
| Basket/BasketItem | `migrations/001_initial_schema.sql` (~:322-338); status `OPEN/...` |
| AllocationPlan/AllocationItem | 001 (:346-369); item status incl. `UNFULFILLED` with NULL vendor (`DOMAIN_MODEL.md` invariant 11) |
| OrderGroup | 001 (:381-385), `group_status` |
| Order | 001 (:394-411). `order_status` CHECK: `CREATED, SUBMITTED, ACCEPTED, PARTIALLY_ACCEPTED, REJECTED, PREPARING, READY, DISPATCHED, DELIVERED, CANCELLED` (:396-401). `dispute_status` projection expanded by `072_orders_dispute_status_projection.sql` |
| OrderItem | 001 (:430-435), immutable snapshots (fulfillment_status per item :435) |
| Delivery / DeliveryAttempt / ProofOfDelivery | 001 (:450-471+); `delivery_status` CHECK `ASSIGNED, PICKED_UP, IN_TRANSIT, ARRIVED, DELIVERED, FAILED` (:457-458); driver fields; OTP column added 030, 6-digit format 077, recipient channel 071, POD security bounds 068 |
| DeliveryException | `delivery_exceptions` (+ timeline events); API `orders.py:385-445` |
| VendorProduct/VendorPrice/VendorInventory | 001 (:259-290); MOQ, freshness, generic units (`inventory_unit`), `inventory_audit_log` (:276-287) |
| InventoryReservation | 001 + hardening in `022`/`056`/`057` (idempotency, reconciliation invariant) |
| Payment / PaymentAttempt / PaymentEvidence | 001 (:529-558): `payment_status PENDING/INITIATED/SUCCESS/FAILED/CANCELLED/REFUNDED`; `custody_model NON_CUSTODIAL_DIRECT`; evidence media provenance 064-066, idempotency 073 |
| Invoice/InvoiceItem | 001 + integrity guards (tests `test_invoice_integrity_guards.py`) |
| Settlement / SettlementAdjustment | 001 (:560-586): `PENDING/CALCULATED/RECONCILED/DISPUTED/CLOSED`; adjustment types SHORTAGE_DEDUCTION, DAMAGE_COMPENSATION, PRICE_CORRECTION, SLA_PENALTY, PROMOTION_CREDIT |
| Dispute / DisputeEvent / DisputeItem | 001 (:500-515): `OPEN/INVESTIGATING/RESOLVED/CLOSED`, outcomes `ADJUSTED_SHORTAGE, REPLACEMENT_ORDER, REJECTED_CLAIM, MUTUAL_AGREEMENT`; adjudication invariants 062; order projection 072 |
| Refund | 001 (:590-607): `PENDING/APPROVED/COMPLETED/REJECTED`; one refund per dispute (unique partial index :605); provenance 059, financial bounds 067 |
| PartialAcceptanceProposal | 001 + `027_partial_acceptance_two_party_contract.sql` (`PENDING/ACCEPTED/DECLINED` :28) |
| Identity/orgs: users, organizations, organization_memberships, user_sessions, user_profiles, otp_challenges | 001 + `017` (profiles), `018` (role transition guard), `026` (OTP rate limit/lockout) |
| RBAC: delegated_permission_grants, permission_audit_events | 002 (:14-26 area) |
| Returns/RMA | 001 (`returns`, `return_items`, `return_events`); state integrity 019 (`REFUND_PENDING/REFUNDED` require approved amount, :15) |
| Support, Notifications, Broadcasts, Field tasks, Media, Privacy, Audit | 002 + later (`049` admin audit immutability, `052` privacy lifecycle, `053-055,070` media) |

**State machines in code vs docs:**
- Order machine: doc `06_PRODUCT/Order_Lifecycle.md` §2 == code CHECK constraint 001:396-401 → `[CODE_VERIFIED]` match, including PARTIALLY_ACCEPTED two-party protocol (implemented in `scripts/canonical_partial_acceptance.py` + orders.py proposals routes; `[TEST_VERIFIED]` `scripts/test_partial_acceptance.py`).
- Vendor acceptance timeout: doc §2.1 — implemented: `scripts/vendor_acceptance_timeout_worker.py`, wired into boundary (`application_boundary.py:38,1347`), reason `VENDOR_TIMEOUT` (`scripts/operational_config.py:13`); `[TEST_VERIFIED]` `scripts/test_vendor_acceptance_timeout.py`.
- Dispute machine: doc claims legacy vocab (UNDER_REVIEW/RESOLVED_ADJUSTED/…) — code uses `OPEN→INVESTIGATING→RESOLVED→CLOSED` (001:505-507) with 072 keeping legacy values only as historical. **Docs stale** `[CODE_VERIFIED]`.
- **Workers:** `08_DATA/DOMAIN_MODEL.md` §1 diagram claims "BullMQ Worker + Redis Stream pol:events" — **that is DOC_ONLY and contradicted by code**: `scripts/test_worker_architecture.py:15-16` asserts `redis`/`bullmq` are NOT in requirements and the BullMQ wording is removed from Event_Architecture docs (:31-33). Real workers are in-process Python (`scripts/worker_runtime.py` + `reservation_expiry_worker.py`, `payment_reconciliation_worker.py`, `notification_retention_worker.py`, `provider_delivery_worker.py`, `canonical_integration_worker.py`, `media_storage_reconcile_worker.py`), run as a compose service (`docker-compose.vps.yml:97`) using the DB outbox (`outbox_events` table).

---

## 5. Tests

**Python (backend) — 87 `test_*.py` files in `C:\Star\pol\2.4\scripts\`** `[CODE_VERIFIED]` (file count via `ls scripts/test_*.py | wc -l`):
- HTTP contract/transport suites per domain: `test_http_transport.py`, `test_http_checkout.py`, `test_http_fulfillment.py`, `test_http_delivery_tracking.py`, `test_http_delivery_exceptions.py`, `test_http_delivery_pod_g440_451.py`, `test_http_payment_evidence.py`, `test_http_finance.py`, `test_http_refunds` (covered by finance), `test_http_returns_disputes.py`, `test_http_support.py`, `test_http_notifications.py`, `test_http_management.py`, `test_http_admin_referrals.py`, `test_http_field_tasks.py`, `test_http_security_adversarial.py`, `test_http_error_contract.py`, `test_http_vendor_catalog.py`, `test_http_vendor_order.py`, `test_http_order_query.py`, `test_http_baskets.py`, `test_http_catalog*.py`, `test_http_daily_inventory.py`, `test_http_inventory.py`, `test_http_pricing.py`, `test_http_reconciliation.py`, `test_http_proof_of_delivery.py`.
- Domain/state: `test_vendor_order_acceptance.py`, `test_vendor_order_rejection.py`, `test_partial_acceptance.py`, `test_vendor_acceptance_timeout.py`, `test_reservation_expiry_worker.py`, `test_postgres_concurrency.py`, `test_postgres_migrations.py`, `test_identity_tenant_isolation.py`, `test_delegated_permissions.py`, `test_admin_authorization.py`, `test_cross_cutting_state_matrix.py`, `test_route_hardening.py`, `test_api_route_hygiene.py`, `test_api_boundary_route_inventory.py` (this last one is the mechanism that keeps route docs honest — it asserts the route inventory).
- E2E harness: `scripts/e2e_db.py` / `e2e_seed.py` / `e2e_serve.py` (migrate+seed+serve for Playwright; `e2e_serve.py:1-13`).
- CI: `.github/workflows/pol-verification.yml` (postgres 18 service, migration chain, verification suite), `pol-browser-e2e.yml`, `pol-mvp-mobile.yml`, `pol-remediation-static.yml`, `pol-ui-screen-visual-qa.yml`, `notification-retention.yml`, `pol-todo-preflight-windows.yml`.

**Web (Next.js) — Playwright, `mvp/apps/web/tests/` (6 specs, 36 tests)** `[CODE_VERIFIED]`:
- `login.spec.ts` (6 tests: phone normalization E.164/Persian digits, request-otp payload, login flow), `basket-sync.spec.ts` (12: basket versioning/allocation sync), `delivery-flow.spec.ts` (2: full retailer→vendor→delivery E2E with OTP), `a11y.spec.ts` (2), `status-labels.spec.ts` (6: Persian label parity between ops and retailer formatters), `visual-capture.spec.ts` (8: RTL/responsive document contract + screenshots to `.pol-design/evidence/screenshots`).
- Harness: `mvp/apps/web/playwright.config.ts` boots backend via `scripts/e2e_serve.py`.

**Mobile — no real test framework.** `mvp/apps/mobile/src/__tests__/` contains only `parity.md` (a human matrix; explicitly notes "No Driver App (D-023)" and fresh-CI caveats). "Tests" are Node source-grep/QA scripts run by `npm run qa:*`: `scripts/mobile_functional_qa.mjs` (65 lines), `mobile_regression_qa.mjs` (277 lines — greps screen source for expected strings/APIs), `mock_transport_qa.ts` (executable assertions against mockTransport — vendor flows only), `pre_apk_qa.mjs`, `live_api_preflight.mjs`, `test_prebuild_todo_gate.mjs`. `[CODE_VERIFIED]`

**Critical paths with NO tests:**
- **Retailer mobile flows in mock mode** — mockTransport covers none of the retailer paths (see §6), and no automated test exercises `RetailerMobileScreen` at all (only source greps).
- **Mobile driver/delivery-stage UI** (`OrderDetailMobileScreen` delivery stage buttons, OTP confirm) — no device-level test; parity.md itself says fresh certification must be re-established.
- **`/finance/refunds` HTTP surface** — no dedicated `test_http_refunds` file (refund state logic covered in domain tests like `test_batch2_rma_and_outbox.py`/`019` invariants; the route-level approve/complete endpoints lack an obvious dedicated HTTP spec file).
- **Media resumable upload** (`test_media_service.py` exists but resumable/multipart paths and `media_storage_reconcile_worker` are thin).
- **Web admin/ops dashboards** — no Playwright specs for `/(dashboard)/admin/*` or `/(dashboard)/ops/*` pages (visual-capture logs in as admin/field but coverage is screenshot-contract, not behavior).
- **Web auth refresh/cookie rotation** — G-029 claims refresh tests exist (`MVP_KNOWN_GAPS.md:186`); I found no web-side spec asserting it (only `test_auth_contract.py` on the backend). `[CODE_VERIFIED]` NOT_FOUND in `mvp/apps/web/tests/`.

---

## 6. Mock vs Live Drift

`mvp/apps/mobile/src/mock/mockTransport.ts` (678 lines) implements ~45 route patterns. Drift vs real backend (`scripts/api/**`) and vs the screens that call it:

1. **Mock is vendor-only by construction.** `MockRole = "VENDOR_OWNER" | "VENDOR_STAFF"` (line 1); `verify-otp` maps any phone not ending `0002` to VENDOR_OWNER, `…0002` to VENDOR_STAFF (:284-293). **A retailer can never log in under `EXPO_PUBLIC_DATA_MODE=mock`** — `AppRetailer` would `clearSession()` on the returned role (`AppShell.tsx:66-70`). MOCK_LIVE_CONTRACT_DRIFT (critical for a retailer build).
2. **Entire retailer API surface missing from mock:** no `POST /baskets`, `/baskets/*/items`, `/allocation-preview`, no `GET /catalog/search`, no `POST /orders` (checkout), no `GET /invoices` (mock has it — yes invoices exist), no `/storefront/vendors/{id}` (mock has both storefront routes — yes), but critically: no `GET /api/v1/catalog/search` and no basket/checkout routes. `RetailerMobileScreen` calls all of these (`RetailerMobileScreen.tsx:106,122,125,152,171,191,237,248,261,275-276`) → mock mode throws `"Mock route not implemented"` (`mockTransport.ts:266-268`). MOCK_LIVE_CONTRACT_DRIFT.
3. **Vendor flow gaps vs live:** mock implements accept/preparing/ready/reject/partial-proposal-create/dispatch but NOT: `/deliver` (delivery OTP), `/cancel`, `/delivery/*` stages, `/payments/*`, `/orders/{id}/returns`, `/disputes`, `/invoices` detail fields beyond basics, notifications read mutations (returns static), profile completion. The live contract has all of these.
4. **Envelope mismatch (benign):** mock returns bare payloads (`envelope()` = clone, :262-264) while `api.ts` mock path treats them as data directly (:150) — correct, but the mock's shapes mirror a frozen 2026-09-29 snapshot (`now = new Date("2026-09-29T09:30:00+03:30")`, :77) — e.g., `MockOrder` lacks `order_group_id`, `vendor_acceptance_deadline_at`, `dispute_status` fields the live API emits.
5. **Permission simulation:** mock enforces a coarse `Mock permission denied` only for `order.accept`-family actions gated on `VENDOR_OWNER` (:312,326,334) — far weaker than the real 17-key delegated-permission engine; QA against mock cannot catch permission regressions.
6. Mock does implement live-faithful 6-digit OTP validation (:287) and E.164 phone `[TEST_VERIFIED]` via `scripts/mock_transport_qa.ts`.

---

## 7. Existing POL Docs — claims vs code

- **`06_PRODUCT/API_Contracts.md`** (841 lines, `API-SPEC-001` v1.0) `[DOC_ONLY]` — comprehensive Persian contract covering §2 catalog/barcode/candidates, §3 vendor inventory scan, §4 baskets, §5 order lifecycle + partial acceptance + payments, §6 disputes, §7 auth/media/privacy, §8-14 support/notifications/broadcasts/invoices/admin-ops/categories/profile. Verified against code: **core endpoints all exist** (see §1.4). Claimed but stale: `partial-accept` path in companion doc `SCHEMA_API_VERIFICATION.md`; dispute vocabulary; no coverage of delivery-stage endpoints, delivery-exceptions, refunds routes, unified `/search`.
- **`06_PRODUCT/SCHEMA_API_VERIFICATION.md`** — claims "100% schema parity, all VERIFIED" `[DOC_ONLY]`; spot-checks confirm the mapped endpoints exist, but its `partial-accept` row and dispute-state vocabulary are outdated (see §1.4, §4). Its `/orders/:id/deliver` row honestly says "6-digit contract; fresh test run needed — IMPLEMENTED/REVERIFY".
- **`06_PRODUCT/Order_Lifecycle.md`** — order state machine, partial-acceptance protocol, 2-hour vendor timeout rules, dispute machine, entity hierarchy `Basket→AllocationPlan→OrderGroup→Order→OrderItem`. Order machine and hierarchy `[CODE_VERIFIED]` (001:396-401; `MULTI_VENDOR_ORDERING_MODEL.md` mapping matches tables). Timeout `[CODE_VERIFIED]` (`vendor_acceptance_timeout_worker.py`). Dispute machine stale (§4).
- **`08_DATA/DOMAIN_MODEL.md`** (139 lines, `DOMAIN-SPEC-001`) — six DDD subdomains, invariants 1-14 (product identity, barcode scopes global/vendor, unit-generic inventory, immutable order-item snapshots, no-owned-fleet D-008, OTP/signature POD). All verified present in schema except: its **cross-cutting diagram's "BullMQ Worker / Redis Stream" contradicts code** (`test_worker_architecture.py:15-16` forbids it) — DOC_ONLY/stale.
- **`08_DATA/MULTI_VENDOR_ORDERING_MODEL.md`** (`POL-DAT-004` v2.0, LOCKED) — aggregate hierarchy and 9 relational mappings; matches migration tables 1:1 `[CODE_VERIFIED]`.
- **`mvp/MVP_API_MAP.md`** — the most accurate doc; route lists largely match runtime; drift items listed in §1.4 (missing delivery stages, refunds, payment evidence/direct-transfer, GET proposals; `/privacy/export` listed but not registered; singular/plural invoice path).
- **`mvp/MVP_KNOWN_GAPS.md`** (1013 lines, G-001…G-039+) — self-reported, mostly RESOLVED entries; each spot-checked claim (G-003 catalog path, G-004 inbox, G-012 basket current GET, G-021 proposals GET, G-029 localStorage→memory+cookie, G-038 duplicate route fix) **verified true in code** — except G-021's fix never propagated into MVP_API_MAP's table, and G-029's "refresh tests assert this behavior" has no matching web test.
- **`mvp/apps/mobile/src/__tests__/parity.md`** — honest parity matrix; states clearly: "No Driver App (D-023)", "client does not infer permissions", "fresh certification must be re-established", vendor camera runtime gap for V-16.

---

## Top 10 Gaps for Building the Three Apps (پل خرده‌فروش / پل بنکدار / پل راننده)

1. **No driver identity anywhere — the third app has no backend substrate.** No DRIVER role in `scripts/permissions.py:38-118`, `migrations/001_initial_schema.sql:19-22`, or `mvp/apps/mobile/src/types.ts:1-8`; no driver auth/session routes; decision D-023 explicitly scoped it out (`mvp/BUILD_PLAN.md:113`, `mvp/apps/mobile/src/__tests__/parity.md:20`). Driver-relevant primitives DO exist: delivery stages (`scripts/api/routes/orders.py:288-318`), driver metadata (`scripts/fulfillment_service.py:192-239`), delivery OTP (`migrations/030`, `071`, `077`). A driver app needs: new role + OPERATOR/CARRIER org type handling, driver sessions, and stage-transition ownership reassignment (currently vendor/ops-triggered).
2. **Build pipeline supports exactly two variants.** `mvp/apps/mobile/scripts/build_android_variant.mjs:7` and `mvp/apps/mobile/app.config.js:2-3,10,29` hardcode `retailer|vendor`; a third variant requires touching entry file, config, and the QA gate (`scripts/pre_apk_qa.mjs` takes variant arg).
3. **Retailer app brand is "پل بازار" (`ir.pol.market`), not "پل خرده‌فروش"** (`app.config.js:10-11,29`) — product naming must be reconciled before store submission.
4. **Mock transport cannot QA the retailer app at all** — vendor-only roles (`src/mock/mockTransport.ts:1,284-293`) and no basket/search/checkout routes (:266-268 fallback throws). Any mock-mode retailer QA or demo build is broken by construction.
5. **Admin route shadowing**: `admin.py:39,57,72,79` vs `management.py:163,180,194,209` both register the same `/admin/broadcasts*` and `/admin/categories*` paths; `main.py:172` vs `:183` mounting order silently decides the winner. Must be de-duplicated before adding a third product's ops surface.
6. **Doc-contract debt that will mislead a build team**: `mvp/MVP_API_MAP.md` missing delivery-stage/refunds/payment-evidence/delivery-exception routes; `/privacy/export` documented (`:77`) but not registered (`scripts/api/routes/privacy.py`); dispute state machine docs (`06_PRODUCT/Order_Lifecycle.md` §3, `SCHEMA_API_VERIFICATION.md` §3.2) describe a vocabulary the DB dropped (`migrations/072_orders_dispute_status_projection.sql`); `DOMAIN_MODEL.md` diagram still claims BullMQ/Redis which the codebase forbids (`scripts/test_worker_architecture.py:15-16`).
7. **Orphaned mobile screens (ops/field/assisted)** are unreachable from both shipped entrypoints (`grep` of `AppRetailer.tsx`/`AppVendor.tsx` imports shows no references), yet `AppShell` and `src/types.ts:36-43` still carry the routes — dead code that must be either re-mounted (e.g., an ops/field variant) or pruned; they also inflate bundle and QA-grep surface (`scripts/mobile_regression_qa.mjs:211-227`).
8. **Mobile has no real automated tests**: `src/__tests__/` holds only `parity.md`; coverage is source-grep QA scripts; parity.md itself requires fresh certification. No test covers retailer order flows, delivery-stage UI, or the driver handoff UX on device.
9. **Un-guarded route-level mutations** in `scripts/api/routes/` (management.py, support.py, referrals.py, field.py, reconciliation.py have zero `require_*` deps; enforcement is boundary-internal, e.g. `application_boundary.py:4862`) — workable today, but each new app surface should standardize on route-level `require_roles/require_permission` to keep the security review tractable.
10. **Ops/admin web dashboards and finance refund routes lack dedicated tests** — no Playwright spec for `/(dashboard)/admin/*` or `/(dashboard)/ops/*`; no dedicated HTTP spec for `/finance/refunds*` approve/complete (`scripts/api/routes/finance.py:113-123`). Settlement/dispute financial flows are the highest-risk code for a three-sided marketplace and are the least directly tested at the HTTP layer.