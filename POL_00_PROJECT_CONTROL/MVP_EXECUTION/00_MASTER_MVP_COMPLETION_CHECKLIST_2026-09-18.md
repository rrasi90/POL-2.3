# POL — Master MVP Completion Checklist
## مسیر کامل از وضعیت فعلی مخزن تا MVP Pilot-Ready

**تاریخ:** 2026-09-18  
**مخزن:** `rrasi90/POL-2.3`  
**Branch مورد بررسی:** `research-hardening-2026-09-14`  
**HEAD مشاهده‌شده در مخزن:** `f97b1a86cd3e9f3b9c4b8d74f07c94f44823b260`  
**Baseline قبلی سبز:** `09ea9b1eed617031441801c8826311a6a6b1856f`

---

# 0. تعریف دقیق «MVP کامل»

در این برنامه، «MVP کامل» صرفاً به معنی سبز شدن تست‌های Domain نیست.

MVP کامل POL باید حداقل به این نقطه برسد:

> یک Retailer واقعی بتواند از طریق client واقعی وارد شود، کاتالوگ و آفر Vendorها را ببیند، سبد بسازد، allocation را بررسی کند، checkout کند، سفارش‌های Vendorها را پیگیری کند، تحویل را ببیند، پرداخت/تسویه مستقیم را ثبت و پیگیری کند، مغایرت یا RMA ثبت کند و از Support استفاده کند؛  
> یک Vendor واقعی بتواند catalog/price/inventory خود را مدیریت کند، سفارش را قبول/رد/partial-accept کند، fulfillment/delivery handoff را انجام دهد، شواهد پرداخت را مدیریت کند و مسائل RMA/Support را پاسخ دهد؛  
> و تیم Ops بتواند onboarding، exception، support، dispute، reconciliation، notification و audit را مدیریت کند؛  
> همه این مسیرها از HTTP واقعی، Auth واقعی، PostgreSQL واقعی، Outbox/Worker واقعی و UI واقعی عبور کنند و با تست E2E قابل بازتولید باشند.

این با «Production at Scale» یکی نیست. بعد از MVP Pilot، کارهای scale، advanced AI، BNPL، loyalty، advertising، owned logistics و سایر قابلیت‌های خارج از MVP باقی می‌مانند.

---

# 1. وضعیت واقعی فعلی — Snapshot

## 1.1 چیزهایی که در هسته سیستم موجود و بسیار جلو رفته‌اند

- [x] معماری اصلی `Retailer → Basket → Allocation → Checkout → Vendor Order → Fulfillment → Delivery → Settlement → Data`
- [x] PostgreSQL 18 به عنوان DB کانونیکال
- [x] زنجیره Migrationهای 001 تا 028
- [x] tenant / organization / membership architecture
- [x] canonical RBAC بر مبنای `organization_memberships.role`
- [x] universal user profile + membership/persona model
- [x] basket versioning
- [x] deterministic allocation
- [x] checkout revalidation
- [x] inventory reservation
- [x] order group / child order model
- [x] vendor accept
- [x] vendor reject
- [x] partial acceptance دوطرفه
- [x] vendor acceptance timeout domain contract
- [x] outbox / integration / provider-delivery architecture
- [x] payment reconciliation foundation
- [x] RMA / refund integrity foundation
- [x] support / feedback foundation
- [x] referral foundation
- [x] daily inventory foundation
- [x] concurrency / tenant-isolation / state-machine tests
- [x] FastAPI transport foundation
- [x] Auth transport foundation
- [x] basket / allocation HTTP routes
- [x] checkout HTTP route
- [x] vendor accept/reject/partial-acceptance HTTP routes

## 1.2 مواردی که هنوز MVP را «کامل» نمی‌کنند

- [ ] Batch 6C-7 را روی یک SHA جدید commit/push و CI-certified کنیم.
- [ ] تمام routeهای کانونیکال باقی‌مانده را از Application Boundary تا HTTP تکمیل کنیم.
- [ ] production Auth/OTP/SMS را واقعی کنیم.
- [ ] refresh-token policy را نهایی کنیم.
- [ ] rate limiting و session/security infrastructure را production-grade کنیم.
- [ ] provider واقعی SMS و Push را certify کنیم.
- [ ] frontend واقعی بسازیم؛ در HEAD فعلی frontend production در repository وجود ندارد.
- [ ] retailer app / vendor web / ops web / field app را به API واقعی متصل کنیم.
- [ ] fulfillment / dispatch / delivery / POD transport را کامل کنیم.
- [ ] payment evidence / payment verification / settlement transport را کامل کنیم.
- [ ] disputes / RMA / support / notifications / inbox / invoice / admin routes را کامل کنیم.
- [ ] deployment و staging environment بسازیم.
- [ ] observability و alerting اضافه کنیم.
- [ ] backup / restore / migration runbook را certify کنیم.
- [ ] catalog و pilot inventory واقعی را seed و validate کنیم.
- [ ] vendor و retailer onboarding عملیاتی را اجرا کنیم.
- [ ] telemetry و KPI dashboard را به داده واقعی متصل کنیم.
- [ ] E2E واقعی از UI تا DB و provider را اجرا و certify کنیم.
- [ ] design / Penpot را به implementation واقعی و QA تصویری متصل کنیم.

---

# 2. نکته بحرانی درباره Batch 6C-7

گزارش OpenCode اعلام کرده است:

- timeout suite: `6/6`
- Checkout Gateway: `3/3`
- Checkout HTTP: `6/6`
- E2E: `17/17`
- regression groups: سبز
- full regression: `209/209`
- repository consistency: `8/8`
- environment: `28 migrations / 93 tables`
- diff-check: clean

اما این نتیجه هنوز در SHA فعلی GitHub (`f97b1a8...`) ثبت نشده است.

GitHub برای همین SHA یک workflow شکست‌خورده دارد:

`POL Independent Verification & Certification CI`  
Run `#326` / `35368804736` → `failure`

بنابراین:

**وضعیت Batch 6C-7 در این فایل: `LOCALALLY VERIFIED / NOT YET REPOSITORY-CERTIFIED`**

قبل از هر Batch بعدی:

- [ ] import fix را commit کنیم.
- [ ] `created_at` mismatch fix را commit کنیم.
- [ ] `pg_connection` fixture fix را commit کنیم.
- [ ] replacement `MIN(uuid)` را بازبینی کنیم و مطمئن شویم `LIMIT 1` با `ORDER BY` deterministic است.
- [ ] `git diff --check`
- [ ] `git status`
- [ ] commit
- [ ] push
- [ ] CI روی SHA جدید
- [ ] فقط در صورت CI green، 6C-7 = CLOSED

---

# 3. PASS 1 — Repository / Governance Review

این پاس بررسی می‌کند آیا برنامه با SSoT و Decision Register سازگار است یا نه.

## 3.1 Governance Sync

- [ ] `DECISION_REGISTER.md` همچنان تنها مرجع تصمیم‌های D-001 تا D-020 باشد.
- [ ] D-019 (Python production runtime) در تمام docs همگام شود.
- [ ] D-020 (FastAPI) در تمام docs همگام شود.
- [ ] هر سندی که هنوز NestJS/Fastify را runtime نهایی معرفی می‌کند اصلاح یا archive شود.
- [ ] هر سندی که Python را فقط test runtime می‌داند اصلاح شود.
- [ ] `GLOBAL_ENGINEERING_AUDIT` قدیمی با architecture فعلی sync یا به‌عنوان historical علامت‌گذاری شود.
- [ ] `CAPABILITY_COVERAGE_MATRIX.md` از وضعیت قدیمی NestJS/19 migration/90-table به وضعیت فعلی repository sync شود.
- [ ] `TEST_VERIFICATION_MANIFEST.md` از baselineهای قدیمی (56 table / migrationهای قدیمی) به baseline فعلی sync شود.
- [ ] اسناد architecture/runtime فعلی یک precedence واضح داشته باشند.
- [ ] contradiction log بعد از sync مجدداً اجرا شود.

## 3.2 Queue / Worker Architecture Contradiction

در architecture فعلی دو گزاره همزمان دیده می‌شوند:

- Python runtime به عنوان runtime authoritative.
- BullMQ بر Redis به عنوان queue engine.

BullMQ یک runtime/library وابسته به Node است و با «single Python runtime / no Node-Python dual runtime» بدون تصمیم تکمیلی سازگار نیست.

- [ ] تصمیم صریح برای worker/queue runtime ثبت شود.
- [ ] یکی از این دو مسیر انتخاب شود:
  - [ ] Python-native worker + Redis
  - [ ] PostgreSQL outbox polling + scheduler بدون queue جداگانه در MVP
  - [ ] یا هر گزینه دیگری با Decision ID صریح.
- [ ] BullMQ به عنوان dependency اجرایی ناخواسته باقی نماند.
- [ ] worker ownership و retry/DLQ semantics بعد از این تصمیم دوباره certify شود.

---

# 4. PASS 2 — Domain → Boundary → HTTP Coverage Review

## 4.1 Auth / Identity

### موجود
- [x] request OTP route
- [x] verify OTP route
- [x] refresh route
- [x] organization switch
- [x] session revoke
- [x] ApplicationContext

### باقی‌مانده
- [ ] production OTP provider
- [ ] real secret management
- [ ] JWT secret rotation policy
- [ ] OTP abuse/rate-limit runtime
- [ ] device/session management UI
- [ ] refresh-token rotation decision طبق D-018
- [ ] refresh-token reuse detection در صورت انتخاب rotation
- [ ] session revocation end-to-end
- [ ] cross-device/session negative tests از HTTP واقعی
- [ ] 401/403 semantics در تمام transport routes
- [ ] security audit of auth middleware
- [ ] production logging بدون leakage از OTP/token/PII

### Delivery OTP
درباره OTP تحویل، D-018 policy آن را از login OTP جدا کرده است.

- [ ] تصمیم canonical برای delivery OTP digits / lifetime / retry / lockout
- [ ] implement در صورت استفاده
- [ ] transport + UI + tests
- [ ] در غیر این صورت delivery confirmation را با روش دیگری canonical کنیم.

---

# 5. Catalog / Product Discovery — باید تا MVP واقعی شود

## وضعیت فعلی
Domain/schema و Master SKU research وجود دارد، ولی route/client production برای این جریان در tree فعلی کامل نیست.

### Backend
- [ ] canonical product search boundary
- [ ] product detail query
- [ ] category tree
- [ ] vendor-offer comparison query
- [ ] vendor SKU mapping query
- [ ] barcode exact-match API
- [ ] ambiguous/no-match candidate flow
- [ ] product candidate review flow برای Ops
- [ ] active price filtering
- [ ] effective-date price handling
- [ ] inventory freshness states
- [ ] MOQ/MOV visibility
- [ ] vendor availability state
- [ ] search pagination / query limits
- [ ] search error / empty state contract

### Vendor Catalog Management
- [ ] vendor listing creation
- [ ] vendor listing update
- [ ] product activation/deactivation
- [ ] packaging metadata
- [ ] SKU code
- [ ] barcode association
- [ ] vendor-specific attributes
- [ ] tenant authorization
- [ ] catalog audit trail
- [ ] bulk import path

### Data
- [ ] pilot Master SKU dataset validated
- [ ] initial categories validated
- [ ] initial brands/products validated
- [ ] pilot vendor SKU mapping
- [ ] duplicate detection
- [ ] missing barcode handling
- [ ] price/data freshness policy
- [ ] catalog bootstrap script
- [ ] repeatable staging seed

---

# 6. Vendor Pricing / Inventory — یکی از اصلی‌ترین MVP gates

## Pricing
- [ ] vendor current price API
- [ ] price create/update HTTP
- [ ] effective-date validation
- [ ] overlap rejection
- [ ] historical price visibility
- [ ] price freshness in checkout
- [ ] vendor-side UI
- [ ] audit history

## Inventory
- [ ] physical inventory update API
- [ ] reserved quantity view
- [ ] available quantity view
- [ ] continuous scan flow
- [ ] inventory publish flow
- [ ] stale/unknown state
- [ ] atomic reservation behavior
- [ ] reservation release
- [ ] reservation consume
- [ ] reservation expiry worker
- [ ] daily confirmation UI
- [ ] missed-confirmation state
- [ ] reminder flow
- [ ] responsibility routing
- [ ] vendor-side inventory dashboard
- [ ] inventory reconciliation view

## Pilot Data
- [ ] each pilot vendor uploads agreed SKU set
- [ ] price list loaded
- [ ] inventory loaded
- [ ] freshness timestamps validated
- [ ] sample orders created against real catalog

---

# 7. Basket → Allocation → Checkout

### Already strong
- [x] basket creation
- [x] item addition
- [x] optimistic versioning
- [x] allocation preview
- [x] deterministic allocator
- [x] allocation persistence
- [x] checkout revalidation
- [x] price/stock/MOQ validation
- [x] reservations
- [x] idempotency/fingerprint
- [x] multi-vendor OrderGroup model

### Remaining
- [ ] production catalog queries feed allocation
- [ ] allocation API returns complete retailer-readable explanation
- [ ] unavailable / stale inventory UX
- [ ] price changed UX
- [ ] MOQ/MOV failure UX
- [ ] allocation expiry UX
- [ ] basket restoration
- [ ] revalidation conflict recovery
- [ ] checkout address/contact confirmation
- [ ] payment-method selection contract
- [ ] final review screen
- [ ] frontend idempotency handling
- [ ] retry-safe checkout UX
- [ ] duplicate submission UI behavior
- [ ] checkout success deep-link to order group

---

# 8. Order Lifecycle — Vendor Response

### Already implemented
- [x] accept
- [x] reject
- [x] partial acceptance proposal
- [x] partial acceptance approve
- [x] partial acceptance decline
- [x] timeout cancellation
- [x] reservation release
- [x] reliability ledger
- [x] tenant-scoped notifications

### Remaining
- [ ] vendor order list API
- [ ] vendor order detail API
- [ ] retailer order/group list API
- [ ] retailer order detail API
- [ ] order timeline API
- [ ] order state timestamps
- [ ] state-specific action availability
- [ ] notification deep-links
- [ ] timeout visibility
- [ ] pending proposal visibility
- [ ] cancellation reason rendering
- [ ] vendor acceptance SLA timer in UI
- [ ] operational queue for timed-out orders
- [ ] full negative HTTP matrix
- [ ] idempotent vendor actions from HTTP
- [ ] concurrent vendor action test through HTTP transport

---

# 9. Fulfillment / Dispatch / Delivery / POD

این قسمت یکی از بزرگ‌ترین فاصله‌های domain-to-product فعلی است.

## Backend
- [ ] `dispatch` application-boundary command
- [ ] `deliver` application-boundary command
- [ ] delivery creation semantics
- [ ] carrier/vendor responsibility
- [ ] dispatch state transition
- [ ] delivery state transition
- [ ] POD creation
- [ ] POD actor authorization
- [ ] POD evidence retention
- [ ] delivery timestamps
- [ ] failed/exception delivery path
- [ ] doorstep rejection flow
- [ ] delivery dispute linkage
- [ ] no-duplicate dispatch constraint verification
- [ ] no-duplicate delivery confirmation
- [ ] concurrency tests

## Delivery UX
- [ ] Retailer delivery tracking surface
- [ ] Vendor fulfillment queue
- [ ] Vendor dispatch confirmation
- [ ] Ops exception view
- [ ] POD status view
- [ ] evidence viewer
- [ ] delivery failure recovery
- [ ] deep-link from notification

## Scope rule
- [ ] dedicated POL Driver app NOT required unless a new decision explicitly creates it.
- [ ] physical logistics remains vendor / partner responsibility.
- [ ] no unsupported live ETA promise.

---

# 10. Payment / Invoice / Settlement

اصل MVP:
`NON-CUSTODIAL DIRECT`

یعنی POL مالک وجه یا escrow نمی‌شود.

## Payment
- [ ] payment method selection contract
- [ ] direct-transfer evidence API
- [ ] payment evidence upload / metadata
- [ ] payment verification API
- [ ] vendor verification UI
- [ ] payment state timeline
- [ ] mismatch state
- [ ] duplicate evidence handling
- [ ] trusted evidence conflict handling
- [ ] payment reconciliation worker
- [ ] reconciliation exception queue
- [ ] settlement calculation
- [ ] settlement adjustment after dispute
- [ ] direct vendor settlement status
- [ ] retailer-facing payment status

## Invoice
- [ ] invoice list API
- [ ] invoice detail API
- [ ] invoice line access-control
- [ ] invoice generation policy
- [ ] printable/PDF invoice path
- [ ] invoice numbering policy
- [ ] split child-order invoice semantics
- [ ] historical immutability test

## Security / finance
- [ ] never store POL-held customer funds
- [ ] never show wallet/escrow balance
- [ ] no unauthorized financial mutations
- [ ] audit trail for verification/adjustment
- [ ] separation of duties for refund-related actions

---

# 11. Dispute / RMA / Refund

## Disputes
- [ ] create dispute HTTP route
- [ ] list/read dispute route
- [ ] evidence upload
- [ ] item/quantity scope
- [ ] dispute deadline enforcement
- [ ] vendor response
- [ ] operator review
- [ ] resolve route
- [ ] settlement adjustment creation
- [ ] tenant isolation
- [ ] dispute does not corrupt order physical state
- [ ] vendor A settlement unaffected by vendor B dispute

## RMA
- [ ] return request HTTP route
- [ ] return item normalization
- [ ] aggregate quantity ceiling
- [ ] return state transitions
- [ ] inspection state where required
- [ ] refund linkage
- [ ] refund approval
- [ ] refund completion
- [ ] two-person separation of duties
- [ ] refund idempotency
- [ ] refund UI
- [ ] evidence/timeline UI

## Final test
- [ ] complete `DELIVERED → issue → dispute/RMA → decision → adjustment/refund → CLOSED` over actual HTTP/UI.

---

# 12. Support

Application boundary methods already exist, but the product surface is not complete.

- [ ] create case HTTP
- [ ] read case HTTP
- [ ] list cases
- [ ] send message
- [ ] assign
- [ ] transition state
- [ ] active-tenant context enforcement
- [ ] operator scope enforcement
- [ ] case SLA/age
- [ ] reopen
- [ ] attachments/evidence policy
- [ ] end-user support UI
- [ ] operator support inbox
- [ ] notification when reply arrives
- [ ] deep-link to case
- [ ] no cross-tenant support leakage
- [ ] HTTP negative tests

---

# 13. Notifications / Inbox / External Providers

## Logical notification layer
- [ ] inbox list endpoint
- [ ] mark-read endpoint
- [ ] mark-all-read endpoint
- [ ] notification preferences endpoint
- [ ] mandatory operational notices immune to optional preference suppression
- [ ] deep-link mapping
- [ ] event/template/route matrix coverage

## Integration worker
- [ ] every critical event mapped
- [ ] recipient membership verified
- [ ] unsupported events quarantined
- [ ] retry/backoff
- [ ] terminal FAILED state
- [ ] dedupe
- [ ] correlation_id propagation

## External delivery
- [ ] SMS provider selection
- [ ] SMS.ir credentials provisioned outside Git
- [ ] SMS template approved
- [ ] test OTP delivery
- [ ] push provider selection
- [ ] push credentials/config
- [ ] delivery receipt behavior
- [ ] provider failure recovery
- [ ] provider timeout behavior
- [ ] DLQ/quarantine visibility
- [ ] provider credential rotation process

## Privacy
- [ ] provider-response retention policy
- [ ] PII minimization
- [ ] no OTP/token/secret in logs
- [ ] notification auditability

---

# 14. Referral MVP

Referral is explicitly MVP.

- [ ] vendor referral creation route
- [ ] referral-link representation
- [ ] retailer redemption route
- [ ] first-touch attribution
- [ ] immutable attribution rule
- [ ] duplicate redemption behavior
- [ ] tenant isolation
- [ ] onboarding UI
- [ ] referral analytics
- [ ] do not implement financial reward wallet
- [ ] no multi-touch incentive logic in MVP

---

# 15. Admin / Ops

## Required operational surface
- [ ] exception dashboard
- [ ] SLA breach queue
- [ ] vendor timeout queue
- [ ] order operational timeline
- [ ] inventory exceptions
- [ ] payment reconciliation exceptions
- [ ] disputes/RMA queue
- [ ] support queue
- [ ] notification failures
- [ ] vendor reliability signals
- [ ] audit-log viewer
- [ ] pilot KPI dashboard

## Admin controls
- [ ] category management
- [ ] vendor activation/onboarding
- [ ] retailer support
- [ ] SLA override if supported
- [ ] audit log access
- [ ] broadcast creation
- [ ] broadcast recipient freeze
- [ ] broadcast dispatch
- [ ] permission matrix
- [ ] operator tenant/job-function restrictions

---

# 16. Vendor Onboarding

Repository document already defines a formal onboarding lifecycle.

- [ ] lead creation
- [ ] docs pending
- [ ] under review
- [ ] verification pending
- [ ] approved
- [ ] active
- [ ] rejection/suspension rules
- [ ] organization creation
- [ ] owner membership
- [ ] vendor profile
- [ ] warehouse/operational metadata
- [ ] payout/settlement information
- [ ] catalog bootstrap
- [ ] initial price upload
- [ ] initial inventory upload
- [ ] test order
- [ ] LOI signed
- [ ] training completed
- [ ] vendor marked pilot-ready

---

# 17. Retailer Onboarding

- [ ] phone registration
- [ ] OTP
- [ ] profile completion
- [ ] organization/store creation or membership creation
- [ ] store address
- [ ] buyer/contact information
- [ ] consent
- [ ] tutorial/coachmarks
- [ ] first catalog visit
- [ ] first assisted order
- [ ] first independent order
- [ ] reorder flow
- [ ] referral attribution if applicable
- [ ] field activator task linkage
- [ ] onboarding analytics

---

# 18. Field Activator

- [ ] task list
- [ ] task assignment
- [ ] retailer activation task
- [ ] assisted order
- [ ] training task
- [ ] follow-up
- [ ] task completion evidence
- [ ] retailer conversion funnel
- [ ] weak-network behavior
- [ ] retry/idempotency
- [ ] field history
- [ ] role-based access
- [ ] mobile UI

---

# 19. Frontend — Major MVP Workstream

## Critical finding
درخت repository فعلی frontend application production ندارد.

بنابراین این بخش از «polish» نیست؛ یک workstream اصلی MVP است.

## 19.1 Retailer — Android + Web/PWA

- [ ] project bootstrap
- [ ] auth screens
- [ ] OTP states
- [ ] session/device states
- [ ] active organization context
- [ ] home/current actions
- [ ] catalog
- [ ] search
- [ ] product detail
- [ ] vendor offers
- [ ] basket
- [ ] allocation preview
- [ ] checkout
- [ ] payment evidence
- [ ] order-group detail
- [ ] child-order detail
- [ ] delivery state
- [ ] POD state
- [ ] reorder
- [ ] disputes
- [ ] RMA
- [ ] support
- [ ] notifications inbox
- [ ] notification preferences
- [ ] profile
- [ ] security/session page
- [ ] deep links
- [ ] offline cache where explicitly specified
- [ ] loading/empty/error states
- [ ] RTL/Persian localization
- [ ] accessibility
- [ ] analytics events

## 19.2 Vendor — Web/Desktop + mobile-responsive

- [ ] auth/context
- [ ] dashboard
- [ ] incoming orders
- [ ] accept
- [ ] reject
- [ ] partial acceptance
- [ ] proposal resolution
- [ ] timeout visibility
- [ ] catalog management
- [ ] pricing
- [ ] inventory
- [ ] daily confirmation
- [ ] fulfillment
- [ ] dispatch
- [ ] delivery handoff
- [ ] payment verification
- [ ] invoices
- [ ] dispute/RMA
- [ ] support
- [ ] referral
- [ ] staff/persona
- [ ] notifications
- [ ] profile/security

## 19.3 Ops

- [ ] exception dashboard
- [ ] order search
- [ ] retailer context
- [ ] vendor context
- [ ] inventory exception
- [ ] timeout queue
- [ ] support
- [ ] RMA/dispute
- [ ] payments
- [ ] notifications
- [ ] audit
- [ ] pilot analytics
- [ ] user/vendor management

## 19.4 Field

- [ ] task list
- [ ] activation
- [ ] assisted first order
- [ ] training
- [ ] follow-up
- [ ] task evidence
- [ ] history

## 19.5 Shared frontend foundation

- [ ] API client
- [ ] auth/session client
- [ ] token refresh handling
- [ ] typed DTOs/contracts
- [ ] retry policy
- [ ] idempotency handling
- [ ] design tokens
- [ ] reusable components
- [ ] state management
- [ ] analytics adapter
- [ ] error boundary
- [ ] feature flags where required
- [ ] localization/i18n
- [ ] Persian RTL
- [ ] mixed-direction number/SKU handling
- [ ] accessibility
- [ ] test harness

---

# 20. Design / Penpot Closure

Design specification is broad, but written specification ≠ implemented design artifact.

Open closure items already documented include:

- [ ] CL-01 centralized-payment wording reconciliation
- [ ] CL-02 wallet/refund wording reconciliation
- [ ] CL-03 frontend framework wording reconciliation
- [ ] CL-04 canonical role naming
- [ ] CL-05 reputation penalty UI decision
- [ ] CL-06 typography/font availability
- [ ] CL-07 final screen-to-contract mapping
- [ ] CL-08 actual reusable component/variant construction
- [ ] CL-09 actual prototype interactions
- [ ] CL-10 final visual evidence/inspection
- [ ] CL-11 design README/index synchronization
- [ ] CL-12 immutable design release snapshot

Additional:
- [ ] final Penpot revision frozen
- [ ] page inventory verified
- [ ] component inventory verified
- [ ] states verified
- [ ] breakpoints verified
- [ ] RTL verified
- [ ] content/localization verified
- [ ] all final screens exported/inspected
- [ ] frontend handoff linked to actual API contracts
- [ ] design QA completed before release

---

# 21. Infrastructure / Deployment

## Current repository gap
Deployment artifacts such as `Dockerfile`, `docker-compose.yml`, `pyproject.toml` and production frontend tree are not present in current branch tree.

## Required
- [ ] production backend packaging
- [ ] Python runtime pinning
- [ ] Uvicorn process
- [ ] reverse proxy / TLS
- [ ] environment configuration
- [ ] secret management
- [ ] PostgreSQL 18 deployment
- [ ] Redis deployment if selected
- [ ] worker process
- [ ] scheduler
- [ ] migration job
- [ ] health endpoint
- [ ] readiness endpoint
- [ ] liveness checks
- [ ] staging environment
- [ ] production/pilot environment
- [ ] domain configuration
- [ ] CORS policy
- [ ] request size limits
- [ ] timeout policy
- [ ] connection pooling
- [ ] DB credential rotation
- [ ] TLS certificate renewal
- [ ] deployment rollback path

---

# 22. Security / Production Hardening

- [ ] HTTPS everywhere
- [ ] JWT secret in secret manager
- [ ] OTP provider secret outside Git
- [ ] rate limit implementation
- [ ] brute-force lockout
- [ ] session revocation
- [ ] refresh-token policy
- [ ] refresh-token rotation if selected
- [ ] CSRF strategy where applicable
- [ ] CORS allowlist
- [ ] secure headers
- [ ] request validation
- [ ] body size limits
- [ ] file-upload restrictions
- [ ] malicious file/content policy
- [ ] tenant-isolation HTTP audit
- [ ] authorization negative matrix
- [ ] sensitive-action audit log
- [ ] PII handling policy
- [ ] secrets scan
- [ ] dependency vulnerability scan
- [ ] dependency pin/lock strategy
- [ ] logging redaction
- [ ] admin separation of duties
- [ ] production access control

---

# 23. Observability

MVP با real users بدون observability ناقص است.

- [ ] structured logs
- [ ] correlation ID propagation
- [ ] request IDs
- [ ] order ID trace
- [ ] outbox event trace
- [ ] worker job trace
- [ ] provider attempt trace
- [ ] API latency metrics
- [ ] API error metrics
- [ ] checkout failure metrics
- [ ] order timeout metrics
- [ ] outbox backlog metric
- [ ] notification FAILED metric
- [ ] worker lag metric
- [ ] payment mismatch metric
- [ ] RMA aging metric
- [ ] support SLA metric
- [ ] DB connection saturation
- [ ] DB slow queries
- [ ] alert thresholds
- [ ] on-call notification
- [ ] incident runbook

---

# 24. Backup / Recovery / Data Operations

- [ ] automated PostgreSQL backup
- [ ] backup encryption
- [ ] restore drill
- [ ] PITR if selected
- [ ] migration backup procedure
- [ ] migration failure recovery
- [ ] rollback procedure
- [ ] data retention policy
- [ ] audit-log retention
- [ ] provider-response retention decision
- [ ] export strategy for pilot evidence
- [ ] staging refresh procedure
- [ ] anonymization/sanitization of copied data

---

# 25. Analytics / KPI / Pilot Measurement

Existing pilot docs define KPIs, but actual operational measurement pipeline must be completed.

- [ ] canonical event dictionary
- [ ] event properties
- [ ] actor/persona
- [ ] screen source
- [ ] success/failure semantics
- [ ] first assisted order
- [ ] first independent order
- [ ] reorder
- [ ] checkout success/failure
- [ ] vendor accept/reject
- [ ] partial acceptance
- [ ] timeout
- [ ] delivery
- [ ] dispute
- [ ] RMA
- [ ] support
- [ ] referral
- [ ] abandonment
- [ ] vendor activation
- [ ] retailer activation
- [ ] catalog quality
- [ ] inventory freshness
- [ ] acceptance SLA
- [ ] fill rate
- [ ] repeat rate
- [ ] self-service rate
- [ ] cost-to-serve
- [ ] CAC realized
- [ ] vendor continuation intent
- [ ] weekly pilot dashboard
- [ ] cohort definition
- [ ] timezone definition
- [ ] metric lineage
- [ ] exportable investor evidence pack

---

# 26. Pilot Operations

Repository pilot documents already define the basic operating model. Execution remains outside the codebase.

## Vendor side
- [ ] 5–10 pilot vendors identified
- [ ] 1–2 anchor vendors selected
- [ ] LOI signed
- [ ] catalog supplied
- [ ] price supplied
- [ ] inventory supplied
- [ ] operational contact nominated
- [ ] acceptance SLA agreed
- [ ] dispatch process agreed
- [ ] payment method agreed
- [ ] dispute/RMA process agreed
- [ ] staff trained
- [ ] sandbox/test order completed
- [ ] live-readiness checklist signed

## Retailer side
- [ ] target cohort identified
- [ ] geography constrained
- [ ] retailers contacted
- [ ] validation evidence collected
- [ ] pilot participation confirmed
- [ ] onboarding slots scheduled
- [ ] field activator assigned
- [ ] assisted order completed
- [ ] independent order observed

## Operational fallback
- [ ] traditional ordering remains valid fallback during early pilot
- [ ] support channel exists
- [ ] outage procedure exists
- [ ] provider failure procedure exists
- [ ] inventory mismatch procedure exists
- [ ] order rejection procedure exists
- [ ] delivery issue procedure exists
- [ ] payment mismatch procedure exists

---

# 27. Real-World Pilot Test Protocol

قبل از Go-Live باید حداقل این سناریوها end-to-end روی environment واقعی staging/pilot اجرا شوند.

## Retailer
- [ ] signup/login
- [ ] OTP failure
- [ ] OTP rate-limit
- [ ] organization context
- [ ] catalog search
- [ ] compare vendor offers
- [ ] add to basket
- [ ] basket modification
- [ ] stale allocation
- [ ] allocation unavailable item
- [ ] price changed
- [ ] insufficient stock
- [ ] MOQ failure
- [ ] MOV failure
- [ ] checkout
- [ ] duplicate checkout
- [ ] order tracking
- [ ] vendor rejection
- [ ] partial acceptance
- [ ] vendor timeout
- [ ] dispatch
- [ ] delivery
- [ ] POD
- [ ] payment evidence
- [ ] dispute
- [ ] RMA
- [ ] refund
- [ ] support
- [ ] notification
- [ ] reorder

## Vendor
- [ ] login
- [ ] catalog edit
- [ ] price edit
- [ ] inventory update
- [ ] daily confirmation
- [ ] accept
- [ ] reject
- [ ] partial proposal
- [ ] proposal race
- [ ] prepare
- [ ] dispatch
- [ ] payment verification
- [ ] dispute response
- [ ] RMA response
- [ ] referral

## Ops
- [ ] timeout queue
- [ ] notification failure
- [ ] support case
- [ ] dispute
- [ ] refund separation-of-duty
- [ ] payment mismatch
- [ ] audit log
- [ ] broadcast
- [ ] vendor onboarding
- [ ] pilot dashboard

---

# 28. HTTP-Level Security / Isolation Matrix

فقط domain-level تست کافی نیست.

برای هر endpoint:

- [ ] wrong user
- [ ] wrong organization
- [ ] revoked membership
- [ ] inactive organization
- [ ] wrong role
- [ ] wrong resource owner
- [ ] expired token
- [ ] revoked session
- [ ] invalid idempotency key
- [ ] duplicate idempotency key
- [ ] conflicting payload with same idempotency key
- [ ] invalid state transition
- [ ] stale version
- [ ] stale price
- [ ] stale inventory
- [ ] missing inventory
- [ ] provider failure
- [ ] timeout
- [ ] retry
- [ ] duplicate event

---

# 29. Performance / Reliability Baseline

اعداد performance باید قبل از pilot تعریف و ثبت شوند؛ برای مواردی که KPI صریح در repository دارد همان KPI مرجع است.

- [ ] API latency baseline
- [ ] catalog search latency baseline
- [ ] checkout latency baseline
- [ ] DB query baseline
- [ ] worker processing baseline
- [ ] notification delivery latency
- [ ] concurrent checkout test
- [ ] concurrent vendor action test
- [ ] provider timeout simulation
- [ ] DB connection exhaustion test
- [ ] retry storm test
- [ ] outbox backlog recovery test
- [ ] worker restart recovery
- [ ] API restart recovery

---

# 30. Documentation Cleanup Before MVP Freeze

این اسناد باید نسخه جاری implementation را بازتاب دهند:

- [ ] `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`
- [ ] `CURRENT_SOURCE_OF_TRUTH.md`
- [ ] `API_APPLICATION_BOUNDARY.md`
- [ ] `ROUTE_COVERAGE_MATRIX.md`
- [ ] `CAPABILITY_COVERAGE_MATRIX.md`
- [ ] `TEST_VERIFICATION_MANIFEST.md`
- [ ] `TECHNICAL_ENVIRONMENT.md`
- [ ] `GLOBAL_ENGINEERING_AUDIT_2026-09-14.md`
- [ ] `REPOSITORY_COMPLETION_AUDIT_2026-09-16.md`
- [ ] `06_PRODUCT/MVP_Definition.md`
- [ ] `06_PRODUCT/PRD.md`
- [ ] `06_PRODUCT/API_Contracts.md`
- [ ] `06_PRODUCT/Technical_Architecture_Spec.md`
- [ ] `06_PRODUCT/Test_Specification.md`
- [ ] `06_PRODUCT/Order_Lifecycle.md`
- [ ] design index / README
- [ ] pilot KPI documents

قانون:
> یک سند stale نباید بتواند agent یا developer بعدی را به معماری قدیمی هدایت کند.

---

# 31. چیزهایی که عمداً تا MVP نباید وارد شوند

برای جلوگیری از scope creep:

- [ ] BNPL / credit underwriting
- [ ] wallet
- [ ] escrow / custody
- [ ] POL-owned warehouse
- [ ] POL-owned fleet
- [ ] advanced route optimization
- [ ] sponsored products / ads
- [ ] advanced recommendation AI
- [ ] complex loyalty
- [ ] gamification
- [ ] social commerce
- [ ] multi-touch referral rewards
- [ ] manufacturer commerce surface
- [ ] quantity splitting یک line بین چند vendor
- [ ] second business-logic layer in frontend
- [ ] second backend runtime
- [ ] speculative microservices

---

# 32. ترتیب اجرای پیشنهادی — Critical Path

## Batch M-01
### Close Batch 6C-7
- [ ] fix
- [ ] test
- [ ] commit
- [ ] push
- [ ] CI
- [ ] certify

## Batch M-02
### Architecture / Documentation Synchronization
- [ ] D-019/D-020 sync
- [ ] capability matrix sync
- [ ] test manifest sync
- [ ] queue runtime decision
- [ ] route matrix refresh

## Batch M-03
### Production Auth / Security
- [ ] real OTP provider
- [ ] rate limit
- [ ] session/revocation
- [ ] refresh policy
- [ ] security middleware

## Batch M-04
### Catalog + Vendor Catalog + Pricing
- [ ] search
- [ ] product detail
- [ ] vendor offers
- [ ] catalog management
- [ ] price management
- [ ] category management
- [ ] barcode/candidate flows

## Batch M-05
### Inventory + Daily Confirmation
- [ ] inventory APIs
- [ ] scan/publish
- [ ] freshness
- [ ] daily confirmation
- [ ] reminders
- [ ] vendor inventory UI

## Batch M-06
### Commerce HTTP Completion
- [ ] vendor order query
- [ ] retailer order query
- [ ] order timeline
- [ ] all checkout failure states
- [ ] idempotency over HTTP

## Batch M-07
### Fulfillment / Delivery
- [ ] prepare
- [ ] dispatch
- [ ] deliver
- [ ] POD
- [ ] delivery exceptions
- [ ] HTTP + UI

## Batch M-08
### Payment / Invoice / Settlement
- [ ] payment evidence
- [ ] verification
- [ ] invoice
- [ ] reconciliation
- [ ] settlement
- [ ] dispute adjustment

## Batch M-09
### Dispute / RMA / Support
- [ ] dispute routes
- [ ] RMA routes
- [ ] refund separation of duties
- [ ] support routes
- [ ] notifications

## Batch M-10
### Notification + Provider Certification
- [ ] inbox
- [ ] preferences
- [ ] SMS
- [ ] push
- [ ] retries
- [ ] receipts
- [ ] DLQ/quarantine

## Batch M-11
### Ops / Admin / Referral / Field
- [ ] admin exception dashboard
- [ ] vendor onboarding
- [ ] broadcast
- [ ] audit
- [ ] referral
- [ ] field tasks

## Batch M-12
### Frontend Foundation + Retailer
- [ ] app bootstrap
- [ ] auth
- [ ] catalog
- [ ] basket
- [ ] allocation
- [ ] checkout
- [ ] orders
- [ ] delivery
- [ ] RMA/support/profile

## Batch M-13
### Vendor + Ops + Field UI
- [ ] vendor panel
- [ ] inventory
- [ ] orders
- [ ] fulfillment
- [ ] payments
- [ ] ops
- [ ] field

## Batch M-14
### Infrastructure
- [ ] staging
- [ ] deployment
- [ ] secrets
- [ ] DB
- [Redis if selected]
- [ ] workers
- [ ] TLS
- [ ] backups
- [ ] monitoring

## Batch M-15
### Real Pilot Data / Onboarding
- [ ] vendor onboarding
- [ ] catalog seed
- [ ] price
- [ ] inventory
- [ ] retailer cohort
- [ ] LOIs
- [ ] training
- [ ] assisted orders

## Batch M-16
### E2E Pilot Certification
- [ ] complete scenario matrix
- [ ] security matrix
- [ ] reliability tests
- [ ] provider failure tests
- [ ] restore test
- [ ] observability test
- [ ] KPI telemetry test
- [ ] final CI
- [ ] release snapshot

## Batch M-17
### MVP Launch Gate
- [ ] no P0 open
- [ ] no critical P1 open
- [ ] all MVP-critical routes green
- [ ] all real clients connected
- [ ] all critical provider flows certified
- [ ] backup verified
- [ ] observability verified
- [ ] pilot operations staffed
- [ ] rollback procedure tested
- [ ] final release SHA recorded
- [ ] MVP declared `PILOT-READY`

---

# 33. Definition of Done — MVP Pilot

MVP را فقط وقتی `DONE` اعلام کنیم که همه این گزاره‌ها درست باشند:

### Product
- [ ] Retailer can complete full order journey without developer intervention.
- [ ] Vendor can manage the commercial and operational order journey.
- [ ] Ops can resolve critical exceptions.
- [ ] Field can onboard/assist users.
- [ ] RMA/support/payment/notification flows are usable.

### Backend
- [ ] All client-facing commands go through FastAPI → ApplicationContext → POLApplicationBoundary.
- [ ] No transport handler writes domain tables directly.
- [ ] No new client-facing path imports legacy `domain_services`.
- [ ] PostgreSQL 18 is the canonical DB.
- [ ] Outbox/worker flow is deterministic and observable.

### Security
- [ ] Auth is production-backed.
- [ ] Tenant isolation is proven at HTTP layer.
- [ ] RBAC is canonical.
- [ ] Sessions can be revoked.
- [ ] Rate limits and OTP protections are active.
- [ ] Secrets never live in Git.

### Commerce
- [ ] Catalog is usable.
- [ ] Prices are current/effective.
- [ ] Inventory is current enough for pilot policy.
- [ ] Basket/allocation/checkout are production-usable.
- [ ] Order transitions work.
- [ ] Fulfillment/delivery/POD works.
- [ ] Payment/reconciliation works without POL custody.

### Exceptions
- [ ] Vendor rejection works.
- [ ] Partial acceptance works.
- [ ] Acceptance timeout works.
- [ ] Dispute works.
- [ ] RMA/refund works.
- [ ] Support works.
- [ ] Provider failure does not corrupt business transactions.

### Client
- [ ] Retailer UI exists.
- [ ] Vendor UI exists.
- [ ] Ops UI exists.
- [ ] Field UI exists where required.
- [ ] RTL/Persian/accessibility pass.

### Infrastructure
- [ ] Staging and pilot deployments exist.
- [ ] Logs/metrics/alerts exist.
- [ ] Backup and restore verified.
- [ ] Migration procedure verified.
- [ ] Rollback verified.

### Evidence
- [ ] Full regression green.
- [ ] HTTP E2E green.
- [ ] Critical negative/security matrix green.
- [ ] Provider certification green.
- [ ] Pilot data loaded.
- [ ] pilot cohort ready.
- [ ] final SHA recorded.

---

# 34. Final Critical Review — Findings After Three Passes

## Finding 1 — Domain is ahead of product runtime
**Severity: P0**

The domain core is mature, but current repository state must not be confused with a user-ready product.

**Implication:** Remaining work is primarily applicationization + client + deployment, not more speculative domain modeling.

## Finding 2 — Route coverage is the main engineering bottleneck
**Severity: P0**

Current HTTP layer covers Auth, Profile, Basket, Allocation, Checkout and early Vendor Order transitions. The API contract defines substantially more capabilities.

**Implication:** The next engineering work should close missing HTTP/application routes systematically.

## Finding 3 — Frontend is a major missing workstream
**Severity: P0**

The current repository tree does not contain the production client applications described by the PRD.

**Implication:** UI implementation is not polish; it is mandatory MVP work.

## Finding 4 — Production provider certification is unfinished
**Severity: P1**

Adapters exist, but adapter code is not equivalent to live SMS/Push/provider certification.

**Implication:** provider credentials, templates, delivery receipts, failure/retry behavior and secrets management must be validated on staging.

## Finding 5 — Deployment is underspecified in the actual repository
**Severity: P1**

Production deployment files are not present in the current repository tree.

**Implication:** MVP pilot deployment must be treated as an engineering batch, not a final DevOps afterthought.

## Finding 6 — Queue architecture has a contradiction
**Severity: P1 / Architecture Decision Required**

Python is authoritative, while documentation still references BullMQ.

**Implication:** resolve before building production workers so the system does not accidentally become a dual-runtime architecture.

## Finding 7 — Several governance documents are stale
**Severity: P1**

Some matrices/manifests still describe earlier migration/table counts or earlier runtime choices.

**Implication:** stale documentation itself is a delivery risk because future agents may implement the wrong architecture.

## Finding 8 — Design is specified more completely than it is implemented
**Severity: P1**

Written screen/state specifications are extensive, but the actual Penpot component/variant/prototype closure still requires evidence.

**Implication:** do not mark design complete until the actual artifact is inspected.

## Finding 9 — Pilot evidence is not the same as pilot readiness
**Severity: P1**

LOI, KPI, cluster and pilot documents exist, but actual onboarding/commitment/catalog/data readiness must be executed operationally.

**Implication:** pilot execution is a separate workstream.

---

# 35. The shortest correct path

اگر هدف فقط این است که POL هرچه سریع‌تر به یک MVP واقعی برای پایلوت برسد، ترتیب بهینه این است:

`6C-7 certification`
→ `Architecture/document sync`
→ `Auth + Security`
→ `Catalog + Pricing + Inventory`
→ `Remaining HTTP applicationization`
→ `Fulfillment + Delivery + Payment`
→ `Dispute/RMA/Support/Notifications`
→ `Frontend Retailer`
→ `Frontend Vendor/Ops/Field`
→ `Staging/Deployment/Observability`
→ `Pilot Data + Onboarding`
→ `Full HTTP E2E`
→ `Pilot Certification`

هر کاری خارج از این مسیر که BNPL، AI recommendation، advertising، loyalty، owned logistics، microservices یا پیچیدگی‌های جدید اضافه کند، تا بسته شدن این مسیر باید خارج از scope بماند.

---

# 36. Release Rule

**MVP Status vocabulary:**

- `FOUNDATION-VERIFIED` = domain/schema/tests are green.
- `APPLICATIONIZED` = canonical HTTP runtime covers required MVP capabilities.
- `CLIENT-READY` = real clients are integrated.
- `STAGING-READY` = deployment/security/provider/observability green.
- `PILOT-READY` = real pilot users/vendors/data/operations ready.
- `MVP-CERTIFIED` = all critical acceptance gates + final CI + release evidence green.

**Target final state:**

`MVP-CERTIFIED / PILOT-READY`

و نه صرفاً:

`209/209 tests passed`.