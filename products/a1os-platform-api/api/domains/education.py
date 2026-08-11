import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request

router = APIRouter(tags=["education"])


def _now():
    return datetime.now(timezone.utc).isoformat()


def _conn(request: Request):
    from api.app import DB_PATH
    import sqlite3
    conn = sqlite3.connect(DB_PATH, timeout=30.0, isolation_level=None)
    conn.row_factory = sqlite3.Row
    return conn


def _actor(request: Request):
    actor = getattr(request.state, "actor", None)
    if not actor:
        raise HTTPException(status_code=401, detail="Authentication required")
    if not actor.get("organization_id"):
        raise HTTPException(status_code=403, detail="Organization context required")
    return actor


def _init_schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS education_students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        organization_id INTEGER NOT NULL,
        admission_no TEXT,
        first_name TEXT NOT NULL,
        last_name TEXT,
        gender TEXT,
        date_of_birth TEXT,
        class_name TEXT,
        status TEXT NOT NULL DEFAULT 'active',
        metadata TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_education_students_org
        ON education_students(organization_id);

    CREATE TABLE IF NOT EXISTS education_parents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        organization_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        relationship TEXT,
        metadata TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_education_parents_org
        ON education_parents(organization_id);

    CREATE TABLE IF NOT EXISTS education_admissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        organization_id INTEGER NOT NULL,
        student_id INTEGER,
        applicant_name TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        application_date TEXT,
        metadata TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_education_admissions_org
        ON education_admissions(organization_id);

    CREATE TABLE IF NOT EXISTS education_attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        organization_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        attendance_date TEXT NOT NULL,
        status TEXT NOT NULL,
        notes TEXT,
        created_at TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_education_attendance_org_date
        ON education_attendance(organization_id, attendance_date);

    CREATE TABLE IF NOT EXISTS education_fees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        organization_id INTEGER NOT NULL,
        student_id INTEGER,
        description TEXT NOT NULL,
        amount REAL NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'pending',
        due_date TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_education_fees_org
        ON education_fees(organization_id);

    CREATE TABLE IF NOT EXISTS education_site_content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        organization_id INTEGER NOT NULL,
        content_key TEXT NOT NULL,
        content TEXT NOT NULL DEFAULT '',
        updated_at TEXT NOT NULL,
        UNIQUE(organization_id, content_key)
    );

    CREATE INDEX IF NOT EXISTS idx_education_site_content_org
        ON education_site_content(organization_id);
    """)
    conn.commit()


def _rows(conn, sql, params=()):
    return [dict(row) for row in conn.execute(sql, params).fetchall()]


@router.get("/health")
def health(request: Request):
    conn = _conn(request)
    try:
        _init_schema(conn)
        return {
            "status": "ok",
            "domain": "education",
            "persistence": "ready",
        }
    finally:
        conn.close()


@router.get("/students")
def students(request: Request):
    actor = _actor(request)
    conn = _conn(request)
    try:
        _init_schema(conn)
        return _rows(
            conn,
            """
            SELECT *
            FROM education_students
            WHERE organization_id = ?
            ORDER BY id DESC
            """,
            (actor["organization_id"],),
        )
    finally:
        conn.close()


@router.get("/parents")
def parents(request: Request):
    actor = _actor(request)
    conn = _conn(request)
    try:
        _init_schema(conn)
        return _rows(
            conn,
            """
            SELECT *
            FROM education_parents
            WHERE organization_id = ?
            ORDER BY id DESC
            """,
            (actor["organization_id"],),
        )
    finally:
        conn.close()


@router.get("/admissions")
def admissions(request: Request):
    actor = _actor(request)
    conn = _conn(request)
    try:
        _init_schema(conn)
        return _rows(
            conn,
            """
            SELECT *
            FROM education_admissions
            WHERE organization_id = ?
            ORDER BY id DESC
            """,
            (actor["organization_id"],),
        )
    finally:
        conn.close()


@router.get("/attendance")
def attendance(request: Request):
    actor = _actor(request)
    conn = _conn(request)
    try:
        _init_schema(conn)
        return _rows(
            conn,
            """
            SELECT *
            FROM education_attendance
            WHERE organization_id = ?
            ORDER BY attendance_date DESC, id DESC
            """,
            (actor["organization_id"],),
        )
    finally:
        conn.close()


@router.get("/fees")
def fees(request: Request):
    actor = _actor(request)
    conn = _conn(request)
    try:
        _init_schema(conn)
        return _rows(
            conn,
            """
            SELECT *
            FROM education_fees
            WHERE organization_id = ?
            ORDER BY id DESC
            """,
            (actor["organization_id"],),
        )
    finally:
        conn.close()


@router.get("/intelligence")
def intelligence(request: Request):
    actor = _actor(request)
    conn = _conn(request)
    try:
        _init_schema(conn)
        org = actor["organization_id"]

        students = conn.execute(
            "SELECT COUNT(*) FROM education_students WHERE organization_id = ?",
            (org,),
        ).fetchone()[0]

        admissions = conn.execute(
            "SELECT COUNT(*) FROM education_admissions WHERE organization_id = ?",
            (org,),
        ).fetchone()[0]

        attendance = conn.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) AS present
            FROM education_attendance
            WHERE organization_id = ?
            """,
            (org,),
        ).fetchone()

        fees = conn.execute(
            """
            SELECT
                COALESCE(SUM(amount), 0) AS total,
                COALESCE(SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END), 0) AS paid
            FROM education_fees
            WHERE organization_id = ?
            """,
            (org,),
        ).fetchone()

        return {
            "organization_id": org,
            "students": students,
            "admissions": admissions,
            "attendance": {
                "records": attendance["total"] or 0,
                "present": attendance["present"] or 0,
            },
            "fees": {
                "total": fees["total"] or 0,
                "paid": fees["paid"] or 0,
                "outstanding": (fees["total"] or 0) - (fees["paid"] or 0),
            },
            "generated_at": _now(),
        }
    finally:
        conn.close()


@router.get("/site-content")
def site_content(request: Request):
    actor = _actor(request)
    conn = _conn(request)
    try:
        _init_schema(conn)
        return _rows(
            conn,
            """
            SELECT content_key, content, updated_at
            FROM education_site_content
            WHERE organization_id = ?
            ORDER BY content_key
            """,
            (actor["organization_id"],),
        )
    finally:
        conn.close()
