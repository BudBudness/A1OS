from contextlib import closing
import json
import sqlite3
import uuid


class CheckpointStore:
    def __init__(self, db_path="a1os_state.db"):
        self.db_path = db_path
        self._init()

    def _init(self):
        with closing(sqlite3.connect(self.db_path)) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS recovery_checkpoints "
                "(checkpoint_id TEXT PRIMARY KEY, component TEXT NOT NULL, state TEXT NOT NULL)"
            )

    def save(self, component, state):
        checkpoint_id = str(uuid.uuid4())
        with closing(sqlite3.connect(self.db_path)) as db:
            db.execute(
                "INSERT INTO recovery_checkpoints VALUES (?, ?, ?)",
                (checkpoint_id, component, json.dumps(state)),
            )
            db.commit()
        return checkpoint_id

    def latest(self, component):
        with closing(sqlite3.connect(self.db_path)) as db:
            row = db.execute(
                "SELECT checkpoint_id, component, state "
                "FROM recovery_checkpoints WHERE component=? "
                "ORDER BY rowid DESC LIMIT 1",
                (component,),
            ).fetchone()

        if row is None:
            return None

        return {
            "checkpoint_id": row[0],
            "component": row[1],
            "state": json.loads(row[2]),
        }
