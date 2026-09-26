-- ============================================================================
-- POL Migration 056
-- Deep-audit remediation: G-341
-- Reservation idempotency must be database-enforced.
-- ============================================================================

CREATE UNIQUE INDEX IF NOT EXISTS uq_inventory_reservations_idempotency
    ON inventory_reservations(idempotency_key)
    WHERE idempotency_key IS NOT NULL;

COMMENT ON INDEX uq_inventory_reservations_idempotency IS
'Canonical reservation idempotency key; exact replay is resolved by the reservation service, conflicting reuse is rejected.';
