# Antigravity — POL Repository Audit & Repair Prompt

## PURPOSE

Do **not** begin Figma/Penpot design yet.

Your first task is to synchronize the local workspace with GitHub, audit the entire POL repository against the canonical source of truth, repair every concrete defect you can verify, run the full verification suite, and only then report that the repository is ready for the Design Completion phase.

## 0. LOCAL WORKSPACE IS NOT TRUSTED

The local workspace may contain stale files from earlier sessions.

Before reading or editing project files:

1. Fetch from GitHub.
2. Checkout branch `research-hardening-2026-09-14`.
3. Compare local HEAD with `origin/research-hardening-2026-09-14`.
4. If local files differ because they are stale/uncommitted, preserve secrets/credentials only, then reset the project working tree to the remote branch.
5. Remove stale generated/untracked project artifacts that are not required by the repository.
6. Verify:
   - `git rev-parse HEAD` == `git rev-parse origin/research-hardening-2026-09-14`
   - `git status --short` contains no unexpected changes.
7. Do not use an older local copy as a source of truth.

Never delete `.env`, credentials, SSH keys, or other secrets merely because they are untracked. Project source files and generated artifacts are different from credentials.

## 1. READ THE GOVERNING FILES FIRST

Read these before changing anything:

- `POL_00_PROJECT_CONTROL/CURRENT_SOURCE_OF_TRUTH.md`
- `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`
- `POL_00_PROJECT_CONTROL/CANONICAL_CONTRACT_MATRIX.md`
- `POL_00_PROJECT_CONTROL/CANONICAL_CONTRACT_MATRIX_CORRECTIONS_2026-09-16.md`
- `POL_00_PROJECT_CONTROL/DATABASE_SCHEMA_MANIFEST_2026-09-16.md`
- `POL_00_PROJECT_CONTROL/TECHNICAL_ENVIRONMENT.md`
- `POL_00_PROJECT_CONTROL/API_APPLICATION_BOUNDARY.md`
- `POL_00_PROJECT_CONTROL/GLOBAL_ENGINEERING_AUDIT_2026-09-14.md`
- `POL_00_PROJECT_CONTROL/USER_PROFILE_AND_PERSONA_MODEL.md`
- all active files under `13_PRODUCT_DESIGN/`

Then inspect:

- `06_PRODUCT/`
- `07_ALGORITHMS/`
- `08_DATA/`
- `09_OPERATIONS/`
- `10_GO_TO_MARKET/`
- `11_PILOT/`
- `12_ROADMAP/`
- `migrations/`
- `scripts/`
- `.github/workflows/`

## 2. AUDIT CATEGORIES

Audit the repository as one system, not as independent documents.

### A. Governance

Find:
- stale canonical paths;
- duplicate decision registers;
- documents marked current that are actually historical;
- superseded Single-Vendor statements presented as current;
- incorrect D-001–D-017 references;
- contradictory role names;
- contradictory basket/order/payment terminology.

### B. Database

Verify the complete migration chain from 001 through the latest numbered migration.

Check:
- table count;
- foreign keys;
- unique indexes;
- exclusion constraints;
- temporal overlap rules;
- tenant boundaries;
- state constraints;
- triggers;
- idempotency constraints;
- RMA/refund invariants;
- profile/persona cardinality.

Never manually edit an already-applied migration. Add a new numbered migration for schema changes.

### C. Application Boundary

Verify that client-facing code uses the canonical application boundary and does not bypass it through legacy domain services.

Explicitly search for:
- imports from legacy `domain_services.py` into client-facing gateways;
- direct SQL writes from client-facing route modules;
- duplicated checkout implementations;
- missing tenant authorization;
- missing actor ownership checks;
- replay/idempotency holes.

### D. Security / IAM

Verify:
- `organization_memberships.role` is the authorization SSoT;
- active session tenant belongs to session user;
- suspended/revoked memberships cannot act;
- user profile fields cannot mutate RBAC;
- support/feedback records cannot be written into another tenant;
- vendor/referral actions require vendor membership;
- retailer actions require retailer membership;
- no production code uses fixed OTPs or placeholder tokens.

Test every security-sensitive invariant against PostgreSQL 18 where practical.

### E. Commerce

Trace:

`User → Membership → Basket → AllocationPlan → Revalidation → Checkout → OrderGroup → Order → Inventory Reservation → Fulfillment → Delivery/POD → Payment/Reconciliation → RMA/Dispute`

Check every boundary for:
- ownership;
- stale state;
- replay;
- price changes;
- inventory changes;
- vendor status;
- MOQ/pack constraints;
- partial allocation;
- cancellation/rejection;
- refund/adjustment.

### F. Documentation / Design Inputs

Find every domain state that exists in code/DDL but is absent from design specification.

Pay particular attention to:
- Auth/OTP/session;
- notifications;
- vendor comparison;
- allocation partial/unfulfilled;
- checkout revalidation;
- payment evidence;
- delivery/POD;
- RMA/disputes;
- support;
- risk/reliability;
- weak network/offline states;
- profile/persona;
- analytics/telemetry;
- localization and Persian RTL/LTR stress cases.

## 3. REPAIR RULES

When a concrete defect is found:

1. Fix it rather than merely documenting it.
2. Prefer the smallest safe change.
3. For database invariants, use a forward migration.
4. Add a regression test for every non-trivial repair.
5. Update the canonical documentation affected by the repair.
6. Never silently invent a business decision.
7. If a business choice is genuinely unknown, record it as `OPEN` in the appropriate decision/specification document.

Do not implement future features merely because their database foundation exists.

## 4. GENERATED ARTIFACT HYGIENE

Do not commit:

- scratch prompts;
- temporary research scripts;
- local test result JSON;
- temporary exports;
- local databases;
- credentials;
- generated build output.

Keep durable research findings, final reports and canonical specifications.

## 5. VERIFICATION GATE

After repairs:

1. Apply the full migration chain to a fresh PostgreSQL 18 database.
2. Run environment verification.
3. Run the complete verification suite.
4. Run repository consistency checks.
5. Confirm the current branch is clean except for intentional commits.
6. Inspect CI.
7. If CI fails, fix the failure before reporting completion.

A successful historical CI run is not sufficient. The current HEAD must pass.

## 6. OUTPUT

Create/update:

`POL_00_PROJECT_CONTROL/REPOSITORY_COMPLETION_AUDIT_2026-09-16.md`

It must contain:

- audit scope;
- repository HEAD audited;
- files/directories reviewed;
- findings by severity;
- exact repairs made;
- tests added/updated;
- CI result;
- remaining production-applicationization gates;
- remaining OPEN product/design decisions;
- explicit readiness decision for the next Design Completion phase.

Do not claim "production ready" merely because the domain verification suite passes.

## 7. STOP CONDITION

Do not start high-fidelity Figma/Penpot work until:

- repository audit is complete;
- concrete defects found in the audit are repaired or explicitly blocked;
- current CI passes;
- canonical terminology is reconciled;
- database and application-boundary integrity gates pass;
- the Design Completion Plan can consume the repository without known specification gaps.

Only after this gate may you proceed to:

`Design Foundation → Components → Shared UX → States → Retailer → Vendor → Operations → Field → Corporate → Prototype → Design QA`.
