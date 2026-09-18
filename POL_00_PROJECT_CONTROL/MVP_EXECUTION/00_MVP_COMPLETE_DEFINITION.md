# 0. تعریف دقیق «MVP کامل»

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 0. تعریف دقیق «MVP کامل»

در این برنامه، «MVP کامل» صرفاً به معنی سبز شدن تست‌های Domain نیست.

MVP کامل POL باید حداقل به این نقطه برسد:

> یک Retailer واقعی بتواند از طریق client واقعی وارد شود، کاتالوگ و آفر Vendorها را ببیند، سبد بسازد، allocation را بررسی کند، checkout کند، سفارش‌های Vendorها را پیگیری کند، تحویل را ببیند، پرداخت/تسویه مستقیم را ثبت و پیگیری کند، مغایرت یا RMA ثبت کند و از Support استفاده کند؛  
> یک Vendor واقعی بتواند catalog/price/inventory خود را مدیریت کند، سفارش را قبول/رد/partial-accept کند، fulfillment/delivery handoff را انجام دهد، شواهد پرداخت را مدیریت کند و مسائل RMA/Support را پاسخ دهد؛  
> و تیم Ops بتواند onboarding، exception، support، dispute، reconciliation، notification و audit را مدیریت کند؛  
> همه این مسیرها از HTTP واقعی، Auth واقعی، PostgreSQL واقعی، Outbox/Worker واقعی و UI واقعی عبور کنند و با تست E2E قابل بازتولید باشند.

این با «Production at Scale» یکی نیست. بعد از MVP Pilot، کارهای scale، advanced AI، BNPL، loyalty، advertising، owned logistics و سایر قابلیت‌های خارج از MVP باقی می‌مانند.

---

## Open work
- [ ] کار باز صریحی در Master ثبت نشده است؛ certification را verify کن.

## Decisions required
1. MVP boundary را به‌صورت رسمی تأیید کنیم: Pilot-Ready با Production-at-Scale یک milestone واحد نیست.
2. حداقل قابلیت‌های pilot-blocking را freeze کنیم.
3. MVP-CERTIFIED / PILOT-READY را به معیار release تبدیل کنیم.

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
