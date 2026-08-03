
from fastapi import APIRouter
import sqlite3

router=APIRouter(prefix="/v1/inventory",tags=["inventory"])

DB="deployments/little-oaks/data/education.db"

@router.get("/")
def inventory():

    conn=sqlite3.connect(DB)

    rows=conn.execute(
        "SELECT * FROM inventory"
    ).fetchall()

    conn.close()

    return {"inventory":rows}
