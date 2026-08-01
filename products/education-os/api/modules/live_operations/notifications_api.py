
from fastapi import APIRouter
import sqlite3

router=APIRouter(prefix="/v1/notifications",tags=["notifications"])

DB="deployments/little-oaks/data/education.db"

@router.get("/")
def notifications():

    conn=sqlite3.connect(DB)

    rows=conn.execute(
        "SELECT * FROM notifications ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return {"notifications":rows}
