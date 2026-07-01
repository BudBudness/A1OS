import sqlite3, uuid
from workflow.security import LedgerSecurity

class WorkflowEngine:
    DB_PATH = "/data/data/com.termux/files/home/A1OS/audit.db"

    @staticmethod
    def create_task(owner, target, app, priority, budget):
        data = f"{owner}:{target}:{app}:{priority}:{budget}"
        prev_hash = LedgerSecurity.get_last_hash()
        new_hash = LedgerSecurity.calculate_hash(data, prev_hash)
        
        with sqlite3.connect(WorkflowEngine.DB_PATH) as conn:
            tid = str(uuid.uuid4())
            conn.execute("INSERT INTO tasks (id, data, hash, state) VALUES (?, ?, ?, ?)", 
                         (tid, data, new_hash, "PENDING"))
        return tid

    @staticmethod
    def recover_state():
        with sqlite3.connect(WorkflowEngine.DB_PATH) as conn:
            tasks = conn.execute("SELECT id, data, hash FROM tasks").fetchall()
        
        last_hash = "0"
        for tid, data, stored_hash in tasks:
            if LedgerSecurity.calculate_hash(data, last_hash) != stored_hash:
                raise Exception(f"KERNEL_CORRUPTION: Chain broken at {tid}")
            last_hash = stored_hash
        return True
