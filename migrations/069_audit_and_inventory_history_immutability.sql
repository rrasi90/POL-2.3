-- 069: Immutable audit/history boundary.
CREATE OR REPLACE FUNCTION pol_append_only_audit_v069()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'AUDIT_HISTORY_IS_APPEND_ONLY'
        USING ERRCODE = '55000';
END;
$$;

DROP TRIGGER IF EXISTS trg_admin_audit_append_only_v069 ON admin_audit_logs;
CREATE TRIGGER trg_admin_audit_append_only_v069
BEFORE UPDATE OR DELETE ON admin_audit_logs
FOR EACH ROW
EXECUTE FUNCTION pol_append_only_audit_v069();

DROP TRIGGER IF EXISTS trg_inventory_audit_append_only_v069 ON inventory_audit_log;
CREATE TRIGGER trg_inventory_audit_append_only_v069
BEFORE UPDATE OR DELETE ON inventory_audit_log
FOR EACH ROW
EXECUTE FUNCTION pol_append_only_audit_v069();

ALTER TABLE inventory_audit_log
    DROP CONSTRAINT IF EXISTS inventory_audit_log_vendor_product_id_fkey;

ALTER TABLE inventory_audit_log
    ALTER COLUMN vendor_product_id DROP NOT NULL;

ALTER TABLE inventory_audit_log
    ADD CONSTRAINT inventory_audit_log_vendor_product_id_fkey
    FOREIGN KEY (vendor_product_id)
    REFERENCES vendor_products(id)
    ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_inventory_audit_vendor_created_v069
    ON inventory_audit_log(vendor_id, created_at DESC);
