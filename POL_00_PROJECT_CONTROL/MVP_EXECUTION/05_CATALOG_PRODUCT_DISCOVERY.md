# 5. Catalog / Product Discovery — باید تا MVP واقعی شود

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 5. Catalog / Product Discovery — باید تا MVP واقعی شود

## وضعیت فعلی
Domain/schema و Master SKU research وجود دارد، ولی route/client production برای این جریان در tree فعلی کامل نیست.

### Backend
- [ ] canonical product search boundary
- [ ] product detail query
- [ ] category tree
- [ ] vendor-offer comparison query
- [ ] vendor SKU mapping query
- [ ] barcode exact-match API
- [ ] ambiguous/no-match candidate flow
- [ ] product candidate review flow برای Ops
- [ ] active price filtering
- [ ] effective-date price handling
- [ ] inventory freshness states
- [ ] MOQ/MOV visibility
- [ ] vendor availability state
- [ ] search pagination / query limits
- [ ] search error / empty state contract

### Vendor Catalog Management
- [ ] vendor listing creation
- [ ] vendor listing update
- [ ] product activation/deactivation
- [ ] packaging metadata
- [ ] SKU code
- [ ] barcode association
- [ ] vendor-specific attributes
- [ ] tenant authorization
- [ ] catalog audit trail
- [ ] bulk import path

### Data
- [ ] pilot Master SKU dataset validated
- [ ] initial categories validated
- [ ] initial brands/products validated
- [ ] pilot vendor SKU mapping
- [ ] duplicate detection
- [ ] missing barcode handling
- [ ] price/data freshness policy
- [ ] catalog bootstrap script
- [ ] repeatable staging seed

---

## Open work
- [ ] canonical product search boundary
- [ ] product detail query
- [ ] category tree
- [ ] vendor-offer comparison query
- [ ] vendor SKU mapping query
- [ ] barcode exact-match API
- [ ] ambiguous/no-match candidate flow
- [ ] product candidate review flow برای Ops
- [ ] active price filtering
- [ ] effective-date price handling
- [ ] inventory freshness states
- [ ] MOQ/MOV visibility
- [ ] vendor availability state
- [ ] search pagination / query limits
- [ ] search error / empty state contract
- [ ] vendor listing creation
- [ ] vendor listing update
- [ ] product activation/deactivation
- [ ] packaging metadata
- [ ] SKU code
- [ ] barcode association
- [ ] vendor-specific attributes
- [ ] tenant authorization
- [ ] catalog audit trail
- [ ] bulk import path
- [ ] pilot Master SKU dataset validated
- [ ] initial categories validated
- [ ] initial brands/products validated
- [ ] pilot vendor SKU mapping
- [ ] duplicate detection
- [ ] missing barcode handling
- [ ] price/data freshness policy
- [ ] catalog bootstrap script
- [ ] repeatable staging seed

## Decisions required
1. حداقل catalog/search surface pilot.
2. سیاست unknown/ambiguous barcode و candidate.
3. حداقل کیفیت Master SKU و vendor mapping.

## Dependencies
- [ ] `06_VENDOR_PRICING_INVENTORY`
- [ ] `16_VENDOR_ONBOARDING`

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
