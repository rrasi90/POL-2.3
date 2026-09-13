-- POL PLATFORM CORE & CROSS-CUTTING DATABASE SCHEMA
-- Migration: 002_platform_core_schema.sql
-- Canonical Database: PostgreSQL 18+ (SSoT per D-015)
-- Description: Adds Identity/Tenancy (Organizations, Memberships, Sessions, Devices, OTP),
--              Notifications & Inbox, Admin Broadcasts, Support Cases, Field Tasks,
--              Inventory Reservations, Invoices, Admin Audit Logs, and Commerce Hardening.
-- =============================================================================

-- 1. Organizations (Tenant Boundary SSoT)
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    org_type VARCHAR(32) NOT NULL CHECK (org_type IN ('RETAILER', 'VENDOR', 'OPERATOR')),
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('LEAD', 'DOCUMENTS_PENDING', 'UNDER_REVIEW', 'VERIFICATION_PENDING', 'APPROVED', 'ACTIVE', 'REJECTED', 'SUSPENDED')),
    national_id VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2. Organization Memberships (User-to-Tenant Scoping)
CREATE TABLE IF NOT EXISTS organization_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(32) NOT NULL CHECK (role IN ('RETAILER_OWNER', 'RETAILER_STAFF', 'VENDOR_OWNER', 'VENDOR_STAFF', 'SUPER_ADMIN', 'OPS_ADMIN', 'FIELD_ACTIVATOR')),
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('INVITED', 'ACTIVE', 'SUSPENDED', 'REVOKED')),
    is_primary BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_org_user UNIQUE (organization_id, user_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_user_primary_membership 
ON organization_memberships (user_id) WHERE is_primary = TRUE;

-- 3. User Devices (Anti-Fraud & Push Tokens)
CREATE TABLE IF NOT EXISTS user_devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_fingerprint VARCHAR(128) NOT NULL,
    device_type VARCHAR(32) NOT NULL CHECK (device_type IN ('ANDROID', 'IOS', 'WEB')),
    push_token TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_user_device UNIQUE (user_id, device_fingerprint)
);

-- 4. User Sessions (Bearer Authentication & Context)
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    active_organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    token_hash VARCHAR(128) NOT NULL UNIQUE,
    refresh_token_hash VARCHAR(128),
    device_id UUID REFERENCES user_devices(id) ON DELETE SET NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'EXPIRED', 'REVOKED')),
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 5. OTP Challenges (Rate-Limiting & Brute Force Defense)
CREATE TABLE IF NOT EXISTS otp_challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(32) NOT NULL,
    code_hash VARCHAR(128) NOT NULL,
    purpose VARCHAR(32) NOT NULL CHECK (purpose IN ('LOGIN', 'REGISTER', 'ORDER_CONFIRMATION', 'DELIVERY_CONFIRM')),
    attempts_count INT NOT NULL DEFAULT 0,
    max_attempts INT NOT NULL DEFAULT 5,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'VERIFIED', 'EXPIRED', 'BLOCKED')),
    expires_at TIMESTAMPTZ NOT NULL,
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 6. Notifications (Abstract Message Intention)
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    event_name VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    data_payload JSONB,
    priority VARCHAR(16) NOT NULL DEFAULT 'NORMAL' CHECK (priority IN ('LOW', 'NORMAL', 'HIGH', 'CRITICAL')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 7. Notification Deliveries (Physical Channel Delivery Status)
CREATE TABLE IF NOT EXISTS notification_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notification_id UUID NOT NULL REFERENCES notifications(id) ON DELETE CASCADE,
    channel VARCHAR(16) NOT NULL CHECK (channel IN ('INBOX', 'PUSH', 'SMS')),
    device_id UUID REFERENCES user_devices(id) ON DELETE SET NULL,
    provider VARCHAR(32),
    provider_message_id VARCHAR(128),
    status VARCHAR(16) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'SENT', 'DELIVERED', 'FAILED', 'SKIPPED')),
    failure_reason TEXT,
    attempt_count INT NOT NULL DEFAULT 0,
    next_retry_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 8. User Inbox Items (Durable In-App Inbox SSoT with Tenant Context)
CREATE TABLE IF NOT EXISTS user_inbox_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    notification_id UUID REFERENCES notifications(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    category VARCHAR(32) NOT NULL DEFAULT 'SYSTEM' CHECK (category IN ('ORDERS', 'DISPUTES', 'PROMOTIONS', 'SYSTEM')),
    deep_link TEXT,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    is_archived BOOLEAN NOT NULL DEFAULT FALSE,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 9. Notification Preferences (User Opt-in/Opt-out)
CREATE TABLE IF NOT EXISTS notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(32) NOT NULL,
    push_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    sms_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_user_notif_pref UNIQUE (user_id, category)
);

-- 10. Broadcast Messages (Admin Cohort Broadcasts)
CREATE TABLE IF NOT EXISTS broadcast_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    target_criteria JSONB NOT NULL,
    channel VARCHAR(32) NOT NULL DEFAULT 'IN_APP' CHECK (channel IN ('IN_APP', 'SMS', 'PUSH', 'INBOX_AND_SMS', 'ALL')),
    priority VARCHAR(32) NOT NULL DEFAULT 'NORMAL' CHECK (priority IN ('LOW', 'NORMAL', 'HIGH', 'URGENT')),
    status VARCHAR(32) NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'SCHEDULED', 'PROCESSING', 'COMPLETED', 'CANCELLED')),
    recipient_count INT NOT NULL DEFAULT 0,
    estimated_recipient_count INT NOT NULL DEFAULT 0,
    approved_by UUID REFERENCES users(id),
    scheduled_at TIMESTAMPTZ,
    dispatched_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 11. Broadcast Recipients (Frozen Snapshot of Target Audience)
CREATE TABLE IF NOT EXISTS broadcast_recipients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    broadcast_id UUID NOT NULL REFERENCES broadcast_messages(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    organization_id UUID REFERENCES organizations(id),
    notification_id UUID REFERENCES notifications(id),
    status VARCHAR(16) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'SENT', 'FAILED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_broadcast_recipient UNIQUE (broadcast_id, user_id)
);

-- 12. Support Cases (User to Ops Support Tickets - Distinct from Disputes)
CREATE TABLE IF NOT EXISTS support_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    case_number VARCHAR(32) NOT NULL UNIQUE,
    case_type VARCHAR(32) NOT NULL CHECK (case_type IN ('GENERAL', 'ORDER_INQUIRY', 'PAYMENT_ASSISTANCE', 'DELIVERY_DELAY', 'ACCOUNT_ISSUE', 'CATALOG_SUGGESTION', 'INVOICE_INQUIRY')),
    priority VARCHAR(16) NOT NULL DEFAULT 'NORMAL' CHECK (priority IN ('LOW', 'NORMAL', 'HIGH', 'URGENT')),
    status VARCHAR(32) NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'IN_PROGRESS', 'WAITING_ON_USER', 'RESOLVED', 'CLOSED')),
    related_order_id UUID REFERENCES orders(id),
    subject VARCHAR(255) NOT NULL,
    assigned_at TIMESTAMPTZ,
    first_response_at TIMESTAMPTZ,
    due_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 13. Support Case Messages (Threaded Messaging with Attachment Media Support)
CREATE TABLE IF NOT EXISTS support_case_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    support_case_id UUID NOT NULL REFERENCES support_cases(id) ON DELETE CASCADE,
    sender_user_id UUID NOT NULL REFERENCES users(id),
    sender_type VARCHAR(16) NOT NULL CHECK (sender_type IN ('USER', 'AGENT', 'SYSTEM')),
    message_text TEXT NOT NULL,
    attachment_media_id UUID REFERENCES media_assets(id),
    is_internal BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 14. Support Case Assignments (Ops Triage Tracking with Active Guard)
CREATE TABLE IF NOT EXISTS support_case_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    support_case_id UUID NOT NULL REFERENCES support_cases(id) ON DELETE CASCADE,
    assigned_to_user_id UUID NOT NULL REFERENCES users(id),
    assigned_by_user_id UUID NOT NULL REFERENCES users(id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_active_support_assignment 
ON support_case_assignments (support_case_id) WHERE is_active = TRUE;

-- 15. Field Tasks (Visitor / Field Force Tracking)
CREATE TABLE IF NOT EXISTS field_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_type VARCHAR(32) NOT NULL CHECK (task_type IN ('ONBOARD_RETAILER', 'TRAIN_RETAILER', 'FIRST_ORDER_ASSIST', 'FOLLOW_UP', 'VENDOR_VISIT', 'DISPUTE_VISIT')),
    target_organization_id UUID REFERENCES organizations(id),
    assigned_to_user_id UUID NOT NULL REFERENCES users(id),
    status VARCHAR(32) NOT NULL DEFAULT 'ASSIGNED' CHECK (status IN ('ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED')),
    due_date TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 16. Inventory Reservations (Explicit Lifecycle Tracking with Idempotency)
CREATE TABLE IF NOT EXISTS inventory_reservations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_product_id UUID NOT NULL REFERENCES vendor_products(id),
    order_id UUID REFERENCES orders(id),
    order_item_id UUID REFERENCES order_items(id),
    idempotency_key VARCHAR(128),
    quantity INT NOT NULL CHECK (quantity > 0),
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'CONSUMED', 'RELEASED', 'EXPIRED')),
    expires_at TIMESTAMPTZ NOT NULL,
    released_at TIMESTAMPTZ,
    consumed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 17. Invoices (Simplified Official Accounting Records / Commercial Invoice Records)
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_number VARCHAR(64) NOT NULL UNIQUE,
    order_id UUID NOT NULL REFERENCES orders(id),
    retailer_organization_id UUID NOT NULL REFERENCES organizations(id),
    vendor_organization_id UUID NOT NULL REFERENCES organizations(id),
    total_amount BIGINT NOT NULL CHECK (total_amount >= 0),
    currency VARCHAR(16) NOT NULL DEFAULT 'TOMAN',
    status VARCHAR(32) NOT NULL DEFAULT 'ISSUED' CHECK (status IN ('DRAFT', 'ISSUED', 'PAID', 'ADJUSTED', 'CANCELLED')),
    document_media_id UUID REFERENCES media_assets(id),
    issued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 18. Invoice Items (Line-Item Financial Consistency)
CREATE TABLE IF NOT EXISTS invoice_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    order_item_id UUID REFERENCES order_items(id),
    product_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price BIGINT NOT NULL CHECK (unit_price >= 0),
    total_line_amount BIGINT NOT NULL CHECK (total_line_amount >= 0)
);

-- 19. Admin Audit Logs (Immutable Governance Trail)
CREATE TABLE IF NOT EXISTS admin_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_user_id UUID NOT NULL REFERENCES users(id),
    action VARCHAR(64) NOT NULL,
    target_entity_type VARCHAR(64) NOT NULL,
    target_entity_id UUID,
    state_before JSONB,
    state_after JSONB,
    reason TEXT,
    ip_address VARCHAR(45),
    correlation_id VARCHAR(128),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =============================================================================
-- COMMERCE & LOGISTICS ENTITY ENHANCEMENTS
-- =============================================================================

-- Basket Versioning
ALTER TABLE baskets ADD COLUMN IF NOT EXISTS version INT NOT NULL DEFAULT 1;

-- Allocation Plan Basket Versioning, Status Lifecycle & Audit Hash
ALTER TABLE allocation_plans ADD COLUMN IF NOT EXISTS basket_version INT NOT NULL DEFAULT 1;
ALTER TABLE allocation_plans ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ;
ALTER TABLE allocation_plans ADD COLUMN IF NOT EXISTS status VARCHAR(32) NOT NULL DEFAULT 'PREVIEW' CHECK (status IN ('PREVIEW', 'CONFIRMED', 'EXPIRED', 'SUPERSEDED'));
ALTER TABLE allocation_plans ADD COLUMN IF NOT EXISTS input_hash VARCHAR(64);
ALTER TABLE allocation_plans ADD COLUMN IF NOT EXISTS algorithm_version VARCHAR(32) DEFAULT 'v1.0';

-- Orders: Address Snapshot, Correlation ID
ALTER TABLE orders ADD COLUMN IF NOT EXISTS delivery_address_snapshot JSONB;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS correlation_id VARCHAR(128);

-- Payments: Evidence of Direct Settlement (NON_CUSTODIAL_DIRECT)
ALTER TABLE payments ADD COLUMN IF NOT EXISTS payment_proof_media_id UUID REFERENCES media_assets(id);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS verified_by UUID REFERENCES users(id);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS verified_at TIMESTAMPTZ;

-- Retailers & Vendors: Canonical Organization Reference (SSoT)
ALTER TABLE retailers ADD COLUMN IF NOT EXISTS organization_id UUID REFERENCES organizations(id);
ALTER TABLE vendors ADD COLUMN IF NOT EXISTS organization_id UUID REFERENCES organizations(id);

-- Deliveries: Driver Details (Option A: Carrier/Vendor driver info attached to Delivery)
ALTER TABLE deliveries ADD COLUMN IF NOT EXISTS driver_name VARCHAR(128);
ALTER TABLE deliveries ADD COLUMN IF NOT EXISTS driver_phone VARCHAR(32);
ALTER TABLE deliveries ADD COLUMN IF NOT EXISTS vehicle_plate VARCHAR(32);

-- Indexes for Platform Performance & Query Scoping
CREATE INDEX IF NOT EXISTS idx_memberships_user ON organization_memberships(user_id);
CREATE INDEX IF NOT EXISTS idx_memberships_org ON organization_memberships(organization_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_inbox_user_unread ON user_inbox_items(user_id) WHERE is_read = FALSE;
CREATE INDEX IF NOT EXISTS idx_reservations_active ON inventory_reservations(vendor_product_id) WHERE status = 'ACTIVE';
CREATE INDEX IF NOT EXISTS idx_support_cases_org ON support_cases(organization_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_actor ON admin_audit_logs(actor_user_id);
CREATE INDEX IF NOT EXISTS idx_retailers_org ON retailers(organization_id);
CREATE INDEX IF NOT EXISTS idx_vendors_org ON vendors(organization_id);
