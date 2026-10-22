# POL — Bug Reproduction Log

Single register for every defect found during QA/verification. One row per defect, one ID per defect, no
duplicates: a bug that reappears gets a new row that links back to the original with `reopened-from`.

## Rules

- `BUG-ID` is permanent. Never renumber, never reuse.
- A row may only be closed with evidence a second person can replay: exact command, SHA, environment, result.
- Never paste secrets, OTPs, tokens, or customer data into this file. Reference the environment and redact.
- "Works for me" is not evidence. Screenshots alone are not evidence; they may accompany a command/log.
- A defect that is intentionally deferred is `DEFERRED` with an owner, a reason, and the TODO-ID that will close it.

## Status vocabulary

| Status | Meaning |
| --- | --- |
| `NEW` | Reported, not triaged |
| `TRIAGED` | Severity, owner, and environment confirmed |
| `IN_PROGRESS` | Fix being written; repro still valid on current SHA |
| `FIXED_PENDING_VERIFY` | Fix pushed; repro must be re-run on the fix SHA |
| `VERIFIED_CLOSED` | Repro fails on fix SHA and regression test exists |
| `DEFERRED` | Accepted risk with owner + closing TODO-ID |
| `DUPLICATE` | Points to the canonical `BUG-ID` |
| `WONT_FIX` | Product decision recorded in `DECISION_REGISTER.md` |

## Severity

`S1` data loss / security / money · `S2` blocked user journey · `S3` degraded but workable · `S4` cosmetic.

## Template

Copy this block per defect:

```markdown
### BUG-000 — <one-line symptom>

| Field | Value |
| --- | --- |
| Status | NEW |
| Severity | S2 |
| Role / persona | Retailer owner |
| Build / variant | retailer (ir.pol.market) · versionCode 100 |
| Branch / SHA | `agent/...` @ `<sha>` |
| Environment | local test · PostgreSQL 18.4 · Android 15 / API 35 emulator |
| Seed / data | `<fixture or seed command>` |
| Preconditions | <state the journey must be in> |
| Steps to reproduce | 1. … 2. … 3. … |
| Expected | <contract / acceptance criterion> |
| Actual | <observed, with request id / correlation id if available> |
| Evidence | command, log path, artifact path, screenshot path |
| Suspected cause | <file:line if known> |
| Linked TODO / BUG | `TODO-0xx` / `BUG-0yy` |
| Owner | <name or `unassigned`> |
| Fix SHA | |
| Regression test | `scripts/test_*.py::test_*` |
| Verified by / at | |
```

## Register

| BUG-ID | Severity | Status | Symptom | Role | SHA found | Linked TODO | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BUG-001 | S4 | `DEFERRED` | `test_photo_proof_requires_delivery_bound_media` used a fixed `storage_key='x'`, so the run failed on any second execution against the same test database — test isolation defect, not a product defect | QA harness | `afa46fc` | `TODO-016`, `TODO-090` | unassigned |
