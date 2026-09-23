#!/usr/bin/env python3
"""Regression checks for the 2026-09-16 repository-wide integrity hardening."""

from psycopg2.extras import RealDictCursor

from scripts.migration_runner import get_connection


def _conn():
    conn, _ = get_connection("pol_test")
    conn.autocommit = False
    return conn


def test_canonical_schema_has_90_tables_and_new_integrity_guards():
    conn = _conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(
            """
            SELECT COUNT(*) AS c
            FROM information_schema.tables
            WHERE table_schema='public' AND table_type='BASE TABLE'
            """
        )
        assert cur.fetchone()["c"] >= 90

        cur.execute(
            """
            SELECT trigger_name
            FROM information_schema.triggers
            WHERE event_object_table='user_sessions'
              AND trigger_name='trg_validate_session_context'
            """
        )
        assert cur.fetchone()

        cur.execute(
            """
            SELECT trigger_name
            FROM information_schema.triggers
            WHERE event_object_table='order_groups'
              AND trigger_name='trg_validate_order_group_allocation_context'
            """
        )
        assert cur.fetchone()

        cur.execute(
            """
            SELECT trigger_name
            FROM information_schema.triggers
            WHERE event_object_table='orders'
              AND trigger_name='trg_validate_child_order_context'
            """
        )
        assert cur.fetchone()

        cur.execute(
            """
            SELECT COUNT(*) AS c
            FROM pg_constraint
            WHERE conname IN (
                'ex_vendor_operating_window_no_overlap',
                'ex_vendor_capacity_profile_no_overlap'
            )
            """
        )
        assert cur.fetchone()["c"] == 2

        cur.execute(
            """
            SELECT COUNT(*) AS c
            FROM pg_indexes
            WHERE schemaname='public'
              AND indexname IN (
                  'uq_retailer_default_saved_list',
                  'uq_active_global_consent',
                  'uq_active_tenant_consent'
              )
            """
        )
        assert cur.fetchone()["c"] == 3
    finally:
        conn.rollback()
        conn.close()
