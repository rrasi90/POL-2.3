-- 074: Consolidate append-only guards on admin_audit_logs.
--
-- Three BEFORE UPDATE/DELETE triggers currently guard admin_audit_logs and
-- PostgreSQL fires them in name order: trg_admin_audit_append_only_v032 wins
-- alphabetically, which leaves the dedicated migration-049 immutability guard
-- (and the 069 audit-history guard) unreachable dead code on this table.
-- Immutability itself stays enforced — by the dedicated 049 guard.

DROP TRIGGER IF EXISTS trg_admin_audit_append_only_v032 ON admin_audit_logs;
DROP TRIGGER IF EXISTS trg_admin_audit_append_only_v069 ON admin_audit_logs;
