from fastapi import APIRouter
from pydantic import BaseModel
import sqlite3

router = APIRouter(prefix="/v1/attendance", tags=["attendance"])

DB = "deployments/little-oaks/data/education.db"


class AttendanceCreate(BaseModel):
    session_id: int
    student_id: int
    status: str = "present"
    notes: str | None = None


def db():
    return sqlite3.connect(DB)


@router.get("")
def list_attendance():
    conn = db()
    rows = conn.execute(
        "SELECT * FROM attendance_records ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return {"attendance": rows}


@router.post("")
def create_attendance(record: AttendanceCreate):
    conn = db()

    cur = conn.execute(
        """
        INSERT INTO attendance_records
        (session_id, student_id, status, notes)
        VALUES (?, ?, ?, ?)
        """,
        (
            record.session_id,
            record.student_id,
            record.status,
            record.notes,
        ),
    )

    conn.commit()
    attendance_id = cur.lastrowid
    conn.close()

    return {
        "status": "created",
        "attendance_id": attendance_id
    }
