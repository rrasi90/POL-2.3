-- ============================================================================
-- 034_checkout_single_use_and_reservation_lineage.sql
-- ============================================================================

ALTER TABLE allocation_plans
    DROP CONSTRAINT IF EXISTS chk_allocation_plans_status;

ALTER TABLE allocation_plans
    ADD CONSTRAINT chk_allocation_plans_status
    CHECK (status IN ('PREVIEW', 'OPTIMIZED', 'CONFIRMED', 'SUPERSEDED', 'REJECTED', 'EXPIRED', 'CONSUMED'));

ALTER TABLE allocation_plans
    ADD COLUMN IF NOT EXISTS consumed_at TIMESTAMPTZ;

CREATE UNIQUE INDEX IF NOT EXISTS uq_order_group_allocation_plan_v034
    ON order_groups(allocation_plan_id)
    WHERE allocation_plan_id IS NOT NULL;

ALTER TABLE baskets
    DROP CONSTRAINT IF EXISTS baskets_status_check;

ALTER TABLE baskets
    ADD CONSTRAINT baskets_status_check
    CHECK (status IN ('OPEN', 'ABANDONED', 'SUBMITTED', 'EXPIRED'));

CREATE UNIQUE INDEX IF NOT EXISTS uq_inventory_reservation_idempotency_v034
    ON inventory_reservations(idempotency_key)
    WHERE idempotency_key IS NOT NULL;

CREATE OR REPLACE FUNCTION pol_validate_reservation_lineage_v034()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_order_item_order UUID;
    v_order_item_vendor_product UUID;
BEGIN
    IF NEW.order_item_id IS NULL THEN
        IF NEW.order_id IS NOT NULL THEN
            RAISE EXCEPTION 'RESERVATION_ORDER_ITEM_REQUIRED'
                USING ERRCODE = '23514';
        END IF;
        RETURN NEW;
    END IF;

    SELECT order_id, vendor_product_id
      INTO v_order_item_order, v_order_item_vendor_product
      FROM order_items
     WHERE id = NEW.order_item_id;

    IF v_order_item_order IS NULL THEN
        RAISE EXCEPTION 'RESERVATION_ORDER_ITEM_NOT_FOUND'
            USING ERRCODE = '23503';
    END IF;

    IF NEW.order_id IS NOT NULL AND NEW.order_id <> v_order_item_order THEN
        RAISE EXCEPTION 'RESERVATION_ORDER_ITEM_ORDER_MISMATCH'
            USING ERRCODE = '23514';
    END IF;

    IF NEW.vendor_product_id <> v_order_item_vendor_product THEN
        RAISE EXCEPTION 'RESERVATION_ORDER_ITEM_VENDOR_PRODUCT_MISMATCH'
            USING ERRCODE = '23514';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_reservation_lineage_v034 ON inventory_reservations;
CREATE CONSTRAINT TRIGGER trg_validate_reservation_lineage_v034
AFTER INSERT OR UPDATE OF order_id, order_item_id, vendor_product_id
ON inventory_reservations
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION pol_validate_reservation_lineage_v034();
