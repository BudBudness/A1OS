from fastapi import APIRouter
from pydantic import BaseModel
import sqlite3

router = APIRouter(prefix="/v1/classrooms", tags=["classrooms"])

DB = "deployments/little-oaks/data/education.db"

class ClassroomCreate(BaseModel):
    organization_id: int = 1
    name: str
    level: str | None = None


def db():
    return sqlite3.connect(DB)


@router.get("")
def list_classrooms():
    conn = db()
    rows = conn.execute(
        "SELECT * FROM classrooms ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return {"classrooms": rows}


@router.post("")
def create_classroom(classroom: ClassroomCreate):
    conn = db()

    cur = conn.execute(
        """
        INSERT INTO classrooms
        (organization_id, name, level)
        VALUES (?, ?, ?)
        """,
        (
            classroom.organization_id,
            classroom.name,
            classroom.level,
        ),
    )

    conn.commit()
    classroom_id = cur.lastrowid
    conn.close()

    return {
        "status": "created",
        "classroom_id": classroom_id
    }
