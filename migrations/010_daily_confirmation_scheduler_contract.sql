-- ============================================================================
-- POL Migration 010
-- Daily inventory scheduler contract
-- ============================================================================

-- Every queued reminder must have a durable daily confirmation row. This makes
-- the later MISSED/STALE transition deterministic even when a vendor has never
-- opened the inventory screen.
CREATE OR REPLACE FUNCTION pol_ensure_daily_inventory_confirmation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    reminder_date DATE;
BEGIN
    IF NEW.event_name = 'DAILY_INVENTORY_REMINDER'
       AND NEW.aggregate_type = 'VENDOR_INVENTORY'
       AND NEW.aggregate_id IS NOT NULL THEN
        reminder_date := NULLIF(NEW.payload ->> 'confirmation_date', '')::DATE;
        IF reminder_date IS NULL THEN
            RAISE EXCEPTION 'Daily inventory reminder requires confirmation_date in payload: %', NEW.event_id;
        END IF;

        INSERT INTO daily_inventory_confirmations(vendor_id, confirmation_date, status)
        VALUES (NEW.aggregate_id::UUID, reminder_date, 'PENDING')
        ON CONFLICT (vendor_id, confirmation_date) DO NOTHING;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_ensure_daily_inventory_confirmation ON outbox_events;
CREATE TRIGGER trg_ensure_daily_inventory_confirmation
AFTER INSERT ON outbox_events
FOR EACH ROW
EXECUTE FUNCTION pol_ensure_daily_inventory_confirmation();
