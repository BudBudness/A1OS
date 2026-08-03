from fastapi import APIRouter
from pydantic import BaseModel
import sqlite3

router = APIRouter(prefix="/v1/parents", tags=["parents"])

DB = "deployments/little-oaks/data/education.db"


class ParentCreate(BaseModel):
    organization_id: int = 1
    full_name: str
    phone: str | None = None
    email: str | None = None
    relationship: str | None = None


def db():
    return sqlite3.connect(DB)


@router.get("")
def list_parents():
    conn = db()
    rows = conn.execute(
        "SELECT * FROM parents ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return {"parents": rows}


@router.post("")
def create_parent(parent: ParentCreate):
    conn = db()

    cur = conn.execute(
        """
        INSERT INTO parents
        (organization_id, full_name, phone, email, relationship)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            parent.organization_id,
            parent.full_name,
            parent.phone,
            parent.email,
            parent.relationship,
        ),
    )

    conn.commit()
    parent_id = cur.lastrowid
    conn.close()

    return {
        "status": "created",
        "parent_id": parent_id
    }
