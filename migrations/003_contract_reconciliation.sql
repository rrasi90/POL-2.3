-- ============================================================================
-- POL Contract Reconciliation & IAM Hardening
-- Migration: 003_contract_reconciliation.sql
-- Target: PostgreSQL 18+ (SSoT per D-015)
-- Purpose:
--   1) Make organization_memberships.role the only authorization role source.
--   2) Reconcile role names with the canonical Roles & Permissions contract (ADMIN_SUPER, OPS_AGENT).
--   3) Enforce role <-> organization type invariants at the database boundary (Section 15).
--   4) Preserve users.role for backwards migration compatibility, but make it optional/nullable.
--   5) Remove retailer/vendor legacy one-user uniqueness so a user may own or
--      staff multiple organizations through memberships (Section 14).
--   6) Reconcile allocation_plans.status constraint to include 'SUPERSEDED'.
--   7) Ensure canonical organization references and indices.
-- ============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- 1. Canonical membership roles
-- ---------------------------------------------------------------------------
ALTER TABLE organization_memberships
    DROP CONSTRAINT IF EXISTS organization_memberships_role_check;
ALTER TABLE organization_memberships
    DROP CONSTRAINT IF EXISTS chk_membership_role;

-- Convert legacy rows before installing the new CHECK constraint
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
        'FIELD_ACTIVATOR',
        'SUPER_ADMIN', -- Legacy alias
        'OPS_ADMIN'    -- Legacy alias
    ));

-- ---------------------------------------------------------------------------
-- 2. Membership role / organization type invariant (Section 15)
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
        RAISE EXCEPTION 'Target organization % does not exist', NEW.organization_id;
    END IF;

    -- Invariant 1: RETAILER roles only in RETAILER organizations
    IF NEW.role IN ('RETAILER_OWNER', 'RETAILER_STAFF')
       AND v_org_type <> 'RETAILER' THEN
        RAISE EXCEPTION 'Role % is only permitted in RETAILER organizations (attempted in %)', NEW.role, v_org_type;
    END IF;

    -- Invariant 2: VENDOR roles only in VENDOR organizations
    IF NEW.role IN ('VENDOR_OWNER', 'VENDOR_STAFF')
       AND v_org_type <> 'VENDOR' THEN
        RAISE EXCEPTION 'Role % is only permitted in VENDOR organizations (attempted in %)', NEW.role, v_org_type;
    END IF;

    -- Invariant 3: OPERATOR roles only in OPERATOR organizations
    IF NEW.role IN ('OPS_AGENT', 'ADMIN_SUPER', 'FIELD_ACTIVATOR', 'SUPER_ADMIN', 'OPS_ADMIN')
       AND v_org_type <> 'OPERATOR' THEN
        RAISE EXCEPTION 'Role % is only permitted in OPERATOR organizations (attempted in %)', NEW.role, v_org_type;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_membership_role_org_type
ON organization_memberships;
DROP TRIGGER IF EXISTS trg_enforce_org_membership_role_invariant
ON organization_memberships;

CREATE TRIGGER trg_enforce_org_membership_role_invariant
BEFORE INSERT OR UPDATE OF organization_id, role
ON organization_memberships
FOR EACH ROW
EXECUTE FUNCTION pol_validate_membership_role_org_type();

-- ---------------------------------------------------------------------------
-- 3. Legacy user role is not an authorization source
-- ---------------------------------------------------------------------------
ALTER TABLE users
    ALTER COLUMN role DROP NOT NULL;

ALTER TABLE users
    DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE users
    DROP CONSTRAINT IF EXISTS chk_users_role_legacy;

ALTER TABLE users
    ADD CONSTRAINT chk_users_role_legacy
    CHECK (role IS NULL OR role IN (
        'SUPER_ADMIN', 'OPS_ADMIN', 'FIELD_ACTIVATOR',
        'VENDOR_OWNER', 'VENDOR_STAFF',
        'RETAILER_OWNER', 'RETAILER_STAFF', 'MANUFACTURER_ANALYST',
        'ADMIN_SUPER', 'OPS_AGENT'
    ));

COMMENT ON COLUMN users.role IS
'LEGACY / DEPRECATED. Not an authorization source. Runtime RBAC MUST use organization_memberships.role scoped by user_sessions.active_organization_id.';

-- ---------------------------------------------------------------------------
-- 4. Remove the legacy one-user-per-actor restriction (Section 14)
-- ---------------------------------------------------------------------------
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
-- 6. Allocation Plans: Reconcile Status CHECK Constraint (Include 'SUPERSEDED')
-- ---------------------------------------------------------------------------
ALTER TABLE allocation_plans
    DROP CONSTRAINT IF EXISTS allocation_plans_status_check;
ALTER TABLE allocation_plans
    DROP CONSTRAINT IF EXISTS chk_allocation_plans_status;

ALTER TABLE allocation_plans
    ADD CONSTRAINT chk_allocation_plans_status
    CHECK (status IN ('PREVIEW', 'OPTIMIZED', 'CONFIRMED', 'SUPERSEDED', 'REJECTED', 'EXPIRED'));

-- ---------------------------------------------------------------------------
-- 7. Consistency indexes
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_org_memberships_user_org_role
    ON organization_memberships (user_id, organization_id, role, status);

CREATE INDEX IF NOT EXISTS idx_retailers_organization
    ON retailers (organization_id);

CREATE INDEX IF NOT EXISTS idx_vendors_organization
    ON vendors (organization_id);

COMMIT;
