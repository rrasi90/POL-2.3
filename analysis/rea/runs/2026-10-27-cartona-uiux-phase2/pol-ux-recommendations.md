# POL UX Recommendations — CP8

Derived from `cartona-to-pol-pattern-mapping.csv` (18 patterns) + `pol-ux-gap-register.csv` (16 gaps, mechanically scored per `priority-scoring-method.md`). **Nothing here is implemented in this mission.** Each item is a future visual-phase work card; `change_class` gates what may be implemented without product decisions.

## Top recommendations (evidence-backed, safe for a future VISUAL phase)

### R1 — Image error placeholder (GAP-003, P0, score 45)
Cartona ships an explicit image-load failure state (full Arabic string verbatim in payload: «حدث خطأ اثناء تحميل الصورة، برجاء المحاولة مره اخري.» — CP6 STATIC_VERIFIED). POL screens render images without a failure state.
- **Proposal:** generic `ImageErrorPlaceholder` in `mvp/apps/mobile/src/components/ui.tsx`; Persian copy: «تصویر بارگذاری نشد — برای تلاش مجدد لمس کنید».
- **Must stay unchanged:** image URLs, caching, no auto-retry loops beyond user tap.
- **Acceptance:** placeholder shows on simulated failure; RTL correct; theme-aware (light/night).
- **Regression:** no network behavior change; existing lists render identically when images load.

### R2 — Illustration-backed empty states (GAP-002, P0, score 43)
Cartona bundles dedicated empty/error-state illustrations (62 PNG assets, several in the empty/error family — CP5). POL's `Empty` component (`ui.tsx:113`) is text-only.
- **Proposal:** extend `Empty` with an optional illustration slot; POL-original neutral illustrations (never Cartona assets). Sample copy stays as-is; example: «هنوز سفارشی ثبت نشده است».
- **Regression:** component API backward-compatible; no data changes.

### R3 — One-tap reorder on past orders (GAP-001, P1, score 46)
Cartona has reorder as a first-class surface (`/order-reorder` route + reorder columns — CP1-confirmed). POL's orders list (`RetailerMobileScreen.tsx` ~553) has no reorder action.
- **Proposal:** reorder button on eligible past orders that **reuses the existing place-order pipeline unchanged**; confirm dialog: «تکرار این سفارش با N قلم کالا؟».
- **Must stay unchanged:** place-order API, idempotency, basket rules, allocation logic. The button only pre-fills what the user could do manually.
- **Acceptance:** reorder produces a draft basket identical to manual re-add; negative test: product unavailable → shows standard unfulfilled handling.
- **Note:** INTERACTION_PRESENTATION class — needs the regression guard above before any implementation phase.

### R4 — Category tiles with real illustrations (GAP-004, P1, score 39)
POL categories use emoji tiles (`RetailerMobileScreen.tsx` ~418); Cartona uses image assets (1024×1024 category art — CP5).
- **Proposal:** POL-original neutral iconography per category; layout unchanged.

### R5 — Supplier card trust/term signals (GAP-006, P1, score 41)
Cartona exposes supplier-level terms (cashback/MOV endpoints — CP6). POL vendor cards show limited signals.
- **Proposal:** surface **already-returned** vendor fields (verify availability first); if the API lacks the fields, escalate — **no API changes in any phase**.

### R6 — Home section hierarchy (GAP-005, P1, score 39)
Anchored section pattern (`/home#offers_section2` — CP6) implies deliberate offer-strip hierarchy. POL home already has categories/offers/quick actions; propose ordering + visual grouping refinements only.

### R7 — Post-registration success moment (GAP-009, P1, score 33)
Cartona's `/signup-celebration` + `account_created.png` (CP6/CP5). POL register flow ends flat.
- **Proposal:** success state after existing register succeeds: «حساب شما ساخته شد؛ خوش آمدید». Flow logic untouched.

### R8 — Read-only account statement view for بنکدار (GAP-010, P1, score 35)
Cartona supplier listing advertises account statements. POL vendor finance has invoices/settlements but no statement-style view.
- **Proposal:** read-only rendering of existing finance data grouped by period — only if the data already exists client-side; otherwise product decision.

## Explicitly NOT recommended for adoption now (HOLD — product decisions)

| Pattern | Why held |
|---|---|
| Wallet/BNPL credit surface (Cartona headline feature) | Net-new business surface for POL; `REQUIRES_PRODUCT_DECISION`; POL finance = invoices today |
| Live map order tracking | New dependency + backend surface |
| New/returning onboarding split | Flow logic change |
| Seasonal campaign system (Ramadan theming) | Campaign strategy decision |
| Dedicated search screen | Navigation change; needs product sign-off (P2 if approved) |
| Group ordering to bypass minimums | BUSINESS_LOGIC_RISK — order-rule mechanics; do not copy |

## Persian text standards for any future implementation phase

- Use Persian ی/ک (U+06CC/U+06A9) — never Arabic ي/ك in POL UI strings.
- RTL via existing `direction: "rtl"` patterns; explicit `direction: "ltr"` for OTP digit rows and numeric inputs (existing POL convention, `LoginScreen.tsx:217`).
- Numbers/currency via existing `i18n/fa.ts` helpers (`formatFaNumber`, `formatToman`).
- No Cartona strings copied — all copy written fresh for POL users (wholesale register, فارسی natural).
