# POL MVP — BUILD_PLAN

**Contract:** Master Build Instruction (repo root session)  
**Root:** `mvp/`  
**Authorized branch:** `main` (current working branch at Phase 0 kickoff)  
**Created:** Phase 0  

---

## 1. Phases

| Phase | Name | Status |
|-------|------|--------|
| 0 | Discovery & Artifacts | **DONE** (2026-09-22) |
| — | BUILD GATE 0 | **PASS** |
| 1 | Foundation + Design System | NEXT |
| 2 | Web MVP | PENDING |
| 3 | Android MVP (Expo) | PENDING |
| 4 | Global QA + Regression | PENDING |
| 5 | Delivery + Final Audit | PENDING |

### BUILD GATE 0 — checklist (Master Instruction §8)

- [x] `MVP_SCREEN_MATRIX.md`: 68 screens, id/route/role/source  
- [x] Every route sourced or GAP/PROPOSED (corporate → G-006)  
- [x] Every API dependency in `MVP_API_MAP.md` (REAL / CONTRACT / MOCK / GAP)  
- [x] Unresolved conflicts in `MVP_KNOWN_GAPS.md` (G-001…G-020)  
- [x] Out-of-scope explicit in this file §2  
- [x] `mvp/` skeleton: workspaces + packages + `apps/web` **typecheck EXIT 0 + next build EXIT 0**

### Phase 2 module order (each to module DoD before next)

1. Auth / Profile / Notifications  
2. Retailer loop (R-01…R-13 + RT-17/18/20/16/19)  
3. Vendor loop (V-01…V-12 + VD-14…18)  
4. Ops (O-01…O-10 + OP-11…15 where in scope)  
5. Field web parity (F-01…F-05)  
6. Corporate (C-01…C-08, PUBLIC_ANON)  

---

## 2. Out of scope (never implement)

Source: `POL_00_PROJECT_CONTROL/MVP_EXECUTION/31_OUT_OF_SCOPE_MVP.md`, `FUTURE_VERSION_NOT_MVP.md`, DECISION_REGISTER.

- [ ] BNPL / credit underwriting  
- [ ] Wallet / stored value UI (D-021)  
- [ ] Escrow / custody UX (D-025)  
- [ ] POL-owned warehouse / fleet (D-008)  
- [ ] Advanced route optimization  
- [ ] Sponsored products / ads  
- [ ] Advanced recommendation AI  
- [ ] Complex loyalty / gamification / social commerce  
- [ ] Multi-touch referral rewards UI (D-016 — attribution only)  
- [ ] Manufacturer commerce surface  
- [ ] Quantity splitting one line across vendors (D-014 inverse)  
- [ ] Second business-logic layer in frontend  
- [ ] Second backend runtime  
- [ ] Speculative microservices  
- [ ] **Full Driver App** (D-023 — handoff link only)  
- [ ] Multi-city (D-001 — Ahvaz only)  
- [ ] Decorative BI before queues work (O-09)  
- [ ] Hero carousels on retailer home (R-02)  

---

## 3. Architecture (locked by Master Instruction §5)

```text
mvp/
├── BUILD_PLAN.md
├── MVP_SCREEN_MATRIX.md
├── MVP_API_MAP.md
├── MVP_KNOWN_GAPS.md
├── apps/web/       # Next.js 15 + TS + Tailwind v4
├── apps/mobile/    # Expo (Phase 3)
└── packages/
    ├── tokens/ types/ api-client/ config/   # genuinely shared
    └── ui/         # shared only where semantics+a11y correct
```

**Layer order:** `config/tokens/types → api-client/auth → state/query → feature → ui/page`  
**analytics:** cross-cutting  

---

## 4. Coverage snapshots

| Cycle | Date | Screens total | VERIFIED | IMPLEMENTED | GAP | BLOCKED_EXTERNAL | N/A | PENDING | Notes |
|-------|------|---------------|----------|-------------|-----|------------------|-----|---------|-------|
| Gate 0 | 2026-09-22 | 68 | 0 | 0 | 0 | 0 | 0 | 68 | artifacts + skeleton; typecheck/build green |

Axes (per screen): Screen · Route · Role · API · State · Responsive/RTL · A11y · Test  

---

## 5. QA cycle log (per module)

| Module | Cycle | Date | Result | Evidence |
|--------|-------|------|--------|----------|
| (Phase 0) | — | — | artifacts only | — |

Rules: min 3 cycles/module; no identical failed check without new evidence; 2 identical blockers → GAP/BLOCKED_EXTERNAL.

---

## 6. Phase exit checklist

### Phase 0
- [x] Four artifacts exist and are source-cited  
- [x] `mvp/` skeleton present  
- [x] **BUILD GATE 0** items all checked (Master Instruction §8)  
- [ ] Milestone commit  

### Phase 1
- [ ] packages build; web typecheck/lint/build green  
- [ ] Tokens Light+Night; golden components with platform-aware states  
- [ ] Shell + middleware role gates  

### Phase 2
- [ ] All web families module-DoD  

### Phase 3
- [ ] Expo scaffold + functional parity matrix  

### Phase 4
- [ ] §10.4 Global Stop  

### Phase 5
- [ ] Final report + gap close-out  
