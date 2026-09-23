-- ============================================================================
-- POL Migration 021
-- Cross-entity integrity guards discovered during the 2026-09-16 repository audit.
-- ============================================================================

-- 1. A session's active tenant must belong to the session user and remain active.
CREATE OR REPLACE FUNCTION pol_validate_session_context()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.active_organization_id IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1
            FROM organization_memberships m
            JOIN organizations o ON o.id = m.organization_id
            WHERE m.user_id = NEW.user_id
              AND m.organization_id = NEW.active_organization_id
              AND m.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
        ) THEN
            RAISE EXCEPTION 'Session active organization is not an active membership of the session user: %', NEW.active_organization_id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_session_context ON user_sessions;
CREATE TRIGGER trg_validate_session_context
BEFORE INSERT OR UPDATE OF user_id, active_organization_id
ON user_sessions
FOR EACH ROW
EXECUTE FUNCTION pol_validate_session_context();

-- 2. Allocation plans and baskets are a single aggregate boundary. A checkout
--    must never combine a plan belonging to one basket with another basket.
CREATE OR REPLACE FUNCTION pol_validate_order_group_allocation_context()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    plan_basket UUID;
    basket_retailer UUID;
BEGIN
    IF NEW.allocation_plan_id IS NOT NULL THEN
        SELECT p.basket_id
        INTO plan_basket
        FROM allocation_plans p
        WHERE p.id = NEW.allocation_plan_id;

        IF plan_basket IS NULL THEN
            RAISE EXCEPTION 'Allocation plan does not exist: %', NEW.allocation_plan_id;
        END IF;

        IF NEW.basket_id IS NULL OR plan_basket <> NEW.basket_id THEN
            RAISE EXCEPTION 'Order group basket does not match allocation plan basket.';
        END IF;
    END IF;

    IF NEW.basket_id IS NOT NULL THEN
        SELECT b.retailer_id
        INTO basket_retailer
        FROM baskets b
        WHERE b.id = NEW.basket_id;

        IF basket_retailer IS NULL THEN
            RAISE EXCEPTION 'Order group basket does not exist: %', NEW.basket_id;
        END IF;

        IF NEW.retailer_id <> basket_retailer THEN
            RAISE EXCEPTION 'Order group retailer does not match basket retailer.';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_order_group_allocation_context ON order_groups;
CREATE TRIGGER trg_validate_order_group_allocation_context
BEFORE INSERT OR UPDATE OF basket_id, allocation_plan_id, retailer_id
ON order_groups
FOR EACH ROW
EXECUTE FUNCTION pol_validate_order_group_allocation_context();

-- 3. Child orders must remain inside the vendor/retailer relationship selected
--    by their parent group. This prevents forged cross-tenant child orders.
CREATE OR REPLACE FUNCTION pol_validate_child_order_context()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    group_retailer UUID;
BEGIN
    SELECT og.retailer_id
    INTO group_retailer
    FROM order_groups og
    WHERE og.id = NEW.order_group_id;

    IF group_retailer IS NULL THEN
        RAISE EXCEPTION 'Order group does not exist: %', NEW.order_group_id;
    END IF;

    IF NEW.retailer_id <> group_retailer THEN
        RAISE EXCEPTION 'Child order retailer does not match order group retailer.';
    END IF;

    IF NOT EXISTS (
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
