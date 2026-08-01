from fastapi import APIRouter
from pydantic import BaseModel
import sqlite3

router = APIRouter(prefix="/v1/attendance-sessions", tags=["attendance_sessions"])

DB = "deployments/little-oaks/data/education.db"


class AttendanceSessionCreate(BaseModel):
    organization_id: int = 1
    session_date: str
    class_level: str
    recorded_by: int | None = None


def db():
    return sqlite3.connect(DB)


@router.get("")
def list_sessions():
    conn = db()
    rows = conn.execute(
        "SELECT * FROM attendance_sessions ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return {"attendance_sessions": rows}


@router.post("")
def create_session(session: AttendanceSessionCreate):
    conn = db()

    cur = conn.execute(
        """
        INSERT INTO attendance_sessions
        (organization_id, session_date, class_level, recorded_by)
        VALUES (?, ?, ?, ?)
        """,
        (
            session.organization_id,
            session.session_date,
            session.class_level,
            session.recorded_by,
        ),
    )

    conn.commit()
    session_id = cur.lastrowid
    conn.close()

    return {
        "status": "created",
        "session_id": session_id
    }
