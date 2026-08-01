from fastapi import APIRouter
import sqlite3

router = APIRouter(prefix="/v1/finance", tags=["finance"])

DB = "deployments/little-oaks/data/education.db"

def db():
    return sqlite3.connect(DB)

@router.get("/summary")
def summary():
    conn = db()
    cur = conn.cursor()

    students = cur.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    invoiced = cur.execute(
        "SELECT COALESCE(SUM(amount),0) FROM invoices"
    ).fetchone()[0]

    paid = cur.execute(
        "SELECT COALESCE(SUM(amount),0) FROM payments"
    ).fetchone()[0]

    conn.close()

    return {
        "students": students,
        "total_invoiced": invoiced,
        "total_paid": paid,
        "outstanding": invoiced - paid
    }
