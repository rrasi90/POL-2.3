# POL Design Closure Backlog & Conflict Resolution — 2026-09-16

## Purpose
Single remaining worklist after the repository-wide design completeness audit. This file prevents old wording, historical rules or implementation details from leaking into the final Penpot artifact.

## Closure items

| ID | Issue | Authority | Required closure | Design impact |
|---|---|---|---|---|
| CL-01 | Centralized-payment wording in `MVP_Definition.md` vs non-custodial direct settlement | `DECISION_REGISTER` + `09_OPERATIONS/Payments_and_Settlement.md` + `08_DATA/MULTI_VENDOR_ORDERING_MODEL.md` | Treat “centralized” as consolidated buyer visibility only; never custody | Checkout/payment/reconciliation copy |
| CL-02 | Wallet-like refund language in older lifecycle material | Current MVP excludes wallet/escrow | Replace with direct vendor refund/manual credit/reconciliation wording | RMA/refund states |
| CL-03 | Framework “not locked” sentence in older frontend strategy doc | Repository completion/readiness gate | Current approved direction: Next.js/React + React Native/Expo unless superseded | Frontend handoff only |
| CL-04 | Legacy role aliases `SUPER_ADMIN` / `OPS_ADMIN` | Current RBAC spec | UI uses current canonical roles / job functions | Ops/admin profile and access states |
| CL-05 | Numeric reputation penalty language in order lifecycle | No approved MVP design rule for reputation scoring UX | Keep internal/undisplayed until explicitly specified | Vendor operations |
| CL-06 | Final font availability in Penpot | Typography contract | Verify `B Lotus` and `Vazirmatn` availability in target workspace before font lock | Foundations + all text |
| CL-07 | Final screen-to-contract mapping | Readiness gate | Produce route/data/state/action/analytics matrix for actual frontend route set | Handoff |
| CL-08 | Actual Penpot reusable components/variants | Written specs do not prove artifact implementation | Build and inspect real components and variants | Entire Penpot |
| CL-09 | Actual prototype interactions | Written prototype matrix does not prove wiring | Build critical happy/failure branches and inspect exports | Prototypes |
| CL-10 | Final visual evidence | Agent protocol requires visual inspection | Export/inspect/fix/approve every final batch | Design QA |
| CL-11 | Design README/index drift | Fixed in latest commit | Keep `13_PRODUCT_DESIGN/README.md` synchronized when adding future design files | Agent discoverability |
| CL-12 | Design release snapshot | No single immutable final design manifest yet | Freeze final Penpot revision, hashes, pages, component count, state count and QA result | Release governance |

## Rules during closure

1. Do not create new business rules while closing visual gaps.
2. Do not revive historical Single-Vendor, wallet/escrow, fixed-vendor-count or old-role semantics.
3. Do not mark Penpot complete based only on written specifications.
4. Every closure item must leave evidence in GitHub or in the final verified design artifact.

## Final release gate

The design release can be marked `DESIGN-VERIFIED` only when CL-01 through CL-12 are either closed or explicitly marked `NOT APPLICABLE` with evidence.

The production product remains subject to separate HTTP/runtime/auth/provider/observability/deployment/recovery gates.
