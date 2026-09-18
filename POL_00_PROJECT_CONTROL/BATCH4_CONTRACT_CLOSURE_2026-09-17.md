# POL Batch 4 — Pre-UI Contract & Route Closure

Baseline: `35f17728f92825cc2594069289c84b370b50d1ce`, branch `research-hardening-2026-09-14`. Status: review record; no production-readiness certification. No decision D-001 through D-017 is changed.

## Authority re-audit

`DECISION_REGISTER.md` and `CURRENT_SOURCE_OF_TRUTH.md` govern product specifications, technical/data models, operations/API contracts and design in that order. Runtime constants, historical handoffs and Penpot artifacts cannot supersede them. Re-audit found no explicit superseding approval resolving either Batch 3 blocker.

### CONTRACT BLOCKER — AUTH OTP POLICY

| Parameter | Sources and values |
|---|---|
| Digits | `06_PRODUCT/Technical_Architecture_Spec.md:80`: 4; `08_DATA/IDENTITY_AND_MEMBERSHIP.md:91`: 5; `06_PRODUCT/API_Contracts.md:372`: 6-digit example; `scripts/operational_config.py:18` and `scripts/domain_services.py:38`: 6. |
| TTL | 120 seconds agrees in technical spec line 80, identity line 96, API line 359, config line 19; legacy implementation hardcodes two minutes. This agreement does not resolve other parameters. |
| Resend | API lines 358–360 specifies 60 seconds; no complete runtime resend gate was found. |
| Rate limiting | Technical spec line 95: 3/5 minutes per phone and IP; API line 345: 3/10 minutes per phone. `POL_00_PROJECT_CONTROL/PRE_MVP_100_SCENARIO_STRESS_TEST.md:32,92-96` additionally describes 5/hour/IP and five requests/10 minutes with Retry-After 900. Scenario expectations are not runtime proof. |
| Maximum attempts | Identity line 94, API line 367 and config line 20 agree on 5. |
| Access-token lifetime | Technical spec lines 89–91: 15 minutes; API line 387: 86400 seconds. Config line 22 defines a 24-hour session, which is not evidence of implemented JWT lifetime. |
| Refresh lifetime | Technical spec line 91: 30 days; identity line 68 defines a refresh-token hash. The inspected legacy auth service does not implement refresh issuance/rotation. |
| Lockout | API line 367 and config line 21: 10-minute phone lockout after five errors; legacy runtime marks a challenge BLOCKED but does not implement the full timed phone-lockout contract. |

Newer design documents also conflict: `13_PRODUCT_DESIGN/26_SCREEN_WIREFRAME_SPEC_RETAILER_VENDOR_2026-09-16.md:113` and `13_PRODUCT_DESIGN/30_RETAILER_SCREEN_BY_SCREEN_SPEC_2026-09-16.md:29` prescribe six digits; `ANTIGRAVITY_EXECUTION_LOG.md:39` claims a co-founder five-box DEC-EXEC-006 decision. That claim has inconsistent traceability in `ANTIGRAVITY_FINAL_HANDOFF.md:108-118` and does not explicitly supersede the conflicting auth policies. Escalate rather than ignore or adopt it. `06_PRODUCT/User_Journeys.md:127,238` also uses six digits. Delivery OTP examples are a separate contract and do not settle login OTP.

Decision brief:
- Authority A: technical architecture authentication policy; Authority B: API authentication contract; Authority C: identity specification. No decisive register entry found.
- Minimum Founder/Architect decision: resolve the digit count and approval provenance, request-limit count/window/key, resend interval, access/refresh lifetimes and lockout scope/reset behavior; confirm the shared TTL and attempt cap in one authoritative policy.
- Affected files: the sources above, legacy auth implementation/configuration, auth tests, written auth design and future Penpot implementation.
- Runtime consequences: challenge validation, throttling, session/token issuance and lockout persistence must be reconciled before production auth. Current tests largely exercise direct SQL membership/session/challenge invariants, not a complete auth transport.
- Design consequences: field length, countdowns, retry and expiry copy, lockout states and session recovery must follow the approved policy. No numeric value was selected or implemented in Batch 4.

### CONTRACT BLOCKER — PRODUCTION RUNTIME STACK

Authority A: `06_PRODUCT/Technical_Architecture_Spec.md:57-62,174-178` calls Node.js 20/TypeScript/NestJS/Fastify approved and build-ready. Authority B: `POL_00_PROJECT_CONTROL/API_APPLICATION_BOUNDARY.md:3-14` and `POL_00_PROJECT_CONTROL/GLOBAL_ENGINEERING_AUDIT_2026-09-14.md:90-91` defer production transport selection. `DECISION_REGISTER.md:40` approves PostgreSQL 18 only. The historical `FINAL_CERTIFICATION_REPORT.md:68` stack claim is not current D-010 authority.

`13_PRODUCT_DESIGN/14_DESIGN_DECISION_REGISTER.md:17-22` (UX-013) aligns frontend with Next.js/React and React Native/Expo. `13_PRODUCT_DESIGN/11_FRONTEND_IMPLEMENTATION_STRATEGY.md:50-51` retains older unlocked-framework wording, recognized as drift in `13_PRODUCT_DESIGN/46_DESIGN_CLOSURE_BACKLOG_AND_CONFLICT_RESOLUTION_2026-09-16.md:12`. Frontend alignment does not choose a backend stack.

Minimum Founder/Architect decision: explicitly reconcile the approved-stack wording with deferred transport selection, including how the chosen transport calls the existing Python boundary without duplicating business logic. A Node transport would need an explicit inter-process invocation contract; a Python transport could invoke it in-process. Neither option is selected here. Affected artifacts are the technical spec, boundary contract, ADR-B3-01 and deployment/transport design. No migration or domain rewrite occurred.

Preserved strategy:
`Transport -> ApplicationContext -> POLApplicationBoundary -> canonical domain service -> PostgreSQL transaction -> outbox -> async worker`.
Transport owns translation, authenticated context, transaction lifecycle and error mapping, not business logic. The Python facade is current executable code, not final production-stack approval. Existing auth/context gaps prevent blanket certification that every facade method is production-safe.

## Recipient isolation

Inspection found that `scripts/canonical_integration_worker.py` checked only non-null routing IDs before notification creation. Independent user/organization foreign keys do not prove membership. The minimal fix queries the existing membership/organization authority for an ACTIVE pair before materialization, locking both rows with `FOR SHARE OF om, o` until transaction end. A missing active pair raises `IntegrationWorkerError`; no notification or delivery is inserted for that event. Explicit routing checks remain unchanged.

`scripts/test_canonical_integration_worker.py::test_batch4_recipient_membership_isolation` has seven PostgreSQL-backed cases: authorized, wrong organization, suspended membership, revoked membership, inactive organization, missing user and missing organization. The authorized case produces one notification and one delivery, publishes the event and produces no duplicate on a second worker pass. Each denied case catches the real worker error inside a transaction, asserts zero notifications/deliveries and a PENDING event, then commits and rechecks zero notifications. This distinguishes prevention from an exception-triggered transaction rollback hiding an unauthorized insert.

The pre-existing positive ORDER_ACCEPTED fixture now has an active retailer membership, matching the recipient matrix, rather than an unassociated vendor user. Its exact recipient/template assertions remain. No migration, alternate notification service, event-role policy or provider change was introduced.

Scope limit: this guard validates the recipient against the explicit target organization, not arbitrary event aggregate ownership or every event-specific role rule. Those remain producer contracts. Direct SQL writes are not certified by worker tests. Invalid events remain PENDING and abort worker processing; poison-event recovery is not newly solved. No pre-fix test execution was performed; the missing guard was established by inspection, and post-fix behavior by PostgreSQL tests.

## Route reassessment

This record and the Batch 4 qualification in `ROUTE_COVERAGE_MATRIX.md` supersede Batch 3's unsupported GREEN-eligibility recommendations. All seven audited AMBER rows remain AMBER.

| Route | Previous -> resulting | Evidence and reason |
|---|---|---|
| Notification -> delivery | AMBER -> AMBER | Recipient materialization is now tested. Complete channel delivery, retry/recovery and live provider certification remain incomplete. Configuration-error tests do not prove credentials are absent from an actual deployment. |
| Feedback -> Admin | AMBER -> AMBER | Direct service tests pass, but facade admin methods do not propagate active operator context; `_require_admin` checks any operator membership. Missing active-context route evidence. |
| Feedback reply -> user | AMBER -> AMBER | Explicit reply outbox exists; active-context authorization, repeated-reply delivery semantics and complete delivery evidence are incomplete. |
| Support -> case lifecycle | AMBER -> AMBER | Owner/ops service tests do not prove active-context enforcement. Facade read/message/assignment/transition omit organization context; full lifecycle/concurrency evidence remains incomplete. |
| Returns / RMA | AMBER -> AMBER | Batch 2/3 request/transition/refund checks do not certify inspection quantities or reverse-logistics execution. The narrower RMA -> Refund row is distinct. |
| Analytics / KPI | AMBER -> AMBER | `11_PILOT/KPIs.md` supplies definitions; schema lineage checks do not certify the full calculation/read pipeline, cohorts or timezones. |
| External provider delivery | AMBER -> AMBER | Adapter/configuration code is not live supplier and recovery certification. |

### Pre-UI gates

- Empty PostgreSQL 18 migration chain: new test databases use the existing fixture applying 001 through 025; full-suite migration tests provide separate evidence. No applied migration changed.
- Zero-failure suite: use the final execution results, not historical CI or documentation claims.
- Async ownership: integration and provider workers are explicit. This does not establish complete event/channel coverage or production scheduling/recovery.
- Legacy access: existing import-regression tests protect the application boundary; historical tests still call legacy services/direct SQL and are not proof of HTTP safety.
- Negative routes: Batch 4 closes the explicit target-membership test gap. Batch 3's four order enum rejections are not illegal transition tests; there is no canonical order-transition facade. Cross-tenant idempotency, concurrent reservation behavior through the complete facade and all event-role negatives must not be certified from source strings or direct SQL tests alone.
- API/client coverage: commands/examples exist, but current lower-level DTO/role/state contradictions and missing production transport/auth remain gates. The API allocation preview exposes `strategy`; raw facade results are not a certified client serializer.
- Simplicity: no new client field or internal data exposure is added. Existing text/UX tests do not prove all response serializers hide allocation/provider/retry internals.
- Profiles/personas: existing PostgreSQL profile tests provide scoped evidence, not full client/HTTP certification.

Batch 3 evidence correction: its document cites dispute/payment tests absent from `test_batch3_contract_matrix.py`, calls all 12 tests PostgreSQL-backed although two are static, and describes ACCEPTED -> REFUNDED although its actual negative is RETURN_REQUESTED -> REFUNDED. Its full-suite-through-facade and broad route-safety claims are not relied upon here. Historical file is preserved; this record qualifies its claims.

## Design synchronization

For this and future batches, latest canonical GitHub product/design requirements take precedence over Penpot. GitHub requirements must never be downgraded or back-ported to match an older artifact. Research -> Principle -> Token -> Component -> Pattern -> Screen -> Prototype -> QA -> Handoff remains the execution sequence; screen existence alone is not completion.

The fetched canonical branch matches this baseline. Repository written requirements are ahead of verified Penpot completion evidence, as recorded in `13_PRODUCT_DESIGN/45_REPOSITORY_WIDE_DESIGN_COMPLETENESS_AUDIT_2026-09-16.md:136-158,225-243` and closure backlog 46. Future design must bring Penpot forward against current requirements, states, permissions and failure branches.

Recorded drift: six-digit written screens versus five-box handoff claims; unverified component/interaction/visual closure; revision-69 export versus older archived binary (`13_PRODUCT_DESIGN/PENPOT_FILES/MANIFEST/PENPOT_REVISION_69_SYNC_REPORT.md:21-41`); rev72 marker is not proof of uploaded binary (`13_PRODUCT_DESIGN/PENPOT_FILES/ARCHIVE/REV72_SYNC_REQUIRED.md`). These archive facts do not override written requirements. No live Penpot inspection was performed; exact live artifact state is UNKNOWN. No stale Penpot rule was adopted and no design/Penpot/frontend file was modified.

## Files and remaining gates

Changed: `scripts/canonical_integration_worker.py` (membership guard), `scripts/test_canonical_integration_worker.py` (seven cases and corrected positive fixture), `POL_00_PROJECT_CONTROL/ROUTE_COVERAGE_MATRIX.md` (qualification, no AMBER promotions), and this record. No staging/commit/push is authorized. `opencode.jsonc` stays local-only.

Policy blockers remain AUTH OTP POLICY and PRODUCTION RUNTIME STACK. Implementation/verification gates remain active-context feedback/support, complete RMA/analytics/provider routes and the pre-UI limitations above. These are not new business decisions and are not falsely closed by passing tests.
