-- 076: Templates for the reservation/product-candidate lifecycle events.
--
-- These six event names were emitted to the outbox without a notification
-- template and without passthrough status, so the canonical integration
-- worker quarantined every row as FAILED (orphaned outbox contract). This
-- migration versions the canonical INBOX templates so the worker can render
-- and route them.

INSERT INTO notification_templates (
    event_name, channel, version, title_template, body_template,
    priority, allow_opt_out, effective_from
)
VALUES
(
    'INVENTORY_RESERVATION_CREATED', 'INBOX', '1.0',
    'رزرو موجودی ثبت شد',
    'برای سفارش شما رزرو موجودی به مقدار {{quantity}} ثبت شد.',
    'NORMAL', FALSE, now()
),
(
    'INVENTORY_RESERVATION_CONSUMED', 'INBOX', '1.0',
    'رزرو موجودی مصرف شد',
    'رزرو موجودی به مقدار {{quantity}} برای سفارش شما مصرف شد.',
    'NORMAL', FALSE, now()
),
(
    'INVENTORY_RESERVATION_RELEASED', 'INBOX', '1.0',
    'رزرو موجودی آزاد شد',
    'رزرو موجودی به مقدار {{quantity}} آزاد شد ({{reason}}).',
    'NORMAL', FALSE, now()
),
(
    'INVENTORY_RESERVATION_EXPIRED', 'INBOX', '1.0',
    'رزرو موجودی منقضی شد',
    'رزرو موجودی به مقدار {{quantity}} منقضی شد.',
    'NORMAL', FALSE, now()
),
(
    'PRODUCT_CANDIDATE_CREATED', 'INBOX', '1.0',
    'کاندیدای کاتالوگ جدید',
    'بارکد {{barcode}} برای بررسی و ایجاد کالای کانونیکال ثبت شد.',
    'NORMAL', FALSE, now()
),
(
    'PRODUCT_CANDIDATE_REVIEWED', 'INBOX', '1.0',
    'بررسی کاندیدای کاتالوگ',
    'نتیجه بررسی کاندیدای کاتالوگ ثبت شد.',
    'NORMAL', FALSE, now()
);
