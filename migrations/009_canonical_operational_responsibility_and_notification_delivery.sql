-- ============================================================================
-- POL Migration 009
-- Canonical operational responsibility + notification delivery boundary
-- ============================================================================

-- 1. Canonical warehouse/inventory responsibility.
-- vendors.user_id is legacy and must not determine who receives daily inventory
-- confirmation requests.
CREATE TABLE IF NOT EXISTS vendor_inventory_responsibilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    responsibility_type VARCHAR(32) NOT NULL DEFAULT 'WAREHOUSE_INVENTORY'
        CHECK (responsibility_type IN ('WAREHOUSE_INVENTORY', 'OPERATIONS', 'OWNER_BACKUP')),
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    effective_from TIMESTAMPTZ NOT NULL DEFAULT now(),
    effective_until TIMESTAMPTZ,
    source VARCHAR(32) NOT NULL DEFAULT 'ADMIN'
        CHECK (source IN ('ADMIN', 'VENDOR_ADMIN', 'ONBOARDING', 'IMPORT')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_inventory_responsibility_effective
        CHECK (effective_until IS NULL OR effective_until > effective_from),
    CONSTRAINT uq_vendor_inventory_responsibility_user
        UNIQUE (vendor_id, user_id, responsibility_type)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_vendor_primary_inventory_responsible
    ON vendor_inventory_responsibilities(vendor_id)
    WHERE responsibility_type = 'WAREHOUSE_INVENTORY'
      AND is_primary = TRUE
      AND effective_until IS NULL;

CREATE INDEX IF NOT EXISTS idx_vendor_inventory_responsibility_active
    ON vendor_inventory_responsibilities(vendor_id, responsibility_type, is_primary, effective_from DESC);

-- 2. Backfill only where the legacy vendor owner is a real active membership.
-- This provides a safe migration bridge without making vendors.user_id the SSoT.
INSERT INTO vendor_inventory_responsibilities (
    vendor_id, user_id, responsibility_type, is_primary, source
)
SELECT v.id, v.user_id, 'WAREHOUSE_INVENTORY', TRUE, 'IMPORT'
FROM vendors v
JOIN organizations o ON o.id = v.organization_id AND o.org_type = 'VENDOR'
JOIN organization_memberships m
  ON m.organization_id = v.organization_id
 AND m.user_id = v.user_id
 AND m.status = 'ACTIVE'
 AND m.role IN ('VENDOR_OWNER', 'VENDOR_STAFF')
WHERE v.user_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1
      FROM vendor_inventory_responsibilities r
      WHERE r.vendor_id = v.id
        AND r.responsibility_type = 'WAREHOUSE_INVENTORY'
        AND r.is_primary = TRUE
        AND r.effective_until IS NULL
  );

-- 3. Rewrite daily-reminder routing around the canonical responsibility.
CREATE OR REPLACE FUNCTION pol_enrich_daily_inventory_outbox()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    responsible_user UUID;
    responsible_org UUID;
BEGIN
    IF NEW.event_name = 'DAILY_INVENTORY_REMINDER'
       AND NEW.aggregate_type = 'VENDOR_INVENTORY'
       AND NEW.aggregate_id IS NOT NULL THEN
        SELECT r.user_id, v.organization_id
        INTO responsible_user, responsible_org
        FROM vendor_inventory_responsibilities r
        JOIN vendors v ON v.id = r.vendor_id
        JOIN organization_memberships m
          ON m.organization_id = v.organization_id
         AND m.user_id = r.user_id
         AND m.status = 'ACTIVE'
        WHERE r.vendor_id::text = NEW.aggregate_id
          AND r.responsibility_type = 'WAREHOUSE_INVENTORY'
          AND r.is_primary = TRUE
          AND r.effective_from <= now()
          AND (r.effective_until IS NULL OR r.effective_until > now())
        ORDER BY r.effective_from DESC
        LIMIT 1;

        IF responsible_user IS NULL OR responsible_org IS NULL THEN
            RAISE EXCEPTION 'Daily inventory reminder requires an active primary warehouse-inventory responsibility: %', NEW.aggregate_id;
        END IF;

        NEW.target_user_id := COALESCE(NEW.target_user_id, responsible_user);
        NEW.target_organization_id := COALESCE(NEW.target_organization_id, responsible_org);
        NEW.channel_hint := COALESCE(NEW.channel_hint, 'PUSH');
        NEW.dedupe_key := COALESCE(NEW.dedupe_key, NEW.event_id);
    END IF;
    RETURN NEW;
END;
$$;

-- 4. Eliminate recursive notification -> outbox -> notification loops.
-- Domain events remain outbox-driven. A logical notification creates physical
-- delivery records directly; provider workers consume notification_deliveries.
DROP TRIGGER IF EXISTS trg_notification_enqueue_delivery ON notifications;
DROP FUNCTION IF EXISTS pol_enqueue_notification_delivery();

CREATE OR REPLACE FUNCTION pol_seed_notification_delivery()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO notification_deliveries (
        id, notification_id, channel, status, attempt_count, scheduled_at, created_at, updated_at
    ) VALUES (
        gen_random_uuid(), NEW.id, 'INBOX', 'PENDING', 0, now(), now(), now()
    )
    ON CONFLICT (notification_id, channel) DO NOTHING;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_notification_seed_delivery ON notifications;
CREATE TRIGGER trg_notification_seed_delivery
AFTER INSERT ON notifications
FOR EACH ROW
EXECUTE FUNCTION pol_seed_notification_delivery();

-- 5. Ensure delivery channel uniqueness exists before application workers rely on it.
CREATE UNIQUE INDEX IF NOT EXISTS uq_notification_delivery_channel_v2
    ON notification_deliveries(notification_id, channel);
