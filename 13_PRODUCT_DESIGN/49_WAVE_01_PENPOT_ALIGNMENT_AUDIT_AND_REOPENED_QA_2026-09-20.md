# POL — Wave 01 Penpot Alignment Audit & Reopened Design QA

**Document ID:** `13_PRODUCT_DESIGN/49_WAVE_01_PENPOT_ALIGNMENT_AUDIT_AND_REOPENED_QA_2026-09-20.md`
**Version:** `1.0.0`
**Date:** `2026-09-20`
**Branch:** `product-architecture-evolution-2026-09-20`
**Status:** `AUDIT EVIDENCE RECORD — QA REOPENED`

---

## 1. Purpose and authority

This document records the evidence-based audit of the live Penpot file (`New File 1`, file ID `d8ac01df-6646-81d2-8008-a4f2f52bf86c`) against the repository source of truth.

Authority order applied (per `17_PENPOT_CANONICAL_BLUEPRINT.md` §1):

1. `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`
2. Canonical product/business/domain/data/operations documents
3. `13_PRODUCT_DESIGN/14_DESIGN_DECISION_REGISTER.md`
4. `13_PRODUCT_DESIGN/15_CROSS_PROJECT_DESIGN_AUDIT_2026-09-15.md`
5. `17_PENPOT_CANONICAL_BLUEPRINT.md`
6. Penpot artifacts

Per the source-of-truth rule: **Architecture / Product Specification > API / Data Model > GitHub Design Specifications > Existing Penpot.**

---

## 2. Method

- Live Penpot inspection through the Penpot MCP plugin boundary (`execute_code`, `export_shape`): page and board inventory, text content, shape geometry.
- Repository reading: the documents named in this audit, plus route and test inventories (`scripts/api/routes/`, `scripts/test_*.py`).
- Export-based verification: board PNG/SVG exports inspected directly; no status inferred from the mere existence of a frame.

**Verified tooling capability:** read page/board geometry; read and update existing text; create page-level rectangles and text; export boards as PNG/SVG.

**Recorded tooling limitation (not a design claim):** shapes created by the plugin inside a board that the same plugin created do not rasterize in exports, while page-level shapes and children of pre-existing boards do. New panels are therefore authored as page-level rectangles plus page-level text.

---

## 3. Live inventory evidence (2026-09-20)

| Page | Live boards |
|---|---|
| `00 — Foundations` | 6 — Brand Identity, Semantic Color Tokens, Persian Typography, Spacing/Radius, RTL & Invariants, Dark Mode Semantic Tokens |
| `01 — Components` | 8 — Buttons, Form Inputs & OTP, Status Badges, Commerce Cards & MOQ, Operational Tables/Queue/SLA, Feedback & Alerts, Dark Buttons, Dark Commerce Cards |
| `02 — Shared UX` | 8 — Navbars, Revalidation & Conflicts, Empty States, Tenant Switcher, Notifications & Inbox (SH-03), Evidence Capture & POD (SH-04), Financial Activity & OrderGroup components, Scanner/Provenance/Handoff components |
| `03 — States & Patterns` | 8 — ST-01 … ST-08 |
| `04 — Retailer` | 20 — RT-01 … RT-20 |
| `05 — Vendor` | 18 — VD-01 … VD-18 |
| `06 — Operations` | 15 — OP-01 … OP-15 |
| `07 — Field Activator` | 5 — FA-01 … FA-05 |
| `08 — Corporate` | 4 — CP-01 … CP-08 (grouped boards) |
| `09 — Prototypes & Flows` | 4 — FL-01 … FL-04 |
| `10 — Design QA` | 4 — QA-01 … QA-04 |

Repository-side corrections that follow:

- `POL_00_PROJECT_CONTROL/PENPOT_COMPLETION_MATRIX.md` (2026-09-16) is stale: it records a 5-box OTP and a 30-minute vendor SLA timer and asserts PASSED for screens that did not exist at that date. It is reopened.
- `13_PRODUCT_DESIGN/48_WAVE_01_...` asserts "100% Operational & Conceptually Consistent" and QA certification. That claim is unsupported while the §4 contradictions remain open.

---

## 4. Contradiction register (Phase 2 output)

| # | Topic | Penpot / design spec | Repository authority | Canonical resolution | Status |
|---|---|---|---|---|---|
| C-01 | **Login / registration OTP digit count** | `01 — Components` board 02 named `Form Inputs, Stepper & 6-Digit OTP`; `48_WAVE_01` asserts 6-digit and that 4-digit is eradicated | `DECISION_REGISTER.md` D-018: **4 digits**, TTL 120s, resend 60s, 3 requests / 5 min per phone+IP, 5 attempts, 10-minute lockout. D-018 supersedes the 6-digit API example and states "Do NOT create or approve a 6-digit template" | **Login/registration OTP UI = 4 digits.** Rename the component and re-spec all auth screens | RESOLVED (Penpot fix pending) |
| C-02 | **Delivery OTP digit count** | `48_WAVE_01` asserts a 6-digit delivery OTP (`RT-19`, `OP-15`, `ST-08`) | `DECISION_REGISTER.md` D-018 note ¶5: delivery OTP is a separate domain concern; digit count, lifetime and policy require a separate canonical contract. `Data_Schema.md` `deliveries` defines no `otp_code` column | **No canonical digit count exists.** Handoff UI must show verification without asserting a fixed length; the item is an open product decision | **OPEN — product decision required** |
| C-03 | **Vendor acceptance SLA** | `PENPOT_COMPLETION_MATRIX.md` records a 30-minute SLA timer; legacy boards | `PLATFORM_COMPLETION_GAP_REGISTER.md` GAP-009 (resolved): 2-hour acceptance timeout under the Ahvaz working calendar (Sat–Thu 08:00–18:00, Friday holiday); `48_WAVE_01` §3: 120 working minutes | **120 working minutes** rendered as a working-calendar countdown. The 45-minute figure in `06_PRODUCT/PRD.md` is a KPI average target, not the hard timeout | RESOLVED (Penpot fix pending) |
| C-04 | **Settlement wording** | Corporate and finance boards contain assurance-style phrasing | `48_WAVE_01` §3 approved neutral sentence: neutral settlement sentence; non-custodial model in `Technical_Architecture_Spec.md` | Neutral, factual settlement language; no wallet, escrow, stored-value or guarantee framing | RESOLVED (Penpot fix pending) |
| C-05 | **Driver / logistics scope** | Risk of a dedicated carrier-app framing | `48_WAVE_01` §3: lightweight handoff surface, not a dedicated driver app | Handoff / operational surface only | RESOLVED (verify in Penpot) |
| C-06 | **Offline richness** | `FA-05 — Weak Network & Offline Queue` may imply a local transactional engine | `PLATFORM_COMPLETION_GAP_REGISTER.md` severity model (P2 = post-pilot); no canonical offline-write contract | Degraded-network UX only: preserve unsent input, retry, pending/failed action, sync status. No offline-write guarantee | OPEN — verify and constrain |
| C-07 | **Dark mode coverage** | Dark boards exist on `01 — Components` (07, 08) and some role pages (RT-12/13, VD-12/13, OP-07/10, FL-03) | `17_PENPOT_CANONICAL_BLUEPRINT.md` §3 and §4: foundations include light and dark semantic tokens; components require theme variants where relevant | Dark-theme coverage must be systematic per surface, not incidental | OPEN — audit required |
| C-08 | **Profile, Search, Settings completeness** | Boards exist but are not full screen sets (search states, profile completeness, session/security, preferences) | `Technical_Architecture_Spec.md`: `/profile`, `/profile/completion`, `/profile/context`, session list/revoke, logout all; `17_..BLUEPRINT` §5 | Complete auth/session/profile/search/settings coverage is a P0 design gap | OPEN — build required |
| C-09 | **Generic top-level artifacts** | Penpot contains top-level shapes named `Text` / `Rectangle` | `17_..BLUEPRINT` §14: no generic names for canonical artifacts | Clean, uniquely named canonical artifacts only | OPEN — cleanup required |

---

## 5. QA reopened

No QA artifact may retain a PASS/certified status while §4 items remain open.

| QA artifact | Previous claim | Reopened status |
|---|---|---|
| `QA-01 — Master Design QA & System Certification` | Certified, all gates passed | `NEEDS REVIEW` |
| `QA-02 — UI Skills Verification Matrix` | Craft standards verified | `NEEDS REVIEW` |
| `QA-03 — Dark Mode & Component Upgrade Audit Checklist` | Compiled | `OPEN` (depends on C-07) |
| `QA-04 — Wave 01 Architecture Compliance Matrix` | 100% compliant | `BLOCKED` (depends on C-02, C-07, C-08) |
| `PENPOT_COMPLETION_MATRIX.md` | All screens READY | `REOPENED — SUPERSEDED` |

QA may return to PASS only with per-claim evidence: an export or live-inspection record for the specific board and state being asserted.

---

## 6. Execution plan for the remaining phases

| Phase | Scope | Exit evidence |
|---|---|---|
| 3 | Foundations and shared-component validation; systematic dark-theme token coverage | live inspection plus exports |
| 4 | Financial Activity as a read model (retailer, vendor, ops, shared components) | states: empty, loading, error, partial, pending, verified, rejected, refunded, failed, reconciled, under review, disputed |
| 5 | OrderGroup / vendor order / invoice hierarchy | traceability: OrderGroup to vendor order to invoice to payment to settlement |
| 6 | Vendor discovery (search, B2B storefront) and vendor storefront management | boards, filters, operational status |
| 7 | Delegated permissions, staff editor, permission audit | grant and revoke with actor, target, reason, timestamp, client |
| 8 | Scanner: permission, continuous scan, four-match contract (`EXACT`, `HIGH_CONFIDENCE`, `AMBIGUOUS`, `NO_MATCH`), ambiguous candidate selection, no-match recovery | state matrix plus interaction spec |
| 9 | Master SKU candidate review and media provenance (`VENDOR_UPLOADED`, `MANUFACTURER_PROVIDED`, `POL_OWNED`, `USER_UPLOADED`) | candidate states plus provenance badges |
| 10 | Partial acceptance end to end (proposal, review, approve or decline, reason codes, quantity comparison) | board set plus timeline and notification trace |
| 11 | Delivery handoff security (restricted single-use token, verification states, ops exceptions) | state matrix; C-02 shown as OPEN in the UI |
| 12 | Auth, sessions, profile, search, settings completion (includes the C-01 fix) | full screen set with all states |
| 13 | Android and Web parity (mobile-first versus desktop-first per persona) | documented interaction differences |
| 14 | States and Patterns completion for the new capability groups | ST board coverage |
| 15 | Prototype rebuild (Scenarios A to G clickable) | prototype flows |
| 16 | Design QA rerun, evidence based | PASS / OPEN / BLOCKED per claim |
| 17 | Final architecture-to-design traceability audit | traceability table |

---

## 7. Evidence standards for this wave

- A capability is complete only when all four layers exist: information architecture, UI, interaction/state, prototype/flow.
- No PASS without an export or live-inspection record for the exact board and state.
- Unresolved items are labelled `OPEN`, `BLOCKED`, `NEEDS REVIEW`, `DEPENDS ON API` or `DEPENDS ON PRODUCT DECISION`.
- No invented product behaviour: financial guarantees, custodial mechanics, a dedicated driver app, an offline transactional engine, or a fixed delivery-OTP length are not to be presented as settled until a canonical source states them.

| C-10 | **Small-size typography** | Non-trivial volume of 9–11 px UI text | `25_VISUAL_DESIGN_REFINEMENT...` and `21_MVP_DESIGN_...` readiness gate: 9–11 px only by explicit exception | Default UI type ≥ 12 px; exceptions documented | OPEN — audit required |
