from pathlib import Path
import sqlite3
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[3]
DB=ROOT/"data"/"professional_services.db"
TENANT="primary-tenant"
def connection():
    c=sqlite3.connect(str(DB)); c.row_factory=sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    c.execute("PRAGMA journal_mode=WAL")
    return c
def tenant(value):
    if not isinstance(value,str) or not value.strip(): raise ValueError("tenant_id required")
    return value.strip()
def money(value):
    x=Decimal(str(value))
    if x<0: raise ValueError("amount cannot be negative")
    return x
def audit(c,actor,action,resource,resource_id=None):
    c.execute("INSERT INTO professional_services_audit_log(tenant_id,actor,action,resource,resource_id) VALUES(?,?,?,?,?)",(TENANT,actor,action,resource,resource_id))
def migrate():
    c=connection()
    c.execute("""CREATE TABLE IF NOT EXISTS a1os_migrations(
      id TEXT PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS professional_services_audit_log(
      id INTEGER PRIMARY KEY AUTOINCREMENT,tenant_id TEXT NOT NULL,
      actor TEXT NOT NULL,action TEXT NOT NULL,resource TEXT NOT NULL,
      resource_id TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.commit(); c.close()
def validate():
    assert DB.exists() and DB.is_file()
    c=connection()
    tables={r["name"] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    required={"professional_services_clients","professional_services_projects","professional_services_quotes","professional_services_invoices","professional_services_payments","professional_services_tasks","professional_services_documents","professional_services_settings","professional_services_audit_log","a1os_migrations"}
    missing=required-tables
    assert not missing,f"missing tables: {sorted(missing)}"
    assert c.execute("PRAGMA foreign_keys").fetchone()[0]==1
    c.execute("PRAGMA integrity_check").fetchone()
    c.close()
