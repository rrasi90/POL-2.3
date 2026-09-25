-- ============================================================================
-- 038_dispute_notification_template.sql
-- Canonical template required by the asynchronous notification integration
-- worker for the DISPUTE_OPENED domain event.
-- ============================================================================

INSERT INTO notification_templates (
    event_name,
    channel,
    version,
    title_template,
    body_template,
    priority,
    allow_opt_out
)
VALUES (
    'DISPUTE_OPENED',
    'INBOX',
    '1.0',
    'پرونده اختلاف ثبت شد',
    'برای سفارش {{order_id}} یک پرونده اختلاف ثبت شد. شناسه اختلاف: {{dispute_id}}.',
    'HIGH',
    FALSE
)
ON CONFLICT (event_name, channel, version) DO NOTHING;
