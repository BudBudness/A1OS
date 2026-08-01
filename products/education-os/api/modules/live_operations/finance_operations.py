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

    invoices = cur.execute(
        "SELECT COALESCE(SUM(amount),0) FROM finance_invoices"
    ).fetchone()[0]

    payments = cur.execute(
        "SELECT COALESCE(SUM(amount),0) FROM finance_payments"
    ).fetchone()[0]

    invoice_count = cur.execute(
        "SELECT COUNT(*) FROM finance_invoices"
    ).fetchone()[0]

    conn.close()

    return {
        "students": students,
        "total_invoiced": invoices,
        "total_paid": payments,
        "outstanding": invoices - payments,
        "invoice_count": invoice_count
    }
