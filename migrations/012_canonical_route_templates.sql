-- Canonical templates for newly hardened application routes.
INSERT INTO notification_templates (event_name, channel, version, title_template, body_template, priority, allow_opt_out)
VALUES
('PAYMENT_RECONCILED', 'INBOX', '1.0', 'پرداخت تأیید شد', 'پرداخت سفارش شما با موفقیت تطبیق داده شد.', 'NORMAL', TRUE),
('RETURN_REQUESTED', 'INBOX', '1.0', 'درخواست مرجوعی ثبت شد', 'درخواست مرجوعی شما ثبت شد و در حال بررسی است.', 'NORMAL', TRUE)
ON CONFLICT (event_name, channel, version) DO NOTHING;
