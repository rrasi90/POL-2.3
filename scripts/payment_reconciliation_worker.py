"""Canonical payment reconciliation worker for NON_CUSTODIAL_DIRECT.

The worker never takes custody of funds. It reconciles evidence already recorded
by POL and only marks a payment successful when a trusted observation matches the
expected payment amount. Evidence rows are observations by default, not additive
cash fragments, so independent confirmations cannot double-count one payment.
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

    @classmethod
    def reconcile_case(cls, cur, case: dict, lease_id: str):
        case_id = str(case["id"])
        expected = int(case["expected_amount_toman"])
        cur.execute(
            """
            SELECT id, evidence_type, external_reference, claimed_amount_toman,
                   observed_amount_toman, evidence_uri, metadata, observation_scope
            FROM payment_evidence
            WHERE payment_id = %s
            ORDER BY captured_at ASC;
            """,
            (case["payment_id"],),
        )
        evidence = cur.fetchall()
        trusted = [r for r in evidence if r["evidence_type"] in TRUSTED_EVIDENCE_TYPES]
        observed = [r for r in trusted if r["observed_amount_toman"] is not None]

        if not trusted or not observed:
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

        # SINGLE_PAYMENT evidence rows are independent observations of the same
        # expected payment. Never sum them. SPLIT_PAYMENT is reserved for a
        # separately approved future flow and is not activated in MVP.
        single_observed = [r for r in observed if r.get("observation_scope", "SINGLE_PAYMENT") == "SINGLE_PAYMENT"]
        observed_values = [int(r["observed_amount_toman"]) for r in single_observed]
        max_observed = max(observed_values)
        exact_match = any(value == expected for value in observed_values)
        references = [r["external_reference"] for r in trusted if r["external_reference"]]
        details = {
            "evidence_count": len(evidence),
            "trusted_count": len(trusted),
            "observation_count": len(observed_values),
            "max_observed_amount": max_observed,
            "references": references,
            "aggregation": "single_payment_observation_max",
        }

        if exact_match:
            outcome = "MATCHED"
            matching_ref = next(
                (r["external_reference"] for r in single_observed if int(r["observed_amount_toman"]) == expected),
                references[0] if references else None,
            )
            cur.execute(
                """
                INSERT INTO payment_reconciliation_attempts
                    (id,reconciliation_case_id,attempt_number,evidence_count,observed_amount_toman,outcome,provider_reference,details)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s);
                """,
                (str(uuid.uuid4()), case_id, case["attempt_count"], len(evidence), expected,
                 outcome, matching_ref, Json(details)),
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
                (expected, matching_ref, case_id, lease_id),
            )
            cur.execute(
                """
                UPDATE payments
                SET payment_status = 'SUCCESS',
                    reference_number = COALESCE(reference_number, %s),
                    paid_at = COALESCE(paid_at, now())
                WHERE id = %s AND payment_status IN ('PENDING','INITIATED');
                """,
                (matching_ref, case["payment_id"]),
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
                 str(case["payment_id"]), expected, matching_ref,
                 "payment_reconciled:" + str(case["payment_id"]), str(case["payment_id"])),
            )
            return outcome

        observed_total = max_observed
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
