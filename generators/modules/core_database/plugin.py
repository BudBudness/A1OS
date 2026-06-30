import sqlite3
from pathlib import Path

def run(payload):
    """
    Core Database Service Provider.
    Payload format: {"action": "write"|"read", "table": str, "data": dict, "query": str}
    """
    db_path = Path(__file__).parent / "sandbox_storage.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    action = payload.get("action")
    
    try:
        if action == "initialize":
            cursor.execute("CREATE TABLE IF NOT EXISTS system_state (key TEXT PRIMARY KEY, val TEXT);")
            conn.commit()
            return {"status": "SUCCESS", "message": "Storage initialized successfully."}
            
        elif action == "write":
            key = payload.get("key")
            val = payload.get("val")
            cursor.execute("INSERT OR REPLACE INTO system_state (key, val) VALUES (?, ?);", (key, val))
            conn.commit()
            return {"status": "SUCCESS", "message": f"Key '{key}' recorded safely."}
            
        elif action == "read":
            key = payload.get("key")
            cursor.execute("SELECT val FROM system_state WHERE key = ?;", (key,))
            row = cursor.fetchone()
            return {"status": "SUCCESS", "data": row[0] if row else None}
            
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}
    finally:
        conn.close()
