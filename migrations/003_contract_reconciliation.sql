-- ============================================================================
-- POL Contract Reconciliation & IAM Hardening
-- Migration: 003_contract_reconciliation.sql
-- Target: PostgreSQL 18+
-- Purpose:
--   1) Make organization_memberships.role the only authorization role source.
--   2) Reconcile role names with the canonical Roles & Permissions contract.
--   3) Enforce role <-> organization type invariants at the database boundary.
--   4) Preserve users.role for backwards migration compatibility, but make it
--      explicitly non-authoritative and optional.
--   5) Remove retailer/vendor legacy one-user uniqueness so a user may own or
--      staff multiple organizations through memberships.
-- ============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- 1. Canonical membership roles
-- ---------------------------------------------------------------------------
-- 001/002 used legacy role names SUPER_ADMIN / OPS_ADMIN. The active IAM
-- contract uses ADMIN_SUPER / OPS_AGENT / FIELD_ACTIVATOR plus the two
-- organization-scoped owner/staff pairs.

ALTER TABLE organization_memberships
    DROP CONSTRAINT IF EXISTS organization_memberships_role_check;

-- Convert legacy rows before installing the new CHECK constraint.
UPDATE organization_memberships
SET role = CASE role
    WHEN 'SUPER_ADMIN' THEN 'ADMIN_SUPER'
    WHEN 'OPS_ADMIN' THEN 'OPS_AGENT'
    ELSE role
END
WHERE role IN ('SUPER_ADMIN', 'OPS_ADMIN');

ALTER TABLE organization_memberships
    ADD CONSTRAINT organization_memberships_role_check
    CHECK (role IN (
        'RETAILER_OWNER',
        'RETAILER_STAFF',
        'VENDOR_OWNER',
        'VENDOR_STAFF',
        'OPS_AGENT',
        'ADMIN_SUPER',
        'FIELD_ACTIVATOR'
    ));

-- ---------------------------------------------------------------------------
-- 2. Membership role / organization type invariant
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION pol_validate_membership_role_org_type()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_org_type VARCHAR(32);
BEGIN
    SELECT org_type INTO v_org_type
    FROM organizations
    WHERE id = NEW.organization_id;

    IF v_org_type IS NULL THEN
        RAISE EXCEPTION 'Organization % does not exist', NEW.organization_id;
    END IF;

    IF NEW.role IN ('RETAILER_OWNER', 'RETAILER_STAFF')
       AND v_org_type <> 'RETAILER' THEN
        RAISE EXCEPTION 'Role % is only valid for RETAILER organizations', NEW.role;
    END IF;

    IF NEW.role IN ('VENDOR_OWNER', 'VENDOR_STAFF')
       AND v_org_type <> 'VENDOR' THEN
        RAISE EXCEPTION 'Role % is only valid for VENDOR organizations', NEW.role;
    END IF;

    IF NEW.role IN ('OPS_AGENT', 'ADMIN_SUPER', 'FIELD_ACTIVATOR')
       AND v_org_type <> 'OPERATOR' THEN
        RAISE EXCEPTION 'Role % is only valid for OPERATOR organizations', NEW.role;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_membership_role_org_type
ON organization_memberships;

CREATE TRIGGER trg_validate_membership_role_org_type
BEFORE INSERT OR UPDATE OF organization_id, role
ON organization_memberships
FOR EACH ROW
EXECUTE FUNCTION pol_validate_membership_role_org_type();

-- ---------------------------------------------------------------------------
-- 3. Legacy user role is not an authorization source
-- ---------------------------------------------------------------------------
-- Keep the column during the migration window so older application binaries
-- can still read it. It may not be required to create a user, and all runtime
-- authorization must use organization_memberships.role + active organization.
ALTER TABLE users
    ALTER COLUMN role DROP NOT NULL;

COMMENT ON COLUMN users.role IS
'LEGACY / DEPRECATED. Not an authorization source. Runtime RBAC MUST use organization_memberships.role scoped by user_sessions.active_organization_id.';

-- ---------------------------------------------------------------------------
-- 4. Remove the legacy one-user-per-actor restriction
-- ---------------------------------------------------------------------------
-- A single user can own or work across multiple organizations. The canonical
-- relationship is organization_memberships; these legacy user_id columns are
-- retained only as compatibility references and are no longer unique.
ALTER TABLE retailers
    DROP CONSTRAINT IF EXISTS retailers_user_id_key;

ALTER TABLE vendors
    DROP CONSTRAINT IF EXISTS vendors_user_id_key;

COMMENT ON COLUMN retailers.user_id IS
'LEGACY / DEPRECATED ownership link. Do not use for authorization. Use organization_id + organization_memberships instead.';

COMMENT ON COLUMN vendors.user_id IS
'LEGACY / DEPRECATED ownership link. Do not use for authorization. Use organization_id + organization_memberships instead.';

-- ---------------------------------------------------------------------------
-- 5. Canonical organization references
-- ---------------------------------------------------------------------------
COMMENT ON COLUMN retailers.organization_id IS
'CANONICAL tenant reference. Authorization and tenant isolation MUST traverse this organization.';

COMMENT ON COLUMN vendors.organization_id IS
'CANONICAL tenant reference. Authorization and tenant isolation MUST traverse this organization.';

-- ---------------------------------------------------------------------------
-- 6. Consistency indexes
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_org_memberships_user_org_role
    ON organization_memberships (user_id, organization_id, role, status);

CREATE INDEX IF NOT EXISTS idx_retailers_organization
    ON retailers (organization_id);

CREATE INDEX IF NOT EXISTS idx_vendors_organization
    ON vendors (organization_id);

COMMIT;
