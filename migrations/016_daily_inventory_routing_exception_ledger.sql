-- ============================================================================
-- POL Migration 016
-- Daily inventory routing exceptions are first-class operational events.
-- ============================================================================

ALTER TABLE vendor_reliability_events
    DROP CONSTRAINT IF EXISTS vendor_reliability_events_event_type_check;

ALTER TABLE vendor_reliability_events
    ADD CONSTRAINT vendor_reliability_events_event_type_check CHECK (event_type IN (
        'ORDER_ACCEPTED', 'ORDER_REJECTED', 'ACCEPTANCE_LATE',
        'PREPARATION_LATE', 'DISPATCH_LATE', 'DELIVERY_LATE',
        'STOCKOUT_AFTER_CONFIRMATION', 'WRONG_ITEM', 'SHORTAGE', 'DAMAGE',
        'PRICE_CHANGED_AFTER_QUOTE', 'PAYMENT_CONFIRMATION_LATE',
        'DISPUTE_OPENED', 'DISPUTE_CONFIRMED',
        'DAILY_CONFIRMATION_COMPLETED', 'DAILY_CONFIRMATION_MISSED',
        'DAILY_CONFIRMATION_ROUTING_ERROR'
    ));
