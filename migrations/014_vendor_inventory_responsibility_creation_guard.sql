-- ============================================================================
-- POL Migration 014
-- Vendor creation -> canonical warehouse responsibility materialization
-- ============================================================================

CREATE OR REPLACE FUNCTION pol_materialize_vendor_inventory_responsibility()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.user_id IS NOT NULL AND NEW.organization_id IS NOT NULL THEN
        INSERT INTO vendor_inventory_responsibilities (
            vendor_id, user_id, responsibility_type, is_primary, source
        )
        SELECT NEW.id, NEW.user_id, 'WAREHOUSE_INVENTORY', TRUE, 'ONBOARDING'
        WHERE EXISTS (
            SELECT 1
            FROM organizations o
            WHERE o.id = NEW.organization_id
              AND o.org_type = 'VENDOR'
              AND o.status = 'ACTIVE'
        )
        ON CONFLICT (vendor_id, user_id, responsibility_type) DO UPDATE
        SET is_primary = TRUE,
            effective_until = NULL,
            updated_at = now();
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_materialize_vendor_inventory_responsibility ON vendors;
CREATE TRIGGER trg_materialize_vendor_inventory_responsibility
AFTER INSERT ON vendors
FOR EACH ROW
EXECUTE FUNCTION pol_materialize_vendor_inventory_responsibility();

-- Repair any vendor rows created before this guard was installed when the
-- canonical source can be derived unambiguously from vendors.user_id.
INSERT INTO vendor_inventory_responsibilities (
    vendor_id, user_id, responsibility_type, is_primary, source
)
SELECT v.id, v.user_id, 'WAREHOUSE_INVENTORY', TRUE, 'ONBOARDING'
FROM vendors v
JOIN organizations o ON o.id = v.organization_id
WHERE v.user_id IS NOT NULL
  AND o.org_type = 'VENDOR'
  AND o.status = 'ACTIVE'
  AND NOT EXISTS (
      SELECT 1
      FROM vendor_inventory_responsibilities r
      WHERE r.vendor_id = v.id
        AND r.responsibility_type = 'WAREHOUSE_INVENTORY'
        AND r.is_primary = TRUE
        AND r.effective_until IS NULL
  );
