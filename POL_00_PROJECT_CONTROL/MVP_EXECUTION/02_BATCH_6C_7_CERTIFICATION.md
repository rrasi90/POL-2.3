# 2. نکته بحرانی درباره Batch 6C-7

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 2. نکته بحرانی درباره Batch 6C-7

گزارش OpenCode اعلام کرده است:

- timeout suite: `6/6`
- Checkout Gateway: `3/3`
- Checkout HTTP: `6/6`
- E2E: `17/17`
- regression groups: سبز
- full regression: `209/209`
- repository consistency: `8/8`
- environment: `28 migrations / 93 tables`
- diff-check: clean

اما این نتیجه هنوز در SHA فعلی GitHub (`f97b1a8...`) ثبت نشده است.

GitHub برای همین SHA یک workflow شکست‌خورده دارد:

`POL Independent Verification & Certification CI`  
Run `#326` / `35368804736` → `failure`

بنابراین:

**وضعیت Batch 6C-7 در این فایل: `LOCALALLY VERIFIED / NOT YET REPOSITORY-CERTIFIED`**

قبل از هر Batch بعدی:

- [ ] import fix را commit کنیم.
- [ ] `created_at` mismatch fix را commit کنیم.
- [ ] `pg_connection` fixture fix را commit کنیم.
- [ ] replacement `MIN(uuid)` را بازبینی کنیم و مطمئن شویم `LIMIT 1` با `ORDER BY` deterministic است.
- [ ] `git diff --check`
- [ ] `git status`
- [ ] commit
- [ ] push
- [ ] CI روی SHA جدید
- [ ] فقط در صورت CI green، 6C-7 = CLOSED

---

## Open work
- [ ] import fix را commit کنیم.
- [ ] `created_at` mismatch fix را commit کنیم.
- [ ] `pg_connection` fixture fix را commit کنیم.
- [ ] replacement `MIN(uuid)` را بازبینی کنیم و مطمئن شویم `LIMIT 1` با `ORDER BY` deterministic است.
- [ ] `git diff --check`
- [ ] `git status`
- [ ] commit
- [ ] push
- [ ] CI روی SHA جدید
- [ ] فقط در صورت CI green، 6C-7 = CLOSED

## Decisions required
1. SHA نهایی Batch 6C-7 مشخص شود.
2. selection assignee در timeout worker deterministic و دارای ORDER BY باشد.
3. 6C-7 فقط بعد از CI روی SHA جدید CLOSED شود.

## Dependencies
- [ ] `01_CURRENT_STATE_SNAPSHOT`
- [ ] `03_GOVERNANCE_REVIEW`

## Acceptance Gate
- [ ] تمام کارهای باز بسته یا با دلیل رسمی NOT APPLICABLE شده‌اند.
- [ ] contradiction باز در این حوزه وجود ندارد.
- [ ] تست/verification مناسب اجرا و evidence ثبت شده است.
- [ ] اگر client-facing است: HTTP + Auth + tenant isolation + failure states تست شده‌اند.
- [ ] commit SHA نهایی قابل اشاره است.

## Execution rules
- business rule جدید بدون Decision ID ممنوع.
- SSoTهای repository از این فایل مقدم‌اند.
- GREEN* domain evidence با production-ready اشتباه نشود.
- failure را با حذف/کاهش تست پنهان نکن.

## Status
NOT STARTED / IN PROGRESS / BLOCKED / VERIFIED / CLOSED
