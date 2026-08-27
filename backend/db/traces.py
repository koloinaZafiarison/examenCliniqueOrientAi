"""Fonctions d'écriture et lecture des traces en base PostgreSQL."""

from backend.db.database import SessionLocal
from backend.db.models import Trace


def write_trace(trace: dict) -> None:
    """Persiste une trace dans PostgreSQL."""
    db = SessionLocal()
    try:
        row = Trace(
            request_id=trace.get("request_id", ""),
            event=trace.get("event", ""),
            payload=trace.get("payload", {}),
        )
        db.add(row)
        db.commit()
    finally:
        db.close()