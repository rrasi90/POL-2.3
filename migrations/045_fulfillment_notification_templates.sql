-- 045: Fulfillment and cancellation notification templates
-- Forward-only remediation for lifecycle events emitted by fulfillment workers.

INSERT INTO notification_templates (
    event_name, channel, version, title_template, body_template, priority, allow_opt_out
)
VALUES
(
    'ORDER_PREPARING',
    'INBOX',
    '1.0',
    'آماده‌سازی سفارش شروع شد',
    'آماده‌سازی سفارش {{order_number}} آغاز شد.',
    'NORMAL',
    TRUE
),
(
    'ORDER_READY',
    'INBOX',
    '1.0',
    'سفارش آماده ارسال است',
    'سفارش {{order_number}} آماده ارسال است.',
    'NORMAL',
    TRUE
),
(
    'ORDER_DISPATCHED',
    'INBOX',
    '1.0',
    'سفارش ارسال شد',
    'سفارش {{order_number}} با شناسه تحویل {{delivery_id}} ارسال شد.',
    'HIGH',
    TRUE
),
(
    'DELIVERY_OTP_GENERATED',
    'INBOX',
    '1.0',
    'کد تحویل ایجاد شد',
    'کد تحویل سفارش {{order_id}} برای دریافت کالا ایجاد شد.',
    'CRITICAL',
    FALSE
),
(
    'ORDER_DELIVERED',
    'INBOX',
    '1.0',
    'تحویل سفارش تأیید شد',
    'تحویل سفارش {{order_number}} با کد یکبارمصرف تأیید شد.',
    'NORMAL',
    TRUE
),
(
    'ORDER_CANCELLED',
    'INBOX',
    '1.0',
    'سفارش لغو شد',
    'سفارش {{order_number}} به دلیل {{cancellation_reason}} لغو شد.',
    'HIGH',
    FALSE
)
ON CONFLICT (event_name, channel, version) DO NOTHING;
