"""Static contract checks for the canonical POL worker architecture."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_worker_architecture_is_postgres_python_canonical():
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    worker_arch = (ROOT / "POL_00_PROJECT_CONTROL" / "WORKER_ARCHITECTURE.md").read_text(encoding="utf-8")
    technical = (ROOT / "06_PRODUCT" / "Technical_Architecture_Spec.md").read_text(encoding="utf-8")
    events = (ROOT / "08_DATA" / "Event_Architecture.md").read_text(encoding="utf-8")

    assert "redis" not in requirements
    assert "bullmq" not in requirements

    assert "PostgreSQL 18" in worker_arch
    assert "Python worker" in worker_arch
    assert "outbox_events" in worker_arch
    assert "FOR UPDATE SKIP LOCKED" in worker_arch
    assert "BullMQ" in worker_arch
    assert "historical / superseded" in worker_arch.lower()

    active_queue_row = next(
        line for line in technical.splitlines()
        if "موتور صف و پردازش رویدادها" in line
    )
    assert "LEGACY / RECONCILIATION PENDING" in active_queue_row

    # Event transport must not retain an active BullMQ/Redis-Streams path.
    assert "BullMQ Outbox Worker" not in events
    assert 'Redis Stream: "pol:events"' not in events
    assert "PostgreSQL 18" in events
