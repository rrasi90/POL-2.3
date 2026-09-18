# 31. چیزهایی که عمداً تا MVP نباید وارد شوند

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 31. چیزهایی که عمداً تا MVP نباید وارد شوند

برای جلوگیری از scope creep:

- [ ] BNPL / credit underwriting
- [ ] wallet
- [ ] escrow / custody
- [ ] POL-owned warehouse
- [ ] POL-owned fleet
- [ ] advanced route optimization
- [ ] sponsored products / ads
- [ ] advanced recommendation AI
- [ ] complex loyalty
- [ ] gamification
- [ ] social commerce
- [ ] multi-touch referral rewards
- [ ] manufacturer commerce surface
- [ ] quantity splitting یک line بین چند vendor
- [ ] second business-logic layer in frontend
- [ ] second backend runtime
- [ ] speculative microservices

---

## Open work
- [ ] BNPL / credit underwriting
- [ ] wallet
- [ ] escrow / custody
- [ ] POL-owned warehouse
- [ ] POL-owned fleet
- [ ] advanced route optimization
- [ ] sponsored products / ads
- [ ] advanced recommendation AI
- [ ] complex loyalty
- [ ] gamification
- [ ] social commerce
- [ ] multi-touch referral rewards
- [ ] manufacturer commerce surface
- [ ] quantity splitting یک line بین چند vendor
- [ ] second business-logic layer in frontend
- [ ] second backend runtime
- [ ] speculative microservices

## Decisions required
1. protect out-of-scope items.
2. scope exception process.
3. منع scope creep.

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
