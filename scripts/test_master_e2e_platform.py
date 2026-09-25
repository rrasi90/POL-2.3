        print("\n[STEP 11] Transactional Outbox Event to Notification Engine & User Inbox via NotificationService...")
        dispatched_count = NotificationService.dispatch_pending_outbox(cur)
        assert dispatched_count >= 1

        cur.execute("SELECT count(*) as cnt FROM user_inbox_items WHERE user_id = %s AND category = 'DISPUTES';", (u_vnda_owner,))
        assert cur.fetchone()["cnt"] >= 1
        print(f"  [PASS] Outbox published to notification engine ({dispatched_count} events dispatched); durable user inbox item verified.")

        # -------------------------------------------------------------
        # 12. Admin Action & Audit Log Tracking
        # -------------------------------------------------------------
        print("\n[STEP 12] Admin Dispute Resolution & Audit Trail via AuditService...")
        audit_id = AuditService.log(
            cur,