# Priority Scoring Method — CP8

## Dimensions (1–5 unless noted)

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| user_impact | cosmetic | saves effort on a common task | unblocks or prevents errors in a core flow (find/buy/receive) |
| business_fit | unrelated to POL's B2B wholesale model | neutral | directly matches POL wholesale order/credit/ops reality |
| evidence_confidence | listing-only or single weak string | multiple consistent static artifacts | runtime-observed or multi-source corroborated |
| implementation_effort (inverted: 5 = trivial) | new surface/dependency | component + wiring | pure CSS/theme/layout tweak in existing component |
| coverage | one screen | a flow | many screens/components |
| accessibility_value | none | minor | meaningfully improves legibility/touch targets |
| logic_risk (inverted: 5 = none) | could alter order/price/credit rules | touches flow decisions | presentation only |

## Composite score (a decision aid, not a scientific measure — published per mission §39)

`score = user_impact*3 + business_fit*2 + evidence_confidence*2 + implementation_effort + coverage*2 + accessibility_value + logic_risk`
(max = 45). Ties broken toward lower implementation_effort.

## Bands

| Band | Rule |
|---|---|
| P0 | score ≥ 34 AND logic_risk = 5 (presentation-only) — strong-evidence experience barrier fix |
| P1 | score 26–33 with logic_risk ≥ 4 |
| P2 | score 18–25 |
| P3 | score < 18 |
| HOLD | REQUIRES_PRODUCT_DECISION patterns (wallet/BNPL, map tracking, seasonal campaigns, onboarding flow split) regardless of score |
| NEEDS_EVIDENCE | static-only patterns whose value can't be judged until CP4 runtime comparison |

## Guardrails

- No pattern is prioritized merely for resembling Cartona (mission §39).
- Any pattern touching order/price/inventory/MOQ/credit rules is BUSINESs_LOGIC_RISK → excluded from implementation in this mission by definition; priorities describe only future visual phases.
- Visual_only column in the mapping CSV is the gate: `yes` = safe for a future UI phase; `no` = product decision required first.
