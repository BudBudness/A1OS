import json
import uuid
from core.persistence.database import Database

class Recovery:
    @staticmethod
    def checkpoint(component, state):
        checkpoint_id = str(uuid.uuid4())
        Database.execute(
            """
            INSERT INTO recovery_checkpoints
            (checkpoint_id,component,state)
            VALUES (?,?,?)
            """,
            (checkpoint_id, component, json.dumps(state))
        )
        return checkpoint_id

    @staticmethod
    def latest(component):
        return Database.fetchone(
            """
            SELECT * FROM recovery_checkpoints
            WHERE component=?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (component,)
        )
