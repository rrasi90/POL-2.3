# 35. The shortest correct path

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 35. The shortest correct path

اگر هدف فقط این است که POL هرچه سریع‌تر به یک MVP واقعی برای پایلوت برسد، ترتیب بهینه این است:

`6C-7 certification`
→ `Architecture/document sync`
→ `Auth + Security`
→ `Catalog + Pricing + Inventory`
→ `Remaining HTTP applicationization`
→ `Fulfillment + Delivery + Payment`
→ `Dispute/RMA/Support/Notifications`
→ `Frontend Retailer`
→ `Frontend Vendor/Ops/Field`
→ `Staging/Deployment/Observability`
→ `Pilot Data + Onboarding`
→ `Full HTTP E2E`
→ `Pilot Certification`

هر کاری خارج از این مسیر که BNPL، AI recommendation، advertising، loyalty، owned logistics، microservices یا پیچیدگی‌های جدید اضافه کند، تا بسته شدن این مسیر باید خارج از scope بماند.

---

## Open work
- [ ] کار باز صریحی در Master ثبت نشده است؛ certification را verify کن.

## Decisions required
1. کوتاه‌ترین مسیر.
2. parallel vs sequential.
3. feature freeze تا بعد از pilot.

## Dependencies
- [ ] Gateهای قبلی سبز باشند.

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
