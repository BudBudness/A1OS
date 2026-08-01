from fastapi import APIRouter
from pydantic import BaseModel
import sqlite3

router = APIRouter(prefix="/v1/school-operations", tags=["school_operations"])

DB = "deployments/little-oaks/data/education.db"


class SchoolOperationCreate(BaseModel):
    organization_id: int = 1
    operation_type: str
    title: str
    description: str | None = None
    status: str = "open"
    assigned_to: int | None = None
    due_date: str | None = None


def db():
    return sqlite3.connect(DB)


@router.get("")
def list_operations():
    conn = db()
    rows = conn.execute(
        "SELECT * FROM school_operations ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return {"school_operations": rows}


@router.post("")
def create_operation(operation: SchoolOperationCreate):
    conn = db()

    cur = conn.execute(
        """
        INSERT INTO school_operations
        (organization_id, operation_type, title, description, status, assigned_to, due_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            operation.organization_id,
            operation.operation_type,
            operation.title,
            operation.description,
            operation.status,
            operation.assigned_to,
            operation.due_date,
        ),
    )

    conn.commit()
    operation_id = cur.lastrowid
    conn.close()

    return {
        "status": "created",
        "operation_id": operation_id
    }
