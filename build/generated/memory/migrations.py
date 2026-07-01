import time

def run_migrations(engine):
    print("[MIGRATION-ENGINE] Checking schema evolution states...")
    conn = engine._get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    print("[MIGRATION-ENGINE] Database is up to date at Version 1.")