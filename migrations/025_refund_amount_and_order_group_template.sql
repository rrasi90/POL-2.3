ALTER TABLE returns
    DROP CONSTRAINT chk_returns_refund_pending_amount;

ALTER TABLE returns
    ADD CONSTRAINT chk_returns_refund_pending_amount
    CHECK (
        status NOT IN ('REFUND_PENDING', 'REFUNDED')
        OR (
            approved_refund_amount_toman IS NOT NULL
            AND approved_refund_amount_toman > 0
        )
    );

INSERT INTO notification_templates (
    event_name, channel, version, title_template, body_template, priority, allow_opt_out
)
VALUES (
    'ORDER_GROUP_SUBMITTED', 'INBOX', '1.0',
    'سبد سفارش ثبت شد', 'سبد سفارش {{group_id}} ثبت شد.', 'HIGH', FALSE
)
ON CONFLICT (event_name, channel, version) DO NOTHING;
