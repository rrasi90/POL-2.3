"""Long-lived canonical POL worker process for self-hosted deployment."""
from __future__ import annotations

import os
import signal
import time
from collections.abc import Callable

from scripts.api.db import get_runtime_connection
from scripts.canonical_integration_worker import CanonicalIntegrationWorker
from scripts.payment_reconciliation_worker import PaymentReconciliationWorker
from scripts.provider_delivery_worker import ProviderDeliveryWorker
from scripts.vendor_acceptance_timeout_worker import VendorAcceptanceTimeoutWorker

_STOP = False


def _stop(_signum, _frame) -> None:
    global _STOP
    _STOP = True


def _run_one(name: str, fn: Callable) -> None:
    conn = get_runtime_connection()
    try:
        with conn.cursor() as cur:
            result = fn(cur)
        conn.commit()
        print(f"[WORKER] {name}: {result}", flush=True)
    except Exception as exc:
        conn.rollback()
        print(f"[WORKER] {name}: ERROR {exc}", flush=True)
    finally:
        conn.close()


def main() -> int:
    if os.getenv("ENVIRONMENT", "").lower() not in {"prod", "production"}:
        raise RuntimeError("Worker runtime requires ENVIRONMENT=production.")

    interval = max(2, int(os.getenv("POL_WORKER_INTERVAL_SECONDS", "5")))
    batch_size = max(1, int(os.getenv("POL_WORKER_BATCH_SIZE", "50")))

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    while not _STOP:
        _run_one(
            "canonical_integration",
            lambda cur: CanonicalIntegrationWorker.process_pending(cur, limit=batch_size),
        )
        _run_one(
            "provider_delivery",
            lambda cur: ProviderDeliveryWorker.process_pending(cur, limit=batch_size),
        )
        _run_one(
            "payment_reconciliation",
            lambda cur: PaymentReconciliationWorker.process_pending(cur, limit=batch_size),
        )
        _run_one(
            "vendor_acceptance_timeout",
            lambda cur: VendorAcceptanceTimeoutWorker.process_expired(cur, limit=batch_size),
        )

        if not _STOP:
            time.sleep(interval)

    print("[WORKER] shutdown complete", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
