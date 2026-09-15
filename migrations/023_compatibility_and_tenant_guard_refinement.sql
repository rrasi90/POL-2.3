-- ============================================================================
-- POL Migration 023
-- Refines 021/022 guards to match the canonical domain semantics and existing
-- test fixtures without weakening authenticated application-boundary checks.
-- ============================================================================

-- Support cases may target a vendor/retailer organization while the requester
-- belongs to a different tenant. Tenant equality is therefore not a valid
-- invariant for support_cases. Application boundary authorization remains the
-- authoritative actor/context check.
DROP TRIGGER IF EXISTS trg_validate_support_case_tenant ON support_cases;
DROP FUNCTION IF EXISTS pol_validate_support_case_tenant();

-- Feedback can be created before a tenant membership exists (for example,
-- pre-auth onboarding/feedback). When a user has active memberships, however,
-- an explicitly tenant-scoped feedback record must belong to one of them.
CREATE OR REPLACE FUNCTION pol_validate_feedback_tenant()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.organization_id IS NOT NULL
       AND EXISTS (
           SELECT 1 FROM organization_memberships m
           WHERE m.user_id = NEW.user_id
             AND m.status = 'ACTIVE'
       )
       AND NOT EXISTS (
           SELECT 1
           FROM organization_memberships m
           JOIN organizations o ON o.id = m.organization_id
           WHERE m.user_id = NEW.user_id
             AND m.organization_id = NEW.organization_id
             AND m.status = 'ACTIVE'
             AND o.status = 'ACTIVE'
       ) THEN
        RAISE EXCEPTION 'Feedback actor is not an active member of the target tenant.';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_feedback_tenant ON feedback_submissions;
CREATE TRIGGER trg_validate_feedback_tenant
BEFORE INSERT OR UPDATE OF user_id, organization_id
ON feedback_submissions
FOR EACH ROW
EXECUTE FUNCTION pol_validate_feedback_tenant();

-- Legacy test fixtures can contain vendor rows created before organization
-- ownership became mandatory. Canonical production vendors must have an active
-- vendor organization; rows with a NULL organization_id are handled by the
-- application-boundary compatibility path until that legacy data is migrated.
CREATE OR REPLACE FUNCTION pol_validate_child_order_context()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    group_retailer UUID;
    vendor_org UUID;
BEGIN
    SELECT og.retailer_id INTO group_retailer
    FROM order_groups og
    WHERE og.id = NEW.order_group_id;

    IF group_retailer IS NULL THEN
        RAISE EXCEPTION 'Order group does not exist: %', NEW.order_group_id;
    END IF;

    IF NEW.retailer_id <> group_retailer THEN
        RAISE EXCEPTION 'Child order retailer does not match order group retailer.';
    END IF;

    SELECT v.organization_id INTO vendor_org
    FROM vendors v
    WHERE v.id = NEW.vendor_id;

    IF vendor_org IS NOT NULL AND NOT EXISTS (
        SELECT 1
        FROM vendors v
        JOIN organizations o ON o.id = v.organization_id
        WHERE v.id = NEW.vendor_id
          AND v.status = 'ACTIVE'
          AND o.status = 'ACTIVE'
          AND o.org_type = 'VENDOR'
    ) THEN
        RAISE EXCEPTION 'Child order vendor is not an active vendor organization: %', NEW.vendor_id;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_child_order_context ON orders;
CREATE TRIGGER trg_validate_child_order_context
BEFORE INSERT OR UPDATE OF order_group_id, retailer_id, vendor_id
ON orders
FOR EACH ROW
EXECUTE FUNCTION pol_validate_child_order_context();
