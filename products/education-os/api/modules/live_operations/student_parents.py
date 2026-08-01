from fastapi import APIRouter
from pydantic import BaseModel
import sqlite3

router = APIRouter(prefix="/v1/student-parents", tags=["student_parents"])

DB = "deployments/little-oaks/data/education.db"


class StudentParentCreate(BaseModel):
    student_id: int
    parent_id: int
    is_primary: int = 0


def db():
    return sqlite3.connect(DB)


@router.get("")
def list_student_parents():
    conn = db()
    rows = conn.execute(
        "SELECT * FROM student_parents ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return {"student_parents": rows}


@router.post("")
def create_student_parent(link: StudentParentCreate):
    conn = db()

    cur = conn.execute(
        """
        INSERT INTO student_parents
        (student_id, parent_id, is_primary)
        VALUES (?, ?, ?)
        """,
        (
            link.student_id,
            link.parent_id,
            link.is_primary,
        ),
    )

    conn.commit()
    link_id = cur.lastrowid
    conn.close()

    return {
        "status": "created",
        "student_parent_id": link_id
    }
