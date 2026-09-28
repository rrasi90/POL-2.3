# POL PROJECT DECISION REGISTER (CANONICAL SOURCE OF TRUTH)

**Document ID:** `POL-DEC-001`  
**Status:** `LOCKED / CANONICAL`  
**Governance Level:** Lead Product Architect / Founder Approved  
**Last Audit:** 2026-09-28 (Governance + implementation reconciliation)  
**Cross-Reference:** `01_RESEARCH/Assumptions_and_Hypotheses.md` (RES-REG-001)  

---

## 1. Governance Principles & Invariant Policy

All decisions recorded in this register are **LOCKED** for Sprint 0 and MVP execution.

- No engineer, product manager, or external contributor may alter or bypass these decisions without explicit Founder/Architect signed authorization based on empirical pilot telemetry.
- These decisions serve as foundational constraints for software architecture, database schema, operational protocols, and commercial modeling.
- A feature marked **MVP** in this register must not be moved to a future phase without a new superseding decision.
- A feature marked **FUTURE / NOT MVP** must not be activated through UI, API, pricing, or operations merely because its database foundation exists.

---

## 2. Canonical Strategic Decision Register (D-001 through D-028)

| Decision ID | Canonical Decision Title | Approved Formal Decision | Strategic Rationale & Invariant Guardrail | Affected Canonical Documents |
|:---:|:---|:---|:---|:---|
| **D-001** | **Launch Geography & Scope** | **Ahvaz** (Specifically the 61-hectare Wholesalers Hub / شهرک بنکداران اهواز) is the sole launch and pilot geography for Year 1. Expansion outside Ahvaz is prohibited prior to Gate 1 passage. | Maximum physical inventory density and localized operations during validation. | `02_STRATEGY/Opportunity_Definition.md`, `06_PRODUCT/PRD.md`, `11_PILOT/Pilot_Strategy.md` |
| **D-002** | **Pilot Duration & Horizon** | Pilot duration is strictly **3 Months (90 calendar days / 12 weeks)**. | Captures multiple FMCG reorder cycles and real operational retention. | `11_PILOT/Pilot_Strategy.md`, `01_RESEARCH/Assumptions_and_Hypotheses.md` |
| **D-003** | **MVP Basket Allocation Rule (HISTORICAL v0)** | Single-vendor basket was the historical MVP v0 rule. **SUPERSEDED by D-014.** | Retained only for traceability. | `POL_00_PROJECT_CONTROL/MVP_MULTI_VENDOR_DECISION.md` |
| **D-004** | **Data Model Multi-Vendor Extensibility** | Database schema, domain aggregates, and outbox event models MUST natively support **N-vendor** order allocation from Day 1. | Prevents architectural rewrite when vendor routing expands. | `08_DATA/Data_Schema.md`, `08_DATA/DOMAIN_MODEL.md`, `08_DATA/MULTI_VENDOR_ORDERING_MODEL.md` |
| **D-005** | **Open Future Vendor Count** | Future maximum vendor count per order remains **OPEN**; no hardcoded `<=2` constraint. | Vendor count must remain an optimization variable. | `07_ALGORITHMS/Future_Cart_Allocation_Research.md`, `07_ALGORITHMS/MVP_MULTI_VENDOR_ALLOCATION.md` |
| **D-006** | **Pilot Take Rate / Commission** | Pilot commission is **0.0%**. | Removes adoption friction during the 90-day validation period. | `05_BUSINESS_MODEL/Revenue_Model.md`, `11_PILOT/Vendor_LOI.md` |
| **D-007** | **Post-Pilot Commission Framework** | Post-pilot take-rate hypothesis is **1.0%–3.0%**, subject to validation. | Revenue must follow observed vendor economics. | `05_BUSINESS_MODEL/Commission_Model.md`, `05_BUSINESS_MODEL/Business_Model_and_Unit_Economics.md` |
| **D-008** | **POL Logistics Fleet Cost** | POL owns **no delivery fleet** in the pilot. Local hub / partner carrier capacity is used. | Preserves asset-light economics. | `09_OPERATIONS/Fulfillment.md`, `02_STRATEGY/Strategic_Thesis.md` |
| **D-009** | **Advertising & Monetization Timeline** | Sponsored listings, banners, and in-app advertising are deferred to **H2 Year 4**. | Trust and supply quality take precedence over early monetization. | `07_ALGORITHMS/Discovery.md`, `05_BUSINESS_MODEL/Revenue_Model.md` |
| **D-010** | **Order Entity Hierarchy Separation** | Strict separation: `Basket -> AllocationPlan -> OrderGroup -> Order -> OrderItem`. | Separates buyer intent from vendor fulfillment commitments. | `08_DATA/Data_Schema.md`, `08_DATA/DOMAIN_MODEL.md`, `08_DATA/MULTI_VENDOR_ORDERING_MODEL.md` |
| **D-011** | **Dual Currency Presentation vs Storage** | UI, invoices, and SMS use **Tomans**; analytical/strategic registers may use **USD**. | Local UX plus inflation-invariant strategic analysis. | `00_PROJECT_OVERVIEW/Glossary.md`, `06_PRODUCT/PRD.md` |
| **D-012** | **Master Product vs Vendor Product Separation** | `Master Product` and `Vendor Product / SKU` are separate canonical entities. | Preserves catalog identity while allowing vendor-specific offers. | `08_DATA/CATALOG_PRODUCT_MASTER.md`, `08_DATA/INVENTORY_MODEL.md` |
| **D-013** | **Imported Dataset Role & Quarantine** | Imported catalog data remains `IMPORTED_REFERENCE` and is never treated as live vendor truth without verification. | Prevents reference data from becoming false operational inventory. | `08_DATA/Master_SKU_Import_Audit.md`, `08_DATA/Data_Schema.md` |
| **D-014** | **Multi-Vendor Basket in MVP** | MVP v1.0 uses ONE unified retailer basket across multiple wholesalers. The deterministic Allocation Engine partitions it into vendor-specific child orders with independent MOV/MOQ, inventory, acceptance, fulfillment, delivery, settlement and dispute lifecycles. | Core POL value proposition; supersedes D-003. | `POL_00_PROJECT_CONTROL/MVP_MULTI_VENDOR_DECISION.md`, `07_ALGORITHMS/MVP_MULTI_VENDOR_ALLOCATION.md`, `08_DATA/MULTI_VENDOR_ORDERING_MODEL.md` |
| **D-015** | **Canonical Database & Technical Environment** | **PostgreSQL 18** is the sole canonical production, staging, migration and runtime database. SQLite is restricted to isolated unit tests only. | Eliminates dialect/concurrency divergence. | `POL_00_PROJECT_CONTROL/TECHNICAL_ENVIRONMENT.md`, `migrations/001_initial_schema.sql` |
| **D-016** | **Vendor Referral in MVP** | **Vendor Referral is a mandatory MVP capability.** Vendors create a referral code/link; a retailer redeems it once as first-touch attribution during onboarding/activation; attribution is persisted, auditable and connected to the order lifecycle. **No monetary referral reward, wallet, credit, or complex incentive engine is activated in MVP.** | Vendor relationships are a direct acquisition channel in the Ahvaz B2B model. POL must measure supplier-led acquisition before adding paid/referral incentives. | `scripts/vendor_referral.py`, `migrations/013_vendor_referral_mvp_and_integrity_fixes.sql`, `scripts/test_vendor_referral.py` |
| **D-017** | **Canonical User Profile & Persona Context in MVP** | Every user MUST have exactly one universal `user_profiles` record. Every organization membership MUST have exactly one `membership_profiles` record plus the appropriate role-specific persona profile. Profile UI may adapt by persona, but authorization MUST remain sourced from `organization_memberships.role` and active tenant context. | A multi-tenant B2B system needs stable personal identity plus tenant-specific context without turning UI profile fields into RBAC. | `POL_00_PROJECT_CONTROL/USER_PROFILE_AND_PERSONA_MODEL.md`, `06_PRODUCT/USER_PROFILE_UX_SPEC.md`, `migrations/017_canonical_user_profiles_and_persona_context.sql` |
| **D-018** | **Authentication / OTP Policy** | **OTP: 4-digit numeric, 120-second TTL, 60-second resend interval. Rate limit: 3 OTP requests per 5 minutes per phone+IP. Max verification attempts: 5 per challenge. Lockout: 10-minute phone lockout after 5 failed attempts. Access token: 15-minute JWT. Refresh token: 30-day lifetime, issued on successful OTP verification. Refresh-token rotation: requires explicit downstream decision (see D-018 note below).** | Founder selected Option A (Technical Architecture alignment). Supersedes conflicting OTP/auth values in `Technical_Architecture_Spec.md`, `IDENTITY_AND_MEMBERSHIP.md`, `API_Contracts.md`, and `operational_config.py`. PostgreSQL D-015, tenant/RBAC rules, ApplicationContext model, domain state machines, and non-custodial payment are preserved. | `06_PRODUCT/Technical_Architecture_Spec.md` §3, `08_DATA/IDENTITY_AND_MEMBERSHIP.md` §2.5, `06_PRODUCT/API_Contracts.md` §7, `scripts/operational_config.py`, `scripts/domain_services.py`, auth tests, design specs 26/30 |
| **D-019** | **Production Backend Runtime** | **Python is the authoritative production backend runtime.** Existing canonical Python domain/application implementation (`scripts/application_boundary.py`, `scripts/domain_services.py`, all domain services, gateways, workers) becomes the production runtime direction. Single-runtime architecture: HTTP transport → authentication/session → `ApplicationContext` → `POLApplicationBoundary` → canonical Python domain services → PostgreSQL 18 transaction → outbox → async workers. | Founder selected Python as production runtime. Supersedes `Technical_Architecture_Spec.md:57-62` Node.js/NestJS/Fastify production-runtime claim ONLY to the extent necessary to make Python authoritative. No Node/Python dual runtime. No communication boundary. No adapter layer migration. | `06_PRODUCT/Technical_Architecture_Spec.md` §2, `POL_00_PROJECT_CONTROL/API_APPLICATION_BOUNDARY.md`, `POL_00_PROJECT_CONTROL/GLOBAL_ENGINEERING_AUDIT_2026-09-14.md` §5A |
| **D-020** | **Production HTTP Framework** | **FastAPI is the production HTTP framework.** FastAPI is a thin transport adapter. It MUST: authenticate the request, construct `ApplicationContext`, validate transport schema, call `POLApplicationBoundary`, map canonical domain errors to transport responses, return API responses. It MUST NOT: implement business rules, write domain tables directly, bypass `POLApplicationBoundary`, import legacy `domain_services`, duplicate state machines, implement allocation logic, or implement authorization independently from canonical membership context. | Founder selected FastAPI. D-019 establishes Python as runtime; D-020 selects the HTTP framework as a separate decision. FastAPI is the thin translation layer: `FastAPI → authentication/session → ApplicationContext → POLApplicationBoundary → canonical service → PostgreSQL → outbox → worker`. No business logic in the adapter. | `06_PRODUCT/Technical_Architecture_Spec.md` §2 (supersedes NestJS/Fastify), `POL_00_PROJECT_CONTROL/API_APPLICATION_BOUNDARY.md`, `POL_00_PROJECT_CONTROL/GLOBAL_ENGINEERING_AUDIT_2026-09-14.md` §5A |

### D-018 — Detailed Decision: Authentication / OTP Policy

**Source:** `POL_00_PROJECT_CONTROL/FOUNDER_ARCHITECT_DECISION_BRIEF_2026-09-18.md` (Founder selected Option A — Technical Architecture alignment).

**Approved values:**

| Parameter | Value | Source |
|---|---|---|
| OTP digit count | 4 | `Technical_Architecture_Spec.md:80` |
| OTP TTL | 120 seconds | All sources agree |
| Resend interval | 60 seconds | `API_Contracts.md:360` |
| Rate-limit window | 3 per 5 minutes | `Technical_Architecture_Spec.md:95` |
| Rate-limit scope | phone + IP | `Technical_Architecture_Spec.md:95` |
| Max verification attempts | 5 per challenge | All sources agree |
| Lockout duration | 10 minutes | `API_Contracts.md:367` |
| Lockout scope | phone | `API_Contracts.md:367` |
| Access-token lifetime | 15 minutes | `Technical_Architecture_Spec.md:90` |
| Refresh-token lifetime | 30 days | `Technical_Architecture_Spec.md:91` |
| Refresh-token rotation | **Requires explicit downstream decision** | No canonical source defines rotation policy; Tech Arch implies but does not specify |
| Session revocation | Single-session DELETE to REVOKED | All sources agree, implemented and tested |
| Session-row expiry (`user_sessions.expires_at`) | 30 days (= refresh-session lifetime) | Derived from D-018 refresh-token lifetime; NOT access-token lifetime |
| Access-token validation | Stateless JWT `exp` claim (15 min) | JWT library per-request validation; not stored in `user_sessions.expires_at` |

**Supersedes:**
- `06_PRODUCT/Technical_Architecture_Spec.md` §3 — OTP digit count, access-token lifetime, rate-limit parameters now authoritative.
- `08_DATA/IDENTITY_AND_MEMBERSHIP.md` §2.5 — `code_hash` description ("5-digit") is superseded.
- `06_PRODUCT/API_Contracts.md` §7 — `otp_code` example (6-digit), `expires_in` (86400), rate-limit (3/10min) are superseded.
- `scripts/operational_config.py` — the old `OTP_CODE_LENGTH = 6` / `SESSION_TTL_HOURS = 24` values are superseded; current implementation has been synchronized to the D-018 values.
- `POL_00_PROJECT_CONTROL/PRE_MVP_100_SCENARIO_STRESS_TEST.md` §32 — 5/hour rate limit superseded.

**Does NOT change:**
- OTP TTL (120s, already aligned across all sources)
- Maximum verification attempts (5, already aligned)
- Session revocation behavior (already implemented and tested)
- PostgreSQL D-015
- Tenant/RBAC rules
- ApplicationContext model
- Domain state machines
- Non-custodial payment

**Implementation synchronization status (2026-09-28):**
- `06_PRODUCT/Technical_Architecture_Spec.md` — align §3 digit count to 4, clarify §3 token semantics: access token = stateless JWT (15-minute `exp` claim, validated by JWT library per request); refresh session = server-tracked `user_sessions.expires_at` (30-day lifetime). Refresh endpoint §4.1 TBD.
- `08_DATA/IDENTITY_AND_MEMBERSHIP.md` — update `code_hash` description from "5-digit" to "4-digit". Add semantic note: `user_sessions.expires_at` represents refresh-session expiry (30 days), NOT access-token expiry (15 minutes). Access-token expiry is embedded in the JWT `exp` claim and validated statelessly.
- `06_PRODUCT/API_Contracts.md` — update §7.1 rate limit to 3/5min per phone+IP, §7.2 `otp_code` example to 4-digit, `expires_in` to 900 (access token only). §7.4 session revocation: session rows live for 30 days (refresh-session lifetime), not 15 minutes.
- `scripts/operational_config.py` — synchronized to `OTP_CODE_LENGTH = 4` and `SESSION_TTL_HOURS = 720` (30 days = refresh-session lifetime)
- `scripts/domain_services.py` — current implementation is reconciled to the 4-digit OTP and 30-day refresh-session semantics; access-token 15-minute expiry remains a JWT concern.
- Auth tests — update expected OTP length, session lifetime assertions to 30 days, add negative test: refresh_token_hash must persist beyond 15 minutes
- Design specs 26/30 — align OTP input field to 4 digits, add 15-minute countdown, add refresh flow
- Frontend auth screens — align input length, countdown display, lockout state

**Note on refresh-token rotation:** The Technical Architecture document implies refresh-token rotation ("Refresh Token (عمر ۳۰ روز)") but does not explicitly define a rotation policy (full rotation, rotation with reuse detection, or no rotation). This parameter requires a separate explicit Founder/Architect decision before implementation. Do not silently inherit any behavior.

**Note on session-expiry semantics (Batch 6A.2 clarification):** D-018 defines two distinct token lifetimes. The repository schema (`user_sessions`) contains a single `expires_at` column. The following interpretation is canonical:

1. **`user_sessions.expires_at`** = refresh-session expiry = **30 days** from creation. This is when the entire session row becomes EXPIRED and the refresh token stored in `refresh_token_hash` becomes invalid. The user must re-authenticate via OTP.

2. **Access-token expiry** = **15 minutes**, embedded in the JWT itself as an `exp` claim. Validated statelessly by the JWT library on every request. NOT stored in `user_sessions.expires_at`. The access token is independent of the session row's expiry.

3. **Refresh flow** (when implemented): Client presents a valid refresh token; server validates `refresh_token_hash` and `user_sessions.expires_at > now()`, then issues a new 15-minute access token. Refresh-token rotation remains undecided per D-018.

4. **No schema migration required.** The `refresh_token_hash` column already exists. The only change is the value assigned to `user_sessions.expires_at` (30 days instead of 15 minutes) and the documentation of its semantic meaning.

5. **Delivery OTP is a separate domain concern.** D-018 governs login/registration OTP only. The canonical `deliveries` table (`Data_Schema.md:556-574`) does not define an `otp_code` column. The `confirm_delivery_otp` path records `proof_of_delivery.otp_verified` but does not establish a canonical delivery OTP generation/verification contract. Delivery OTP digit count, lifetime, and security policy require a separate domain decision or explicit canonical contract later.

---

### Governance Reconciliation Note — 2026-09-18
- **D-018 refresh-token rotation remains UNDECIDED.** Existing runtime/API behavior may be described as current implementation behavior only; no document may present “no rotation” as a new approved product/security decision. Stage 10 owns explicit rotation-policy closure.
- **D-019 single-runtime constraint prevails over legacy queue wording.** The current technical specification still contains BullMQ/Redis queue references; those references are not a superseding decision. Stage 06 must reconcile the worker/queue mechanism without introducing a Node.js runtime that violates D-019, unless a new explicit decision supersedes D-019.
- **D-020 FastAPI is already canonical and implemented as the production HTTP transport boundary.** Legacy “framework-neutral” wording is historical/stale and must not remain an active architecture claim.
- No new Founder/Architect Decision ID was required by this reconciliation.

### D-019 — Detailed Decision: Production Backend Runtime

**Source:** `POL_00_PROJECT_CONTROL/FOUNDER_ARCHITECT_DECISION_BRIEF_2026-09-18.md` (Founder selected Python production backend runtime).

**Approved architecture:**

```
HTTP transport → authentication/session → ApplicationContext → POLApplicationBoundary
→ canonical Python domain services → PostgreSQL 18 transaction → transactional outbox → async workers
```

**What D-019 establishes:**
- Python is the authoritative production backend runtime.
- The existing canonical Python implementation (`scripts/application_boundary.py`, `scripts/domain_services.py`, all domain services, gateways, workers) becomes the production runtime direction.
- Single-runtime architecture: no Node/Python dual runtime, no communication boundary, no adapter layer migration.

**Supersedes:**
- `06_PRODUCT/Technical_Architecture_Spec.md:57-62` — Node.js 20 / TypeScript / NestJS / Fastify production-runtime claim is superseded ONLY to the extent necessary to make Python authoritative.

**Does NOT change:**
- D-015 PostgreSQL 18 (sole canonical database)
- Redis 7 (cache/session/queue infrastructure)
- Outbox architecture and worker architecture
- Frontend architecture (Next.js/React for web, React Native/Expo for mobile per UX-013)
- Domain/application boundary (`POLApplicationBoundary`)
- Business invariants and domain state machines
- Authorization SSoT (`organization_memberships.role`)
- Non-custodial payment model

**Downstream synchronization required (next engineering batch):**
- `06_PRODUCT/Technical_Architecture_Spec.md` — update §2 runtime row from Node.js to Python, update §2 framework row to reference D-020
- `POL_00_PROJECT_CONTROL/API_APPLICATION_BOUNDARY.md` — update §1 from "framework-neutral" to "FastAPI (D-020)" as transport adapter
- `POL_00_PROJECT_CONTROL/GLOBAL_ENGINEERING_AUDIT_2026-09-14.md` §5A — close "production HTTP/API runtime" gate (stack now selected: Python + FastAPI)
- Docker Compose — update deployment topology to single-runtime Python
- CI pipeline — update backend build/test to use Python production runtime; frontend Node.js/Next.js toolchain remains unchanged

---

### D-020 — Detailed Decision: Production HTTP Framework

**Source:** `POL_00_PROJECT_CONTROL/FOUNDER_ARCHITECT_DECISION_BRIEF_2026-09-18.md` (Founder selected FastAPI as separate decision from D-019).

**Approved framework:** FastAPI

**Architecture rule — FastAPI is a thin transport adapter:**

FastAPI MUST:
- Authenticate the request (JWT validation, session check)
- Construct `ApplicationContext(user_id, organization_id, correlation_id)`
- Validate transport schema (Pydantic models)
- Call `POLApplicationBoundary` method
- Map canonical domain errors to transport responses per `API_APPLICATION_BOUNDARY.md:66-73`
- Return API responses matching `API_Contracts.md`

FastAPI MUST NOT:
- Implement business rules
- Write domain tables directly
- Bypass `POLApplicationBoundary`
- Import legacy `domain_services`
- Duplicate state machines
- Implement allocation logic
- Implement authorization independently from canonical membership context
- Create a second business-logic layer

**Canonical chain:**
```
FastAPI → authentication/session → ApplicationContext → POLApplicationBoundary
→ canonical service → PostgreSQL → outbox → worker
```

**Supersedes:**
- `06_PRODUCT/Technical_Architecture_Spec.md:62` — NestJS with Fastify adapter is superseded as the HTTP framework.

**Does NOT change:**
- D-015 PostgreSQL 18
- D-019 Python runtime
- Domain/application boundary (`POLApplicationBoundary`)
- Business invariants
- Authorization SSoT
- Frontend architecture

**Downstream synchronization required (next engineering batch):**
- `06_PRODUCT/Technical_Architecture_Spec.md` — update §2 framework row from NestJS/Fastify to FastAPI
- `POL_00_PROJECT_CONTROL/API_APPLICATION_BOUNDARY.md` — update §1 transport adapter from "framework-neutral" to "FastAPI"
- New: `requirements.txt` / `pyproject.toml` — add `fastapi`, `uvicorn` dependencies
- New: HTTP route module (e.g., `scripts/api/`) — thin FastAPI app mapping routes to `POLApplicationBoundary`
- Auth middleware — JWT validation, rate limiting, lockout enforcement
- Docker Compose — add Uvicorn process

---

### SMS.ir — Provider Readiness

**Status:** SMS.ir is the current operational OTP/SMS provider candidate. The founder has successfully registered and activated an SMS.ir account.

**Environment contract (no credentials in Git):**

```text
POL_SMS_PROVIDER=SMSIR
SMSIR_API_KEY=<secret from environment>
SMSIR_TEMPLATE_ID=<approved OTP pattern>
SMSIR_LINE_NUMBER=<configured line if required>
```

**Constraints:**
- Do NOT store API key, secret, password, token, or production credential in Git.
- Do NOT ask the founder to paste credentials into chat or commit them.
- Use the provider adapter boundary already defined in `scripts/provider_adapters.py`.
- Keep provider-specific behavior behind the adapter; do not expose SMS.ir details to product/domain services.
- Future SMS.ir OTP template MUST support a 4-digit verification code (per D-018).
- Do NOT create or approve a 6-digit template.
- Do NOT modify auth runtime in this batch — this is decision formalization only.

---

The presence of a database foundation does **not** mean the feature is active.

### ACTIVE IN MVP
- Assisted onboarding / assisted first order
- Vendor catalog + price + inventory visibility
- Unified multi-vendor basket and deterministic allocation
- Checkout revalidation + reservation
- Order acceptance / fulfillment / delivery / POD
- Digital invoice / order history
- Support / dispute / RMA foundations
- Transactional notifications
- Daily vendor inventory confirmation
- **Vendor Referral attribution (D-016)**
- **Universal User Profile + tenant-specific Persona Context (D-017)**
- Non-custodial direct payment + reconciliation foundation
- **Authentication / OTP Policy (D-018)** — 4-digit OTP, 15-min access token, 3/5min rate limit, 30-day refresh
- **Production Backend Runtime: Python (D-019)** — canonical domain/application implementation is production direction
- **Production HTTP Framework: FastAPI (D-020)** — thin transport adapter behind `POLApplicationBoundary`

### ARCHITECTURE-READY BUT NOT ACTIVATED IN MVP
- Personalized pricing
- Advanced commercial terms / trade promotions
- BNPL / embedded credit
- Wallet / escrow / custody
- Sponsored products / advertising
- Advanced AI recommendation / forecasting
- Complex loyalty / gamification / social commerce
- Owned logistics / warehouse infrastructure
- Multi-touch referral incentives

See `POL_00_PROJECT_CONTROL/FUTURE_VERSION_NOT_MVP.md`. That document is explicitly non-MVP and must not be treated as a current product specification.

---

## 4. Downstream Traceability Verification

All code generators, database migration scripts, API controllers and operational playbooks must link their design constraints directly to one of the Decision IDs above.

- **Sprint 0 Migrations:** D-004, D-010, D-012, D-013, D-014, D-016, D-017.
- **Order Engine MVP:** D-014 plus D-004/D-005.
- **Vendor Referral MVP:** D-016; attribution-first and incentive-free.
- **Profile / Identity MVP:** D-017; universal user profile plus membership persona context.
- **Auth / OTP implementation:** D-018; 4-digit OTP, 15-min access token, 3/5min rate limit per phone+IP, 30-day refresh, 5 max attempts, 10min lockout.
- **Production HTTP transport:** D-019 (Python runtime) + D-020 (FastAPI framework); thin adapter behind `POLApplicationBoundary`.
- **SMS provider integration:** D-018 (OTP values) + SMS.ir provider readiness (environment contract, adapter boundary).
- **Pilot Operations:** D-001, D-002, D-006, D-008, D-014, D-016, D-017, D-018.

---

## 5. Change Control Policy

Modifications to any decision in this register require:
1. Documented failure or disconfirmation of the underlying hypothesis via pilot telemetry in `01_RESEARCH/Evidence_Register.md`.
2. Architecture review between Lead Architect and Lead Engineer.
3. Formal version increment of this document with signed Git commit.


---

# 3. Product Architecture Amendments — 2026-09-20

The following founder-directed amendments extend D-001 through D-020. They are adopted product directions and implementation contracts; they do not silently change the already-certified production runtime or financial-custody model.

| Decision ID | Direction | Canonical Rule |
|:---:|:---|:---|
| D-021 | Financial Activity / Future Wallet | MVP exposes payment, refund, order amount, invoice amount, payment status and authorized settlement visibility through existing financial records. POL does not hold a user stored-value balance in MVP. Future Wallet must be a separate ledger/accounting domain. |
| D-022 | Unified Order / Multi-Invoice UX | A single retailer checkout may produce multiple vendor child orders and invoices. The UI must present the parent order first and expose vendor-specific invoices beneath it. Existing D-014/D-010 entity separation remains authoritative. |
| D-023 | MVP Delivery Handoff | No full Driver App is required for MVP. Delivery uses a restricted, short-lived handoff surface/link plus retailer or authorized-receiver confirmation/POD. The link is not an authenticated user session and cannot independently change financial state. |
| D-024 | Vendor Discovery | POL supports both product-first discovery and vendor-first discovery. Vendor storefronts are a first-class read/order surface over canonical Vendor, Product and Inventory data. |
| D-025 | Settlement Language | UI/marketing copy must not promise permanent direct settlement guarantees by POL. Canonical neutral wording: «پرداخت و تسویه طبق شرایط ثبت‌شده سفارش و طرفین معامله انجام می‌شود.» |
| D-026 | Dual Client / Delegated Permissions | Every persona is supported on both Web and Android. Role gives baseline responsibilities; organization managers may grant/revoke allowed delegated permissions within platform boundaries. Authorization remains server-side, organization-scoped and deny-by-default. |
| D-027 | Product Media Provenance | Master Product identity remains separate from Vendor SKU. Product media must preserve source/provenance metadata and must not embed unverified intellectual-property/right claims. Manufacturer-source import is an ingestion workflow, not an assumption of unrestricted rights. |
| D-028 | Barcode Scanner | Barcode scanning is a first-class operational capability for eligible users, primarily on Android. Unknown scans create catalog candidates; scanning cannot bypass Master Product governance. |

## D-026 — Authorization Model Clarification

The target authorization chain is:

Organization -> Membership -> Role -> Delegated Permissions -> Client Surface

Client UI visibility is never sufficient for authorization. All protected resources and commands remain server-authorized using the active organization membership context. Web and Android consume the same authorization boundary.

## D-023 — Delivery Security Boundary

Delivery handoff links must use server-generated high-entropy opaque tokens, short expiry, rate limiting and invalidation after completion. A delivery link is a restricted operational capability, not a reusable authentication/session token.

## D-021 — Wallet Boundary

The absence of a stored-value Wallet in MVP is deliberate. Existing payments/refunds/invoices/settlements remain operational records and are not reinterpreted as wallet balance. Any future wallet must be introduced through a separately approved financial ledger design.
