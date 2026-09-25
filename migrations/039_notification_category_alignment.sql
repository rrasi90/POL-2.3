-- ============================================================================
-- 039_notification_category_alignment.sql
-- Align durable inbox category constraint with the canonical Notification Domain.
-- ============================================================================

ALTER TABLE user_inbox_items
    DROP CONSTRAINT IF EXISTS user_inbox_items_category_check;

ALTER TABLE user_inbox_items
    ADD CONSTRAINT user_inbox_items_category_check
    CHECK (
        category IN (
            'ORDERS',
            'PAYMENTS',
            'DELIVERY',
            'DISPUTES',
            'SECURITY',
            'SUPPORT',
            'SYSTEM',
            'MARKETING'
        )
    );
