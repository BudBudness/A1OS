from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sqlite3

router = APIRouter(prefix="/v1/students", tags=["students"])

DB = "deployments/little-oaks/data/education.db"

class StudentCreate(BaseModel):
    organization_id: int = 1
    full_name: str
    gender: str | None = None
    date_of_birth: str | None = None


def db():
    return sqlite3.connect(DB)


@router.get("")
def list_students():
    conn = db()
    rows = conn.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return {"students": rows}


@router.post("")
def create_student(student: StudentCreate):
    conn = db()
    cur = conn.execute(
        """
        INSERT INTO students
        (organization_id, full_name, gender, date_of_birth)
        VALUES (?, ?, ?, ?)
        """,
        (
            student.organization_id,
            student.full_name,
            student.gender,
            student.date_of_birth,
        ),
    )
    conn.commit()
    student_id = cur.lastrowid
    conn.close()

    return {
        "status": "created",
        "student_id": student_id
    }
