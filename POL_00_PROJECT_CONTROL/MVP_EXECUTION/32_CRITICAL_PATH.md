# 32. ترتیب اجرای پیشنهادی — Critical Path

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
این بخش اکنون توسط یک برنامه‌ی ۵۰ مرحله‌ای کنترل می‌شود. هر مرحله یک work package مستقل است و فقط پس از ثبت evidence، نتیجه و next action بسته می‌شود.

## Stage controller
- Canonical staged execution plan: `POL_00_PROJECT_CONTROL/MVP_EXECUTION/50_STAGE_MASTER_EXECUTION_PLAN_2026-09-18.md`
- Current work item: `EXEC50-001`
- Rule: each user `ادامه` executes the next not-completed stage.
- Every stage updates: master plan, relevant Section Work Log, Active Work Ledger, and affected source/test/design/config documentation.
- No stage may claim a green test that was not actually run.
- Work outside this environment is marked `EXTERNAL_PENDING`, never silently treated as done.

## Macro batches
1. M-01 Certification / truth synchronization
2. M-02 Security / authentication / HTTP hardening
3. M-03 Catalog / pricing / inventory
4. M-04 Commerce / order / fulfillment
5. M-05 Finance / dispute / support / notifications
6. M-06 Ops / referral / field / analytics
7. M-07 Frontend implementation and handoff
8. M-08 Infrastructure / recovery / performance
9. M-09 Pilot preparation and evidence
10. M-10 Final release and external handoff

## Open work
- [ ] Execute 50-stage plan sequentially.
- [ ] Keep repository documentation synchronized with real code and evidence.
- [ ] Isolate external blockers such as live Penpot editing, local-only infrastructure access, real provider credentials and large final regression runs.

## Decisions required
1. Existing decisions remain authoritative.
2. New business/architecture rules require an explicit Decision ID.
3. External blockers must be recorded with exact handoff instructions.

## Dependencies
- [ ] `02_BATCH_6C_7_CERTIFICATION`
- [ ] `03_GOVERNANCE_REVIEW`
- [ ] `19_FRONTEND_MVP_WORKSTREAM`
- [ ] `20_DESIGN_PENPOT_CLOSURE`
- [ ] `21_INFRASTRUCTURE_DEPLOYMENT`

## Acceptance Gate
- [ ] All 50 stages are CLOSED/VERIFIED or explicitly EXTERNAL_PENDING with exact handoff instructions.
- [ ] Final test/CI bundle is green where executable evidence exists.
- [ ] Final Penpot and live-environment blockers are isolated for the external agent.
- [ ] Final release SHA and evidence pack are recorded.

## Execution rules
- Business rule جدید بدون Decision ID ممنوع.
- SSoTهای repository از این فایل مقدم‌اند.
- GREEN* domain evidence با production-ready اشتباه نشود.
- failure را با حذف/کاهش تست پنهان نکن.
- Test execution can be batched; stage execution does not imply one-test-at-a-time.
- Documentation updates are part of each stage.

## Status
IN_PROGRESS
