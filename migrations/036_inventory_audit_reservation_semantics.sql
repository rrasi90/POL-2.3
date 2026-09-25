-- ============================================================================
-- 036_inventory_audit_reservation_semantics.sql
-- ============================================================================

ALTER TABLE inventory_audit_log
    ALTER COLUMN actor_user_id DROP NOT NULL;

ALTER TABLE inventory_audit_log
    ADD COLUMN IF NOT EXISTS old_reserved_quantity INTEGER,
    ADD COLUMN IF NOT EXISTS new_reserved_quantity INTEGER;

ALTER TABLE inventory_audit_log
    ADD CONSTRAINT chk_inventory_audit_reserved_nonnegative_v036
    CHECK (
        (old_reserved_quantity IS NULL OR old_reserved_quantity >= 0)
        AND (new_reserved_quantity IS NULL OR new_reserved_quantity >= 0)
    );

CREATE INDEX IF NOT EXISTS idx_inventory_audit_reference_v036
    ON inventory_audit_log(reference_id, created_at DESC)
    WHERE reference_id IS NOT NULL;
