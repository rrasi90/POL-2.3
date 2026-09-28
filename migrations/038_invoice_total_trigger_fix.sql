-- ============================================================================
-- 038_invoice_total_trigger_fix.sql
-- ============================================================================

CREATE OR REPLACE FUNCTION pol_validate_invoice_total_v037()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_invoice_id UUID;
    v_expected BIGINT;
    v_actual BIGINT;
BEGIN
    IF TG_TABLE_NAME = 'invoices' THEN
        v_invoice_id := COALESCE(NEW.id, OLD.id);
    ELSIF TG_TABLE_NAME = 'invoice_items' THEN
        v_invoice_id := COALESCE(NEW.invoice_id, OLD.invoice_id);
    ELSE
        RAISE EXCEPTION 'INVOICE_TOTAL_TRIGGER_TABLE_UNSUPPORTED'
            USING ERRCODE='23514';
    END IF;

    SELECT total_amount INTO v_actual
    FROM invoices WHERE id=v_invoice_id;

    IF v_actual IS NULL THEN
        RETURN COALESCE(NEW, OLD);
    END IF;

    SELECT COALESCE(SUM(total_line_amount),0)
      INTO v_expected
      FROM invoice_items
     WHERE invoice_id=v_invoice_id;

    IF v_actual <> v_expected THEN
        RAISE EXCEPTION 'INVOICE_TOTAL_MISMATCH: invoice=% stored=% calculated=%',
            v_invoice_id, v_actual, v_expected
            USING ERRCODE='23514';
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$;
