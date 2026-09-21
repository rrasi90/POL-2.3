# POL — Wave 01 Penpot Fix Backlog (Evidence-Based)

**Document ID:** `13_PRODUCT_DESIGN/50_WAVE_01_PENPOT_FIX_BACKLOG_2026-09-20.md`
**Date:** `2026-09-20`
**Companion to:** `49_WAVE_01_PENPOT_ALIGNMENT_AUDIT_AND_REOPENED_QA_2026-09-20.md`
**Status:** `EXECUTION BACKLOG — PENDING LIVE PENPOT APPLICATION`

Evidence source: repository snapshot exported from Penpot (`13_PRODUCT_DESIGN/PENPOT_FILES/SOURCE/New File 1.penpot.zip`, file `d8ac01df-…`), text extracted from the nested `content` tree of every text shape on all 11 pages.

> **Verification rule:** the snapshot predates the live file. Every string below must be re-located in the live file before editing (`inspect → locate → modify → export-verify`). If a string is already corrected live, mark it `ALREADY RESOLVED` and do not touch it.

---

## A. Acceptance SLA — 30 minutes must become 120 working minutes

Canonical authority: `PLATFORM_COMPLETION_GAP_REGISTER.md` GAP-009 (Ahvaz working calendar, Sat–Thu 08:00–18:00); `48_WAVE_01` §3.

| Page | Located string (snapshot) | Required direction |
|---|---|---|
| `05 — Vendor` (VD-02 queue) | «حداکثر زمان مجاز بررسی و پذیرش هر سفارش: ۳۰ دقیقه از زمان ثبت» | replace the 30-minute figure with **۱۲۰ دقیقه کاری** and add working-calendar context (شنبه–پنجشنبه ۰۸:۰۰–۱۸:۰۰) |
| `05 — Vendor` (VD-02 countdown) | «⏱ مهلت پاسخ: ۱۴ دقیقه مانده» | countdown must express **working minutes remaining**, not wall-clock minutes |
| `05 — Vendor` (VD-01 inventory) | «در صورت عدم تأیید تا ۲ ساعت و ۲۵ دقیقه دیگر، موجودی… تعلیق می‌گردد» | retain, but label it as the daily-inventory cutoff rule, distinct from the acceptance SLA |
| `06 — Operations` (OP-01) | «وضعیت: ۳۸ دقیقه از زمان ثبت سفارش گذشته… (حد مجاز: ۳۰ دقیقه)» | recalculate against the 120-working-minute deadline; queue must show working-calendar age |
| `06 — Operations` (OP-01) | «۴۵ دقیقه مانده به Cutoff ۱۱:۰۰» | retain: daily inventory cutoff (11:00), a separate operational rule — do not conflate with acceptance SLA |
| `09 — Prototypes & Flows` (FL-01) | «تایمر معکوس ۳۰ دقیقه‌ای» / «شمارنده معکوس ۳۰ دقیقه SLA» | update the flow narration to 120 working minutes |
| `10 — Design QA` (QA-01) | «صف پذیرش ۳۰ دقیقه‌ای» | update the certification text to 120 working minutes |

---

## B. OTP digit contract

Canonical authority: `DECISION_REGISTER.md` D-018 — login/registration OTP is **4 digits** (TTL 120s, resend 60s, 3 requests / 5 min per phone+IP, 5 attempts, 10-minute lockout). D-018 explicitly forbids a 6-digit template and supersedes the 6-digit API example.

| Page | Located string (snapshot) | Required direction |
|---|---|---|
| `01 — Components` (board 02) | «احراز هویت پیامکی (5-Digit Discrete OTP)» | rename to **4-digit** discrete OTP (four boxes), matching D-018 |
| `01 — Components` (board 02) | «کد ۵ رقمی ارسال‌شده به شماره ۰۹۱۲***۶۷۸۹ را وارد کنید:» | re-spec as a 4-box input with Persian numerals |
| `01 — Components` (board 02 title) | any remaining `6-Digit OTP` naming | rename to 4-digit; the live board name must not contradict D-018 |
| `04 — Retailer` (RT-01 auth) | OTP input length | four boxes; add resend countdown (60s), lockout state (10 min), expired state |
| `10 — Design QA` (QA-01) | «کد ۵ رقمی OTP» | update to the 4-digit contract |

**Delivery OTP (separate concern — C-02 in document 49):** the snapshot contains «کد ۴ رقمی تحویل (POD)» on `05`, `08`, `09`, `10`. No canonical contract defines the delivery-OTP length (`DECISION_REGISTER.md` D-018 note ¶5; `Data_Schema.md` `deliveries` has no `otp_code` column).

- Required UI behaviour: verification surfaces must work **without asserting a fixed length** until a canonical contract exists.
- Required label: mark the deliverable as `OPEN — DEPENDS ON PRODUCT DECISION` in the QA page; do not certify a digit count.

---

## C. Guarantee-style settlement and delivery wording (C-04)

Canonical direction: neutral, factual settlement language; non-custodial read-only financial visibility; no wallet, escrow, stored value or guarantee framing.

| Page | Located string (snapshot) | Required direction |
|---|---|---|
| `04 — Retailer` | «بدون واسطه • تسویه آنی • تضمین فاکتور رسمی» | remove the guarantee claim: state that an official invoice is issued per vendor order |
| `07 — Field Activator` | «…جهت تخصیص سهمیه بنکدار تضمین می‌شود» | state the recorded request as a fact; POL does not guarantee allocation |
| `08 — Corporate` | «✓ تضمین تحویل با کد احراز فیزیکی (POD)» | "تحویل با احراز کد در مقصد (POD)" — verification method, not a guarantee |
| `08 — Corporate` | «…تسویه غیرامانی تضمین می‌شود» | neutral settlement sentence approved in `48_WAVE_01` §3 |
| `00 — Foundations` | «تضمین انطباق طراحی بصری با قراردادهای دامنه…» | internal design-governance wording; keep but reword to "انطباق" to avoid financial-sounding assurance |
| `09 — Prototypes & Flows` | «انطباق تضمین‌شده با معماری مرجع پُل» | reword to "منطبق با" |

---

## D. Driver-app framing (C-05)

The snapshot implies a dedicated driver application:

- `05 — Vendor`: «راننده این کد را در اپ خود وارد می‌کند»
- `08 — Corporate`: «ثبت کد محرمانه ۴ رقمی در اپلیکیشن راننده»
- `09 — Prototypes & Flows`: «راننده کد را در اپ وارد کرده و تحویل قطعی می‌شود»

Required direction: MVP ships **no dedicated driver app**. Present these surfaces as a lightweight handoff/operational verification surface (web or in-app handoff panel) on the delivery-party side.

---

## E. Dark-theme coverage (C-07)

Repository requirement: `17_PENPOT_CANONICAL_BLUEPRINT.md` §3 (light and dark semantic tokens) and §4 (theme variants where relevant).

Snapshot baseline: **zero boards carry a dark/theme variant name on any page** (see per-page count of dark-named frames). Live file has dark boards only on `01 — Components` (07, 08) and a small number of role pages.

Required per-surface coverage:

| Surface | Light | Dark required |
|---|---|---|
| `00 — Foundations` | yes | semantic-token sheet exists; component/pattern dark sheet to be confirmed |
| `01 — Components` | yes | present (boards 07, 08) — extend to all component families |
| `02 — Shared UX` | yes | **add** dark sheet (navigation, empty states, revalidation, modals, notifications) |
| `03 — States & Patterns` | yes | **add** dark state sheet |
| `04 — Retailer` | yes | partial (`RT-12/13`) — **add** auth, basket, checkout, order detail, financial, handoff |
| `05 — Vendor` | yes | partial (`VD-12/13`) — **add** queue, acceptance, scanner, permissions |
| `06 — Operations` | yes | partial (`OP-07/10`) — **add** audit, investigation, provenance, handoff exceptions |
| `07 — Field Activator` | yes | **add** |
| `08 — Corporate` | yes | **add** |
| `09 — Prototypes & Flows` | yes | partial (`FL-03`) — confirm coverage |
| `10 — Design QA` | yes | **add** (QA-03 checklist requires it) |

---

## F. Profile / Search / Settings completeness (C-08)

Canonical API surface that must be reachable from the design: `/profile`, `/profile/completion`, `/profile/context`, session list, revoke session, logout all, notification preferences.

Missing screen families to design:

1. **Account / Profile** — profile edit, profile completeness indicator, membership and role, organization context switcher, active sessions with device/client/last-active/revoke, logout-all with confirmation.
2. **Search** — initial, suggestions, results, no result, loading, error, filter-active, barcode search, ambiguous result, mixed RTL/LTR rendering of SKU/barcode.
3. **Settings** — notification preferences (mandatory versus optional channels), language and direction, organization defaults, vendor-side operating information and policies.

---

## G. Generic artifact cleanup (C-09) and typography audit (C-10)

- Locate top-level shapes named exactly `Text`, `Rectangle`, `Board`, or `Frame <n>`; delete unused ones or move their content into the canonical board and delete the container.
- Audit UI text at 9–11 px. Default UI type is ≥ 12 px; where a smaller size is retained, record it as an explicit exception in `25_VISUAL_DESIGN_REFINEMENT...`.

---

## H. QA page updates required by this backlog

- `QA-01` and `QA-04` may not display "100% PASSED" or "ALL PAGES PASSED" while C-02, C-07 and C-08 are open.
- `QA-04` must list each contradiction with its status: SLA `RESOLVED`, login OTP `RESOLVED`, delivery OTP `OPEN — DEPENDS ON PRODUCT DECISION`, settlement wording `RESOLVED`, driver framing `RESOLVED`, dark theme `OPEN`, profile/search/settings `OPEN`.

---

## I. Execution and verification protocol per fix batch

1. Locate the target string live (`execute_code` scan) and record the board and shape id.
2. Confirm the target string is not already canonical.
3. Apply the edit; keep Persian numerals, RTL direction and the file's Vazirmatn font.
4. Export the affected board (`export_shape`) and inspect the output visually.
5. Record the batch result (board, before, after, export evidence) in this document or the mission log.
6. Never edit inside boards created by the automation boundary: author new panels as page-level rectangles plus page-level text (see document 49 §2).


---

## J. Frontend (mock-first) alignment gaps — evidence

Scope: `frontend/` (Next.js 15 App Router, Tailwind v4, React 19, zustand, SWR). 19 source files under `src/`.

**Present pages/components**

- `src/app/page.tsx` (home), `src/app/auth/page.tsx` (phone + OTP)
- `components/auth/LoginForm.tsx`, `components/auth/OtpVerifyForm.tsx`
- `components/common/NotificationList.tsx`
- `components/field/FieldTaskList.tsx`, `components/ops/SupportCaseList.tsx`
- `components/retailer/` (CatalogGrid, CheckoutForm, OrderDetail, OrderList)
- `components/vendor/` (VendorInventoryTable, VendorOrderQueue, VendorSettlementList)
- `lib/api/client.ts`, `lib/hooks/useDirection.ts`, `lib/types/index.ts`

**Gaps confirmed by inspection**

| # | Gap | Evidence | Canonical requirement |
|---|---|---|---|
| F-01 | **No dark theme** | `src/app/globals.css` hard-codes `color-scheme: light`; `layout.tsx` hard-codes `bg-gray-50 text-gray-900`; no theme switch or `dark:` variants anywhere | `17_PENPOT_CANONICAL_BLUEPRINT.md` §3 (light and dark semantic tokens) |
| F-02 | **No design-token layer** | No CSS variables for color/spacing/radius/elevation; components use raw Tailwind palette values (`blue-600`, `gray-50`) | Foundations boards `02 Semantic Color Tokens`, `04 Spacing & Radius`, `06 Dark Mode Semantic Tokens` |
| F-03 | **Font contract not applied** | `font-family: Arial, "Tahoma", sans-serif` while the design system and Penpot file use **Vazirmatn** | `03 — Persian Typography & Numeric Scales`; `48_WAVE_01` §5 (Vazirmatn typography tokens) |
| F-04 | **Missing screen families** | No profile, search, settings, sessions/security, permissions, financial activity, scanner, handoff or partial-acceptance components | `17_..BLUEPRINT` §5 (auth/session, profile, search, preferences); document 50 §F |
| F-05 | **Notifications preferences unused** | `NotificationPreference` exists in `lib/types/index.ts` but no UI consumes it | Notification preference screen requirement |

**Cross-check that supports contradiction C-01:** `components/auth/OtpVerifyForm.tsx` already implements a **4-digit** OTP (label text "Enter the 4-digit code", `slice(0, 4)`, `maxLength={4}`), consistent with `DECISION_REGISTER.md` D-018. The Penpot component naming ("5-Digit", live board 02 naming) is therefore the outlier and must be brought to 4 digits.

**Frontend work is only in scope after the Penpot canonical source is corrected** (pipeline order: written source of truth → Penpot → mock-first frontend → backend integration).


---

## K. Batch execution record — 2026-09-20 (live Penpot, MCP `execute_code`)

**Batch 1 applied — 24 changes across 7 pages** (live file `d8ac01df-…`, session `f3d9a9a2-…`):

| Page | Changes | Representative fixes |
|---|---|---|
| `01 — Components` | 3 | «کد ۵ رقمی» → «کد ۴ رقمی»; «(5-Digit Discrete OTP)» → «(4-Digit Discrete OTP)»; board renamed `02 — Form Inputs, Stepper & **4-Digit OTP**` |
| `04 — Retailer` | 7 | RT-01 «کد تأیید ۶ رقمی پیامک‌شده» → «۴ رقمی» (D-018); RT-05/RT-19 delivery code made digit-agnostic; «تضمین تسویه مستقیم» → «تسویه مستقیم»; «تضمین شفافیت» → «شفافیت»; «تحویل به راننده» → «تحویل به طرف تحویل‌دهنده» (×2) |
| `05 — Vendor` | 1 | «OTP شش رقمی» → «کد امنیتی تحویل» |
| `07 — Field Activator` | 1 | «تخصیص سهمیه بنکدار تضمین می‌شود» → «ثبت و رهگیری می‌شود» |
| `08 — Corporate` | 3 | «تسویه غیرامانی تضمین می‌شود» → «ثبت و رهگیری می‌شود»; «تضمین تحویل با کد احراز فیزیکی» → «تحویل با احراز کد فیزیکی»; «اپلیکیشن راننده» → «سطح تحویل (Handoff)» |
| `09 — Prototypes & Flows` | 6 | FL-01/FL-04 «تایمر معکوس ۳۰ دقیقه» / «شمارنده معکوس ۳۰ دقیقه SLA» → «۱۲۰ دقیقه کاری»; «OTP شش رقمی» → «کد امنیتی تحویل»; «انطباق تضمین‌شده» → «منطبق»; «تضمین یکپارچگی» → «یکپارچگی» |
| `10 — Design QA` | 3 | QA-04 «۴. کد ۶ رقمی تحویل…» → «کد تحویل و استثناها (طول رقم: OPEN — تصمیم محصولی)»; QA-01 «صف پذیرش ۳۰ دقیقه‌ای» → «۱۲۰ دقیقه کاری»; QA-01 «کد ۵ رقمی OTP» → «کد ۴ رقمی OTP» |

**Note:** Live evidence showed the file had already partially absorbed Wave 01 claims before this batch (QA-04 and FL-04 already referenced 120 working minutes and 6-digit delivery OTP). The unresolved delivery-OTP length is now explicitly marked `OPEN` in QA-04 instead of being asserted as canonical.

**Batch 2 (verification + residue cleanup) — PENDING**: tab suspended mid-run. Pending items: residue of the form «…کاری‌ای» (artifact of rule 12/13 on «۳۰ دقیقه‌ای»), VD-02 «حداکثر زمان مجاز…: ۳۰ دقیقه» and «مهلت پاسخ: ۱۴ دقیقه مانده» countdown, OP-01 «حد مجاز: ۳۰ دقیقه», QA-03 «فیلد ورود کد تأیید (OTP) ۵ رقمی مستقل», final leftover scan for `۳۰ دقیقه | ۵ رقمی | ۶ رقمی | 5-Digit | 6-Digit | تضمین | راننده` on all pages, then export-based visual verification of the edited boards (QA-01, RT-01, board 02 of `01 — Components`).


---

## L. Batch execution record — continuation (2026-09-20)

**Batch 2 applied — 1 change:** residue «۱۲۰ دقیقه کاری‌ای» → «۱۲۰ دقیقه‌ای کاری». Full-page leftover scan produced the input for batch 3.

**Batch 3 applied — 24 changes across 9 pages:**

- Login OTP residues to 4 digits: `01` board 08 («کد تأیید ۵ رقمی ورود» → ۴ رقمی), `QA-03` component spec, catch-all «۵ رقمی» / «5-Digit».
- Delivery-OTP digit claims neutralised everywhere (لوose «ى» variants included): `QA-04` «منحصراً ۶ رقمی», `ST-08` «چرخه عمر توکن و کد ۶ رقمی» / «تولید کد رمزنگاری‌شده ۶ رقمی», `VD-03`, `RT-19` «کد امنیتی (OTP) اعلام‌شده به راننده», `OP-15` «Resend 6-Digit Delivery OTP», `FL-04` «6-Digit OTP» / «6-Digit Restricted Handoff», `QA-01` «کد تحویل محرمانه ۴ رقمی». All now read digit-agnostic with the `OPEN` marker where a contract assertion existed.
- Acceptance-SLA leftovers → 120 working minutes: `VD-07` «حداکثر ۳۰ دقیقه», `OP-01` «بیش از ۳۰ دقیقه» and «(>۳۰ دقیقه)», `OP-10` «مهلت ۳۰ دقیقه جهت بررسی و صدور حواله انبار».
- Guarantee wording neutralised: `CP-03` «تضمین حاکمیتی», `ST-02` «تضمین ثبت», `ST-01` «تضمین زمان تحویل قطعی» → «ثبت زمان تحویل قطعی», `RT-14` «با تضمین» → «با اولویت», `QA-03` «تضمین حاشیه سود», `00 — Foundations` «تضمین انطباق طراحی بصری».

**Batch 4 applied — 1 correction (self-audit catch):** `03 — States & Patterns` (ST-02): the inventory-reservation expiry text had been caught by the generic «بیش از ۳۰ دقیقه» rule and wrongly rewritten to 120 working minutes. `CANONICAL_CONTRACT_MATRIX.md` row 12 and `scripts/test_inventory_reservations.py` define an explicit **15-minute** reservation lifecycle; the text now reads «به دلیل عدم فعالیت بیش از ۱۵ دقیقه، رزرو موقت موجودی انبارها منقضی گردید». Lesson recorded: domain-specific timers must be resolved against their own canonical source before any find-and-replace.

**Running total: 50 live text changes across 9 pages**, all pattern-based with before/after recorded in the mission output.

**Pending verification exports** (blocked by tab suspension at time of run): `QA-01`, `RT-01`, `01 — Components` board 02 (`comp02` = `b6b30b77-…a57f9d45fa67`, `rt01` = `b6b30b77-…a5831d5160d3`, `qa01` = `b6b30b77-…a5883f368cca`).

**Deliberately untouched (verify against canonical source before editing):** none remaining — the reservation-expiry value was corrected to the canonical 15 minutes in batch 4.

- The claim in `48_WAVE_01` (6-digit, 4-digit eradicated) is **not** canonical and must not be implemented as settled behaviour.
