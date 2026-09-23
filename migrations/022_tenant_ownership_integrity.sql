-- ============================================================================
-- POL Migration 022
-- Database-level tenant ownership guards for client-facing records.
-- ============================================================================

CREATE OR REPLACE FUNCTION pol_validate_support_case_tenant()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM organization_memberships m
        JOIN organizations o ON o.id = m.organization_id
        WHERE m.user_id = NEW.user_id
          AND m.organization_id = NEW.organization_id
          AND m.status = 'ACTIVE'
          AND o.status = 'ACTIVE'
    ) THEN
        RAISE EXCEPTION 'Support case actor is not an active member of the target tenant.';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_support_case_tenant ON support_cases;
CREATE TRIGGER trg_validate_support_case_tenant
BEFORE INSERT OR UPDATE OF user_id, organization_id
ON support_cases
FOR EACH ROW
EXECUTE FUNCTION pol_validate_support_case_tenant();

CREATE OR REPLACE FUNCTION pol_validate_feedback_tenant()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.organization_id IS NOT NULL AND NOT EXISTS (
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
