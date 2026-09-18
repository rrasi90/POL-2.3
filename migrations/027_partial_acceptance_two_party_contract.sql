-- 027_partial_acceptance_two_party_contract.sql
-- Batch 6C-6: two-party partial-acceptance contract.
-- The vendor proposes a shortage; the retailer explicitly approves or declines.
-- The order remains SUBMITTED until retailer approval.

ALTER TABLE inventory_reservations
    ADD COLUMN IF NOT EXISTS consumed_quantity INT;

UPDATE inventory_reservations
SET consumed_quantity = quantity
WHERE status = 'CONSUMED'
  AND consumed_quantity IS NULL;

ALTER TABLE inventory_reservations
    ADD CONSTRAINT chk_inventory_reservations_consumed_quantity
    CHECK (
        consumed_quantity IS NULL
        OR (consumed_quantity >= 0 AND consumed_quantity <= quantity)
    );

CREATE TABLE IF NOT EXISTS order_partial_acceptance_proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    vendor_id UUID NOT NULL REFERENCES vendors(id),
    retailer_id UUID NOT NULL REFERENCES retailers(id),
    proposed_by_user_id UUID NOT NULL REFERENCES users(id),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'ACCEPTED', 'DECLINED')),
    idempotency_key VARCHAR(128) NOT NULL,
    request_fingerprint VARCHAR(64) NOT NULL,
    decision_by_user_id UUID REFERENCES users(id),
    decision_reason TEXT,
    decided_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_partial_acceptance_proposal_idempotency
        UNIQUE (order_id, idempotency_key)
);

CREATE TABLE IF NOT EXISTS order_partial_acceptance_proposal_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id UUID NOT NULL
        REFERENCES order_partial_acceptance_proposals(id) ON DELETE CASCADE,
    order_item_id UUID NOT NULL REFERENCES order_items(id) ON DELETE CASCADE,
    accepted_quantity INT NOT NULL CHECK (accepted_quantity >= 0),
    reason VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_partial_acceptance_proposal_item
        UNIQUE (proposal_id, order_item_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_partial_acceptance_one_pending_order
    ON order_partial_acceptance_proposals(order_id)
    WHERE status = 'PENDING';

CREATE INDEX IF NOT EXISTS idx_partial_acceptance_proposals_order
    ON order_partial_acceptance_proposals(order_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_partial_acceptance_proposals_status
    ON order_partial_acceptance_proposals(status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_partial_acceptance_proposal_items_proposal
    ON order_partial_acceptance_proposal_items(proposal_id);

CREATE INDEX IF NOT EXISTS idx_partial_acceptance_proposal_items_order_item
    ON order_partial_acceptance_proposal_items(order_item_id);
