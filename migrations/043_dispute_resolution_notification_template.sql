-- 043: Dispute resolution notification template
-- Forward-only remediation: DISPUTE_RESOLVED is consumed by the canonical
-- integration worker and therefore requires an active renderable template.

INSERT INTO notification_templates (
    event_name, channel, version, title_template, body_template, priority, allow_opt_out
)
VALUES (
    'DISPUTE_RESOLVED',
    'INBOX',
    '1.0',
    'پرونده اختلاف تعیین تکلیف شد',
    'پرونده اختلاف سفارش {{order_id}} با نتیجه {{outcome}} و مبلغ تأییدشده {{approved_amount_toman}} تومان تعیین تکلیف شد.',
    'HIGH',
    FALSE
)
ON CONFLICT (event_name, channel, version) DO NOTHING;
