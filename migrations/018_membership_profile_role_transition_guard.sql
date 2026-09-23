-- ============================================================================
-- POL Migration 018
-- Ensure a membership changing role cannot retain stale persona subprofiles.
-- ============================================================================

CREATE OR REPLACE FUNCTION pol_ensure_membership_profile()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND OLD.role IS DISTINCT FROM NEW.role THEN
        DELETE FROM retailer_membership_profiles WHERE membership_id = NEW.id;
        DELETE FROM vendor_membership_profiles WHERE membership_id = NEW.id;
        DELETE FROM field_activator_profiles WHERE membership_id = NEW.id;
        DELETE FROM operator_membership_profiles WHERE membership_id = NEW.id;
    END IF;

    INSERT INTO membership_profiles (membership_id, preferred_dashboard, job_function)
    VALUES (
        NEW.id,
        CASE
            WHEN NEW.role IN ('RETAILER_OWNER','RETAILER_STAFF') THEN 'RETAILER_HOME'
            WHEN NEW.role IN ('VENDOR_OWNER','VENDOR_STAFF') THEN 'VENDOR_HOME'
            WHEN NEW.role = 'FIELD_ACTIVATOR' THEN 'FIELD_HOME'
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
    ON CONFLICT (membership_id) DO UPDATE
    SET preferred_dashboard = EXCLUDED.preferred_dashboard,
        job_function = EXCLUDED.job_function,
        updated_at = now();

    IF NEW.role IN ('RETAILER_OWNER','RETAILER_STAFF') THEN
        INSERT INTO retailer_membership_profiles (membership_id, store_role)
        VALUES (NEW.id, CASE WHEN NEW.role = 'RETAILER_OWNER' THEN 'OWNER' ELSE 'STAFF' END)
        ON CONFLICT (membership_id) DO NOTHING;
    ELSIF NEW.role IN ('VENDOR_OWNER','VENDOR_STAFF') THEN
        INSERT INTO vendor_membership_profiles (
            membership_id, job_function, can_manage_catalog,
            can_manage_inventory, can_manage_orders, can_create_referrals
        )
        VALUES (
            NEW.id,
            CASE WHEN NEW.role = 'VENDOR_OWNER' THEN 'OWNER' ELSE 'OPERATIONS' END,
            NEW.role = 'VENDOR_OWNER', NEW.role = 'VENDOR_OWNER',
            TRUE, NEW.role = 'VENDOR_OWNER'
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

-- Re-seed existing memberships defensively.
UPDATE membership_profiles mp
SET preferred_dashboard = CASE
        WHEN m.role IN ('RETAILER_OWNER','RETAILER_STAFF') THEN 'RETAILER_HOME'
        WHEN m.role IN ('VENDOR_OWNER','VENDOR_STAFF') THEN 'VENDOR_HOME'
        WHEN m.role = 'FIELD_ACTIVATOR' THEN 'FIELD_HOME'
        ELSE 'OPS_HOME'
    END,
    job_function = CASE
        WHEN m.role = 'RETAILER_OWNER' THEN 'OWNER'
        WHEN m.role = 'RETAILER_STAFF' THEN 'STAFF'
        WHEN m.role = 'VENDOR_OWNER' THEN 'OWNER'
        WHEN m.role = 'VENDOR_STAFF' THEN 'OPERATIONS'
        WHEN m.role = 'FIELD_ACTIVATOR' THEN 'FIELD'
        ELSE 'OPS'
    END,
    updated_at = now()
FROM organization_memberships m
WHERE mp.membership_id = m.id;
