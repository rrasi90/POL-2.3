-- ============================================================================
-- 032_cross_entity_integrity_and_append_only_guards.sql
-- Canonical post-031 hardening:
--   * cross-aggregate ownership consistency
--   * quantity invariants for order items
--   * immutable audit/timeline/event history
--   * financial/RMA lineage consistency
-- ============================================================================

-- ---------------------------------------------------------------------------
-- OrderItem: order/vendor-product/product ownership + quantity semantics
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION pol_validate_order_item_context_v032()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_order_retailer UUID;
    v_order_vendor UUID;
    v_product_id UUID;
    v_vendor_id UUID;
    v_vendor_product_product UUID;
BEGIN
    SELECT retailer_id, vendor_id
      INTO v_order_retailer, v_order_vendor
      FROM orders
     WHERE id = NEW.order_id;

    IF v_order_retailer IS NULL OR v_order_vendor IS NULL THEN
        RAISE EXCEPTION 'ORDER_ITEM_ORDER_CONTEXT_INVALID: order % has no valid commercial context', NEW.order_id
            USING ERRCODE = '23514';
    END IF;

    SELECT product_id, vendor_id
      INTO v_vendor_product_product, v_vendor_id
      FROM vendor_products
     WHERE id = NEW.vendor_product_id;

    IF v_vendor_product_product IS NULL OR v_vendor_id IS NULL THEN
        RAISE EXCEPTION 'ORDER_ITEM_VENDOR_PRODUCT_NOT_FOUND: vendor_product %', NEW.vendor_product_id
            USING ERRCODE = '23503';
    END IF;

    v_product_id := NEW.product_id;

    IF v_vendor_id <> v_order_vendor THEN
        RAISE EXCEPTION 'ORDER_ITEM_VENDOR_MISMATCH: order vendor % != vendor_product vendor %',
            v_order_vendor, v_vendor_id
            USING ERRCODE = '23514';
    END IF;

    IF v_product_id <> v_vendor_product_product THEN
        RAISE EXCEPTION 'ORDER_ITEM_PRODUCT_MISMATCH: product % != vendor_product product %',
            v_product_id, v_vendor_product_product
            USING ERRCODE = '23514';
    END IF;

    IF NEW.accepted_quantity IS NOT NULL
       AND (NEW.accepted_quantity < 0 OR NEW.accepted_quantity > NEW.ordered_quantity) THEN
        RAISE EXCEPTION 'ORDER_ITEM_ACCEPTED_QUANTITY_INVALID: accepted=% ordered=%',
            NEW.accepted_quantity, NEW.ordered_quantity
            USING ERRCODE = '23514';
    END IF;

    IF NEW.delivered_quantity IS NOT NULL
       AND (NEW.delivered_quantity < 0
            OR NEW.delivered_quantity > COALESCE(NEW.accepted_quantity, NEW.ordered_quantity)) THEN
        RAISE EXCEPTION 'ORDER_ITEM_DELIVERED_QUANTITY_INVALID: delivered=% accepted/order=%',
            NEW.delivered_quantity, COALESCE(NEW.accepted_quantity, NEW.ordered_quantity)
            USING ERRCODE = '23514';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_order_item_context_v032 ON order_items;
CREATE CONSTRAINT TRIGGER trg_validate_order_item_context_v032
AFTER INSERT OR UPDATE OF order_id, product_id, vendor_product_id, accepted_quantity, delivered_quantity
ON order_items
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION pol_validate_order_item_context_v032();

-- ---------------------------------------------------------------------------
-- Commercial financial lineages
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION pol_validate_payment_context_v032()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_order_retailer UUID;
    v_order_vendor UUID;
BEGIN
    SELECT retailer_id, vendor_id
      INTO v_order_retailer, v_order_vendor
      FROM orders
     WHERE id = NEW.order_id;

    IF v_order_retailer IS NULL OR v_order_vendor IS NULL THEN
        RAISE EXCEPTION 'PAYMENT_ORDER_CONTEXT_INVALID: order %', NEW.order_id
            USING ERRCODE = '23514';
    END IF;

    IF NEW.retailer_id <> v_order_retailer OR NEW.vendor_id <> v_order_vendor THEN
        RAISE EXCEPTION 'PAYMENT_PARTICIPANT_MISMATCH: order=(%,%) payment=(%,%)',
            v_order_retailer, v_order_vendor, NEW.retailer_id, NEW.vendor_id
            USING ERRCODE = '23514';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_payment_context_v032 ON payments;
CREATE CONSTRAINT TRIGGER trg_validate_payment_context_v032
AFTER INSERT OR UPDATE OF order_id, retailer_id, vendor_id
ON payments
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION pol_validate_payment_context_v032();

CREATE OR REPLACE FUNCTION pol_validate_settlement_context_v032()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_order_vendor UUID;
BEGIN
    SELECT vendor_id INTO v_order_vendor FROM orders WHERE id = NEW.order_id;
    IF v_order_vendor IS NULL THEN
        RAISE EXCEPTION 'SETTLEMENT_ORDER_CONTEXT_INVALID: order %', NEW.order_id
            USING ERRCODE = '23514';
    END IF;
    IF NEW.vendor_id <> v_order_vendor THEN
        RAISE EXCEPTION 'SETTLEMENT_VENDOR_MISMATCH: order vendor % != settlement vendor %',
            v_order_vendor, NEW.vendor_id
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_settlement_context_v032 ON settlements;
CREATE CONSTRAINT TRIGGER trg_validate_settlement_context_v032
AFTER INSERT OR UPDATE OF order_id, vendor_id
ON settlements
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION pol_validate_settlement_context_v032();

CREATE OR REPLACE FUNCTION pol_validate_refund_context_v032()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_order_retailer UUID;
    v_payment_order UUID;
    v_payment_retailer UUID;
    v_payment_vendor UUID;
    v_dispute_order UUID;
    v_return_order UUID;
    v_return_retailer UUID;
BEGIN
    SELECT retailer_id INTO v_order_retailer FROM orders WHERE id = NEW.order_id;
    IF v_order_retailer IS NULL OR NEW.retailer_id <> v_order_retailer THEN
        RAISE EXCEPTION 'REFUND_RETAILER_MISMATCH: order=% refund_retailer=%',
            NEW.order_id, NEW.retailer_id
            USING ERRCODE = '23514';
    END IF;

    IF NEW.payment_id IS NOT NULL THEN
        SELECT order_id, retailer_id, vendor_id
          INTO v_payment_order, v_payment_retailer, v_payment_vendor
          FROM payments
         WHERE id = NEW.payment_id;
        IF v_payment_order IS NULL
           OR v_payment_order <> NEW.order_id
           OR v_payment_retailer <> NEW.retailer_id THEN
            RAISE EXCEPTION 'REFUND_PAYMENT_LINEAGE_MISMATCH: refund order=% payment=%',
                NEW.order_id, NEW.payment_id
                USING ERRCODE = '23514';
        END IF;
    END IF;

    IF NEW.dispute_id IS NOT NULL THEN
        SELECT order_id INTO v_dispute_order FROM disputes WHERE id = NEW.dispute_id;
        IF v_dispute_order IS NULL OR v_dispute_order <> NEW.order_id THEN
            RAISE EXCEPTION 'REFUND_DISPUTE_LINEAGE_MISMATCH: refund order=% dispute=%',
                NEW.order_id, NEW.dispute_id
                USING ERRCODE = '23514';
        END IF;
    END IF;

    IF NEW.return_id IS NOT NULL THEN
        SELECT order_id, retailer_id
          INTO v_return_order, v_return_retailer
          FROM returns
         WHERE id = NEW.return_id;
        IF v_return_order IS NULL
           OR v_return_order <> NEW.order_id
           OR v_return_retailer <> NEW.retailer_id THEN
            RAISE EXCEPTION 'REFUND_RETURN_LINEAGE_MISMATCH: refund order=% return=%',
                NEW.order_id, NEW.return_id
                USING ERRCODE = '23514';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_refund_context_v032 ON refunds;
CREATE CONSTRAINT TRIGGER trg_validate_refund_context_v032
AFTER INSERT OR UPDATE OF order_id, payment_id, dispute_id, retailer_id, return_id
ON refunds
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION pol_validate_refund_context_v032();

-- ---------------------------------------------------------------------------
-- Delivery order/vendor ownership
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION pol_validate_delivery_context_v032()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_order_vendor UUID;
BEGIN
    SELECT vendor_id INTO v_order_vendor FROM orders WHERE id = NEW.order_id;
    IF v_order_vendor IS NULL OR NEW.vendor_id <> v_order_vendor THEN
        RAISE EXCEPTION 'DELIVERY_VENDOR_MISMATCH: order vendor % != delivery vendor %',
            v_order_vendor, NEW.vendor_id
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_delivery_context_v032 ON deliveries;
CREATE CONSTRAINT TRIGGER trg_validate_delivery_context_v032
AFTER INSERT OR UPDATE OF order_id, vendor_id
ON deliveries
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION pol_validate_delivery_context_v032();

-- ---------------------------------------------------------------------------
-- Return item arithmetic: accepted <= received <= requested
-- (Existing checks remain; explicit names make the invariant discoverable.)
-- ---------------------------------------------------------------------------
ALTER TABLE return_items
    ADD CONSTRAINT chk_return_item_received_nonnegative_v032
    CHECK (received_quantity >= 0);

ALTER TABLE return_items
    ADD CONSTRAINT chk_return_item_accepted_nonnegative_v032
    CHECK (accepted_quantity >= 0);

-- ---------------------------------------------------------------------------
-- Immutable append-only audit/event trails
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION pol_guard_append_only_v032()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION '% is append-only and cannot be updated or deleted', TG_TABLE_NAME
        USING ERRCODE = '55000';
END;
$$;

DROP TRIGGER IF EXISTS trg_order_timeline_append_only_v032 ON order_timeline_events;
CREATE TRIGGER trg_order_timeline_append_only_v032
BEFORE UPDATE OR DELETE ON order_timeline_events
FOR EACH ROW EXECUTE FUNCTION pol_guard_append_only_v032();

DROP TRIGGER IF EXISTS trg_return_events_append_only_v032 ON return_events;
CREATE TRIGGER trg_return_events_append_only_v032
BEFORE UPDATE OR DELETE ON return_events
FOR EACH ROW EXECUTE FUNCTION pol_guard_append_only_v032();

DROP TRIGGER IF EXISTS trg_admin_audit_append_only_v032 ON admin_audit_logs;
CREATE TRIGGER trg_admin_audit_append_only_v032
BEFORE UPDATE OR DELETE ON admin_audit_logs
FOR EACH ROW EXECUTE FUNCTION pol_guard_append_only_v032();

DROP TRIGGER IF EXISTS trg_domain_events_append_only_v032 ON domain_events_log;
CREATE TRIGGER trg_domain_events_append_only_v032
BEFORE UPDATE OR DELETE ON domain_events_log
FOR EACH ROW EXECUTE FUNCTION pol_guard_append_only_v032();

-- ---------------------------------------------------------------------------
-- Helpful indexes for FK lineage checks and worker/reconciliation queries
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_refunds_payment_order_v032
    ON refunds(payment_id, order_id)
    WHERE payment_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_refunds_return_order_v032
    ON refunds(return_id, order_id)
    WHERE return_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_order_items_context_v032
    ON order_items(order_id, vendor_product_id);
