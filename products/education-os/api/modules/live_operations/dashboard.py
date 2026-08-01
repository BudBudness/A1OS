from fastapi import APIRouter
import sqlite3

router = APIRouter(prefix="/v1/dashboard", tags=["dashboard"])

DB = "deployments/little-oaks/data/education.db"


def db():
    return sqlite3.connect(DB)


@router.get("")
def dashboard():
    conn = db()

    students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    parents = conn.execute(
        "SELECT COUNT(*) FROM parents"
    ).fetchone()[0]

    classrooms = conn.execute(
        "SELECT COUNT(*) FROM classrooms"
    ).fetchone()[0]

    attendance_today = conn.execute(
        """
        SELECT COUNT(*)
        FROM attendance_records
        WHERE recorded_at LIKE date('now') || '%'
        """
    ).fetchone()[0]

    attendance_present = conn.execute(
        """
        SELECT COUNT(*)
        FROM attendance_records
        WHERE status='present'
        AND recorded_at LIKE date('now') || '%'
        """
    ).fetchone()[0]

    open_operations = conn.execute(
        """
        SELECT COUNT(*)
        FROM school_operations
        WHERE status='open'
        """
    ).fetchone()[0]

    recent_operations = conn.execute(
        """
        SELECT id, operation_type, title, status, created_at
        FROM school_operations
        ORDER BY id DESC
        LIMIT 5
        """
    ).fetchall()

    conn.close()

    attendance_rate = (
        round((attendance_present / attendance_today) * 100, 2)
        if attendance_today else 0
    )

    return {
        "organization": "Little Oaks Montessori Nursery & Kindergarten",
        "summary": {
            "students": students,
            "parents": parents,
            "classrooms": classrooms,
            "attendance_today": attendance_today,
            "attendance_rate": attendance_rate
        },
        "operations": {
            "open_tasks": open_operations
        },
        "recent_operations": recent_operations
    }
