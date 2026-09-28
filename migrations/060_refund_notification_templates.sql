-- 060: Canonical refund lifecycle notification templates
INSERT INTO notification_templates
    (event_name, channel, version, title_template, body_template, priority, allow_opt_out)
VALUES
 ('REFUND_CREATED','INBOX','1.0','استرداد ایجاد شد','استرداد سفارش {{order_id}} به مبلغ {{amount_toman}} تومان ایجاد شد.','HIGH',FALSE),
 ('REFUND_APPROVED','INBOX','1.0','استرداد تأیید شد','استرداد سفارش {{order_id}} به مبلغ {{amount_toman}} تومان تأیید شد.','HIGH',FALSE),
 ('REFUND_COMPLETED','INBOX','1.0','استرداد انجام شد','استرداد سفارش {{order_id}} به مبلغ {{amount_toman}} تومان انجام شد.','HIGH',FALSE),
 ('PAYMENT_REFUNDED','INBOX','1.0','پرداخت مسترد شد','پرداخت مرتبط با سفارش {{order_id}} به مبلغ {{amount_toman}} تومان مسترد شد.','HIGH',FALSE)
ON CONFLICT (event_name, channel, version) DO NOTHING;
