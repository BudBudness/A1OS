from fastapi import FastAPI, HTTPException
from pathlib import Path
import sqlite3

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PRODUCT_ROOT / "deployments" / "little-oaks" / "data" / "education.db"

app = FastAPI(
    title="Little Oaks Montessori Nursery & Kindergarten — Education OS",
    version="0.1.0",
)

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/health")
def health():
    conn = db()
    try:
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        return {
            "status": "healthy" if integrity == "ok" else "degraded",
            "product": "Education OS",
            "deployment": "Little Oaks Montessori Nursery & Kindergarten",
            "database_integrity": integrity,
        }
    finally:
        conn.close()

@app.get("/organization")
def organization():
    conn = db()
    try:
        row = conn.execute(
            "SELECT * FROM organization LIMIT 1"
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Organization not initialized",
            )

        return dict(row)
    finally:
        conn.close()

@app.get("/students")
def students():
    conn = db()
    try:
        rows = conn.execute(
            "SELECT * FROM students ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

@app.get("/admissions")
def admissions():
    conn = db()
    try:
        rows = conn.execute(
            "SELECT * FROM admissions ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

@app.get("/fees")
def fees():
    conn = db()
    try:
        rows = conn.execute(
            "SELECT * FROM fee_obligations ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

@app.get("/attendance")
def attendance():
    conn = db()
    try:
        rows = conn.execute(
            "SELECT * FROM attendance ORDER BY attendance_date DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
