# POL MVP — KNOWN GAPS / CONFLICTS / BLOCKED

**Rule (Master Instruction §3):** higher authority wins; log here; unresolved = screen status `GAP` + minimal stub; do not guess; do not stop build unless critical dependency.

**Status values in this file:** `CONFLICT` | `GAP` | `BLOCKED_EXTERNAL` | `PROPOSED`

---

## G-001 — OTP digit count (CONFLICT — RESOLVED)

- **Sources:** `frontend_route_contract_map.md` “OTP 6-digit” vs **D-018** + `scripts/operational_config.py` `OTP_CODE_LENGTH = 4`
- **Resolution:** D-018 wins → **4-digit**. Route map note is stale.
- **Action:** implement 4-digit; no further guess.

## G-002 — Master Tree filename in SoT (CONFLICT — RESOLVED)

- **SoT** names `50_POL_MASTER_PENPOT_UI_UX_TREE_SPEC_…`; actual file `50_POL_MASTER_PRODUCT_EXPERIENCE_DELIVERY_CONTROL_TREE_SPEC_…` v4.3.0
- **Resolution:** actual file + v4.3.0 is canonical.

## G-003 — Catalog list path (CONFLICT)

- **Contract #1:** GET `/api/v1/products/search`
- **Implemented:** GET `/api/v1/catalog/search`, GET `/api/v1/search`
- **Resolution for build:** use REAL paths for live calls; do not invent `/products/search`.
- **Open:** whether contract will be renamed backend-side → `BLOCKED_EXTERNAL` for literal contract parity only if a test requires `/products/search`.
- **Status:** CONFLICT (documented); screens use REAL.

## G-004 — Notifications inbox path (CONFLICT)

- **Contract:** `/api/v1/inbox/items*`
- **Implemented:** `/api/v1/notifications` + preferences
- **Build:** use REAL `/notifications`; mark contract inbox as non-HTTP until backend aligns.
- **Status:** CONFLICT

## G-005 — Notification read field name (CONFLICT — verify at wire time)

- **Some Phase C UI:** `is_read` vs type/backend `read`
- **Action:** when wiring, read `notifications.py` response model; use backend field only.
- **Status:** CONFLICT (pending verify cycle)

## G-006 — Corporate routes absent from route map (GAP)

- Spec 22 C-01…C-08 + Master Tree CP-* exist; `frontend_route_contract_map.md` has **no corporate routes**.
- **Build:** propose routes `/`, `/retailers`, `/vendors`, `/how`, `/pilot-ahvaz`, `/about`, `/contact`, `/legal` as `PROPOSED` in matrix with source = screen IDs only; record here.
- **Status:** GAP → screens implemented as static marketing under proposed routes; mark route source `PROPOSED-G006`.

## G-007 — Admin dedicated screen family underspecified (GAP)

- Spec 22 folds admin into O-10; route map has `/admin/users`, `/admin/orgs` with **no API source** (not in 50-endpoint or REAL list except audit/exceptions).
- **Build:** implement O-10 admin/context using REAL `/admin/audit-logs` + `/admin/exceptions/dashboard`; users/orgs screens = stub list UI without fake CRUD success → **GAP** rows.
- **Status:** GAP

## G-008 — No HTTP for pilot analytics O-09 (GAP)

- No analytics endpoints in inventory.
- **Build:** screen with empty/loading + explicit “data unavailable” or mock aggregate **without** inventing metrics API paths; prefer GAP UI shell.
- **Status:** GAP

## G-009 — Vendor customers V-09 list API missing (GAP)

- No `GET /customers` in inventory or routes.
- **Build:** stub + GAP; optional derive from retailer-facing orders only if documented (not documented → no derive).
- **Status:** GAP

## G-010 — Staff/access management V-11 / permission APIs (GAP)

- No membership admin HTTP beyond profile/membership self-serve.
- **Build:** read-only stub or GAP; no fake invite success.
- **Status:** GAP

## G-011 — Admin broadcasts / SLA overrides / category admin (CONTRACT)

- Contract-only endpoints; mock allowed with same contract if screens need them in Phase 2 Ops.
- **Status:** GAP until mock or backend HTTP

## G-012 — Basket GET list not in routes (GAP)

- Only POST create/items/preview; no GET basket.
- Screens that reload basket need client persistence **or** GAP; checkout uses allocation-preview + POST orders.
- **Status:** GAP (client basket cache is presentation, not business rule)

## G-013 — Returns list all-orders (GAP)

- Only `GET /orders/{order_id}/returns` — no global returns list.
- R-11 entry via order → returns; global RMA queue for ops may need GAP.
- **Status:** GAP for global list

## G-014 — Design contradictions register (PROPOSED / multi)

Prior research noted: brand blue vs tokens, type scale variants, radius, motion bands, density labels, WCAG version wording, Latin fallback font, breakpoints, focus ring details, golden-screen set.
- **Resolution:** doc 56 (Precision Commerce) wins for visual tokens; motion bands 120–160 / 160–240 / 200–280 / ≤400ms; WCAG 2.2 where doc 21/22 adopt it.
- Anything still undefined at implement time → new `G-0xx` + `PROPOSED` token marked in code.
- **Status:** PROPOSED (rolling)

## G-015 — OP-06 / OP-09 missing from Master Tree §9 listing (CONFLICT)

- Spec 22 has O-06, O-09; Master Tree tree listing gaps numbering.
- **Resolution:** implement per spec 22 (higher for screen detail after decisions); tree is navigation aid.
- **Status:** CONFLICT (resolved for build)

## G-016 — Phase C dead routes (historical)

- `/admin/users`, `/admin/orgs`, `/ops/finance`, `/ops/reconciliation` were nav-only.
- **Build:** only routes in SCREEN_MATRIX with sources; no dead links.

## G-017 — Backend HTTP coverage 21/50 at inventory snapshot (BLOCKED_EXTERNAL for non-mock)

- Many CONTRACT endpoints not yet on FastAPI at Stage 07 snapshot; research-hardening added many REAL routes (orders list, support, field, etc.) beyond that snapshot.
- **Build:** prefer REAL map in API_MAP §3; remaining CONTRACT → MOCK same-contract.
- **Status:** BLOCKED_EXTERNAL for true e2e against missing HTTP; not a stop — continue with mocks.

## G-018 — Android readiness RED in design audit 60 (BLOCKED_EXTERNAL sequencing)

- Dual-client mandated (D-026) but audit marks Android RED pre-build.
- **Build:** Phase 3 still required by contract; not a Phase 0 blocker.
- **Status:** informational

## G-019 — Working tree lacks many canonical files (CONFLICT — tooling)

- Docs on `origin/product-architecture-evolution-2026-09-20` / research-hardening; working tree `main` has partial 50/56 staged.
- **Resolution:** `git show <ref>:<path>` for reads (§2.8); do not switch branches unless necessary.
- **Status:** CONFLICT (tooling)

## G-020 — Corporate `PUBLIC_ANON` not a backend role (GAP — expected)

- Marketing screens need no auth; no API required for C-01…08 static content.
- **Status:** GAP (by design — static)

---

## How to add

```
## G-0xx — Title (TYPE)
- Sources: …
- Resolution / Build action: …
- Status: …
```

Update SCREEN_MATRIX status + API_MAP when an entry changes.
