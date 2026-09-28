-- ============================================================================
-- POL Migration 050
-- Deep-audit remediation: G-313
-- Inventory audit history must survive vendor-product lifecycle changes.
-- ============================================================================

ALTER TABLE inventory_audit_log
    DROP CONSTRAINT IF EXISTS inventory_audit_log_vendor_product_id_fkey;

ALTER TABLE inventory_audit_log
    ADD CONSTRAINT inventory_audit_log_vendor_product_id_fkey
    FOREIGN KEY (vendor_product_id)
    REFERENCES vendor_products(id)
    ON DELETE RESTRICT;
