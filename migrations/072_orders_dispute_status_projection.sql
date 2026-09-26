-- 072: Align the orders.dispute_status projection vocabulary with the
-- canonical dispute lifecycle (G-431/G-433).
--
-- The projection previously carried the legacy vocabulary (NONE, OPEN,
-- UNDER_REVIEW, RESOLVED_ADJUSTED, RESOLVED_REJECTED, CLOSED). The canonical
-- dispute chain (OPEN -> INVESTIGATING -> RESOLVED -> CLOSED) projects
-- INVESTIGATING and RESOLVED onto the order. Legacy values are retained so
-- historical rows remain valid.

ALTER TABLE orders
    DROP CONSTRAINT IF EXISTS orders_dispute_status_check;

ALTER TABLE orders
    ADD CONSTRAINT orders_dispute_status_check
    CHECK (
        dispute_status IN (
            'NONE', 'OPEN', 'INVESTIGATING', 'RESOLVED', 'CLOSED',
            'UNDER_REVIEW', 'RESOLVED_ADJUSTED', 'RESOLVED_REJECTED'
        )
    );
