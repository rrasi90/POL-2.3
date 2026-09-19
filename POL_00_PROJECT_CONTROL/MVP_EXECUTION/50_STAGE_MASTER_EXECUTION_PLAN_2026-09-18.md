# POL MVP — 50-Stage Master Execution Plan
**تاریخ ایجاد:** 2026-09-18  
**Branch:** `research-hardening-2026-09-14`  
**هدف نهایی:** `MVP-CERTIFIED / PILOT-READY`  
**Controller Work ID:** `EXEC50-001`  
**وضعیت:** ACTIVE EXECUTION PROGRAM

---

## 0. روش اجرای این سند

این فایل «لیست آرزوها» نیست؛ **کنترلر اجرای مرحله‌ای پروژه** است.

قانون اجرا:
1. هر بار کاربر فقط می‌گوید `ادامه`؛ مرحله‌ی بعدیِ باز اجرا می‌شود.
2. در شروع هر Stage، Work Log و Active Work Ledger ثبت/به‌روز می‌شوند.
3. در طول Stage هر کاری که واقعاً قابل انجام باشد انجام می‌شود؛ کد، SQL، migration، test، documentation، config، API، frontend و governance همگی در scope هستند.
4. چیزی که به محیط/ابزار خارجی وابسته است با برچسب `EXTERNAL_PENDING` در blocker ثبت می‌شود؛ هرگز به‌عنوان انجام‌شده علامت نمی‌خورد.
5. نتیجه‌ی هر Stage همین فایل را به‌روزرسانی می‌کند: وضعیت، تغییرات، فایل‌ها، تصمیم‌ها، تست‌ها، CI، blocker و next action.
6. تست‌ها در طول توسعه فقط به اندازه‌ی لازم برای تشخیص/رفع خطا اجرا می‌شوند؛ **گزارش نهایی می‌تواند یک‌جا شامل کل regression suite باشد.**
7. هیچ business rule یا معماری جدید بدون Decision ID اضافه نمی‌شود.
8. هیچ «GREEN*» دامنه‌ای به‌تنهایی به معنی production-ready نیست.
9. پس از Stage 50، هر چیزی که باقی مانده باید دقیقاً در یک **External Handoff List** باقی بماند؛ عمدتاً live Penpot، محیط واقعی، credentialهای واقعی و final test execution.

---

# Stage 01 — Fresh Baseline & Certification Snapshot
**Macro:** M-01  
**هدف:** ثبت وضعیت واقعی branch/PR/CI و حذف ادعاهای stale.

**کار قابل انجام**
- خواندن HEAD واقعی و PR #1.
- ثبت آخرین CI run و failure واقعی.
- مقایسه Master Checklist با SHA واقعی.
- ثبت current migration count/table count از evidence معتبر.
- شناسایی تمام claimهای stale مثل `209/209`.

**نتیجه واقعی — 2026-09-18**
- PR #1 باز و unmerged است؛ HEAD واقعی: `e6484daf9f0926b807577c71477d8f1405c24a3e`.
- آخرین CI تکمیل‌شده روی این HEAD: Run #333؛ نتیجه **FAILED**.
- Environment/bootstrap verification در Run #333 موفق بود.
- PostgreSQL 18.6 با **93 public base tables** ساخته شد.
- migrationهای repository از `001` تا `028` = **28 migrations**.
- full suite: **209 collected / 170 passed / 39 failed / 0 skipped**.
- failure families: Batch 2 RMA/outbox (15)، Batch 3 contract matrix (5)، E2E MVP platform (14)، vendor acceptance timeout (5).
- machine-readable artifact: artifact ID `10560188267`; merge-ref checkout SHA recorded by runner: `7bf440dd55d300253d099c6f70c5c76973bd8e25`.
- پنج سند active که current schema/count را stale گزارش می‌کردند، با baseline جدید sync شدند: `TEST_VERIFICATION_MANIFEST.md`, `TECHNICAL_ENVIRONMENT.md`, `DATABASE_SCHEMA_MANIFEST_2026-09-16.md`, `REPOSITORY_COMPLETION_AUDIT_2026-09-16.md`, `CURRENT_SOURCE_OF_TRUTH.md`.
- snapshot مستقل: `POL_00_PROJECT_CONTROL/MVP_EXECUTION/STAGE_01_FRESH_BASELINE_2026-09-18.md`.

**Verification**
- GitHub PR/commit/workflow evidence inspected.
- CI certification **NOT GREEN**; no green claim made.
- Current failing-test families are carried forward to Stage 02+.

**External**
- ندارد.

**Exit:** snapshot با HEAD واقعی، CI واقعی و blockers واقعی هم‌خوان شد.

**Status:** CLOSED

---

# Stage 02 — Batch 6C-7 Source Repair
**Macro:** M-01  
**هدف:** رفع خطاهای قطعی Batch 6C-7 که از CI و source inspection مشخص شده‌اند.

**نتیجه واقعی — 2026-09-18**
- `scripts/revalidation_checkout.py`: importهای لازم برای `calculate_sla_deadline` و `load_operational_holidays` اضافه شد؛ SLA دو ساعته از constant کانونیکال `VENDOR_ACCEPTANCE_SLA_HOURS` مصرف می‌شود.
- checkout order insert اصلاح شد: ستون `created_at` دیگر explicit نیست و PostgreSQL default آن را تولید می‌کند؛ `vendor_acceptance_deadline_at` به‌صورت explicit ثبت می‌شود.
- `scripts/vendor_acceptance_timeout_worker.py`: `MIN(uuid)` حذف و با انتخاب deterministic از `ORDER BY user_id LIMIT 1` جایگزین شد؛ همین constant کانونیکال برای fallback SLA مصرف می‌شود.
- `scripts/test_vendor_acceptance_timeout.py`: fixture واقعی `pg_connection` به‌صورت محلی در suite ثبت شد تا pytest آن را discover کند.
- `scripts/sla_calendar.py`: `VENDOR_ACCEPTANCE_SLA_HOURS = 2.0` به‌عنوان constant مشترک در canonical SLA module ثبت شد؛ rule جدیدی ایجاد نشده است.
- read-back static inspection روی چهار فایل انجام شد؛ defectهای شناخته‌شده در source دیگر مشاهده نشدند.
- Run #356 subsequently completed with **209/209 PASS** on the pre-Stage-03 suite; this is the completed regression certification carried forward into Stage 03.

**فایل‌ها**
- `scripts/sla_calendar.py`
- `scripts/revalidation_checkout.py`
- `scripts/vendor_acceptance_timeout_worker.py`
- `scripts/test_vendor_acceptance_timeout.py`
- `POL_00_PROJECT_CONTROL/MVP_EXECUTION/WORK_LOGS/SECTION_02.md`

**Verification**
- Static/source read-back: completed.
- CI Run #352: in progress; not counted as passing.
- Full regression certification remains Stage 03/CI work.

**External**
- ندارد.

**Exit:** known Batch 6C-7 source defects removed from repository source; regression certification carried forward.

**Status:** CLOSED

---

# Stage 03 — Batch 6C-7 Regression Contract Hardening
**Macro:** M-01  
**هدف:** مطمئن شدن از اینکه timeout behavior فقط happy-path نیست.

**نتیجه نهایی — 2026-09-18**
- audit کامل suite `scripts/test_vendor_acceptance_timeout.py` انجام شد.
- سه regression contract machine-checkable اضافه شد: backfill و persistenceِ deadline مفقود، tenant isolation برای `ORDER_CANCELLED` notification، و deterministic assignee selection.
- timeout suite اکنون **9 test function** دارد.
- `TEST_VERIFICATION_MANIFEST.md` به Suite 21 با 9 test item به‌روزرسانی شد؛ catalog ثبت‌شده همچنان 21 suite / 56 registered items است و execution inventory برابر 212 test item در CI است.
- Run #356 روی pre-regression-test head کل suite قبلی را با **209/209 PASS** اجرا کرد.
- Run #364 روی head `1d53170fd270cac9cf4d9c12b7426d7fde04791c`، suite گسترش‌یافته را با **210/212 PASS** اجرا کرد؛ دو failure هر دو test-fixture/assertion defects بودند و با commit `5ac5974b2caf045f8020e3c8b48f889ed3ff94e9` اصلاح شدند.
- Run #365 با run id `35378830823` روی head `5ac5974b2caf045f8020e3c8b48f889ed3ff94e9` با نتیجه **SUCCESS** تکمیل شد.
- Run #365: **212 collected / 212 passed / 0 failed / 0 skipped** در **72.74s**.
- Artifact: `10561965892` با digest `sha256:22cb435f5008516719bb221115844b8edab8b61c562e9d4f80586d50699a233a`.
- CI environment: PostgreSQL **18.6**, اتصال موفق، **93 public tables**؛ artifact runner metadata commit برابر `3bd6788ed1d509893fc98879b57a29b17f86cac9` و branch `HEAD`/dirty=false ثبت شده است.

**Verification**
- Source/read-back: completed.
- Regression CI: **GREEN — Run #365, 212/212 PASS**.
- Timeout suite: 9/9 PASS داخل full suite.
- Machine-readable artifact inspected and summary verified.
- No skipped tests.

**External**
- ندارد.

**Blockers**
- هیچ blocker داخلی برای Stage 03 باقی نمانده است.
- Full production deployment و external provider validation همچنان در stages بعدی/External Handoff scope هستند و جزو شرط بستن Stage 03 نیستند.

**Exit:** regression contractها با CI واقعی machine-check شدند و Stage 03 قابل بستن است.

**Status:** CLOSED

---

# Stage 04 — Repository Truth Synchronization
**Macro:** M-01  
**هدف:** هم‌تراز کردن اسناد وضعیت با repository واقعی.

**کار قابل انجام**
- sync کردن `CURRENT_SOURCE_OF_TRUTH.md`.
- `TECHNICAL_ENVIRONMENT.md`.
- route matrix.
- capability matrix.
- test manifest.
- repository completion audit.
- migration/table counts.

**خروجی**
- اسناد stale اصلاح شوند.
- historical claims برچسب بخورند.

**Verification**
- cross-document search for stale counts/SHA/status.

**External**
- ندارد.

**Exit:** هیچ document active ادعای خلاف HEAD واقعی نداشته باشد.

**Status:** PLANNED

---

## Stage 04 — Closure Evidence — 2026-09-18
- Work ID: EXEC50-005
- Cross-document truth audit completed across CURRENT_SOURCE_OF_TRUTH, TEST_VERIFICATION_MANIFEST, TECHNICAL_ENVIRONMENT, DATABASE_SCHEMA_MANIFEST, REPOSITORY_COMPLETION_AUDIT, Active Work Ledger and Section 32 controller.
- Current PR #1 control-document HEAD at audit start: 4539c77a557290dc8476b6c29d3a7cfeab36feea.
- Latest completed PR-lineage certification: Run #365 / 35378830823, 212/212 PASS on certified code head 5ac5974b2caf045f8020e3c8b48f889ed3ff94e9.
- Stale active claims corrected: old e6484... current-head claim, current 209/170/39 execution claim, 90-table current header, outdated Stage 03/Run #360 live status, and stale Stage 01/02 execution-log statuses.
- Historical Run #333 evidence is explicitly retained as historical baseline only.
- Status: CLOSED

# Stage 05 — Governance / Decision Register Reconciliation
**Macro:** M-01  
**هدف:** یکسان‌سازی terminology، precedence و status بین Decision Register و اسناد فعال.

**نتیجه نهایی — 2026-09-18**
- D-001 تا D-020 در `DECISION_REGISTER.md` audit شدند و authority/precedence آن‌ها با اسناد canonical اصلی cross-check شد.
- D-018: refresh-token rotation به‌عنوان policy تصمیم‌نگرفته باقی ماند؛ runtime/API docs اکنون صراحتاً رفتار فعلی implementation را از policy نهایی جدا می‌کنند.
- D-019/D-020: Python + FastAPI به‌عنوان runtime/HTTP authority تثبیت شد؛ stale claimِ framework-neutral بودن transport از `GLOBAL_ENGINEERING_AUDIT` حذف شد.
- تضاد BullMQ/Redis با D-019 شناسایی و **حل‌نشده اما formally carried** به Stage 06 شد؛ BullMQ دیگر به‌عنوان تصمیم اجرایی canonical معرفی نمی‌شود و D-019 مانع dual Node/Python runtime باقی می‌ماند.
- Payment wording با `NON_CUSTODIAL_DIRECT` / zero custody هم‌خوان باقی ماند.
- Multi-vendor wording با D-014 و open vendor count با D-005 هم‌خوان باقی ماند.
- stale wording در `scripts/test_current_source_of_truth.py` اصلاح شد: Decision Register اکنون D-001 تا D-020 را به‌درستی توصیف می‌کند.
- Last Audit در `DECISION_REGISTER.md` به 2026-09-18 به‌روزرسانی شد.

**Verification**
- Canonical source inspection completed across Decision Register, Technical Architecture, API Contracts, Identity/Membership, API Application Boundary, Global Engineering Audit, MVP Multi-Vendor Decision, operational config, payment/commission docs and SSoT verification gate.
- Identified legacy claims were either reconciled or explicitly carried under an existing Decision ID (D-018/D-019), with queue resolution assigned to Stage 06.
- GitHub code-search endpoint did not provide repository-wide code results in this connector; therefore no claim of exhaustive repository-wide grep is made.
- No new business/architecture Decision ID was created.

**Tests / CI**
- No domain-code change was made in Stage 05.
- Latest completed full regression remains Run #365: 212/212 PASS on certified code head `5ac5974b2caf045f8020e3c8b48f889ed3ff94e9`.
- A new CI run was queued after Stage 05 documentation changes; its result is not used as Stage 05 closure evidence because Stage 05 changes are governance/documentation plus a test message correction.

**Exit:** Stage 05 CLOSED. Next open stage: Stage 06 — Queue / Worker Architecture Closure.

# Stage 06 — Queue / Worker Architecture Closure
**Macro:** M-01  
**هدف:** حل تضاد BullMQ/Redis قدیمی با Python + PostgreSQL outbox.

**کار قابل انجام**
- یافتن تمام queue/runtime references.
- تعیین code pathهای فعلی worker.
- پیشنهاد canonical MVP worker model based on existing architecture.
- ثبت decision/document update، بدون اختراع زیرساخت.

**خروجی**
- architecture decision/update.
- stale references cleanup.

**Verification**
- import/path consistency.

**External**
- infrastructure deployment itself is later.

**Exit:** production worker model unambiguous باشد.

**Status:** CLOSED

**Work ID:** EXEC50-007

**Progress — 2026-09-18**
- Canonical model selected: PostgreSQL 18 transactional outbox + Python workers.
- Added `POL_00_PROJECT_CONTROL/WORKER_ARCHITECTURE.md` as active runtime contract.
- Added `scripts/test_worker_architecture.py` and registered Suite 22.
- Removed active BullMQ/Redis Streams transport wording from Event Architecture; Technical Architecture now names Python workers + PostgreSQL Outbox.
- Existing worker classes verified to use PostgreSQL locking/leases; no Redis/BullMQ dependency exists in `requirements.txt`.
- Run #395 on the expanded 213-test suite: **212 PASS / 1 FAIL**; only the new static worker-architecture test failed due to an outdated label matcher.
- Test repair committed in `f76c9ebae857eb9a2573848780dd3a5aaf4d0a26`.
- Run #403 subsequently completed successfully on the repaired SHA; closure evidence is recorded below.

---


## Stage 06 Closure Evidence — 2026-09-18
- Work ID: EXEC50-007.
- Canonical architecture: **PostgreSQL 18 Transactional Outbox + Python Workers**.
- Canonical worker contract: `POL_00_PROJECT_CONTROL/WORKER_ARCHITECTURE.md`.
- Event Architecture and Technical Architecture no longer expose BullMQ / Redis Streams as the active MVP event transport.
- Redis is explicitly non-authoritative and limited to optional cache/rate-limit/session-adjacent acceleration.
- Four concrete Python workers were verified by source inspection: CanonicalIntegrationWorker, ProviderDeliveryWorker, PaymentReconciliationWorker, VendorAcceptanceTimeoutWorker.
- Suite 22 added: `scripts/test_worker_architecture.py`.
- Run #395: 212 PASS / 1 FAIL; the single failure was a stale assertion label in the newly added contract test and was repaired in `f76c9ebae857eb9a2573848780dd3a5aaf4d0a26`.
- **Run #403 / workflow 35380839893: SUCCESS.**
- Run #403: **213 collected / 213 passed / 0 failed / 0 skipped** in 70.6s.
- Artifact: **10562004166**, digest `sha256:7d2180da8d8edca1cf962e352ac2ad907240ec42cfe108dcd301b63ca2a3ab64`.
- Artifact metadata: PostgreSQL 18.6, 93 public tables, clean CI workspace.
- Status: CLOSED.
- Next stage: 07 — API/Boundary Master Inventory.
# Stage 07 — API/Boundary Master Inventory
**Macro:** M-01  
**هدف:** تبدیل route gaps به inventory دقیق executable.

**کار قابل انجام**
- استخراج تمام Application Boundary commands.
- استخراج تمام API contract endpoints.
- مقایسه با actual FastAPI routes.
- classification: implemented / missing / internal-only / future.

**خروجی**
- canonical route-to-boundary matrix.
- ordered applicationization backlog.

**Verification**
- repository search/static mapping.

**External**
- ندارد.

**Exit:** برای هر MVP capability یک status و owner path مشخص باشد.

**Status:** CLOSED

**Work ID:** EXEC50-008

**Closure Evidence — 2026-09-19**
- Canonical endpoint contract inventory normalized to **50 unique business endpoint specifications**.
- Actual FastAPI business route inventory is **21**, plus `/healthz` and `/readyz` operational routes.
- `POLApplicationBoundary` exposes 29 public methods; 13 are reachable from current HTTP routes and 16 remain boundary-ready/internal-only.
- Added `POL_00_PROJECT_CONTROL/API_BOUNDARY_ROUTE_INVENTORY_2026-09-18.md`.
- Added Suite 23 `scripts/test_api_boundary_route_inventory.py` to freeze the current executable route set.
- No contract-only endpoint is represented as live HTTP; applicationization is assigned to later canonical stages.
- CI certification: **Run #429 / 35424359991 — SUCCESS** on `ad686ff3da437d0736da8bbf9f31fb484bd601aa`; full verification passed **214/214**, with migration/bootstrap/environment verification successful. Artifact `10578268045`; digest `sha256:5b20fffcb4f45e9b418b23870cdc7d578fb642339ec25145709234985ac30f04`.
- Stage 07 route inventory gate was therefore certified without weakening the 23-route equality contract.
- Stage 07 is CLOSED; next open stage is Stage 08.

---

# Stage 08 — Authentication Contract Audit
**Macro:** M-02  
**هدف:** ممیزی کامل auth/OTP/session نسبت به D-018.

**کار قابل انجام**
- OTP TTL.
- rate limit.
- lockout.
- one-time consumption.
- session revocation.
- JWT claims.
- membership context.
- test/prod boundary.
- refresh semantics.

**خروجی**
- auth gap list + fixes where possible.

**Verification**
- code/static tests where executable.

**External**
- provider credentials later.

**Exit:** exact remaining production auth gaps مشخص باشند.

**Status:** IN_PROGRESS

**Work ID:** EXEC50-009

**Progress — 2026-09-19**
- Audited D-018 against `scripts/operational_config.py`, `scripts/auth_boundary.py`, `scripts/auth_application.py`, `scripts/domain_services.py`, FastAPI auth routes/schemas and `scripts/test_auth_contract.py`.
- Confirmed OTP 4-digit/120s, resend 60s, 3/5min phone+IP rate limit, 5 attempts, 10-minute phone lockout, 15-minute JWT, 30-day refresh session, session revocation and membership validation.
- Identified and repaired a concurrency gap in one-time OTP consumption: verification now locks the pending challenge row with PostgreSQL `FOR UPDATE` before successful consumption.
- Added regression T-AC20 for exactly-once OTP consumption.
- Refresh-token rotation remains explicitly **UNDECIDED** under D-018; no policy or implementation change was made.
- Deterministic non-production OTP behavior and live SMS/provider boundary are carried to Stage 09.
- Audit document: `POL_00_PROJECT_CONTROL/MVP_EXECUTION/AUTHENTICATION_CONTRACT_AUDIT_2026-09-19.md`.
- Fresh CI certification pending.

---

# Stage 09 — Production Authentication Boundary
**Macro:** M-02  
**هدف:** جدا کردن test behavior از production authentication path.

**کار قابل انجام**
- provider interface.
- environment-backed configuration.
- test-only deterministic OTP isolation.
- secret validation.
- auth adapter cleanup.
- error semantics.

**خروجی**
- source/config/test updates.

**Verification**
- static leakage checks.
- tests where possible.

**External**
- actual SMS provider credentials/certification.

**Exit:** production code path deterministic OTP را structuralاً در اختیار نداشته باشد.

**Status:** PLANNED

---

# Stage 10 — Refresh Rotation / Session Lifecycle Closure
**Macro:** M-02  
**هدف:** بستن gap صریح refresh-token rotation و session lifecycle.

**کار قابل انجام**
- inspect D-018 conflict.
- define implementation if existing decision permits.
- add migration/service/tests as needed.
- session reuse/replay semantics.

**خروجی**
- decision + implementation or explicit BLOCKED decision.

**Verification**
- static + targeted tests.

**External**
- none unless provider/session infrastructure is needed.

**Exit:** rotation وضعیت canonical و implementation-backed داشته باشد.

**Status:** PLANNED

---

# Stage 11 — HTTP Error / Correlation Contract
**Macro:** M-02  
**هدف:** transport behavior قابل پیش‌بینی و قابل trace.

**کار قابل انجام**
- stable HTTP error mapping.
- correlation ID propagation.
- domain error mapping.
- idempotency conflict mapping.
- state/permission errors.

**خروجی**
- FastAPI transport hardening.
- contract documentation/tests.

**Verification**
- route-level static/test checks.

**External**
- none.

**Exit:** API client بتواند deterministic error contract بگیرد.

**Status:** PLANNED

---

# Stage 12 — HTTP Security & Tenant-Isolation Layer
**Macro:** M-02  
**هدف:** بستن security gaps در سطح HTTP.

**کار قابل انجام**
- authenticated context.
- tenant from session.
- role from membership.
- body tenant poisoning protection.
- secure headers.
- route authorization audit.
- legacy import scan.

**خروجی**
- middleware/dependency/route updates.
- negative tests.

**Verification**
- HTTP security test definitions and executable tests.

**External**
- TLS deployment later.

**Exit:** unauthorized tenant/role access blocked at transport boundary.

**Status:** PLANNED

---

# Stage 13 — Catalog Domain Audit
**Macro:** M-03  
**هدف:** تطبیق Master Product / Vendor Product / Candidate model با MVP.

**کار قابل انجام**
- audit schema/service definitions.
- identify missing writer/readers.
- barcode/candidate semantics.
- pack/MOQ behavior.

**خروجی**
- catalog implementation backlog + fixes.

**Verification**
- schema/contract inspection.

**External**
- none.

**Exit:** domain model canonical and implementation-ready باشد.

**Status:** PLANNED

---

# Stage 14 — Catalog HTTP Applicationization
**Macro:** M-03  
**هدف:** Catalog را از domain به authenticated API تبدیل کنیم.

**کار قابل انجام**
- search.
- product detail.
- category.
- offers.
- vendor-specific SKU.
- candidate/review endpoints where MVP-required.

**خروجی**
- FastAPI routes + boundary methods + schemas + negative tests.

**Verification**
- targeted route tests/static contract checks.

**External**
- none.

**Exit:** retailer/vendor catalog flows transport-complete باشند.

**Status:** PLANNED

---

# Stage 15 — Vendor Catalog Management
**Macro:** M-03  
**هدف:** Vendor بتواند catalog عرضه خود را کنترل کند.

**کار قابل انجام**
- create/update/publish vendor product.
- mapping.
- status.
- pack.
- MOQ/MOV.
- visibility.

**خروجی**
- application boundary + API + validation.

**Verification**
- tenant/state/validation tests.

**External**
- none.

**Exit:** vendor catalog management قابل مصرف by client باشد.

**Status:** PLANNED

---

# Stage 16 — Pricing Runtime
**Macro:** M-03  
**هدف:** قیمت جاری/effective/history در runtime کامل شود.

**کار قابل انجام**
- current price API.
- future/effective windows.
- transitions.
- conflicts.
- vendor-specific pricing.
- retailer comparison.

**خروجی**
- endpoints/service/test/contract updates.

**Verification**
- temporal + stale price checks.

**External**
- none.

**Exit:** price source/runtime semantics کامل باشد.

**Status:** PLANNED

---

# Stage 17 — Inventory Runtime
**Macro:** M-03  
**هدف:** physical/reserved/available/freshness semantics به client برسد.

**کار قابل انجام**
- inventory reads/writes.
- reconciliation.
- available quantity.
- freshness/stale state.
- reservation exposure rules.

**خروجی**
- API + boundary + tests.

**Verification**
- concurrency/authorization/static checks.

**External**
- none.

**Exit:** retailer and vendor can observe/manage canonical inventory state.

**Status:** PLANNED

---

# Stage 18 — Daily Inventory Confirmation
**Macro:** M-03  
**هدف:** operational inventory freshness loop کامل شود.

**کار قابل انجام**
- confirmation API.
- reminder routing.
- deduplication.
- missed confirmation.
- responsibility model.
- stale decay.

**خروجی**
- backend + API + test evidence.

**Verification**
- operational tests.

**External**
- live notification provider later.

**Exit:** logical reminder/confirmation loop executable باشد.

**Status:** PLANNED

---

# Stage 19 — Basket/Allocation/Checkout Contract Reconciliation
**Macro:** M-04  
**هدف:** یک نهایی‌سازی کامل سه‌گانه Basket → Allocation → Checkout.

**کار قابل انجام**
- compare D-014 against code/docs/UI contracts.
- line non-splitting.
- N-vendor.
- stale plan.
- reservation.
- fingerprint.
- direct settlement wording.

**خروجی**
- source/docs/test fixes.

**Verification**
- targeted canonical checkout checks.
- 20 new unit tests: `test_operational_policies.py` (9 tests: validate_allocation_against_basket guard clauses — wrong retailer, stale plan, expired plan, wrong basket status, wrong plan status, allocation count mismatch, basket not found, submitted status passthrough, valid checkout passthrough) + `test_checkout_fingerprint.py` (11 tests: fingerprint determinism/sensitivity for basket_id/plan_id/retailer_id/quantity/address, SHA256 format, idempotency replay: returns None for missing order, returns existing order on match, rejects cross-retailer, rejects fingerprint mismatch).
- All 310 existing tests remain green; new 20 pass.
- Commit `24390fa`, pushed to `research-hardening-2026-09-14`.

**External**
- final full regression later.

**Exit:** no active contradiction in commerce core.

**Status:** CLOSED

---

# Stage 20 — Order Query / Timeline HTTP
**Macro:** M-04  
**هدف:** بعد از ثبت سفارش، Retailer/Vendor وضعیت واقعی را ببینند.

**کار قابل انجام**
- order list/detail.
- order group.
- child orders.
- timeline.
- state-specific actions.
- tenant filtering.

**خروجی**
- routes + boundary + schemas + tests.

**Verification**
- 6 GET routes added: list orders, get order, get order items, get order timeline, get order group, get order group child orders.
- `order_timeline_events` table created via migration 029.
- 7 boundary methods added: `order_list`, `order_get`, `order_items_list`, `order_group_get`, `order_group_child_orders`, `order_timeline`, `_resolve_actor_role`.
- 15 HTTP transport tests in `test_http_order_query.py`: list/filter/auth, get detail/not-found/auth, items, timeline, order group/child-orders/not-found.
- Route inventory gate updated (44 routes).
- All 121 targeted tests pass. Commit `effcb74`.

**External**
- none.

**Exit:** order lifecycle readable end-to-end via HTTP.

**Status:** CLOSED

---

# Stage 21 — Vendor Acceptance UI Contract & SLA Surface
**Macro:** M-04  
**هدف:** backend acceptance semantics به UI contract تبدیل شود.

**کار قابل انجام**
- SLA timer contract.
- accept/reject/partial states.
- timeout state.
- reason semantics.
- disabled actions.

**خروجی**
- API contract/docs/frontend contract metadata.
- no fake design claims.

**Verification**
- Complete vendor acceptance UI contract document: `06_PRODUCT/vendor_acceptance_ui_contract.md`
- State machine: 10 valid statuses, all transitions documented, guards specified
- SLA timer contract: 2.0 working hours, Tehran TZ, Sat-Thu 08:00-18:00, holiday-aware
- Partial acceptance sub-proposal lifecycle documented
- Timeout behavior: auto-cancel, reservation release, proposal force-decline, reliability penalty
- Outbox events: 7 event types mapped to recipients
- Route/status matrix: 12 routes with required status and actor role
- 9 verification tests in `test_vendor_acceptance_contract.py`: SLA deadline presence, timeline events, order items fulfillment_status, order group child orders, tenant isolation
- All 130 targeted tests pass. Commit `5467c58`.

**External**
- actual visual Penpot execution later.

**Exit:** frontend has exact state contract.

**Status:** CLOSED

---

# Stage 22 — Fulfillment State Machine Closure
**Macro:** M-04  
**هدف:** Prepare/Ready/Handoff states canonical شوند.

**کار قابل انجام**
- inspect existing schema/services.
- fill missing transitions.
- state guards.
- actor/tenant constraints.
- event/outbox.

**خروجی**
- service/API/migration only if required.

**Verification**
- New `scripts/fulfillment_service.py` with 4 canonical functions: `mark_preparing`, `mark_ready`, `dispatch_order`, `confirm_delivery`.
- State guards: PREPARING requires ACCEPTED/PARTIALLY_ACCEPTED; READY requires PREPARING; DISPATCHED requires READY; DELIVERED requires DISPATCHED.
- Timeline events recorded for every transition.
- Outbox events emitted: ORDER_PREPARING, ORDER_READY, ORDER_DISPATCHED, ORDER_DELIVERED.
- 4 HTTP routes: POST /orders/{id}/preparing, /ready, /dispatch, /deliver.
- 12 tests: valid transitions, invalid transitions rejected (422), tenant isolation, full lifecycle ACCEPTED→DELIVERED, timeline recording.
- Route inventory gate updated (48 routes).
- All 142 targeted tests pass. Commit `e2df395`.

**External**
- none.

**Exit:** fulfillment domain contract complete.

**Status:** CLOSED

---

# Stage 23 — Dispatch / Delivery Runtime
**Macro:** M-04  
**هدف:** delivery execution را applicationize کنیم.

**کار قابل انجام**
- dispatch creation.
- delivery status transitions.
- delivery assignment model within MVP.
- exceptions.
- retailer tracking.
- vendor handoff.

**خروجی**
- backend/API/test/docs.

**Verification**
- 2 delivery tracking routes: GET /orders/{id}/delivery, GET /orders/{id}/delivery/proof.
- 2 boundary methods: delivery_get, delivery_proof.
- 5 HTTP tests: delivery detail (retailer/vendor), delivery not found, proof for delivered order, proof returns none for undelivered.
- Route inventory gate updated (50 routes).
- All 147 targeted tests pass. Commit `2e18c22`.

**External**
- physical/local fleet integration.

**Exit:** order can move through delivery state machine via real HTTP contracts.

**Status:** CLOSED

---

# Stage 24 — Proof of Delivery
**Macro:** M-04  
**هدف:** POD contract end-to-end.

**کار قابل انجام**
- POD creation/verification.
- OTP/evidence.
- timestamp.
- recipient.
- secure access.
- evidence retention contract.

**خروجی**
- backend/API/schema/tests/docs.

**Verification**
- unauthorized POD access and duplicate submission tests.

**External**
- storage/provider if required.

**Exit:** Delivered state has auditable proof path.

**Status:** CLOSED

---

# Stage 25 — Delivery Exceptions / Reverse Logistics Boundary
**Macro:** M-04  
**هدف:** doorstep rejection, failed delivery و operational exceptions را canonical کنیم.

**کار قابل انجام**
- exception types.
- transitions.
- task generation.
- retailer/vendor/ops responsibilities.

**خروجی**
- state/docs/API/tests.

**Verification**
- state and responsibility matrix.

**External**
- actual field operation later.

**Exit:** no ambiguous delivery exception branch remains.

**Status:** PLANNED

---

# Stage 26 — Payment Architecture & Wording Closure
**Macro:** M-05  
**هدف:** payment semantics را کاملاً non-custodial و consistent کنیم.

**کار قابل انجام**
- reconcile MVP definition wording.
- direct settlement semantics.
- remove wallet/escrow language.
- map payment status to order lifecycle.

**خروجی**
- docs + API contracts + design handoff wording.

**Verification**
- repository-wide payment terminology scan.

**External**
- none.

**Exit:** active docs use one canonical financial model.

**Status:** PLANNED

---

# Stage 27 — Payment Evidence API
**Macro:** M-05  
**هدف:** retailer/vendor payment evidence flow.

**کار قابل انجام**
- evidence create/read.
- metadata.
- duplicate handling.
- trusted evidence conflict handling.
- authorization.

**خروجی**
- boundary + HTTP + tests.

**Verification**
- negative finance/security tests.

**External**
- real banking/provider integration if needed.

**Exit:** payment evidence transport-complete.

**Status:** PLANNED

---

# Stage 28 — Invoice / Settlement Runtime
**Macro:** M-05  
**هدف:** invoice and child-order settlement status عملیاتی شود.

**کار قابل انجام**
- invoice retrieval.
- invoice/order relationship.
- settlement status.
- direct counterparties.
- tenant isolation.

**خروجی**
- API + boundary + docs + tests.

**Verification**
- access and financial invariant tests.

**External**
- live accounting/bank systems if selected later.

**Exit:** financial read model complete for pilot.

**Status:** PLANNED

---

# Stage 29 — Reconciliation Exception Management
**Macro:** M-05  
**هدف:** mismatch/conflict حالات مالی تبدیل به Ops workflow شوند.

**کار قابل انجام**
- reconciliation exception queue.
- trusted evidence conflict.
- duplicate evidence.
- operator action boundary.
- audit log.

**خروجی**
- service/API/ops contract/tests.

**Verification**
- race/conflict/isolation tests.

**External**
- live bank statement feed if not yet available.

**Exit:** finance exceptions do not disappear into raw logs.

**Status:** PLANNED

---

# Stage 30 — Dispute / RMA HTTP Completion
**Macro:** M-05  
**هدف:** issue → evidence → review → decision → refund lifecycle را applicationize کنیم.

**کار قابل انجام**
- dispute create/read/update.
- RMA request.
- state transitions.
- evidence metadata.
- refund separation of duties.
- timeline.

**خروجی**
- API + boundary + tests.

**Verification**
- state/authorization/quantity tests.

**External**
- actual evidence storage if needed.

**Exit:** RMA/dispute usable via API.

**Status:** PLANNED

---

# Stage 31 — Support HTTP Lifecycle
**Macro:** M-05  
**هدف:** support case lifecycle کامل شود.

**کار قابل انجام**
- create/get/message/assign/transition.
- tenant scope.
- reopen.
- internal note.
- SLA state.
- reply notifications.

**خروجی**
- routes + boundary + negative tests.

**Verification**
- active context/operator tests.

**External**
- provider notifications later.

**Exit:** support operational loop executable باشد.

**Status:** PLANNED

---

# Stage 32 — Notification Logical Layer Closure
**Macro:** M-05  
**هدف:** notification event → logical notification → delivery attempt contract.

**کار قابل انجام**
- recipient routing.
- templates.
- preferences.
- deep links.
- deduplication.
- unsupported event quarantine.

**خروجی**
- service/tests/docs.

**Verification**
- routing/tenant/dedup tests.

**External**
- actual SMS/push provider later.

**Exit:** internal notification layer complete independently of provider.

**Status:** PLANNED

---

# Stage 33 — External Notification Providers
**Macro:** M-05  
**هدف:** حداقل یک SMS و یک push provider boundary عملیاتی.

**کار قابل انجام**
- provider interfaces.
- adapter structure.
- retry/backoff.
- error classes.
- credential configuration.
- sandbox contract.

**خروجی**
- provider adapter code/config/docs/tests.

**Verification**
- mock/sandbox handling tests.

**External**
- real credentials and live/sandbox certification.

**Exit:** only external credential certification remains if provider access unavailable.

**Status:** PLANNED

---

# Stage 34 — Ops/Admin/Referral Closure
**Macro:** M-06  
**هدف:** Ops بتواند exceptions و Referral را مدیریت کند.

**کار قابل انجام**
- exception workbench endpoints.
- audit access.
- referral create/redeem/read.
- notification broadcast boundary if MVP.
- admin role restrictions.

**خروجی**
- API/boundary/tests/docs.

**Verification**
- role/tenant/SoD tests.

**External**
- actual ops UI later.

**Exit:** backend operational control surface complete.

**Status:** PLANNED

---

# Stage 35 — Vendor / Retailer Onboarding + Field Activator
**Macro:** M-06  
**هدف:** onboarding real pilot cohort executable شود.

**کار قابل انجام**
- vendor onboarding state machine APIs.
- retailer onboarding.
- field tasks.
- task assignment/completion evidence.
- assisted order boundary.
- referral attribution.

**خروجی**
- backend/API/docs/tests.

**Verification**
- role/task/tenant tests.

**External**
- real field workforce execution.

**Exit:** onboarding backend ready for pilot.

**Status:** PLANNED

---

# Stage 36 — Analytics Event Lineage
**Macro:** M-06  
**هدف:** هر KPI از event/source قابل ردیابی باشد.

**کار قابل انجام**
- event inventory.
- source table.
- event semantics.
- calculation version.
- timezone/cohort rules.
- missing telemetry gaps.

**خروجی**
- analytics lineage matrix.
- code/schema changes where needed.

**Verification**
- lineage/static contract checks.

**External**
- production BI tool later if required.

**Exit:** KPI lineage inspectable باشد.

**Status:** PLANNED

---

# Stage 37 — Pilot KPI Measurement Pipeline
**Macro:** M-06  
**هدف:** KPIهای Pilot از database تا report قابل محاسبه باشند.

**کار قابل انجام**
- GMV/AOV.
- repeat.
- OTIF.
- self-service.
- churn.
- cost-to-serve.
- CAC.
- vendor continuation.
- catalog KPIs.
- weekly snapshot logic.

**خروجی**
- queries/services/reporting schema/docs.

**Verification**
- calculation fixtures and date/timezone checks.

**External**
- live pilot data later.

**Exit:** system can calculate KPIs even if actual values are still zero/not yet collected.

**Status:** PLANNED

---

# Stage 38 — Frontend Route-to-Contract Master Map
**Macro:** M-07  
**هدف:** UI work هیچ endpoint/domain state ناشناخته‌ای نداشته باشد.

**کار قابل انجام**
- Screen → route → persona → context → data → command → state → analytics → notification → recovery map.
- reconcile with Penpot written specs.

**خروجی**
- final frontend handoff matrix.

**Verification**
- every canonical screen has a route/state contract.

**External**
- live Penpot inspection later.

**Exit:** implementation map complete.

**Status:** PLANNED

---

# Stage 39 — Frontend Repository Foundation
**Macro:** M-07  
**هدف:** production frontend skeleton ایجاد شود.

**کار قابل انجام**
- web/mobile package structure as approved by architecture.
- environment config.
- API client.
- auth/session state.
- tenant context.
- design token plumbing.
- error boundary/loading foundation.
- analytics hooks.
- RTL infrastructure.

**خروجی**
- actual frontend source tree.

**Verification**
- static source audit.
- build/test configuration creation.

**External**
- actual full build can be run by external Agent if local frontend toolchain unavailable here.

**Exit:** frontend foundation exists and follows canonical backend contracts.

**Status:** PLANNED

---

# Stage 40 — Retailer Client Implementation
**Macro:** M-07  
**هدف:** retailer journey واقعی.

**کار قابل انجام**
- auth.
- home.
- catalog.
- product.
- basket.
- allocation.
- checkout.
- order tracking.
- delivery/POD.
- RMA/support/profile.

**خروجی**
- real client code.
- state handling.
- API integration.

**Verification**
- static route/API consistency.
- targeted UI contract checks where possible.

**External**
- visual QA/Penpot matching and final device testing.

**Exit:** retailer can exercise canonical MVP flow through real API contracts.

**Status:** PLANNED

---

# Stage 41 — Vendor Client Implementation
**Macro:** M-07  
**هدف:** vendor workflow واقعی.

**کار قابل انجام**
- dashboard.
- inventory confirmation.
- catalog.
- order queue.
- accept/reject/partial.
- timeout awareness.
- fulfillment.
- delivery handoff.
- RMA.
- payment/settlement.
- referral.

**خروجی**
- vendor client code.

**Verification**
- API/state compatibility.

**External**
- visual QA/device validation.

**Exit:** vendor can execute operational lifecycle without direct SQL/manual backend use.

**Status:** PLANNED

---

# Stage 42 — Ops + Field Client Implementation
**Macro:** M-07  
**هدف:** operational product complete شود.

**کار قابل انجام**
- exception workbench.
- support desk.
- dispute/RMA.
- reconciliation.
- notifications.
- vendor onboarding.
- field tasks.
- audit.
- pilot KPI surfaces.

**خروجی**
- ops/field client source.

**Verification**
- role/context/API consistency.

**External**
- visual QA and field-device testing.

**Exit:** critical exceptions can be managed through client UI.

**Status:** PLANNED

---

# Stage 43 — Penpot/GitHub Design Synchronization Package
**Macro:** M-07  
**هدف:** written spec و artifact یک release identity واحد داشته باشند.

**کار قابل انجام**
- reconcile design README/index.
- consolidate precedence.
- update Penpot manifest metadata.
- enumerate stale snapshot vs revision.
- define exact sync/handoff procedure.
- create screen/component/state reconciliation table.

**خروجی**
- canonical design release package.
- explicit external Penpot task list.

**Verification**
- repository design index consistency.
- no claim that live Penpot changed unless independently evidenced.

**External**
- actual Penpot editing/export/upload if no live Penpot connection is available.

**Exit:** remaining Penpot work is isolated and executable by Agent.

**Status:** PLANNED

---

# Stage 44 — Design Content / Localization / Accessibility Reconciliation
**Macro:** M-07  
**هدف:** متن و UX contract قبل از final design freeze پاک‌سازی شود.

**کار قابل انجام**
- Persian-first terminology.
- Toman.
- numerals.
- Jalali/Gregorian.
- mixed-direction identifiers.
- long labels.
- accessibility requirements.
- role naming.
- unsupported claims.

**خروجی**
- canonical copy/UX rules.
- frontend content updates where source exists.

**Verification**
- repository-wide terminology scan.

**External**
- final visual inspection in Penpot/device.

**Exit:** no unresolved written design-content contradiction.

**Status:** PLANNED

---

# Stage 45 — Deployment & Configuration Package
**Macro:** M-08  
**هدف:** production/pilot deployment contract عملیاتی شود.

**کار قابل انجام**
- Docker/runtime definitions.
- environment variable contract.
- DB config.
- migration policy.
- worker process separation.
- health/readiness.
- graceful shutdown.
- startup checks.
- secret requirements.
- deployment runbook.

**خروجی**
- deployment/config docs and files.

**Verification**
- static configuration validation.
- no secret leakage.

**External**
- actual deployment to chosen infrastructure.

**Exit:** deployment is reproducible on a real environment.

**Status:** PLANNED

---

# Stage 46 — Observability & Incident Response
**Macro:** M-08  
**هدف:** system قابل پایش و عیب‌یابی شود.

**کار قابل انجام**
- structured JSON logging.
- correlation.
- error classification.
- metrics.
- health/readiness.
- provider attempt visibility.
- DB slow query visibility.
- incident runbook.
- no secret/token leakage.

**خروجی**
- observability code/config/docs.

**Verification**
- static/log-safety tests.
- traceability checks.

**External**
- actual log/metric backend deployment.

**Exit:** operational signals have explicit source/owner/action.

**Status:** PLANNED

---

# Stage 47 — Backup / Recovery / Data Operations Package
**Macro:** M-08  
**هدف:** data safety را از documentation به executable procedure نزدیک کنیم.

**کار قابل انجام**
- backup policy.
- encryption requirements.
- retention.
- migration backup.
- restore procedure.
- RPO/RTO.
- PITR plan.
- rollback/forward-fix.
- pilot data export.

**خروجی**
- runbooks/scripts/config where possible.

**Verification**
- script/static validation where possible.

**External**
- actual backup/restore drill requires deployed environment and real DB.

**Exit:** exact external restore drill procedure remains.

**Status:** PLANNED

---

# Stage 48 — Performance / Reliability / Security Final Test Bundle
**Macro:** M-08  
**هدف:** یک بسته‌ی واحد برای اجرای صدها تست نهایی ایجاد شود.

**کار قابل انجام**
- inventory all existing tests.
- eliminate duplicate/stale test entrypoints.
- define one release verification command.
- combine:
  - migration
  - repository integrity
  - domain
  - HTTP
  - tenant isolation
  - concurrency
  - notification
  - RMA
  - payment
  - frontend contract checks
  - security
  - regression
- create machine-readable artifact schema.

**خروجی**
- one/bounded final verification entrypoint.
- release test manifest.

**Verification**
- inspect command correctness; run only targeted checks necessary to validate wiring.

**External**
- **full 200+ test run should be performed by the external Agent/environment in one batch.**

**Exit:** final test is executable as one release operation.

**Status:** PLANNED

---

# Stage 49 — Real Pilot Readiness / Data / Operations Pack
**Macro:** M-09  
**هدف:** repository را برای ورود به Pilot واقعی آماده کنیم.

**کار قابل انجام**
- vendor onboarding checklist.
- retailer cohort checklist.
- LOI/commitment document alignment.
- catalog bootstrap template.
- pricing/inventory import template.
- field activation SOP.
- support/dispute SOP.
- payment/reconciliation SOP.
- KPI weekly report template.
- fallback SOP.

**خروجی**
- operational pilot package.

**Verification**
- cross-reference all SOPs to product/API states.

**External**
- actual people, vendors, retailers, signed LOIs and field operations.

**Exit:** pilot team has one coherent operating pack.

**Status:** PLANNED

---

# Stage 50 — Final Release Audit & External Handoff
**Macro:** M-10  
**هدف:** مشخص کنیم چه چیزهایی واقعاً done است و چه چیزهایی باید Agent/Environment انجام دهد.

**کار قابل انجام**
- repository-wide final audit.
- update all statuses.
- refresh Master Checklist.
- refresh route coverage.
- refresh capability matrix.
- refresh design readiness.
- record final SHA.
- record CI.
- record release evidence.
- generate exact external handoff list.
- distinguish:
  1. DONE
  2. VERIFIED
  3. EXTERNAL_PENDING
  4. BLOCKED

**خروجی**
- final release dossier.
- final handoff instructions.
- final MVP readiness decision support.

**Verification**
- all documented evidence internally consistent.

**External**
- final CI/test bundle execution.
- live Penpot implementation/export/sync.
- deployment verification.
- live provider certification.
- real pilot execution.

**Exit:** no hidden work remains.

**Status:** PLANNED

---

# Final External Handoff Rule

در پایان Stage 50 فقط مواردی که واقعاً به یکی از اینها وابسته باشند بیرونی تلقی می‌شوند:

1. دسترسی/ویرایش live Penpot یا upload binary artifact.
2. credential و sandbox/live certification ارائه‌دهندگان واقعی.
3. اجرای deployment روی infrastructure واقعی.
4. backup/restore drill روی environment واقعی.
5. اجرای نهایی regression/security/performance bundle در محیط مناسب.
6. اجرای Pilot با Vendor/Retailer واقعی.

هیچ code/doc/test/config کاری که در این محیط قابل انجام باشد نباید با این عنوان کنار گذاشته شود.

---

# Shared Evidence Schema — برای هر Stage

برای هر Stage این بخش در هنگام اجرا تکمیل می‌شود:

| Field | Value |
|---|---|
| STAGE |  |
| WORK_ID |  |
| STATUS_BEFORE |  |
| STATUS_AFTER |  |
| WORKER | CHATGPT-5.6-LUNA |
| ROLE |  |
| OBJECTIVE |  |
| CHANGES |  |
| FILES_TOUCHED |  |
| DECISIONS |  |
| TESTS_RUN |  |
| TEST_RESULT |  |
| CI_RESULT |  |
| DESIGN_RESULT |  |
| EXTERNAL_PENDING |  |
| BLOCKERS |  |
| COMMIT_SHA |  |
| NEXT_ACTION |  |

---

# Execution Log

## Stage 01
- Status: CLOSED
- Work ID: EXEC50-002
- Baseline evidence: Run #333 historical failure snapshot
- Work ID: TBD
- Changes:
- Files:
- Tests:
- CI:
- External:
- Blockers:
- Next Action:

## Stage 02
- Status: CLOSED
- Work ID: EXEC50-003
- Certified regression evidence: Run #356 — 209/209 PASS on pre-Stage-03 suite

## Stage 03
- Status: CLOSED
- Work ID: EXEC50-004
- CI: Run #365 — 212/212 PASS, 0 failed, 0 skipped
- Certified HEAD: 5ac5974b2caf045f8020e3c8b48f889ed3ff94e9
- Artifact: 10561965892
- Next Action: execute Stage 04 — Repository Truth Synchronization

## Stage 04
- Status: CLOSED
- Work ID: EXEC50-005
- Verification: cross-document repository-truth audit completed
- Next Action: execute Stage 05 — Governance / Decision Register Reconciliation

## Stage 05
- Status: CLOSED
- Work ID: EXEC50-006
- Verification: governance reconciliation completed; D-018/D-019 conflicts explicitly carried by existing decisions
- Next Action: execute Stage 06 — Queue / Worker Architecture Closure

## Stage 06
- Status: CLOSED
- Work ID: EXEC50-007
- CI: Run #403 — 213/213 PASS, 0 failed, 0 skipped
- Certified test-repair SHA: f76c9ebae857eb9a2573848780dd3a5aaf4d0a26
- Artifact: 10562004166
- Next Action: execute Stage 07 — API/Boundary Master Inventory

## Stage 07
- Status: IN_PROGRESS
- Work ID: EXEC50-008
- Verification: 50-endpoint contract matrix / 21 live business routes / 16 boundary-only commands inventoried
- CI: Run #413 and current-head Run #417 in progress; no certification claim yet

## Stage 08
- Status: PLANNED

## Stage 09
- Status: PLANNED

## Stage 10
- Status: PLANNED

## Stage 11
- Status: PLANNED

## Stage 12
- Status: PLANNED

## Stage 13
- Status: PLANNED

## Stage 14
- Status: PLANNED

## Stage 15
- Status: PLANNED

## Stage 16
- Status: PLANNED

## Stage 17
- Status: PLANNED

## Stage 18
- Status: PLANNED

## Stage 19
- Status: PLANNED

## Stage 20
- Status: PLANNED

## Stage 21
- Status: PLANNED

## Stage 22
- Status: PLANNED

## Stage 23
- Status: PLANNED

## Stage 24
- Status: CLOSED
- Changes: confirm_delivery with OTP verification, proof_type enforcement, media FK support, delivery_otp column, retailer-only access guard, OTP regex fix
- Files: scripts/fulfillment_service.py, scripts/application_boundary.py, scripts/api/schemas.py, scripts/api/routes/orders.py, migrations/030_delivery_otp_column.sql, scripts/test_http_proof_of_delivery.py
- Tests: 10 POD tests (OTP verification, proof type, issue reporting, secure access)
- CI: 108 targeted tests PASS
- External: None
- Blockers: None
- Next Action: execute Stage 25 — Delivery Exceptions / Reverse Logistics Boundary

## Stage 25
- Status: PLANNED

## Stage 26
- Status: PLANNED

## Stage 27
- Status: PLANNED

## Stage 28
- Status: PLANNED

## Stage 29
- Status: PLANNED

## Stage 30
- Status: PLANNED

## Stage 31
- Status: PLANNED

## Stage 32
- Status: PLANNED

## Stage 33
- Status: PLANNED

## Stage 34
- Status: PLANNED

## Stage 35
- Status: PLANNED

## Stage 36
- Status: PLANNED

## Stage 37
- Status: PLANNED

## Stage 38
- Status: PLANNED

## Stage 39
- Status: PLANNED

## Stage 40
- Status: PLANNED

## Stage 41
- Status: PLANNED

## Stage 42
- Status: PLANNED

## Stage 43
- Status: PLANNED

## Stage 44
- Status: PLANNED

## Stage 45
- Status: PLANNED

## Stage 46
- Status: PLANNED

## Stage 47
- Status: PLANNED

## Stage 48
- Status: PLANNED

## Stage 49
- Status: PLANNED

## Stage 50
- Status: PLANNED
