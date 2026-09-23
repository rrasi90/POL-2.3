-- ============================================================================
-- POL Temporal Price Transition
-- Migration 006
-- Ensures inserting a new current/effective price closes the previous current
-- version atomically before PostgreSQL exclusion/unique constraints evaluate.
-- ============================================================================

CREATE OR REPLACE FUNCTION pol_rotate_vendor_price_version()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.effective_from IS NULL THEN
        NEW.effective_from := now();
    END IF;

    IF NEW.is_current = TRUE THEN
        IF EXISTS (
            SELECT 1
            FROM vendor_prices vp
            WHERE vp.vendor_product_id = NEW.vendor_product_id
              AND vp.effective_from >= NEW.effective_from
              AND vp.id <> NEW.id
        ) THEN
            RAISE EXCEPTION
                'New vendor price effective_from must be later than existing price versions for vendor_product_id %',
                NEW.vendor_product_id;
        END IF;

        UPDATE vendor_prices
        SET is_current = FALSE,
            effective_until = NEW.effective_from,
            effective_to = NEW.effective_from
        WHERE vendor_product_id = NEW.vendor_product_id
          AND is_current = TRUE
          AND id <> NEW.id
          AND effective_from < NEW.effective_from;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_rotate_vendor_price_version ON vendor_prices;
CREATE TRIGGER trg_rotate_vendor_price_version
BEFORE INSERT ON vendor_prices
FOR EACH ROW
EXECUTE FUNCTION pol_rotate_vendor_price_version();

-- PostgreSQL NULL semantics otherwise allow multiple active rows for a
-- user-level consent when organization_id is NULL.
DROP INDEX IF EXISTS uq_active_consent;
CREATE UNIQUE INDEX IF NOT EXISTS uq_active_consent
    ON data_consents (
        user_id,
        COALESCE(organization_id, '00000000-0000-0000-0000-000000000000'::uuid),
        consent_type
    )
    WHERE status = 'GRANTED';
