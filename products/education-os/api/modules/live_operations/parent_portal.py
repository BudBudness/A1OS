
from fastapi import APIRouter
import sqlite3

router=APIRouter(prefix="/v1/parents",tags=["parents"])

DB="deployments/little-oaks/data/education.db"

def db():
    return sqlite3.connect(DB)

@router.get("/{parent_id}/balance")
def balance(parent_id:int):

    conn=db()

    row=conn.execute(
        "SELECT * FROM parent_finance_views WHERE parent_id=?",
        (parent_id,)
    ).fetchall()

    conn.close()

    return {"parent_id":parent_id,"balance":row}
