"""Canonical payment reconciliation worker for NON_CUSTODIAL_DIRECT.

The worker never takes custody of funds. It reconciles evidence already recorded
by POL and only marks a payment successful when trusted evidence totals exactly
the expected payment amount.
"""

from __future__ import annotations

import uuid

from psycopg2.extras import Json


class PaymentReconciliationError(RuntimeError):
    pass


TRUSTED_EVIDENCE_TYPES = {"BANK_REFERENCE", "POS_REFERENCE", "VENDOR_CONFIRMATION"}


class PaymentReconciliationWorker:
    @staticmethod
    def claim_pending(cur, limit: int = 50, lease_minutes: int = 5):
        lease_id = str(uuid.uuid4())
        cur.execute(
            """
            WITH candidates AS (
                SELECT id
                FROM payment_reconciliation_cases
                WHERE status IN ('OPEN','MISMATCH','PARTIALLY_MATCHED')
                  AND (next_retry_at IS NULL OR next_retry_at <= now())
                  AND (worker_lease_until IS NULL OR worker_lease_until <= now())
                ORDER BY opened_at
                FOR UPDATE SKIP LOCKED
                LIMIT %s
            )
            UPDATE payment_reconciliation_cases c
            SET worker_lease_id = %s,
                worker_lease_until = now() + (%s || ' minutes')::interval,
                attempt_count = attempt_count + 1,
                last_attempt_at = now()
            FROM candidates x
            WHERE c.id = x.id
            RETURNING c.*;
            """,
            (limit, lease_id, lease_minutes),
        )
        return lease_id, cur.fetchall()

    @staticmethod
    def _release(cur, case_id: str, lease_id: str, next_retry_at=None):
        cur.execute(
            """
            UPDATE payment_reconciliation_cases
            SET worker_lease_id = NULL,
                worker_lease_until = NULL,
                next_retry_at = %s
            WHERE id = %s AND worker_lease_id = %s;
            """,
            (next_retry_at, case_id, lease_id),
        )

    @classmethod
    def reconcile_case(cls, cur, case: dict, lease_id: str):
        case_id = str(case["id"])
        expected = int(case["expected_amount_toman"])
        cur.execute(
            """
            SELECT evidence_type, external_reference, claimed_amount_toman,
                   observed_amount_toman, evidence_uri, metadata
            FROM payment_evidence
            WHERE payment_id = %s
            ORDER BY captured_at ASC;
            """,
            (case["payment_id"],),
        )
        evidence = cur.fetchall()
        trusted = [r for r in evidence if r["evidence_type"] in TRUSTED_EVIDENCE_TYPES]
        observed_values = [r["observed_amount_toman"] for r in trusted if r["observed_amount_toman"] is not None]

        if not trusted or not observed_values:
            cur.execute(
                """
                INSERT INTO payment_reconciliation_attempts
                    (id,reconciliation_case_id,attempt_number,evidence_count,outcome,details)
                VALUES (%s,%s,%s,%s,'NO_EVIDENCE',%s);
                """,
                (str(uuid.uuid4()), case_id, case["attempt_count"], len(evidence), Json({"trusted": len(trusted)})),
            )
            cur.execute(
                """
                UPDATE payment_reconciliation_cases
                SET worker_lease_id = NULL,
                    worker_lease_until = NULL,
                    next_retry_at = now() + interval '15 minutes'
                WHERE id = %s AND worker_lease_id = %s;
                """,
                (case_id, lease_id),
            )
            return "NO_EVIDENCE"

        observed_total = sum(int(v) for v in observed_values)
        references = [r["external_reference"] for r in trusted if r["external_reference"]]
        details = {"evidence_count": len(evidence), "trusted_count": len(trusted), "references": references}

        if observed_total == expected:
            outcome = "MATCHED"
            cur.execute(
                """
                INSERT INTO payment_reconciliation_attempts
                    (id,reconciliation_case_id,attempt_number,evidence_count,observed_amount_toman,outcome,provider_reference,details)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s);
                """,
                (str(uuid.uuid4()), case_id, case["attempt_count"], len(evidence), observed_total,
                 outcome, references[0] if references else None, Json(details)),
            )
            cur.execute(
                """
                UPDATE payment_reconciliation_cases
                SET status = 'MATCHED',
                    observed_amount_toman = %s,
                    external_reference = COALESCE(%s, external_reference),
                    resolved_at = now(),
                    resolved_by_user_id = NULL,
                    worker_lease_id = NULL,
                    worker_lease_until = NULL,
                    next_retry_at = NULL
                WHERE id = %s AND worker_lease_id = %s;
                """,
                (observed_total, references[0] if references else None, case_id, lease_id),
            )
            cur.execute(
                """
                UPDATE payments
                SET payment_status = 'SUCCESS',
                    reference_number = COALESCE(reference_number, %s),
                    paid_at = COALESCE(paid_at, now())
                WHERE id = %s AND payment_status IN ('PENDING','INITIATED');
                """,
                (references[0] if references else None, case["payment_id"]),
            )
            cur.execute(
                """
                INSERT INTO outbox_events
                    (id,event_id,event_name,aggregate_type,aggregate_id,payload,status,target_user_id,target_organization_id,dedupe_key)
                SELECT gen_random_uuid(), %s, 'PAYMENT_RECONCILED', 'PAYMENT', %s,
                       jsonb_build_object('payment_id', %s, 'amount_toman', %s, 'reference_number', %s),
                       'PENDING', r.user_id, r.organization_id, %s
                FROM payments p
                JOIN retailers r ON r.id = p.retailer_id
                WHERE p.id = %s
                ON CONFLICT (event_name, dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING;
                """,
                ("payment_reconciled:" + str(case["payment_id"]), str(case["payment_id"]),
                 str(case["payment_id"]), observed_total, references[0] if references else None,
                 "payment_reconciled:" + str(case["payment_id"]), str(case["payment_id"])),
            )
            return outcome

        outcome = "PARTIAL" if observed_total < expected else "MISMATCH"
        cur.execute(
            """
            INSERT INTO payment_reconciliation_attempts
                (id,reconciliation_case_id,attempt_number,evidence_count,observed_amount_toman,outcome,provider_reference,details)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s);
            """,
            (str(uuid.uuid4()), case_id, case["attempt_count"], len(evidence), observed_total,
             outcome, references[0] if references else None, Json(details)),
        )
        cur.execute(
            """
            UPDATE payment_reconciliation_cases
            SET status = %s,
                observed_amount_toman = %s,
                external_reference = COALESCE(%s, external_reference),
                worker_lease_id = NULL,
                worker_lease_until = NULL,
                next_retry_at = CASE WHEN %s = 'PARTIAL' THEN now() + interval '15 minutes' ELSE NULL END
            WHERE id = %s AND worker_lease_id = %s;
            """,
            ("PARTIALLY_MATCHED" if outcome == "PARTIAL" else "MISMATCH", observed_total,
             references[0] if references else None, outcome, case_id, lease_id),
        )
        return outcome

    @classmethod
    def process_pending(cls, cur, limit: int = 50) -> int:
        lease_id, cases = cls.claim_pending(cur, limit=limit)
        processed = 0
        for case in cases:
            cls.reconcile_case(cur, case, lease_id)
            processed += 1
        return processed
