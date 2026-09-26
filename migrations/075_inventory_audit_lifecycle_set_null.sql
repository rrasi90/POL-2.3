-- 075: Reconcile the inventory audit append-only guard with the lifecycle
-- contract declared by migration 069.
--
-- Migration 069 made inventory_audit_log.vendor_product_id nullable and switched
-- its foreign key to ON DELETE SET NULL so audit history survives vendor-product
-- lifecycle changes (the intent first recorded in migration 050 as G-313).
-- PostgreSQL implements that referential action as an internal UPDATE on
-- inventory_audit_log, and because the BEFORE UPDATE guard installed by 069
-- rejected every UPDATE, the SET NULL action could never execute: deleting a
-- vendor product that had ever produced audit history failed with
-- AUDIT_HISTORY_IS_APPEND_ONLY (SQLSTATE 55000) and aborted the caller's whole
-- transaction. This made the 069 lifecycle declaration unreachable dead code.
--
-- The guard below keeps rejecting every client-issued UPDATE/DELETE unchanged.
-- It yields only for the nested referential action (pg_trigger_depth() > 1)
-- and only when the sole change is vendor_product_id becoming NULL, exactly
-- the row shape the ON DELETE SET NULL contract produces.

CREATE OR REPLACE FUNCTION pol_inventory_audit_append_only_v075()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'UPDATE'
       AND pg_trigger_depth() > 1
       AND NEW.vendor_product_id IS NULL
       AND OLD.vendor_product_id IS NOT NULL
       AND NEW.id IS NOT DISTINCT FROM OLD.id
       AND NEW.vendor_id IS NOT DISTINCT FROM OLD.vendor_id
       AND NEW.old_quantity IS NOT DISTINCT FROM OLD.old_quantity
       AND NEW.new_quantity IS NOT DISTINCT FROM OLD.new_quantity
       AND NEW.old_price_toman IS NOT DISTINCT FROM OLD.old_price_toman
       AND NEW.new_price_toman IS NOT DISTINCT FROM OLD.new_price_toman
       AND NEW.source_trigger IS NOT DISTINCT FROM OLD.source_trigger
       AND NEW.reference_id IS NOT DISTINCT FROM OLD.reference_id
       AND NEW.actor_user_id IS NOT DISTINCT FROM OLD.actor_user_id
       AND NEW.created_at IS NOT DISTINCT FROM OLD.created_at
       AND NEW.old_reserved_quantity IS NOT DISTINCT FROM OLD.old_reserved_quantity
       AND NEW.new_reserved_quantity IS NOT DISTINCT FROM OLD.new_reserved_quantity
    THEN
        RETURN NEW;
    END IF;

    RAISE EXCEPTION 'AUDIT_HISTORY_IS_APPEND_ONLY'
        USING ERRCODE = '55000';
END;
$$;

DROP TRIGGER IF EXISTS trg_inventory_audit_append_only_v069 ON inventory_audit_log;
CREATE TRIGGER trg_inventory_audit_append_only_v069
BEFORE UPDATE OR DELETE ON inventory_audit_log
FOR EACH ROW
EXECUTE FUNCTION pol_inventory_audit_append_only_v075();
