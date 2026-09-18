# 32. ترتیب اجرای پیشنهادی — Critical Path

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 32. ترتیب اجرای پیشنهادی — Critical Path

## Batch M-01
### Close Batch 6C-7
- [ ] fix
- [ ] test
- [ ] commit
- [ ] push
- [ ] CI
- [ ] certify

## Batch M-02
### Architecture / Documentation Synchronization
- [ ] D-019/D-020 sync
- [ ] capability matrix sync
- [ ] test manifest sync
- [ ] queue runtime decision
- [ ] route matrix refresh

## Batch M-03
### Production Auth / Security
- [ ] real OTP provider
- [ ] rate limit
- [ ] session/revocation
- [ ] refresh policy
- [ ] security middleware

## Batch M-04
### Catalog + Vendor Catalog + Pricing
- [ ] search
- [ ] product detail
- [ ] vendor offers
- [ ] catalog management
- [ ] price management
- [ ] category management
- [ ] barcode/candidate flows

## Batch M-05
### Inventory + Daily Confirmation
- [ ] inventory APIs
- [ ] scan/publish
- [ ] freshness
- [ ] daily confirmation
- [ ] reminders
- [ ] vendor inventory UI

## Batch M-06
### Commerce HTTP Completion
- [ ] vendor order query
- [ ] retailer order query
- [ ] order timeline
- [ ] all checkout failure states
- [ ] idempotency over HTTP

## Batch M-07
### Fulfillment / Delivery
- [ ] prepare
- [ ] dispatch
- [ ] deliver
- [ ] POD
- [ ] delivery exceptions
- [ ] HTTP + UI

## Batch M-08
### Payment / Invoice / Settlement
- [ ] payment evidence
- [ ] verification
- [ ] invoice
- [ ] reconciliation
- [ ] settlement
- [ ] dispute adjustment

## Batch M-09
### Dispute / RMA / Support
- [ ] dispute routes
- [ ] RMA routes
- [ ] refund separation of duties
- [ ] support routes
- [ ] notifications

## Batch M-10
### Notification + Provider Certification
- [ ] inbox
- [ ] preferences
- [ ] SMS
- [ ] push
- [ ] retries
- [ ] receipts
- [ ] DLQ/quarantine

## Batch M-11
### Ops / Admin / Referral / Field
- [ ] admin exception dashboard
- [ ] vendor onboarding
- [ ] broadcast
- [ ] audit
- [ ] referral
- [ ] field tasks

## Batch M-12
### Frontend Foundation + Retailer
- [ ] app bootstrap
- [ ] auth
- [ ] catalog
- [ ] basket
- [ ] allocation
- [ ] checkout
- [ ] orders
- [ ] delivery
- [ ] RMA/support/profile

## Batch M-13
### Vendor + Ops + Field UI
- [ ] vendor panel
- [ ] inventory
- [ ] orders
- [ ] fulfillment
- [ ] payments
- [ ] ops
- [ ] field

## Batch M-14
### Infrastructure
- [ ] staging
- [ ] deployment
- [ ] secrets
- [ ] DB
- [Redis if selected]
- [ ] workers
- [ ] TLS
- [ ] backups
- [ ] monitoring

## Batch M-15
### Real Pilot Data / Onboarding
- [ ] vendor onboarding
- [ ] catalog seed
- [ ] price
- [ ] inventory
- [ ] retailer cohort
- [ ] LOIs
- [ ] training
- [ ] assisted orders

## Batch M-16
### E2E Pilot Certification
- [ ] complete scenario matrix
- [ ] security matrix
- [ ] reliability tests
- [ ] provider failure tests
- [ ] restore test
- [ ] observability test
- [ ] KPI telemetry test
- [ ] final CI
- [ ] release snapshot

## Batch M-17
### MVP Launch Gate
- [ ] no P0 open
- [ ] no critical P1 open
- [ ] all MVP-critical routes green
- [ ] all real clients connected
- [ ] all critical provider flows certified
- [ ] backup verified
- [ ] observability verified
- [ ] pilot operations staffed
- [ ] rollback procedure tested
- [ ] final release SHA recorded
- [ ] MVP declared `PILOT-READY`

---

## Open work
- [ ] fix
- [ ] test
- [ ] commit
- [ ] push
- [ ] CI
- [ ] certify
- [ ] D-019/D-020 sync
- [ ] capability matrix sync
- [ ] test manifest sync
- [ ] queue runtime decision
- [ ] route matrix refresh
- [ ] real OTP provider
- [ ] rate limit
- [ ] session/revocation
- [ ] refresh policy
- [ ] security middleware
- [ ] search
- [ ] product detail
- [ ] vendor offers
- [ ] catalog management
- [ ] price management
- [ ] category management
- [ ] barcode/candidate flows
- [ ] inventory APIs
- [ ] scan/publish
- [ ] freshness
- [ ] daily confirmation
- [ ] reminders
- [ ] vendor inventory UI
- [ ] vendor order query
- [ ] retailer order query
- [ ] order timeline
- [ ] all checkout failure states
- [ ] idempotency over HTTP
- [ ] prepare
- [ ] dispatch
- [ ] deliver
- [ ] POD
- [ ] delivery exceptions
- [ ] HTTP + UI
- [ ] payment evidence
- [ ] verification
- [ ] invoice
- [ ] reconciliation
- [ ] settlement
- [ ] dispute adjustment
- [ ] dispute routes
- [ ] RMA routes
- [ ] refund separation of duties
- [ ] support routes
- [ ] notifications
- [ ] inbox
- [ ] preferences
- [ ] SMS
- [ ] push
- [ ] retries
- [ ] receipts
- [ ] DLQ/quarantine
- [ ] admin exception dashboard
- [ ] vendor onboarding
- [ ] broadcast
- [ ] audit
- [ ] referral
- [ ] field tasks
- [ ] app bootstrap
- [ ] auth
- [ ] catalog
- [ ] basket
- [ ] allocation
- [ ] checkout
- [ ] orders
- [ ] delivery
- [ ] RMA/support/profile
- [ ] vendor panel
- [ ] inventory
- [ ] orders
- [ ] fulfillment
- [ ] payments
- [ ] ops
- [ ] field
- [ ] staging
- [ ] deployment
- [ ] secrets
- [ ] DB
- [ ] workers
- [ ] TLS
- [ ] backups
- [ ] monitoring
- [ ] vendor onboarding
- [ ] catalog seed
- [ ] price
- [ ] inventory
- [ ] retailer cohort
- [ ] LOIs
- [ ] training
- [ ] assisted orders
- [ ] complete scenario matrix
- [ ] security matrix
- [ ] reliability tests
- [ ] provider failure tests
- [ ] restore test
- [ ] observability test
- [ ] KPI telemetry test
- [ ] final CI
- [ ] release snapshot
- [ ] no P0 open
- [ ] no critical P1 open
- [ ] all MVP-critical routes green
- [ ] all real clients connected
- [ ] all critical provider flows certified
- [ ] backup verified
- [ ] observability verified
- [ ] pilot operations staffed
- [ ] rollback procedure tested
- [ ] final release SHA recorded
- [ ] MVP declared `PILOT-READY`

## Decisions required
1. batch order/dependencies.
2. exit criteria.
3. stop rule on failure/contradiction.

## Dependencies
- [ ] `02_BATCH_6C_7_CERTIFICATION`
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
