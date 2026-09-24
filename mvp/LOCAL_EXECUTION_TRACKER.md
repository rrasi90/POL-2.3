# POL — Local Execution & Verification Tracker

**Purpose:** This file is the handoff/control sheet for work that cannot be completed through the GitHub repository integration alone.  
**Rule:** When a local item is completed, tell the assistant **«انجام شد»** (or provide the result/log). The assistant will re-check the repository, CI evidence, and this tracker before closing the item.

**Repository:** `rrasi90/POL-2.3`  
**Branch:** `main`  
**Last repository-verified commit:** `5494420ff350385a3d96fc1a7d63a95216a7aa8a` (latest main HEAD verified remotely)  
**Code under verification:** `f8ef267e6666a03b483afdd8618585ed82086014`  
**Latest main HEAD:** `5494420ff350385a3d96fc1a7d63a95216a7aa8a`

---

## 1. Current stage

### Stage 6 — Mobile QA Cycle 3
**STATUS: CLOSED / PASS**

Evidence:
- Mobile CI `35893284378` — SUCCESS
  - Typecheck
  - Functional QA **23/23**
  - Regression/Cross-module QA **11/11**
  - Expo config validation
  - Expo Android export
- Backend CI `35893284312` — SUCCESS
  - migration chain
  - bootstrap verification
  - full verification suite
  - machine-readable artifact

---

## 2. Local-only gates

These require a running local environment/device/emulator and therefore cannot be honestly marked PASS from repository inspection alone.

### LOCAL-01 — Night Theme Visual Verification
**STATUS: OPEN / LOCAL REQUIRED**

What is already implemented:
- `mvp/apps/mobile/src/theme.ts` contains independent `light` and `night` palettes.
- Screens consume the centralized `colors.*` tokens.
- No screen-by-screen visual evidence has yet been recorded.
- Current `App.tsx` does not expose an end-user Light/Night toggle; `setThemeMode()` exists but is not currently wired into the app navigation/UI.

Local work:
1. Start the Expo mobile app.
2. Verify every applicable mobile screen in **Light** mode.
3. Verify every applicable mobile screen in **Night** mode.
4. Check:
   - background/surface contrast
   - primary/secondary/muted text contrast
   - borders/dividers
   - warning/success/danger states
   - inputs and buttons
   - empty/error/loading states
   - scrolling content
   - RTL/Farsi readability
   - status bar/readability
5. If Night mode needs an app-level toggle to make the visual gate executable, wire it without introducing a second theme system.
6. Record screenshots or another reproducible visual evidence set.
7. Report the result back for repository reconciliation.

**Do not mark PASS merely because `theme.ts` contains a Night palette.**

---

### LOCAL-02 — Live Basket → Allocation → Checkout → Order E2E
**STATUS: OPEN / LOCAL API + DB REQUIRED**

Canonical flow:
`Search → Product → Basket → Allocation Preview → Checkout → Order Group → Child Orders → Order Detail`

Required environment:
- PostgreSQL 18 with the canonical `pol` schema.
- FastAPI on `:8000`.
- Valid authenticated retailer session/token.
- At least one product/vendor combination with allocatable inventory.

Authoritative routes:
- `GET /api/v1/catalog/search`
- `POST /api/v1/baskets`
- `POST /api/v1/baskets/{basket_id}/items`
- `POST /api/v1/baskets/{basket_id}/allocation-preview`
- `POST /api/v1/orders`
- `GET /api/v1/orders`
- `GET /api/v1/orders/{order_id}`
- `GET /api/v1/orders/{order_id}/timeline`

Checkout requirements:
- `Idempotency-Key` must be UUIDv4.
- Checkout payload must contain the authoritative allocation plan and delivery address.
- Do not bypass `CanonicalCheckoutGateway`.

Acceptance evidence:
- Basket created.
- Basket item added.
- Allocation plan created.
- Checkout returns an order group.
- Child vendor orders exist.
- Order list contains the resulting order(s).
- Order detail/timeline resolves.
- No duplicate order group is created by the normal request.

---

### LOCAL-03 — Checkout Idempotency Replay
**STATUS: OPEN / LOCAL API + DB REQUIRED**

Use the **same**:
- authenticated retailer
- allocation plan
- checkout payload
- exact same UUIDv4 `Idempotency-Key`

Expected behavior:
1. First request creates the order group.
2. Exact replay with the same key returns the existing checkout result.
3. Replay must indicate `idempotent_replay: true` where exposed by the response contract.
4. Database must not contain a second order group for that idempotency key.
5. Reusing the same key with a materially different checkout payload must be rejected.

Canonical implementation authority:
`scripts/checkout_gateway.py`

---

### LOCAL-04 — Device-level mobile smoke
**STATUS: OPEN / RECOMMENDED**

After the Night gate:
- Launch the exported/buildable mobile app on emulator or physical Android device.
- Verify login → role workspace.
- Verify retailer catalog → basket → allocation → checkout.
- Verify vendor order lifecycle.
- Verify Ops surfaces.
- Verify Field task flow.
- Verify account/notification preferences.
- Verify order detail.
- Verify back navigation and error states.

This is exploratory/device-level evidence and is distinct from deterministic CI QA.

---

## 3. Known unresolved repository gaps

These are **not automatically local bugs**. Do not invent implementations for them.

| ID | Status | Current rule |
|---|---|---|
| D-028 / barcode | GAP / CONTRACT | No runtime barcode adapter until authoritative HTTP/runtime contract exists |
| V-09 Vendor Customers | GAP | No invented CRUD |
| V-11 Vendor Staff | GAP | No invented permission CRUD |
| G-003 catalog path | documented conflict | Use REAL `/catalog/search`; do not force contract-only `/products/search` |
| G-004 inbox path | documented conflict | Use REAL `/notifications` |
| Refresh-token rotation policy | OPEN | Do not invent policy |
| Invoice timing | OPEN | Existing default is invoice on ACCEPTED; confirm before finance E2E |
| OpenPencil WAVE-02 | BLOCKED_EXTERNAL | Requires local OpenPencil MCP on `:7600` |
| Real driver metrics | BLOCKED_EXTERNAL | No production metrics source supplied |
| SMS provider | BLOCKED_EXTERNAL | Live provider credentials absent |

---

## 4. Work already completed remotely

- Source-of-truth reconciliation.
- Repository audit.
- Backend verification.
- Mobile CI Cycle 1.
- Mobile functional/state-transition/parity Cycle 2.
- Supported mobile REAL-API parity expansion.
- Mobile Regression/Cross-module Cycle 3.
- Regression test defect correction.
- Documentation reconciliation through the current CI evidence.

Latest mobile Cycle 3 evidence:
- Run `35893284378`
- Functional QA **23/23**
- Regression QA **11/11**
- Expo config **PASS**
- Android export **PASS**

Latest backend evidence:
- Run `35893284312`
- Full verification **SUCCESS**

---

## 5. Execution order from here

1. **LOCAL-01** — Night visual verification.
2. **LOCAL-02** — live basket → allocation → checkout → order E2E.
3. **LOCAL-03** — checkout idempotency replay.
4. **LOCAL-04** — device-level mobile smoke.
5. Assistant re-checks evidence and reconciles repository documents.
6. Final global regression.
7. Final Delivery DoD audit.

**Important:** Completing a local item does not itself close the stage. The assistant must verify the reported evidence and update the authoritative project documents.

---

## 6. Handoff protocol

When a local task is finished, send:

`انجام شد LOCAL-01`

or, preferably:

`LOCAL-01 انجام شد — نتیجه: PASS — screenshots/log available`

For E2E:

`LOCAL-02 انجام شد — order_group_id: <id> — child_orders: <count>`

For idempotency:

`LOCAL-03 انجام شد — first=<result> replay=<result> duplicate_groups=<count>`

The assistant will then perform the repository-side verification and reconciliation.


---

## 7. Source remediation batch — 2026-09-24

Remote fixes applied for the locally reported findings:

- G-023: F-03 no longer calls catalog search without q.
- G-024: F-03 maps canonical_name_fa and master_sku.
- G-025: runtime Light/Night theme wiring added across the mobile style system, system-aware initialization added, and explicit Light/Night controls added to Account.
- G-026: supported Iranian local phone input is normalized to E.164 and backend OTP transport schemas now enforce E.164.

Verification evidence after source changes:
- Mobile CI run 35987850765 on commit 62870503e36a6f2c95929862f839e8bd8258e894 — SUCCESS.
- Functional/state-transition QA: 28/28.
- Regression/cross-module QA: 15/15.
- Typecheck, Expo config validation, and Android export: PASS.

LOCAL-01 Night and LOCAL-04 device smoke still require a fresh install/retest of the updated build; CI does not replace device visual evidence.
