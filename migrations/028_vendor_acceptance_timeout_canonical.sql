-- 028_vendor_acceptance_timeout_canonical.sql
-- Batch 6C-7: canonical vendor-acceptance timeout persistence and calendar.

ALTER TABLE orders
    ADD COLUMN IF NOT EXISTS vendor_acceptance_deadline_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS cancellation_reason VARCHAR(64);

CREATE INDEX IF NOT EXISTS idx_orders_vendor_acceptance_timeout
    ON orders(order_status, vendor_acceptance_deadline_at)
    WHERE order_status = 'SUBMITTED';

CREATE TABLE IF NOT EXISTS operational_holidays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    calendar_key VARCHAR(64) NOT NULL DEFAULT 'AHVAZ_WHOLESALE',
    holiday_date DATE NOT NULL,
    description VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_operational_holiday UNIQUE (calendar_key, holiday_date)
);

CREATE INDEX IF NOT EXISTS idx_operational_holidays_active
    ON operational_holidays(calendar_key, holiday_date)
    WHERE is_active = TRUE;

ALTER TABLE field_tasks
    DROP CONSTRAINT IF EXISTS field_tasks_task_type_check;

ALTER TABLE field_tasks
    ADD CONSTRAINT field_tasks_task_type_check
    CHECK (
        task_type IN (
            'ONBOARD_RETAILER',
            'TRAIN_RETAILER',
            'FIRST_ORDER_ASSIST',
            'FOLLOW_UP',
            'VENDOR_VISIT',
            'DISPUTE_VISIT',
            'VENDOR_TIMEOUT'
        )
    );

INSERT INTO notification_templates (
    event_name, channel, version, title_template, body_template, priority, allow_opt_out
)
VALUES (
    'ORDER_CANCELLED',
    'INBOX',
    '1.0',
    'سفارش لغو شد',
    'سفارش {{order_number}} به دلیل عدم پاسخ بنکدار در مهلت تعیین‌شده لغو شد.',
    'HIGH',
    TRUE
)
ON CONFLICT (event_name, channel, version) DO NOTHING;
