-- 042: Delivery exception notification templates
-- Forward-only remediation: every delivery-exception outbox event must be
-- renderable by the canonical integration worker.

INSERT INTO notification_templates (
    event_name, channel, version, title_template, body_template, priority, allow_opt_out
)
VALUES
(
    'DELIVERY_EXCEPTION_REPORTED',
    'INBOX',
    '1.0',
    'استثنای تحویل ثبت شد',
    'برای سفارش {{order_id}} یک استثنای تحویل با نوع {{exception_type}} ثبت شد.',
    'HIGH',
    FALSE
),
(
    'DELIVERY_EXCEPTION_RESOLVED',
    'INBOX',
    '1.0',
    'استثنای تحویل رسیدگی شد',
    'استثنای تحویل سفارش {{order_id}} با نتیجه {{resolution_type}} رسیدگی شد.',
    'NORMAL',
    TRUE
),
(
    'DELIVERY_EXCEPTION_ESCALATED',
    'INBOX',
    '1.0',
    'استثنای تحویل ارجاع شد',
    'استثنای تحویل سفارش {{order_id}} برای رسیدگی عملیاتی ارجاع شد.',
    'HIGH',
    FALSE
)
ON CONFLICT (event_name, channel, version) DO NOTHING;
