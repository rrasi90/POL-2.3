-- ============================================================================
-- POL Migration 051
-- Deep-audit remediation: G-314
-- Notification inbox retention is materialized at write time and existing
-- rows with missing expiry are backfilled from the canonical category policy.
-- ============================================================================

UPDATE user_inbox_items
SET expires_at = created_at + CASE
    WHEN category = 'PROMOTIONS' THEN interval '30 days'
    ELSE interval '90 days'
END
WHERE expires_at IS NULL;

CREATE OR REPLACE FUNCTION set_user_inbox_expiry()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.expires_at IS NULL THEN
        NEW.expires_at := NEW.created_at + CASE
            WHEN NEW.category = 'PROMOTIONS' THEN interval '30 days'
            ELSE interval '90 days'
        END;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_user_inbox_items_retention ON user_inbox_items;

CREATE TRIGGER trg_user_inbox_items_retention
BEFORE INSERT ON user_inbox_items
FOR EACH ROW
EXECUTE FUNCTION set_user_inbox_expiry();
