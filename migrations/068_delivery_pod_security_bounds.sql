-- 068: Delivery/POD hardening.
ALTER TABLE deliveries
    DROP CONSTRAINT IF EXISTS chk_delivery_otp_attempt_count_max_v068;

ALTER TABLE deliveries
    ADD CONSTRAINT chk_delivery_otp_attempt_count_max_v068
    CHECK (delivery_otp_attempt_count BETWEEN 0 AND 5)
    NOT VALID;

ALTER TABLE deliveries
    DROP CONSTRAINT IF EXISTS chk_delivery_otp_format_v068;

ALTER TABLE deliveries
    ADD CONSTRAINT chk_delivery_otp_format_v068
    CHECK (delivery_otp IS NULL OR delivery_otp ~ '^[0-9]{4}$')
    NOT VALID;

ALTER TABLE order_items
    DROP CONSTRAINT IF EXISTS chk_order_item_accepted_quantity_v068;

ALTER TABLE order_items
    ADD CONSTRAINT chk_order_item_accepted_quantity_v068
    CHECK (
        accepted_quantity IS NULL
        OR (accepted_quantity >= 0 AND accepted_quantity <= ordered_quantity)
    )
    NOT VALID;

ALTER TABLE order_items
    DROP CONSTRAINT IF EXISTS chk_order_item_delivered_quantity_v068;

ALTER TABLE order_items
    ADD CONSTRAINT chk_order_item_delivered_quantity_v068
    CHECK (
        delivered_quantity IS NULL
        OR (delivered_quantity >= 0 AND delivered_quantity <= ordered_quantity)
    )
    NOT VALID;

ALTER TABLE order_items
    DROP CONSTRAINT IF EXISTS chk_order_item_fulfillment_quantity_consistency_v068;

ALTER TABLE order_items
    ADD CONSTRAINT chk_order_item_fulfillment_quantity_consistency_v068
    CHECK (
        fulfillment_status = 'PENDING'
        OR delivered_quantity IS NOT NULL
    )
    NOT VALID;
