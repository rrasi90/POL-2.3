-- ============================================================================
-- 037_invoice_financial_invariants.sql
-- ============================================================================

CREATE OR REPLACE FUNCTION pol_validate_invoice_item_v037()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_invoice_order UUID;
    v_item_order UUID;
BEGIN
    IF NEW.total_line_amount <> NEW.quantity * NEW.unit_price THEN
        RAISE EXCEPTION 'INVOICE_LINE_TOTAL_MISMATCH'
            USING ERRCODE='23514';
    END IF;

    IF NEW.order_item_id IS NOT NULL THEN
        SELECT order_id INTO v_invoice_order
        FROM invoices WHERE id=NEW.invoice_id;

        SELECT order_id INTO v_item_order
        FROM order_items WHERE id=NEW.order_item_id;

        IF v_item_order IS NULL OR v_invoice_order IS NULL OR v_item_order <> v_invoice_order THEN
            RAISE EXCEPTION 'INVOICE_ORDER_ITEM_MISMATCH'
                USING ERRCODE='23514';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_invoice_item_v037 ON invoice_items;
CREATE CONSTRAINT TRIGGER trg_validate_invoice_item_v037
AFTER INSERT OR UPDATE OF invoice_id, order_item_id, quantity, unit_price, total_line_amount
ON invoice_items
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION pol_validate_invoice_item_v037();

CREATE OR REPLACE FUNCTION pol_validate_invoice_total_v037()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_invoice_id UUID;
    v_expected BIGINT;
    v_actual BIGINT;
BEGIN
    v_invoice_id := COALESCE(NEW.invoice_id, OLD.invoice_id);

    SELECT total_amount INTO v_actual
    FROM invoices WHERE id=v_invoice_id;

    IF v_actual IS NULL THEN
        IF TG_OP = 'DELETE' THEN
            RETURN OLD;
        END IF;
        RETURN NEW;
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

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_invoice_items_total_v037 ON invoice_items;
CREATE CONSTRAINT TRIGGER trg_invoice_items_total_v037
AFTER INSERT OR UPDATE OR DELETE ON invoice_items
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION pol_validate_invoice_total_v037();

DROP TRIGGER IF EXISTS trg_invoice_total_v037 ON invoices;
CREATE CONSTRAINT TRIGGER trg_invoice_total_v037
AFTER INSERT OR UPDATE OF total_amount ON invoices
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION pol_validate_invoice_total_v037();

CREATE INDEX IF NOT EXISTS idx_invoice_items_order_item_v037
    ON invoice_items(order_item_id)
    WHERE order_item_id IS NOT NULL;
