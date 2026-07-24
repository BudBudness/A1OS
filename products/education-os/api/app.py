import secrets
from pathlib import Path
import sqlite3
from typing import Optional

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[3]
DB_PATH = ROOT / "products" / "education-os" / "deployments" / "little-oaks" / "data" / "education.db"



app = FastAPI(

    title="Little Oaks Montessori Nursery & Kindergarten — Education OS",
    version="0.1.0",
)

# =========================
# LITTLE OAKS AUTHENTICATION
# =========================

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from fastapi import Header

AUTH_SESSION_DAYS = 30

ROLE_PERMISSIONS = {
    "director_ceo_teacher": {
        "*"
    },

    "head_mistress": {
        "dashboard.view",
        "students.view",
        "students.create",
        "students.update",
        "admissions.view",
        "admissions.review",
        "attendance.view",
        "attendance.record",
        "operations.view",
        "operations.create",
        "operations.update",
        "fees.view",
        "reports.view",
        "academic.manage",
        "staff.view",
    },

    "staff": {
        "dashboard.view",
        "students.view",
        "attendance.view",
        "attendance.record",
        "operations.view",
        "operations.create",
    },
}


def _password_hash(password: str) -> str:
    salt = secrets.token_bytes(16)
    iterations = 310000
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        iterations,
    )
    return (
        f"pbkdf2_sha256$"
        f"{iterations}$"
        f"{salt.hex()}$"
        f"{digest.hex()}"
    )


def _verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = encoded.split("$")
        if algorithm != "pbkdf2_sha256":
            return False

        calculated = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            bytes.fromhex(salt_hex),
            int(iterations),
        )

        return hmac.compare_digest(
            calculated.hex(),
            digest_hex,
        )

    except Exception:
        return False


def _get_bearer_token(authorization: str | None):
    if not authorization:
        return None

    if not authorization.lower().startswith("bearer "):
        return None

    return authorization[7:].strip()


def _current_user(
    authorization: str | None = Header(default=None),
):
    token = _get_bearer_token(authorization)

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    with db() as conn:
        row = conn.execute(
            """
            SELECT
                u.id,
                u.organization_id,
                u.full_name,
                u.role,
                u.email,
                u.phone,
                u.active,
                s.session_token,
                s.expires_at
            FROM auth_sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.session_token = ?
            """,
            (token,),
        ).fetchone()

        if not row:
            raise HTTPException(
                status_code=401,
                detail="Invalid session",
            )

        if not row["active"]:
            raise HTTPException(
                status_code=403,
                detail="User account is inactive",
            )

        expires_at = datetime.fromisoformat(
            row["expires_at"].replace("Z", "+00:00")
        )

        if expires_at < datetime.now(timezone.utc):
            conn.execute(
                "DELETE FROM auth_sessions WHERE session_token = ?",
                (token,),
            )
            conn.commit()

            raise HTTPException(
                status_code=401,
                detail="Session expired",
            )

        conn.execute(
            """
            UPDATE auth_sessions
            SET last_used_at = CURRENT_TIMESTAMP
            WHERE session_token = ?
            """,
            (token,),
        )

        conn.commit()

        return dict(row)


def _require_permission(
    permission: str,
    authorization: str | None = Header(default=None),
):
    user = _current_user(authorization)

    permissions = ROLE_PERMISSIONS.get(
        user["role"],
        set(),
    )

    if "*" not in permissions and permission not in permissions:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied: {permission}",
        )

    return user


@app.post("/auth/login")
def auth_login(payload: dict):
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))

    if not email or not password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required",
        )

    with db() as conn:
        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE lower(email) = ?
            AND active = 1
            LIMIT 1
            """,
            (email,),
        ).fetchone()

        if not user or not user["password_hash"]:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
            )

        if not _verify_password(
            password,
            user["password_hash"],
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
            )

        token = secrets.token_urlsafe(48)

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(days=AUTH_SESSION_DAYS)
        ).isoformat()

        conn.execute(
            """
            INSERT INTO auth_sessions
            (
                user_id,
                session_token,
                expires_at
            )
            VALUES (?, ?, ?)
            """,
            (
                user["id"],
                token,
                expires_at,
            ),
        )

        conn.execute(
            """
            INSERT INTO audit_log
            (
                organization_id,
                actor_user_id,
                entity_type,
                entity_id,
                action,
                details
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user["organization_id"],
                user["id"],
                "auth",
                user["id"],
                "login",
                json.dumps({
                    "email": user["email"],
                    "role": user["role"],
                }),
            ),
        )

        conn.commit()

        return {
            "status": "authenticated",
            "token": token,
            "expires_at": expires_at,
            "user": {
                "id": user["id"],
                "full_name": user["full_name"],
                "role": user["role"],
                "email": user["email"],
                "permissions": list(
                    ROLE_PERMISSIONS.get(
                        user["role"],
                        set(),
                    )
                ),
            },
        }


@app.post("/auth/logout")
def auth_logout(
    authorization: str | None = Header(default=None),
):
    token = _get_bearer_token(authorization)

    if token:
        with db() as conn:
            conn.execute(
                """
                DELETE FROM auth_sessions
                WHERE session_token = ?
                """,
                (token,),
            )
            conn.commit()

    return {
        "status": "logged_out"
    }


@app.get("/auth/me")
def auth_me(
    authorization: str | None = Header(default=None),
):
    user = _current_user(authorization)

    return {
        "authenticated": True,
        "user": {
            "id": user["id"],
            "organization_id": user["organization_id"],
            "full_name": user["full_name"],
            "role": user["role"],
            "email": user["email"],
            "phone": user["phone"],
            "permissions": list(
                ROLE_PERMISSIONS.get(
                    user["role"],
                    set(),
                )
            ),
        },
    }


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
    enrollment_status: str = "active"

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

@app.get("/v1/health")
def v1_health():
    return {
        "status": "healthy",
        "product": "Education OS",
        "deployment": "Little Oaks Montessori Nursery & Kindergarten",
        "database": "connected"
    }

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
def create_student(payload: StudentCreate):
    with db() as conn:
        organization = conn.execute(
            """
            SELECT id
            FROM organization
            ORDER BY id
            LIMIT 1
            """
        ).fetchone()

        if not organization:
            raise HTTPException(
                status_code=500,
                detail="Organization not configured",
            )

        if payload.admission_number:
            admission_number = payload.admission_number
        else:
            next_number = conn.execute(
                """
                SELECT COALESCE(MAX(id), 0) + 1
                FROM students
                """
            ).fetchone()[0]
            admission_number = f"LO-{next_number:06d}"

        cursor = conn.execute(
            """
            INSERT INTO students
            (
                organization_id,
                admission_number,
                first_name,
                last_name,
                date_of_birth,
                gender,
                enrollment_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                organization["id"],
                admission_number,
                payload.first_name,
                payload.last_name,
                payload.date_of_birth,
                payload.gender,
                payload.enrollment_status,
            ),
        )

        conn.commit()

        return {
            "status": "created",
            "student_id": cursor.lastrowid,
            "organization_id": organization["id"],
        }


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


class AttendanceSessionCreate(BaseModel):
    attendance_date: str
    class_name: str
    notes: Optional[str] = None


class AttendanceRecordCreate(BaseModel):
    student_id: int
    status: str
    notes: Optional[str] = None


class SchoolOperationCreate(BaseModel):
    operation_type: str
    title: str
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[str] = None
    status: str = "open"


@app.post("/operations", status_code=201)
def create_school_operation(payload: SchoolOperationCreate):
    allowed_statuses = {"open", "in_progress", "completed", "cancelled"}

    if payload.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"status must be one of: {', '.join(sorted(allowed_statuses))}",
        )

    if not payload.operation_type.strip():
        raise HTTPException(
            status_code=400,
            detail="operation_type is required",
        )

    if not payload.title.strip():
        raise HTTPException(
            status_code=400,
            detail="title is required",
        )

    with db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO school_operations
            (
                operation_type,
                title,
                description,
                assigned_to,
                due_date,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload.operation_type,
                payload.title,
                payload.description,
                payload.assigned_to,
                payload.due_date,
                payload.status,
            ),
        )
        operation_id = cursor.lastrowid
        conn.commit()

    return {
        "status": "created",
        "operation_id": operation_id,
        "operation_type": payload.operation_type,
        "title": payload.title,
        "operation_status": payload.status,
    }


@app.get("/operations")
def list_school_operations(
    status: Optional[str] = None,
):
    with db() as conn:
        if status:
            rows = conn.execute(
                """
                SELECT
                    id,
                    operation_type,
                    title,
                    description,
                    assigned_to,
                    due_date,
                    status,
                    created_at,
                    updated_at
                FROM school_operations
                WHERE status = ?
                ORDER BY
                    CASE WHEN due_date IS NULL THEN 1 ELSE 0 END,
                    due_date ASC,
                    id DESC
                """,
                (status,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT
                    id,
                    operation_type,
                    title,
                    description,
                    assigned_to,
                    due_date,
                    status,
                    created_at,
                    updated_at
                FROM school_operations
                ORDER BY
                    CASE WHEN due_date IS NULL THEN 1 ELSE 0 END,
                    due_date ASC,
                    id DESC
                """
            ).fetchall()

    return [dict(row) for row in rows]


@app.get("/operations/{operation_id}")
def get_school_operation(operation_id: int):
    with db() as conn:
        row = conn.execute(
            """
            SELECT
                id,
                operation_type,
                title,
                description,
                assigned_to,
                due_date,
                status,
                created_at,
                updated_at
            FROM school_operations
            WHERE id = ?
            """,
            (operation_id,),
        ).fetchone()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="School operation not found",
        )

    return dict(row)


@app.patch("/operations/{operation_id}/status")
def update_school_operation_status(
    operation_id: int,
    status: str,
):
    allowed_statuses = {
        "open",
        "in_progress",
        "completed",
        "cancelled",
    }

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"status must be one of: {', '.join(sorted(allowed_statuses))}",
        )

    with db() as conn:
        cursor = conn.execute(
            """
            UPDATE school_operations
            SET status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, operation_id),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="School operation not found",
            )

        conn.commit()

    return {
        "status": "updated",
        "operation_id": operation_id,
        "operation_status": status,
    }


@app.post("/attendance/sessions", status_code=201)
def create_attendance_session(payload: AttendanceSessionCreate):
    if payload.attendance_date.strip() == "":
        raise HTTPException(status_code=400, detail="attendance_date is required")

    if payload.class_name.strip() == "":
        raise HTTPException(status_code=400, detail="class_name is required")

    with db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO attendance_sessions
            (attendance_date, class_name, notes)
            VALUES (?, ?, ?)
            """,
            (
                payload.attendance_date,
                payload.class_name,
                payload.notes,
            ),
        )
        session_id = cursor.lastrowid
        conn.commit()

    return {
        "status": "created",
        "session_id": session_id,
        "attendance_date": payload.attendance_date,
        "class_name": payload.class_name,
    }


@app.post("/attendance/sessions/{session_id}/records", status_code=201)
def record_attendance(
    session_id: int,
    payload: AttendanceRecordCreate,
):
    allowed = {"present", "absent", "late", "excused"}

    if payload.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"status must be one of: {', '.join(sorted(allowed))}",
        )

    with db() as conn:
        session = conn.execute(
            "SELECT id FROM attendance_sessions WHERE id = ?",
            (session_id,),
        ).fetchone()

        if not session:
            raise HTTPException(
                status_code=404,
                detail="Attendance session not found",
            )

        student = conn.execute(
            "SELECT id FROM students WHERE id = ?",
            (payload.student_id,),
        ).fetchone()

        if not student:
            raise HTTPException(
                status_code=404,
                detail="Student not found",
            )

        try:
            cursor = conn.execute(
                """
                INSERT INTO attendance_records
                (session_id, student_id, status, notes)
                VALUES (?, ?, ?, ?)
                """,
                (
                    session_id,
                    payload.student_id,
                    payload.status,
                    payload.notes,
                ),
            )
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=409,
                detail="Attendance already recorded for this student and session",
            )

        conn.commit()

    return {
        "status": "recorded",
        "record_id": cursor.lastrowid,
        "session_id": session_id,
        "student_id": payload.student_id,
        "attendance_status": payload.status,
    }


@app.get("/attendance/sessions")
def list_attendance_sessions():
    with db() as conn:
        rows = conn.execute(
            """
            SELECT
                id,
                attendance_date,
                class_name,
                notes,
                created_at
            FROM attendance_sessions
            ORDER BY attendance_date DESC, id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


@app.get("/attendance/sessions/{session_id}")
def get_attendance_session(session_id: int):
    with db() as conn:
        session = conn.execute(
            """
            SELECT
                id,
                attendance_date,
                class_name,
                notes,
                created_at
            FROM attendance_sessions
            WHERE id = ?
            """,
            (session_id,),
        ).fetchone()

        if not session:
            raise HTTPException(
                status_code=404,
                detail="Attendance session not found",
            )

        records = conn.execute(
            """
            SELECT
                ar.id,
                ar.student_id,
                s.first_name,
                s.last_name,
                ar.status,
                ar.notes,
                ar.created_at
            FROM attendance_records ar
            JOIN students s ON s.id = ar.student_id
            WHERE ar.session_id = ?
            ORDER BY s.last_name, s.first_name
            """,
            (session_id,),
        ).fetchall()

    result = dict(session)
    result["records"] = [dict(row) for row in records]
    return result


@app.post("/admissions")
def create_admission(admission: AdmissionCreate):
    conn = db()

    student = conn.execute(
        """
        SELECT
            id,
            first_name,
            last_name
        FROM students
        WHERE id = ?
        """,
        (admission.student_id,)
    ).fetchone()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    organization = conn.execute(
        "SELECT id FROM organization ORDER BY id LIMIT 1"
    ).fetchone()

    if not organization:
        raise HTTPException(
            status_code=500,
            detail="Organization not configured"
        )

    application_reference = f"LO-{admission.student_id:06d}"

    applicant_name = f"{student['first_name']} {student['last_name']}"

    cur = conn.execute(
        """
        INSERT INTO admissions
        (
            organization_id,
            application_reference,
            applicant_name,
            requested_class,
            status,
            decision_notes,
            student_id,
            admission_date,
            class_name,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            organization["id"],
            application_reference,
            applicant_name,
            admission.class_name,
            admission.status,
            admission.notes,
            admission.student_id,
            admission.admission_date,
            admission.class_name,
            admission.notes,
        ),
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
    conn = db()

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
    conn = db()

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
    conn = db()

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
