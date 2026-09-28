"""Long-lived canonical POL worker process for self-hosted deployment."""
from __future__ import annotations

import os
import signal
import time
from typing import Callable

from scripts.api.db import get_runtime_connection
from scripts.canonical_integration_worker import CanonicalIntegrationWorker
from scripts.payment_reconciliation_worker import PaymentReconciliationWorker
from scripts.provider_delivery_worker import ProviderDeliveryWorker
from scripts.vendor_acceptance_timeout_worker import VendorAcceptanceTimeoutWorker

_STOP = False


def _stop(_signum, _frame) -> None:
    global _STOP
    _STOP = True


def _run_one(name: str, fn: Callable[[], object]) -> None:
    conn = get_runtime_connection()
    try:
        with conn.cursor() as cur:
            result = fn()
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
            lambda: CanonicalIntegrationWorker.process_pending if False else _run_canonical(batch_size),
        )
        _run_one(
            "provider_delivery",
            lambda: ProviderDeliveryWorker.process_pending(_cursor_placeholder, limit=batch_size)
            if False else _run_provider(batch_size),
        )
        _run_one(
            "payment_reconciliation",
            lambda: PaymentReconciliationWorker.process_pending(_cursor_placeholder, limit=batch_size)
            if False else _run_payment(batch_size),
        )
        _run_one(
            "vendor_acceptance_timeout",
            lambda: _run_timeout(batch_size),
        )
        time.sleep(interval)

    return 0


# These helpers keep each worker invocation explicit and transaction-scoped.
# They receive a DB cursor from a fresh connection owned by _run_one.


def _run_canonical(batch_size: int):
    conn = get_runtime_connection()
    raise RuntimeError("internal wiring error")


# Placeholder symbol used only to keep static type checkers from treating the
# lambda branch as a live call; the functions below perform the real work.
_cursor_placeholder = None


def _run_provider(batch_size: int):
    conn = get_runtime_connection()
    try:
        with conn.cursor() as cur:
            result = ProviderDeliveryWorker.process_pending(cur, limit=batch_size)
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _run_payment(batch_size: int):
    conn = get_runtime_connection()
    try:
        with conn.cursor() as cur:
            result = PaymentReconciliationWorker.process_pending(cur, limit=batch_size)
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _run_timeout(batch_size: int):
    conn = get_runtime_connection()
    try:
        with conn.cursor() as cur:
            result = VendorAcceptanceTimeoutWorker.process_expired(cur, limit=batch_size)
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
