-- 044: Partial-acceptance notification templates
-- Forward-only remediation for canonical integration worker rendering.

INSERT INTO notification_templates (
    event_name, channel, version, title_template, body_template, priority, allow_opt_out
)
VALUES
(
    'ORDER_PARTIAL_ACCEPTANCE_PROPOSED',
    'INBOX',
    '1.0',
    'پیشنهاد کسری سفارش ثبت شد',
    'برای سفارش {{order_number}} پیشنهاد پذیرش بخشی با شناسه {{proposal_id}} ثبت شده است.',
    'HIGH',
    FALSE
),
(
    'ORDER_PARTIALLY_ACCEPTED',
    'INBOX',
    '1.0',
    'سفارش با کسری تأیید شد',
    'سفارش {{order_number}} با مقادیر اصلاح‌شده تأیید شد.',
    'HIGH',
    FALSE
),
(
    'ORDER_PARTIAL_ACCEPTANCE_DECLINED',
    'INBOX',
    '1.0',
    'پیشنهاد کسری رد شد',
    'پیشنهاد کسری سفارش {{order_number}} رد شد.',
    'NORMAL',
    TRUE
)
ON CONFLICT (event_name, channel, version) DO NOTHING;
