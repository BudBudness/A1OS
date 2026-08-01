
from fastapi import APIRouter
import sqlite3

router = APIRouter(prefix="/v1/dashboard", tags=["dashboard"])

DB="deployments/little-oaks/data/education.db"

def db():
    return sqlite3.connect(DB)

@router.get("/director")
def director():

    conn=db()
    cur=conn.cursor()

    students=cur.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    staff=cur.execute(
        "SELECT COUNT(*) FROM staff"
    ).fetchone()[0]

    inventory=cur.execute(
        "SELECT COUNT(*) FROM inventory"
    ).fetchone()[0]

    conn.close()

    return {
        "role":"director",
        "students":students,
        "staff":staff,
        "inventory_items":inventory
    }


@router.get("/headmistress")
def headmistress():

    conn=db()
    cur=conn.cursor()

    students=cur.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    conn.close()

    return {
        "role":"head_mistress",
        "students":students
    }


@router.get("/teacher")
def teacher():

    return {
        "role":"teacher",
        "features":[
            "students",
            "attendance",
            "observations",
            "reports"
        ]
    }


@router.get("/parent")
def parent():

    return {
        "role":"parent",
        "features":[
            "child_profile",
            "fees",
            "receipts",
            "progress",
            "notifications"
        ]
    }
