-- 046: pending barcode candidate concurrency guard
-- Prevents two concurrent barcode-only submissions for one vendor from
-- creating competing PENDING_REVIEW candidates.

CREATE UNIQUE INDEX IF NOT EXISTS uq_product_candidates_pending_vendor_barcode
    ON product_candidates (vendor_id, barcode)
    WHERE barcode IS NOT NULL
      AND status = 'PENDING_REVIEW';
