from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any


def ensure_audit_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER,
            actor_user_id INTEGER,
            action TEXT NOT NULL,
            entity_type TEXT,
            entity_id TEXT,
            metadata_json TEXT,
            created_at TEXT NOT NULL
        )
        """
    )


def record_audit(
    conn: sqlite3.Connection,
    *,
    organization_id: int | None,
    actor_user_id: int | None,
    action: str,
    entity_type: str | None = None,
    entity_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    ensure_audit_table(conn)
    conn.execute(
        """
        INSERT INTO audit_events
        (
            organization_id,
            actor_user_id,
            action,
            entity_type,
            entity_id,
            metadata_json,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            organization_id,
            actor_user_id,
            action,
            entity_type,
            entity_id,
            json.dumps(metadata or {}, default=str),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
