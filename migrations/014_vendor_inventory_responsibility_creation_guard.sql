-- ============================================================================
-- POL Migration 014
-- Vendor creation -> canonical warehouse responsibility materialization
-- ============================================================================

CREATE OR REPLACE FUNCTION pol_materialize_vendor_inventory_responsibility()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.user_id IS NOT NULL AND NEW.organization_id IS NOT NULL
       AND COALESCE(NEW.status, 'ACTIVE') IN ('ACTIVE', 'PENDING_VERIFICATION', 'OFFLINE', 'SUSPENDED') THEN
        INSERT INTO vendor_inventory_responsibilities (
            vendor_id, user_id, responsibility_type, is_primary, source
        )
        SELECT NEW.id, NEW.user_id, 'WAREHOUSE_INVENTORY', TRUE, 'ONBOARDING'
        WHERE EXISTS (
            SELECT 1
            FROM organizations o
            WHERE o.id = NEW.organization_id
              AND o.org_type = 'VENDOR'
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

-- Repair vendor rows created before this guard when vendors.user_id is an
-- unambiguous operational owner. Vendor status, not organization workflow
-- status, controls whether the vendor row itself is operationally usable.
INSERT INTO vendor_inventory_responsibilities (
    vendor_id, user_id, responsibility_type, is_primary, source
)
SELECT v.id, v.user_id, 'WAREHOUSE_INVENTORY', TRUE, 'ONBOARDING'
FROM vendors v
JOIN organizations o ON o.id = v.organization_id
WHERE v.user_id IS NOT NULL
  AND o.org_type = 'VENDOR'
  AND COALESCE(v.status, 'ACTIVE') IN ('ACTIVE', 'PENDING_VERIFICATION', 'OFFLINE', 'SUSPENDED')
  AND NOT EXISTS (
      SELECT 1
      FROM vendor_inventory_responsibilities r
      WHERE r.vendor_id = v.id
        AND r.responsibility_type = 'WAREHOUSE_INVENTORY'
        AND r.is_primary = TRUE
        AND r.effective_until IS NULL
  );
