from pathlib import Path
import sqlite3
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[3]
DB_PATH = ROOT / "products" / "education-os" / "deployments" / "little-oaks" / "data" / "education.db"

app = FastAPI(
    title="Little Oaks Montessori Nursery & Kindergarten — Education OS",
    version="0.1.0",
)

class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    admission_number: Optional[str] = None

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

@app.get("/health")
def health():
    conn = db()
    try:
        conn.execute("SELECT 1")
        return {
            "status": "healthy",
            "product": "Education OS",
            "deployment": "Little Oaks Montessori Nursery & Kindergarten",
            "database": "connected",
        }
    finally:
        conn.close()

@app.get("/organization")
def organization():
    conn = db()
    try:
        row = conn.execute(
            "SELECT * FROM organization ORDER BY id LIMIT 1"
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Organization not configured"
            )

        return dict(row)
    finally:
        conn.close()

@app.post("/students", status_code=201)
def create_student(student: StudentCreate):
    conn = db()

    try:
        cursor = conn.execute(
            """
            INSERT INTO students
            (
                first_name,
                last_name,
                date_of_birth,
                gender,
                admission_number
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                student.first_name,
                student.last_name,
                student.date_of_birth,
                student.gender,
                student.admission_number,
            ),
        )

        conn.commit()

        row = conn.execute(
            "SELECT * FROM students WHERE id=?",
            (cursor.lastrowid,),
        ).fetchone()

        return dict(row)

    except sqlite3.IntegrityError as exc:
        conn.rollback()
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    finally:
        conn.close()

@app.get("/students")
def list_students():
    conn = db()

    try:
        rows = conn.execute(
            """
            SELECT *
            FROM students
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()

        return {
            "count": len(rows),
            "students": [dict(row) for row in rows],
        }

    finally:
        conn.close()

@app.get("/students/{student_id}")
def get_student(student_id: int):
    conn = db()

    try:
        row = conn.execute(
            "SELECT * FROM students WHERE id=?",
            (student_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Student not found",
            )

        return dict(row)

    finally:
        conn.close()
