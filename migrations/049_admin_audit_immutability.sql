-- ============================================================================
-- POL Migration 049
-- Deep-audit remediation: G-312
-- Admin audit logs are append-only evidence and must not be mutable.
-- ============================================================================

CREATE OR REPLACE FUNCTION prevent_admin_audit_log_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'admin_audit_logs are immutable: % is not permitted', TG_OP
        USING ERRCODE = '55000';
END;
$$;

DROP TRIGGER IF EXISTS trg_admin_audit_logs_immutable ON admin_audit_logs;

CREATE TRIGGER trg_admin_audit_logs_immutable
BEFORE UPDATE OR DELETE ON admin_audit_logs
FOR EACH ROW
EXECUTE FUNCTION prevent_admin_audit_log_mutation();
