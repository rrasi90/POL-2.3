-- ============================================================================
-- POL Migration 057
-- Deep-audit remediation: G-342
-- Deferred invariant: vendor_inventory.reserved_quantity must equal the sum
-- of ACTIVE inventory reservations for the same vendor product.
-- ============================================================================

CREATE OR REPLACE FUNCTION enforce_inventory_reservation_reconciliation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    target_vendor_product_id UUID;
    recorded_reserved NUMERIC;
    expected_reserved NUMERIC;
BEGIN
    target_vendor_product_id := COALESCE(
        CASE WHEN TG_TABLE_NAME = 'inventory_reservations' THEN NEW.vendor_product_id END,
        CASE WHEN TG_TABLE_NAME = 'inventory_reservations' THEN OLD.vendor_product_id END,
        CASE WHEN TG_TABLE_NAME = 'vendor_inventory' THEN NEW.vendor_product_id END,
        CASE WHEN TG_TABLE_NAME = 'vendor_inventory' THEN OLD.vendor_product_id END
    );

    SELECT reserved_quantity
      INTO recorded_reserved
      FROM vendor_inventory
     WHERE vendor_product_id = target_vendor_product_id;

    IF recorded_reserved IS NULL THEN
        RETURN NULL;
    END IF;

    SELECT COALESCE(SUM(quantity),0)
      INTO expected_reserved
      FROM inventory_reservations
     WHERE vendor_product_id = target_vendor_product_id
       AND status = 'ACTIVE';

    IF recorded_reserved <> expected_reserved THEN
        RAISE EXCEPTION
            'Inventory reservation reconciliation invariant failed for vendor_product %, recorded %, expected %',
            target_vendor_product_id, recorded_reserved, expected_reserved
            USING ERRCODE = '23514';
    END IF;

    RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS trg_reservation_reconciliation_reservations ON inventory_reservations;
CREATE CONSTRAINT TRIGGER trg_reservation_reconciliation_reservations
AFTER INSERT OR UPDATE OR DELETE ON inventory_reservations
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION enforce_inventory_reservation_reconciliation();

DROP TRIGGER IF EXISTS trg_reservation_reconciliation_inventory ON vendor_inventory;
CREATE CONSTRAINT TRIGGER trg_reservation_reconciliation_inventory
AFTER INSERT OR UPDATE ON vendor_inventory
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION enforce_inventory_reservation_reconciliation();

CREATE INDEX IF NOT EXISTS idx_active_reservations_vendor_product
    ON inventory_reservations(vendor_product_id)
    WHERE status = 'ACTIVE';
