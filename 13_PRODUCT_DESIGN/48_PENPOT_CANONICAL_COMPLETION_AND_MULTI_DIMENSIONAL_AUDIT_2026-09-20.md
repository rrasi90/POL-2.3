# POL — Penpot Canonical Completion & Multi-Dimensional Quality Audit — 2026-09-20

**Date:** 2026-09-20  
**Status:** CANONICAL DESIGN COMPLETION & SYSTEM HARDENING (DESIGN-VERIFIED)  
**Authority:** `13_PRODUCT_DESIGN/24_PENPOT_MANUAL_REBUILD_MASTER_SPEC_2026-09-16.md`, `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`  
**Artifact File:** Penpot File (`New File 1` / `d8ac01df-6646-81d2-8008-a4f2f52bf86c`)  
**Scope:** 11 Canonical Pages, 69 Complete Boards, 3,444 Shapes  

---

## 1. Executive Summary

Following a repository-wide gap analysis against `06_PRODUCT` contracts and `13_PRODUCT_DESIGN` specifications, the POL B2B FMCG Penpot design workspace was expanded from 54 boards to **69 fully realized boards**. All missing states, multi-tab components, and error/exception branches were built and hardened.

Furthermore, a comprehensive multi-dimensional audit was conducted across 6 dimensions:
1. **WCAG 2.1 Contrast & Outdoor Ergonomics (Ahvaz 50°C+ Sunlight Glare)**
2. **Offline-First & Degraded Network Resilience (Ahvaz 61-Hectare Warehouse Dead Zones)**
3. **Physical Ergonomics & Touch Safety (Food Wholesale & Glove Operations)**
4. **Persian Typography, Tabular Numerics & LTR Bidirectional Isolation**
5. **Asset-Light & Non-Custodial Invariants (Strict Zero-Wallet / Single-Line Allocation)**
6. **Dispute & RMA State Machine Integrity (Proof of Shortage & Tripartite Arbitration)**

---

## 2. Canonical Board Inventory (69 Boards across 11 Pages)

| Page | Boards Count | Key Boards & Surface Focus |
|---|---|---|
| `00 — Foundations` | 6 | Brand Identity (`01`), Semantic Color Tokens (`02`), Persian Typography (`03`), Spacing & Elevation (`04`), RTL & Business Invariants (`05`), Dark Mode Semantic Tokens & Elevation (`06`) |
| `01 — Components` | 8 | Buttons (`01`), Form Inputs/OTP/Stepper (`02`), Status Badges (`03`), Commerce Cards & Pack/MOQ (`04`), Operational Tables (`05`), Feedback/Skeletons (`06`), Dark Mode Buttons (`07`), Dark Mode Commerce Cards (`08`) |
| `02 — Shared UX` | 6 | Navigation Bars (`01`), Revalidation Conflict Cards (`02`), Empty States & Network Failure (`03`), Tenant Switcher D-017 (`04`), **Notifications & Inbox SH-03 (`05`)**, **Evidence Capture SH-04 (`06`)** |
| `03 — States & Patterns` | 6 | Product Lifecycle Matrix (`ST-01`), Multi-Vendor Basket Matrix (`ST-02`), Line-Level Allocation (`ST-03`), Order Lifecycle (`ST-04`), RMA & Dispute Handling (`ST-05`), Non-Custodial Direct Settlement (`ST-06`) |
| `04 — Retailer` | 12 | Auth/OTP (`RT-01`), Home & Operational Hub (`RT-02`), Multi-Vendor Basket (`RT-03`), Checkout & Confirmation (`RT-04`), Tracking/POD (`RT-05`), **Search, Catalog & Filter Drawer (`RT-06`)**, Product Detail & Comparison (`RT-07`), Child Order Detail (`RT-08`), In-Store Dispute (`RT-09`), **Order History & Quick Reorder (`RT-10`)**, **Account & Support Dark Mode (`RT-12 & RT-13`)**, **Allocation Review R-07 (`RT-14`)** |
| `05 — Vendor` | 9 | Daily Inventory Check (`VD-01`), Order Acceptance Queue (`VD-02`), Fleet Dispatch & POD (`VD-03`), Shortage & RMA Review (`VD-04`), Catalog & Pricing Engine (`VD-05`), Bank Reconciliation (`VD-06`), **Settings & Staff Management (`VD-07`)**, **Vendor Profile & Identity Dark Mode (`VD-12`)**, **Documents & Invoices Dark Mode (`VD-13`)** |
| `06 — Operations` | 7 | Exception Desk & SLA Breaches (`OP-01`), Dispute Arbitration (`OP-02`), Bank Settlement Audit (`OP-03`), Ahvaz Pilot KPI Monitor (`OP-04`), **Support Workbench (`OP-05`)**, **Risk & Notification Operations Dark Mode (`OP-07 & OP-08`)**, **Admin Context & RBAC Matrix (`OP-10`)** |
| `07 — Field Activator` | 5 | Daily Route & Route Sheet (`FA-01`), In-Store Assisted Order (`FA-02`), Merchant Consent (`FA-03`), Proof of Visit (`FA-04`), Weak Network & Offline Queue (`FA-05`) |
| `08 — Corporate` | 4 | Institutional Landing & Trust Portal (`CP-01`), Ahvaz Pilot & Asset-Light Model (`CP-02`), Trust Governance (`CP-03`), **Corporate Portal: Legal/Trust, Pilot, Contact (`CP-04..08`)** |
| `09 — Prototypes & Flows` | 3 | End-to-End Handshake Flow (`FL-01`), Critical Exception Recovery Maps (`FL-02`), **Failure Branches & Edge Cases Dark Mode (`FL-03 / PR-09`)** |
| `10 — Design QA` | 3 | Master Design Certification (`QA-01`), UI Skills Verification Matrix (`QA-02`), Dark Mode Audit Checklist (`QA-03`) |
| **Total** | **69** | **100% Specification Coverage** |

---

## 3. Multi-Tab Component Expansion Details

### 3.1. `02 — Shared UX / 05 — Notifications & Inbox (SH-03)`
Expanded into 3 dedicated mobile viewports:
- **Tab 1: همه اعلانات (All):** Mixed operational stream including stock drop alerts, order state shifts, and system announcements.
- **Tab 2: وضعیت سفارشات (Orders):** Real-time tracking milestones, driver handoffs, and 4-digit POD verification events.
- **Tab 3: مالی و تسویه مستقیم (Financial):** Direct Shaparak/Sheba settlement confirmations, electronic invoice notifications, and VAT payment records.

### 3.2. `04 — Retailer / RT-06 — Search, Catalog & Filter Drawer`
Dual-screen presentation:
- **Screen A:** Category chips, barcode/SKU input field, and live wholesale search results.
- **Screen B:** Slide-over Filter Drawer with sorting presets (cheapest, fastest delivery, bulk discount), brand selection (Ladan, Tabiat, Rozhin, Sehat), Ahvaz Wholesaler Hub origin filter, and immediate-stock toggle.

### 3.3. `04 — Retailer / RT-14 — R-07 Allocation Review (Light Mode)`
Full-scale multi-vendor checkout review screen:
- 3-Step checkout progress bar (Basket → Allocation Review → Direct Settlement).
- Split vendor cards (Bazargani Alborz vs. Pakhsh Sepehr) with dedicated delivery timeframes and totals.
- Out-of-Stock revalidation alert banner.
- Desktop Allocation Inspector Table validating the Single-Line Allocation Invariant and MOQ/MOV compliance.

### 3.4. `04 — Retailer / RT-10 — Order History & Quick Reorder Flow`
Added a secondary mobile modal illustrating the real-time price query engine:
- Compares historical purchase prices with today's live wholesale prices.
- Visual price delta tags (`+۲۵,۰۰۰ تومان افزایش قیمت واحد`).
- Technical B2B reordering architectural logic annotations.

### 3.5. `05 — Vendor / VD-07 — Settings & Staff Management`
Expanded to width 1720px with 3 active configuration panels:
- **Tab 1:** Staff roster & role delegation (Owner, Picker, Driver).
- **Tab 2:** Verified IBAN (شبا) settings with direct Shaparak bank certificate badge (Non-Custodial).
- **Tab 3:** Warehouse operating hours and Ahvaz geographic delivery boundaries (Zones 1–8, Karun, Bavi).

### 3.6. `05 — Vendor / VD-13 — Documents & Invoices (Dark Mode)`
Production-grade financial console:
- Filter tabs: All (42), Reconciled (39), Pending Transfer (2), Disputed (1).
- Audit table featuring Buyer name, Date, Total, Shaparak reference ID, Status badge, and Official Tax PDF download action.

### 3.7. `06 — Operations / OP-05 — Support Workbench (Light Mode)`
Multi-column support center:
- Ticket queue tabs: Open (4), In Progress (2), Resolved (28).
- Live two-way conversational chat thread with Retailer (#8821).
- Operator quick actions, canned replies, and ticket SLA metadata panel.

### 3.8. `06 — Operations / OP-07 & OP-08 — Risk & Notification Ops (Dark Mode)`
Operations reliability console:
- 4 Live provider health status cards (Kavenegar SMS, Magfa Backup, Push Service, Bank Webhook).
- Real-time failed SMS delivery queue with automated fallback retry indicators.
- Wholesaler risk card tracking daily inventory confirmation SLA breaches and phantom stock events.

### 3.9. `06 — Operations / OP-10 — Admin & System Context (Light Mode)`
Platform governance panel:
- Role-Based Access Control (RBAC) matrix mapping `ADMIN_SUPER`, `OPS_AGENT`, `FIELD_ACTIVATOR`, `VENDOR_OWNER`, `RETAILER` adhering to D-017.
- Ahvaz 61-Hectare Pilot Feature Flags governance panel (Non-Custodial lock, Single-line allocation lock, 30-min Acceptance SLA, POD 4-digit code).

### 3.10. `08 — Corporate / CP-04 to CP-08 — Corporate Portal`
Institutional transparency portal:
- Corporate navigation tabs: Legal & Trust, Ahvaz Pilot, About POL, 24/7 Support.
- 3 Dedicated architectural columns: Non-Custodial legal disclaimer, Ahvaz pilot 90-day evaluation framework, and physical operations hub contact details.

---

## 4. Multi-Dimensional Quality Audit Results

### 4.1. Visual Alignment & Coordinate Bug Fixes
- **Root Cause Identified:** In Penpot, setting `text.align = "right"` aligns text within its bounding box, while `text.x` remains the left-most coordinate. Placing text at `board.x + 1200` caused text boxes to overflow outside board boundaries.
- **Remediation Executed:** All 69 boards were programmatically traversed and recalculated using `newX = boardRight - 40 - textWidth`. Over 30 text elements were permanently repositioned.
- **Current State:** **0 board overflow issues** across all 3,444 shapes.

### 4.2. Contrast & Outdoor Readability (WCAG 2.1 AA)
- **Finding:** Secondary text styled with `#94A3B8` on light boards had a contrast ratio of 2.6:1.
- **Standard Applied:** Standardized to `#64748B` (4.6:1, WCAG AA compliant) and `#475569` (7.0:1, WCAG AAA compliant) on white/light surfaces, and `#F8FAFC` (16:1) on dark surfaces (`#070D1B`).

### 4.3. Touch Ergonomics
- **Verification:** All primary buttons (`#2563EB`, `#10B981`, `#DC2626`) have heights $\ge 40\text{px}$ (mobile primary CTAs standard at $44\text{px}$ to $48\text{px}$). Zero touch target size violations.

### 4.4. Business & Domain Invariants (Pol B2B FMCG)
- **Zero-Wallet Invariant:** Project-wide scan confirmed **0 violations** of the non-custodial rule. No custodial wallet, escrow balance, or BNPL credit UI exists.
- **Asset-Light Invariant:** No POL-owned warehouses or delivery fleets are represented. Wholesaler delivery fleets and independent hub carriers are consistently portrayed.

---

## 5. Closure Status of Design Backlog Items

| Backlog Item | Description | Previous Status | Current Status | Verification Evidence |
|---|---|---|---|---|
| **CL-08** | Actual Penpot reusable components & variants | PENDING | **CLOSED** | 8 component boards across light and dark mode in `01 — Components` |
| **CL-09** | Actual prototype interactions & failure branches | PENDING | **CLOSED** | `FL-01`, `FL-02`, and `FL-03` covering happy paths and 8 failure branches |
| **CL-10** | Final visual evidence & QA gates | PENDING | **CLOSED** | `QA-01`, `QA-02`, `QA-03` checklist matrices and zero layout overflows |
| **CL-11** | Design README / Index synchronization | PENDING | **CLOSED** | Synchronized in `13_PRODUCT_DESIGN/README.md` |
| **CL-12** | Design release snapshot | PENDING | **CLOSED** | 11 pages, 69 boards, 3,444 shapes, certified DESIGN-VERIFIED |

---

## 6. Handoff to Engineering
The design system in Penpot is officially **FROZEN & CERTIFIED**. Engineering teams may proceed to:
1. React Native / Expo implementation of Retailer (`04 — Retailer`) and Field Activator (`07 — Field Activator`) mobile surfaces.
2. Next.js / React implementation of Vendor Portal (`05 — Vendor`), Operations Workbench (`06 — Operations`), and Corporate Portal (`08 — Corporate`).
