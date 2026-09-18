# 33. Definition of Done — MVP Pilot

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 33. Definition of Done — MVP Pilot

MVP را فقط وقتی `DONE` اعلام کنیم که همه این گزاره‌ها درست باشند:

### Product
- [ ] Retailer can complete full order journey without developer intervention.
- [ ] Vendor can manage the commercial and operational order journey.
- [ ] Ops can resolve critical exceptions.
- [ ] Field can onboard/assist users.
- [ ] RMA/support/payment/notification flows are usable.

### Backend
- [ ] All client-facing commands go through FastAPI → ApplicationContext → POLApplicationBoundary.
- [ ] No transport handler writes domain tables directly.
- [ ] No new client-facing path imports legacy `domain_services`.
- [ ] PostgreSQL 18 is the canonical DB.
- [ ] Outbox/worker flow is deterministic and observable.

### Security
- [ ] Auth is production-backed.
- [ ] Tenant isolation is proven at HTTP layer.
- [ ] RBAC is canonical.
- [ ] Sessions can be revoked.
- [ ] Rate limits and OTP protections are active.
- [ ] Secrets never live in Git.

### Commerce
- [ ] Catalog is usable.
- [ ] Prices are current/effective.
- [ ] Inventory is current enough for pilot policy.
- [ ] Basket/allocation/checkout are production-usable.
- [ ] Order transitions work.
- [ ] Fulfillment/delivery/POD works.
- [ ] Payment/reconciliation works without POL custody.

### Exceptions
- [ ] Vendor rejection works.
- [ ] Partial acceptance works.
- [ ] Acceptance timeout works.
- [ ] Dispute works.
- [ ] RMA/refund works.
- [ ] Support works.
- [ ] Provider failure does not corrupt business transactions.

### Client
- [ ] Retailer UI exists.
- [ ] Vendor UI exists.
- [ ] Ops UI exists.
- [ ] Field UI exists where required.
- [ ] RTL/Persian/accessibility pass.

### Infrastructure
- [ ] Staging and pilot deployments exist.
- [ ] Logs/metrics/alerts exist.
- [ ] Backup and restore verified.
- [ ] Migration procedure verified.
- [ ] Rollback verified.

### Evidence
- [ ] Full regression green.
- [ ] HTTP E2E green.
- [ ] Critical negative/security matrix green.
- [ ] Provider certification green.
- [ ] Pilot data loaded.
- [ ] pilot cohort ready.
- [ ] final SHA recorded.

---

## Open work
- [ ] Retailer can complete full order journey without developer intervention.
- [ ] Vendor can manage the commercial and operational order journey.
- [ ] Ops can resolve critical exceptions.
- [ ] Field can onboard/assist users.
- [ ] RMA/support/payment/notification flows are usable.
- [ ] All client-facing commands go through FastAPI → ApplicationContext → POLApplicationBoundary.
- [ ] No transport handler writes domain tables directly.
- [ ] No new client-facing path imports legacy `domain_services`.
- [ ] PostgreSQL 18 is the canonical DB.
- [ ] Outbox/worker flow is deterministic and observable.
- [ ] Auth is production-backed.
- [ ] Tenant isolation is proven at HTTP layer.
- [ ] RBAC is canonical.
- [ ] Sessions can be revoked.
- [ ] Rate limits and OTP protections are active.
- [ ] Secrets never live in Git.
- [ ] Catalog is usable.
- [ ] Prices are current/effective.
- [ ] Inventory is current enough for pilot policy.
- [ ] Basket/allocation/checkout are production-usable.
- [ ] Order transitions work.
- [ ] Fulfillment/delivery/POD works.
- [ ] Payment/reconciliation works without POL custody.
- [ ] Vendor rejection works.
- [ ] Partial acceptance works.
- [ ] Acceptance timeout works.
- [ ] Dispute works.
- [ ] RMA/refund works.
- [ ] Support works.
- [ ] Provider failure does not corrupt business transactions.
- [ ] Retailer UI exists.
- [ ] Vendor UI exists.
- [ ] Ops UI exists.
- [ ] Field UI exists where required.
- [ ] RTL/Persian/accessibility pass.
- [ ] Staging and pilot deployments exist.
- [ ] Logs/metrics/alerts exist.
- [ ] Backup and restore verified.
- [ ] Migration procedure verified.
- [ ] Rollback verified.
- [ ] Full regression green.
- [ ] HTTP E2E green.
- [ ] Critical negative/security matrix green.
- [ ] Provider certification green.
- [ ] Pilot data loaded.
- [ ] pilot cohort ready.
- [ ] final SHA recorded.

## Decisions required
1. DoD approval.
2. evidence per gate.
3. owners/sign-off.

## Dependencies
- [ ] `27_REAL_WORLD_PILOT_TEST_PROTOCOL`
- [ ] `32_CRITICAL_PATH`

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
