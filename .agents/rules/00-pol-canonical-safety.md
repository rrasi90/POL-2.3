# POL Canonical Safety Rules

These rules are persistent workspace constraints for Antigravity when working on POL.

## Authority

1. `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`
2. Canonical product/domain/data/operations documents
3. `POL_00_PROJECT_CONTROL/API_APPLICATION_BOUNDARY.md`
4. `13_PRODUCT_DESIGN/14_DESIGN_DECISION_REGISTER.md`
5. `13_PRODUCT_DESIGN/21_MVP_DESIGN_AND_FRONTEND_READINESS_GATE_2026-09-16.md`
6. `13_PRODUCT_DESIGN/22_UI_UX_PAGE_AND_SECTION_COMPLETION_SPEC_2026-09-16.md`
7. Visual artifacts

Never invent an undocumented business rule. Mark materially unresolved behavior `OPEN`.

## Repository safety

Target design branch: `research-hardening-2026-09-14`.

Before editing:
- fetch remote;
- verify branch and HEAD;
- verify clean status or explicitly reconcile existing work;
- never trust a stale local file over GitHub.

Never force-push, rewrite history, or delete secrets blindly.

## Scope safety

One batch must have one declared objective and bounded file scope.
Do not combine design work with unrelated backend/database refactors.
Do not opportunistically clean unrelated files.

## Product safety

Never invent or activate:
- wallet/escrow/custody;
- BNPL/credit;
- advertising;
- AI recommendations as a required MVP capability;
- owned logistics;
- final commission policy;
- unsupported delivery guarantees.

Do not turn UI visibility into authorization. Server/application boundary is authoritative.

## UX simplicity

Prefer:
- one primary job per screen;
- one dominant primary action;
- progressive disclosure;
- search/reorder/task queues;
- minimal required fields;
- contextual recovery.

Reject decorative complexity that increases decision count without increasing operational value.

For retailer ordering prefer:
`Open → Search/Reorder → Decide → Add → Review → Confirm`.

## State fidelity

Never collapse materially different states into one generic success/error state.
Preserve canonical states for basket, allocation, order, payment, delivery, dispute and support.

## Frontend/API boundary

Frontend renders canonical state and submits canonical commands.
It must not own business truth for:
- price;
- inventory;
- allocation;
- permissions;
- order-state transitions;
- settlement/reconciliation.

Mocks must follow canonical API shapes and remain removable.

## Verification

Never report success without evidence.
Distinguish unit, domain, database, application-boundary, visual and production verification.
A passing mock or historical CI run does not certify production readiness.

## Stop conditions

Stop and report when:
- a material product decision is missing;
- an irreversible/destructive operation is proposed;
- required credentials are unavailable;
- a backend capability would have to be invented;
- tests must be weakened to pass;
- visual automation cannot be inspected;
- conflicting canonical sources cannot be reconciled.
