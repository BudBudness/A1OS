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

class AdmissionCreate(BaseModel):
    student_id: int
    admission_date: str
    class_name: str
    status: str = "pending"
    notes: str | None = None


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


@app.post("/admissions")
def create_admission(admission: AdmissionCreate):
    conn = get_db()

    student = conn.execute(
        "SELECT id FROM students WHERE id = ?",
        (admission.student_id,)
    ).fetchone()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    cur = conn.execute(
        '''
        INSERT INTO admissions
        (student_id, admission_date, class_name, status, notes)
        VALUES (?, ?, ?, ?, ?)
        ''',
        (
            admission.student_id,
            admission.admission_date,
            admission.class_name,
            admission.status,
            admission.notes,
        )
    )

    conn.commit()

    return {
        "status": "created",
        "admission_id": cur.lastrowid,
        "student_id": admission.student_id,
        "admission_date": admission.admission_date,
        "class_name": admission.class_name,
        "admission_status": admission.status,
    }


@app.get("/admissions")
def list_admissions():
    conn = get_db()

    rows = conn.execute(
        '''
        SELECT
            a.id,
            a.student_id,
            s.first_name,
            s.last_name,
            a.admission_date,
            a.class_name,
            a.status,
            a.notes,
            a.created_at
        FROM admissions a
        JOIN students s ON s.id = a.student_id
        ORDER BY a.created_at DESC
        '''
    ).fetchall()

    return [dict(row) for row in rows]


@app.get("/admissions/{admission_id}")
def get_admission(admission_id: int):
    conn = get_db()

    row = conn.execute(
        '''
        SELECT
            a.id,
            a.student_id,
            s.first_name,
            s.last_name,
            a.admission_date,
            a.class_name,
            a.status,
            a.notes,
            a.created_at
        FROM admissions a
        JOIN students s ON s.id = a.student_id
        WHERE a.id = ?
        ''',
        (admission_id,)
    ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Admission not found")

    return dict(row)


@app.patch("/admissions/{admission_id}/status")
def update_admission_status(admission_id: int, status: str):
    conn = get_db()

    cur = conn.execute(
        "UPDATE admissions SET status = ? WHERE id = ?",
        (status, admission_id)
    )

    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Admission not found")

    conn.commit()

    return {
        "status": "updated",
        "admission_id": admission_id,
        "admission_status": status,
    }
