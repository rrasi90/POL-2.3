-- ============================================================================
-- POL Migration 052
-- Deep-audit remediation: G-315
-- Privacy export / account-deletion request lifecycle.
-- ============================================================================

CREATE TABLE IF NOT EXISTS privacy_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    request_type VARCHAR(16) NOT NULL CHECK (request_type IN ('EXPORT', 'DELETION')),
    status VARCHAR(24) NOT NULL DEFAULT 'REQUESTED'
        CHECK (status IN ('REQUESTED', 'PROCESSING', 'COMPLETED', 'REJECTED', 'CANCELLED')),
    requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    export_sha256 VARCHAR(64),
    result_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    error_code VARCHAR(64),
    CONSTRAINT chk_privacy_request_completion
        CHECK (
            (status = 'COMPLETED' AND completed_at IS NOT NULL)
            OR status <> 'COMPLETED'
        )
);

CREATE INDEX IF NOT EXISTS idx_privacy_requests_user
    ON privacy_requests(user_id, requested_at DESC);

CREATE UNIQUE INDEX IF NOT EXISTS uq_privacy_active_deletion
    ON privacy_requests(user_id)
    WHERE request_type = 'DELETION'
      AND status IN ('REQUESTED', 'PROCESSING');

COMMENT ON TABLE privacy_requests IS
'Canonical privacy request lifecycle. Export content is returned to the authenticated requester and only its SHA-256 is persisted; deletion de-identifies direct PII while preserving auditable/financial history.';
