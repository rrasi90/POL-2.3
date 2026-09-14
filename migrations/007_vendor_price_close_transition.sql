-- ============================================================================
-- POL Vendor Price Close Transition
-- Migration 007
-- Preserve the unique-current invariant while making explicit price retirement
-- update the temporal validity window automatically.
-- ============================================================================

DROP TRIGGER IF EXISTS trg_rotate_vendor_price_version ON vendor_prices;

CREATE OR REPLACE FUNCTION pol_close_vendor_price_version()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    close_at TIMESTAMPTZ;
BEGIN
    IF OLD.is_current = TRUE AND NEW.is_current = FALSE THEN
        close_at := COALESCE(NEW.effective_until, NEW.effective_to, now());
        IF close_at <= OLD.effective_from THEN
            RAISE EXCEPTION
                'Vendor price effective_until must be later than effective_from for price %',
                OLD.id;
        END IF;
        NEW.effective_until := close_at;
        NEW.effective_to := close_at;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_close_vendor_price_version ON vendor_prices;
CREATE TRIGGER trg_close_vendor_price_version
BEFORE UPDATE OF is_current, effective_until, effective_to ON vendor_prices
FOR EACH ROW
EXECUTE FUNCTION pol_close_vendor_price_version();
