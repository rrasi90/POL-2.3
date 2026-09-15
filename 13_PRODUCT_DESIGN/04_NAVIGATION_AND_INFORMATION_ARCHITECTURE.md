# POL Navigation & Information Architecture

## Global principle
Navigation follows the user's current job and active organization/persona context. It does not expose every capability to every user.

## POL Market navigation
Primary mobile navigation:
1. خانه
2. خرید / جستجو
3. سفارش‌ها
4. سبد
5. حساب

Secondary entry points: دسته‌بندی‌ها، تکرار سفارش، لیست‌های ذخیره‌شده، پشتیبانی، اعلان‌ها.

Home should prioritize current orders, reorder opportunities and high-confidence operational information before promotional content.

## POL Vendor navigation
Desktop-first with responsive mobile support:
- داشبورد
- سفارش‌ها
- موجودی
- کاتالوگ و قیمت
- مشتریان
- تأیید موجودی روزانه
- معرفی بنکدار
- تسویه/اسناد
- کارکنان و دسترسی‌ها
- پروفایل

Navigation is persona-adaptive for owner, sales, warehouse, operations and finance, but permission remains server-side.

## POL Ops navigation
- Overview / queues
- Orders
- Vendors
- Retailers
- Fulfillment exceptions
- Support
- Returns / RMA
- Reconciliation
- Risk / reliability
- Notifications
- Pilot analytics

## Field Activator navigation
Task-first:
- امروز
- مشتریان/سرنخ‌ها
- فعال‌سازی
- سفارش کمکی
- پیگیری‌ها
- مشکلات
- حساب

## Corporate site IA
Home → For Retailers → For Vendors → How POL Works → Pilot/Ahvaz → About → Contact.

## Navigation behavior
- Keep active tenant visible when relevant.
- Profile switcher is explicit when the user has multiple memberships.
- Do not expose an organization switcher that changes tenant without re-resolving authenticated membership context.
- Deep links from notifications should land on the underlying task/state, not on a generic dashboard.
