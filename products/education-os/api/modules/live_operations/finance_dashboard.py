
from fastapi import APIRouter
import sqlite3

router=APIRouter(prefix="/v1/finance/dashboard",tags=["finance"])

DB="deployments/little-oaks/data/education.db"

@router.get("")
def dashboard():

    conn=sqlite3.connect(DB)

    obligations=conn.execute(
    "SELECT COUNT(*) FROM fee_obligations"
    ).fetchone()[0]

    transactions=conn.execute(
    "SELECT COUNT(*) FROM fee_transactions"
    ).fetchone()[0]

    payments=conn.execute(
    "SELECT COUNT(*) FROM payments"
    ).fetchone()[0]

    conn.close()

    return {
    "fee_obligations":obligations,
    "transactions":transactions,
    "payments":payments
    }
