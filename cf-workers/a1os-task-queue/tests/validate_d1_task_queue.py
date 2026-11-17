"""SQLite contract tests for the A1OS D1 task queue migration."""
from pathlib import Path
import sqlite3

MIGRATION = Path(__file__).resolve().parents[1] / "migrations" / "0001_initial.sql"


def main():
    db = sqlite3.connect(":memory:")
    db.executescript(MIGRATION.read_text(encoding="utf-8"))

    db.execute(
        """INSERT INTO tasks(task_id,target,role,action,payload_json)
           VALUES('task-1','research','analyst','scan','{"asset":"BTC"}')"""
    )
    claim_sql = """UPDATE tasks SET status='running',attempts=attempts+1,updated_at=CURRENT_TIMESTAMP
                   WHERE task_id=? AND (status='queued' OR
                   (status='retry' AND (next_attempt_at IS NULL OR
                   datetime(next_attempt_at)<=CURRENT_TIMESTAMP))) RETURNING task_id,status,attempts"""
    first = db.execute(claim_sql, ("task-1",)).fetchone()
    assert first == ("task-1", "running", 1), first
    assert db.execute(claim_sql, ("task-1",)).fetchone() is None

    completed = db.execute(
        """UPDATE tasks SET status='completed',completed_at=CURRENT_TIMESTAMP
           WHERE task_id=? AND status='running' RETURNING status""",
        ("task-1",),
    ).fetchone()
    assert completed == ("completed",)

    db.execute(
        """INSERT INTO tasks(task_id,target,role,action,payload_json,status,attempts,max_attempts,
           updated_at) VALUES('task-2','research','analyst','scan','{}','running',1,3,
           datetime('now','-10 minutes'))"""
    )
    recovered = db.execute(
        """UPDATE tasks SET status=CASE WHEN attempts>=max_attempts THEN 'failed' ELSE 'retry' END,
           next_attempt_at=CASE WHEN attempts>=max_attempts THEN NULL ELSE CURRENT_TIMESTAMP END,
           updated_at=CURRENT_TIMESTAMP
           WHERE task_id IN (SELECT task_id FROM tasks WHERE status='running'
           AND datetime(updated_at)<datetime('now','-300 seconds')) RETURNING task_id,status"""
    ).fetchall()
    assert recovered == [("task-2", "retry")], recovered

    db.execute(
        """INSERT INTO tasks(task_id,target,role,action,payload_json,status,attempts,max_attempts,
           updated_at) VALUES('task-3','research','analyst','scan','{}','running',3,3,
           datetime('now','-10 minutes'))"""
    )
    terminal = db.execute(
        """UPDATE tasks SET status=CASE WHEN attempts>=max_attempts THEN 'failed' ELSE 'retry' END
           WHERE task_id='task-3' RETURNING status"""
    ).fetchone()
    assert terminal == ("failed",)

    try:
        db.execute(
            """INSERT INTO tasks(task_id,target,role,action,payload_json)
               VALUES('bad','research','analyst','scan','not-json')"""
        )
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError("invalid JSON payload must be rejected")

    assert db.execute("PRAGMA foreign_key_check").fetchall() == []
    print("A1OS D1 task queue: schema, atomic claim, completion, stale recovery and payload validation passed")


if __name__ == "__main__":
    main()
