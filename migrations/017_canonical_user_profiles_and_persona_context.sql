-- ============================================================================
-- POL Migration 017
-- Canonical User Profile + Membership Persona Context
--
-- Design rule:
--   users = authentication identity / legacy display projection
--   user_profiles = universal user profile SSoT for human-facing identity/preferences
--   membership_profiles = tenant-specific persona context
--   role-specific membership tables = structured fields for the active persona
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    display_name VARCHAR(120) NOT NULL,
    avatar_media_asset_id UUID REFERENCES media_assets(id) ON DELETE SET NULL,
    email VARCHAR(254),
    preferred_language VARCHAR(10) NOT NULL DEFAULT 'fa-IR'
        CHECK (preferred_language IN ('fa-IR', 'en-US')),
    timezone VARCHAR(64) NOT NULL DEFAULT 'Asia/Tehran',
    bio VARCHAR(500),
    profile_status VARCHAR(24) NOT NULL DEFAULT 'ACTIVE'
        CHECK (profile_status IN ('ACTIVE', 'INCOMPLETE', 'SUSPENDED')),
    onboarding_completed_at TIMESTAMPTZ,
    last_seen_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_user_profiles_email_ci
    ON user_profiles (lower(email))
    WHERE email IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_user_profiles_status
    ON user_profiles(profile_status);

COMMENT ON TABLE user_profiles IS
'CANONICAL universal human profile. One profile is automatically materialized for every user.';

CREATE TABLE IF NOT EXISTS membership_profiles (
    membership_id UUID PRIMARY KEY REFERENCES organization_memberships(id) ON DELETE CASCADE,
    display_name_override VARCHAR(120),
    title VARCHAR(120),
    job_function VARCHAR(64),
    preferred_dashboard VARCHAR(64),
    default_contact_channel VARCHAR(16) NOT NULL DEFAULT 'IN_APP'
        CHECK (default_contact_channel IN ('IN_APP', 'PUSH', 'SMS')),
    locale_override VARCHAR(10),
    preferences JSONB NOT NULL DEFAULT '{}'::jsonb,
    onboarding_status VARCHAR(24) NOT NULL DEFAULT 'STARTED'
        CHECK (onboarding_status IN ('STARTED', 'PROFILE_IN_PROGRESS', 'READY', 'SUSPENDED')),
    onboarding_completed_at TIMESTAMPTZ,
    last_active_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_membership_profiles_dashboard
    ON membership_profiles(preferred_dashboard);

CREATE TABLE IF NOT EXISTS retailer_membership_profiles (
    membership_id UUID PRIMARY KEY REFERENCES membership_profiles(membership_id) ON DELETE CASCADE,
    store_role VARCHAR(24) NOT NULL DEFAULT 'STAFF'
        CHECK (store_role IN ('OWNER', 'MANAGER', 'BUYER', 'CASHIER', 'STAFF')),
    procurement_scope VARCHAR(32) NOT NULL DEFAULT 'FULL_CATALOG'
        CHECK (procurement_scope IN ('FULL_CATALOG', 'ASSIGNED_CATEGORIES', 'ASSIGNED_VENDORS')),
    preferred_order_channel VARCHAR(16) NOT NULL DEFAULT 'WEB'
        CHECK (preferred_order_channel IN ('WEB', 'ANDROID', 'ASSISTED')),
    default_reorder_window_days INTEGER NOT NULL DEFAULT 14
        CHECK (default_reorder_window_days BETWEEN 1 AND 365)
);

CREATE TABLE IF NOT EXISTS vendor_membership_profiles (
    membership_id UUID PRIMARY KEY REFERENCES membership_profiles(membership_id) ON DELETE CASCADE,
    job_function VARCHAR(24) NOT NULL DEFAULT 'OPERATIONS'
        CHECK (job_function IN ('OWNER', 'SALES', 'WAREHOUSE', 'OPERATIONS', 'FINANCE', 'STAFF')),
    can_manage_catalog BOOLEAN NOT NULL DEFAULT FALSE,
    can_manage_inventory BOOLEAN NOT NULL DEFAULT FALSE,
    can_manage_orders BOOLEAN NOT NULL DEFAULT FALSE,
    can_create_referrals BOOLEAN NOT NULL DEFAULT FALSE,
    approval_limit_toman BIGINT
);

CREATE TABLE IF NOT EXISTS operator_membership_profiles (
    membership_id UUID PRIMARY KEY REFERENCES membership_profiles(membership_id) ON DELETE CASCADE,
    job_function VARCHAR(24) NOT NULL DEFAULT 'OPS'
        CHECK (job_function IN ('ADMIN', 'OPS', 'SUPPORT', 'FINANCE', 'FIELD', 'ANALYTICS')),
    dashboard_scope VARCHAR(32) NOT NULL DEFAULT 'OPERATIONS'
        CHECK (dashboard_scope IN ('GLOBAL', 'OPERATIONS', 'SUPPORT', 'FINANCE', 'FIELD', 'ANALYTICS')),
    queue_scope JSONB NOT NULL DEFAULT '[]'::jsonb
);

CREATE TABLE IF NOT EXISTS field_activator_profiles (
    membership_id UUID PRIMARY KEY REFERENCES membership_profiles(membership_id) ON DELETE CASCADE,
    territory VARCHAR(120) NOT NULL DEFAULT 'Ahvaz',
    daily_activation_target INTEGER NOT NULL DEFAULT 5
        CHECK (daily_activation_target BETWEEN 0 AND 100),
    assisted_order_enabled BOOLEAN NOT NULL DEFAULT TRUE
);

-- ---------------------------------------------------------------------------
-- Automatic universal profile creation: every user gets a profile.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION pol_ensure_user_profile()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO user_profiles (user_id, display_name)
    VALUES (NEW.id, COALESCE(NULLIF(NEW.full_name, ''), 'POL User'))
    ON CONFLICT (user_id) DO NOTHING;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_ensure_user_profile ON users;
CREATE TRIGGER trg_ensure_user_profile
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION pol_ensure_user_profile();

-- Backfill existing users so the invariant holds for the current dataset.
INSERT INTO user_profiles (user_id, display_name)
SELECT u.id, COALESCE(NULLIF(u.full_name, ''), 'POL User')
FROM users u
ON CONFLICT (user_id) DO NOTHING;

-- ---------------------------------------------------------------------------
-- Automatic contextual membership profile creation.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION pol_ensure_membership_profile()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO membership_profiles (membership_id, preferred_dashboard, job_function)
    VALUES (
        NEW.id,
        CASE
            WHEN NEW.role IN ('RETAILER_OWNER','RETAILER_STAFF') THEN 'RETAILER_HOME'
            WHEN NEW.role IN ('VENDOR_OWNER','VENDOR_STAFF') THEN 'VENDOR_HOME'
            WHEN NEW.role IN ('FIELD_ACTIVATOR') THEN 'FIELD_HOME'
            ELSE 'OPS_HOME'
        END,
        CASE
            WHEN NEW.role = 'RETAILER_OWNER' THEN 'OWNER'
            WHEN NEW.role = 'RETAILER_STAFF' THEN 'STAFF'
            WHEN NEW.role = 'VENDOR_OWNER' THEN 'OWNER'
            WHEN NEW.role = 'VENDOR_STAFF' THEN 'OPERATIONS'
            WHEN NEW.role = 'FIELD_ACTIVATOR' THEN 'FIELD'
            ELSE 'OPS'
        END
    )
    ON CONFLICT (membership_id) DO NOTHING;

    IF NEW.role IN ('RETAILER_OWNER','RETAILER_STAFF') THEN
        INSERT INTO retailer_membership_profiles (membership_id, store_role)
        VALUES (
            NEW.id,
            CASE WHEN NEW.role = 'RETAILER_OWNER' THEN 'OWNER' ELSE 'STAFF' END
        )
        ON CONFLICT (membership_id) DO NOTHING;
    ELSIF NEW.role IN ('VENDOR_OWNER','VENDOR_STAFF') THEN
        INSERT INTO vendor_membership_profiles (
            membership_id,
            job_function,
            can_manage_catalog,
            can_manage_inventory,
            can_manage_orders,
            can_create_referrals
        )
        VALUES (
            NEW.id,
            CASE WHEN NEW.role = 'VENDOR_OWNER' THEN 'OWNER' ELSE 'OPERATIONS' END,
            NEW.role = 'VENDOR_OWNER',
            NEW.role = 'VENDOR_OWNER',
            TRUE,
            NEW.role = 'VENDOR_OWNER'
        )
        ON CONFLICT (membership_id) DO NOTHING;
    ELSIF NEW.role = 'FIELD_ACTIVATOR' THEN
        INSERT INTO field_activator_profiles (membership_id)
        VALUES (NEW.id)
        ON CONFLICT (membership_id) DO NOTHING;
    ELSE
        INSERT INTO operator_membership_profiles (membership_id)
        VALUES (NEW.id)
        ON CONFLICT (membership_id) DO NOTHING;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_ensure_membership_profile ON organization_memberships;
CREATE TRIGGER trg_ensure_membership_profile
AFTER INSERT OR UPDATE OF role
ON organization_memberships
FOR EACH ROW
EXECUTE FUNCTION pol_ensure_membership_profile();

-- Backfill contextual profile rows for the existing membership population.
INSERT INTO membership_profiles (membership_id, preferred_dashboard, job_function)
SELECT m.id,
       CASE
           WHEN m.role IN ('RETAILER_OWNER','RETAILER_STAFF') THEN 'RETAILER_HOME'
           WHEN m.role IN ('VENDOR_OWNER','VENDOR_STAFF') THEN 'VENDOR_HOME'
           WHEN m.role = 'FIELD_ACTIVATOR' THEN 'FIELD_HOME'
           ELSE 'OPS_HOME'
       END,
       CASE
           WHEN m.role = 'RETAILER_OWNER' THEN 'OWNER'
           WHEN m.role = 'RETAILER_STAFF' THEN 'STAFF'
           WHEN m.role = 'VENDOR_OWNER' THEN 'OWNER'
           WHEN m.role = 'VENDOR_STAFF' THEN 'OPERATIONS'
           WHEN m.role = 'FIELD_ACTIVATOR' THEN 'FIELD'
           ELSE 'OPS'
       END
FROM organization_memberships m
ON CONFLICT (membership_id) DO NOTHING;

INSERT INTO retailer_membership_profiles (membership_id, store_role)
SELECT m.id, CASE WHEN m.role = 'RETAILER_OWNER' THEN 'OWNER' ELSE 'STAFF' END
FROM organization_memberships m
WHERE m.role IN ('RETAILER_OWNER','RETAILER_STAFF')
ON CONFLICT (membership_id) DO NOTHING;

INSERT INTO vendor_membership_profiles (
    membership_id, job_function, can_manage_catalog, can_manage_inventory,
    can_manage_orders, can_create_referrals
)
SELECT m.id,
       CASE WHEN m.role = 'VENDOR_OWNER' THEN 'OWNER' ELSE 'OPERATIONS' END,
       m.role = 'VENDOR_OWNER',
       m.role = 'VENDOR_OWNER',
       TRUE,
       m.role = 'VENDOR_OWNER'
FROM organization_memberships m
WHERE m.role IN ('VENDOR_OWNER','VENDOR_STAFF')
ON CONFLICT (membership_id) DO NOTHING;

INSERT INTO field_activator_profiles (membership_id)
SELECT id FROM organization_memberships
WHERE role = 'FIELD_ACTIVATOR'
ON CONFLICT (membership_id) DO NOTHING;

INSERT INTO operator_membership_profiles (membership_id)
SELECT id FROM organization_memberships
WHERE role IN ('OPS_AGENT','ADMIN_SUPER','SUPER_ADMIN','OPS_ADMIN')
ON CONFLICT (membership_id) DO NOTHING;

-- Guardrails: profile cardinality must match identity cardinality.
CREATE OR REPLACE FUNCTION pol_validate_profile_cardinality()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF (SELECT COUNT(*) FROM user_profiles WHERE user_id = NEW.user_id) <> 1 THEN
        RAISE EXCEPTION 'Every user must have exactly one canonical profile: %', NEW.user_id;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_profile_cardinality ON organization_memberships;
CREATE TRIGGER trg_validate_profile_cardinality
AFTER INSERT OR UPDATE OF user_id
ON organization_memberships
FOR EACH ROW
EXECUTE FUNCTION pol_validate_profile_cardinality();
