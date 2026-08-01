
from fastapi import APIRouter
import sqlite3

router=APIRouter(prefix="/v1/staff",tags=["staff"])

DB="deployments/little-oaks/data/education.db"

@router.get("/")
def staff():

    conn=sqlite3.connect(DB)

    rows=conn.execute(
        "SELECT * FROM staff"
    ).fetchall()

    conn.close()

    return {"staff":rows}
