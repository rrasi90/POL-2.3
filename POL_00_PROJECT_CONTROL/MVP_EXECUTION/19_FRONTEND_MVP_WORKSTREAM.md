# 19. Frontend — Major MVP Workstream

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 19. Frontend — Major MVP Workstream

## Critical finding
درخت repository فعلی frontend application production ندارد.

بنابراین این بخش از «polish» نیست؛ یک workstream اصلی MVP است.

## 19.1 Retailer — Android + Web/PWA

- [ ] project bootstrap
- [ ] auth screens
- [ ] OTP states
- [ ] session/device states
- [ ] active organization context
- [ ] home/current actions
- [ ] catalog
- [ ] search
- [ ] product detail
- [ ] vendor offers
- [ ] basket
- [ ] allocation preview
- [ ] checkout
- [ ] payment evidence
- [ ] order-group detail
- [ ] child-order detail
- [ ] delivery state
- [ ] POD state
- [ ] reorder
- [ ] disputes
- [ ] RMA
- [ ] support
- [ ] notifications inbox
- [ ] notification preferences
- [ ] profile
- [ ] security/session page
- [ ] deep links
- [ ] offline cache where explicitly specified
- [ ] loading/empty/error states
- [ ] RTL/Persian localization
- [ ] accessibility
- [ ] analytics events

## 19.2 Vendor — Web/Desktop + mobile-responsive

- [ ] auth/context
- [ ] dashboard
- [ ] incoming orders
- [ ] accept
- [ ] reject
- [ ] partial acceptance
- [ ] proposal resolution
- [ ] timeout visibility
- [ ] catalog management
- [ ] pricing
- [ ] inventory
- [ ] daily confirmation
- [ ] fulfillment
- [ ] dispatch
- [ ] delivery handoff
- [ ] payment verification
- [ ] invoices
- [ ] dispute/RMA
- [ ] support
- [ ] referral
- [ ] staff/persona
- [ ] notifications
- [ ] profile/security

## 19.3 Ops

- [ ] exception dashboard
- [ ] order search
- [ ] retailer context
- [ ] vendor context
- [ ] inventory exception
- [ ] timeout queue
- [ ] support
- [ ] RMA/dispute
- [ ] payments
- [ ] notifications
- [ ] audit
- [ ] pilot analytics
- [ ] user/vendor management

## 19.4 Field

- [ ] task list
- [ ] activation
- [ ] assisted first order
- [ ] training
- [ ] follow-up
- [ ] task evidence
- [ ] history

## 19.5 Shared frontend foundation

- [ ] API client
- [ ] auth/session client
- [ ] token refresh handling
- [ ] typed DTOs/contracts
- [ ] retry policy
- [ ] idempotency handling
- [ ] design tokens
- [ ] reusable components
- [ ] state management
- [ ] analytics adapter
- [ ] error boundary
- [ ] feature flags where required
- [ ] localization/i18n
- [ ] Persian RTL
- [ ] mixed-direction number/SKU handling
- [ ] accessibility
- [ ] test harness

---

## Open work
- [ ] project bootstrap
- [ ] auth screens
- [ ] OTP states
- [ ] session/device states
- [ ] active organization context
- [ ] home/current actions
- [ ] catalog
- [ ] search
- [ ] product detail
- [ ] vendor offers
- [ ] basket
- [ ] allocation preview
- [ ] checkout
- [ ] payment evidence
- [ ] order-group detail
- [ ] child-order detail
- [ ] delivery state
- [ ] POD state
- [ ] reorder
- [ ] disputes
- [ ] RMA
- [ ] support
- [ ] notifications inbox
- [ ] notification preferences
- [ ] profile
- [ ] security/session page
- [ ] deep links
- [ ] offline cache where explicitly specified
- [ ] loading/empty/error states
- [ ] RTL/Persian localization
- [ ] accessibility
- [ ] analytics events
- [ ] auth/context
- [ ] dashboard
- [ ] incoming orders
- [ ] accept
- [ ] reject
- [ ] partial acceptance
- [ ] proposal resolution
- [ ] timeout visibility
- [ ] catalog management
- [ ] pricing
- [ ] inventory
- [ ] daily confirmation
- [ ] fulfillment
- [ ] dispatch
- [ ] delivery handoff
- [ ] payment verification
- [ ] invoices
- [ ] dispute/RMA
- [ ] support
- [ ] referral
- [ ] staff/persona
- [ ] notifications
- [ ] profile/security
- [ ] exception dashboard
- [ ] order search
- [ ] retailer context
- [ ] vendor context
- [ ] inventory exception
- [ ] timeout queue
- [ ] support
- [ ] RMA/dispute
- [ ] payments
- [ ] notifications
- [ ] audit
- [ ] pilot analytics
- [ ] user/vendor management
- [ ] task list
- [ ] activation
- [ ] assisted first order
- [ ] training
- [ ] follow-up
- [ ] task evidence
- [ ] history
- [ ] API client
- [ ] auth/session client
- [ ] token refresh handling
- [ ] typed DTOs/contracts
- [ ] retry policy
- [ ] idempotency handling
- [ ] design tokens
- [ ] reusable components
- [ ] state management
- [ ] analytics adapter
- [ ] error boundary
- [ ] feature flags where required
- [ ] localization/i18n
- [ ] Persian RTL
- [ ] mixed-direction number/SKU handling
- [ ] accessibility
- [ ] test harness

## Decisions required
1. اولویت Retailer/Vendor/Ops/Field.
2. single frontend architecture و API adapter.
3. حداقل screen/state set.

## Dependencies
- [ ] `04_DOMAIN_BOUNDARY_HTTP_COVERAGE`
- [ ] `20_DESIGN_PENPOT_CLOSURE`

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
