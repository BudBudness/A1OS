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


@router.post("/students", status_code=201)
def create_student(payload: dict, request: Request):
    actor = _actor(request)
    conn = _conn(request)
    try:
        first_name = str(payload.get("first_name", "")).strip()
        if not first_name:
            raise HTTPException(status_code=400, detail="first_name is required")

        now = _now()
        cur = conn.execute(
            """
            INSERT INTO education_students
                (organization_id, admission_no, first_name, last_name,
                 gender, date_of_birth, class_name, status,
                 metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                actor["organization_id"],
                payload.get("admission_no"),
                first_name,
                payload.get("last_name"),
                payload.get("gender"),
                payload.get("date_of_birth"),
                payload.get("class_name"),
                payload.get("status", "active"),
                json.dumps(payload.get("metadata", {})),
                now,
                now,
            ),
        )
        conn.commit()

        row = conn.execute(
            """
            SELECT *
            FROM education_students
            WHERE id = ? AND organization_id = ?
            """,
            (cur.lastrowid, actor["organization_id"]),
        ).fetchone()

        return dict(row)
    finally:
        conn.close()


@router.patch("/students/{student_id}")
def update_student(student_id: int, payload: dict, request: Request):
    actor = _actor(request)
    conn = _conn(request)
    try:
        allowed = {
            "admission_no",
            "first_name",
            "last_name",
            "gender",
            "date_of_birth",
            "class_name",
            "status",
            "metadata",
        }

        fields = []
        values = []

        for key, value in payload.items():
            if key not in allowed:
                continue
            if key == "first_name":
                value = str(value).strip()
                if not value:
                    raise HTTPException(
                        status_code=400,
                        detail="first_name cannot be empty",
                    )
            if key == "metadata":
                value = json.dumps(value)
            fields.append(f"{key} = ?")
            values.append(value)

        if not fields:
            raise HTTPException(status_code=400, detail="No mutable fields supplied")

        fields.append("updated_at = ?")
        values.append(_now())

        values.extend([student_id, actor["organization_id"]])

        cur = conn.execute(
            f"""
            UPDATE education_students
            SET {", ".join(fields)}
            WHERE id = ? AND organization_id = ?
            """,
            values,
        )
        conn.commit()

        if cur.rowcount != 1:
            raise HTTPException(status_code=404, detail="Student not found")

        row = conn.execute(
            """
            SELECT *
            FROM education_students
            WHERE id = ? AND organization_id = ?
            """,
            (student_id, actor["organization_id"]),
        ).fetchone()

        return dict(row)
    finally:
        conn.close()


@router.delete("/students/{student_id}")
def archive_student(student_id: int, request: Request):
    actor = _actor(request)
    conn = _conn(request)
    try:
        cur = conn.execute(
            """
            UPDATE education_students
            SET status = 'archived', updated_at = ?
            WHERE id = ? AND organization_id = ?
            """,
            (_now(), student_id, actor["organization_id"]),
        )
        conn.commit()

        if cur.rowcount != 1:
            raise HTTPException(status_code=404, detail="Student not found")

        return {
            "status": "archived",
            "student_id": student_id,
            "organization_id": actor["organization_id"],
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



@router.post("/parents", status_code=201)
def create_parent(payload: dict, request: Request):
    actor = _actor(request)
    conn = _conn(request)
    try:
        _init_schema(conn)

        name = str(payload.get("name", "")).strip()
        if not name:
            raise HTTPException(status_code=400, detail="name is required")

        now = _now()
        cur = conn.execute(
            """
            INSERT INTO education_parents
                (organization_id, name, phone, email, relationship,
                 metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                actor["organization_id"],
                name,
                payload.get("phone"),
                payload.get("email"),
                payload.get("relationship"),
                json.dumps(payload.get("metadata", {})),
                now,
                now,
            ),
        )
        conn.commit()

        row = conn.execute(
            """
            SELECT *
            FROM education_parents
            WHERE id = ? AND organization_id = ?
            """,
            (cur.lastrowid, actor["organization_id"]),
        ).fetchone()

        return dict(row)
    finally:
        conn.close()


@router.patch("/parents/{parent_id}")
def update_parent(parent_id: int, payload: dict, request: Request):
    actor = _actor(request)
    conn = _conn(request)
    try:
        _init_schema(conn)

        row = conn.execute(
            """
            SELECT *
            FROM education_parents
            WHERE id = ? AND organization_id = ?
            """,
            (parent_id, actor["organization_id"]),
        ).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Parent not found")

        allowed = {
            "name",
            "phone",
            "email",
            "relationship",
            "metadata",
        }

        fields = []
        values = []

        for key in allowed:
            if key not in payload:
                continue

            value = payload[key]

            if key == "name":
                value = str(value).strip()
                if not value:
                    raise HTTPException(
                        status_code=400,
                        detail="name cannot be empty",
                    )

            if key == "metadata":
                value = json.dumps(value)

            fields.append(f"{key} = ?")
            values.append(value)

        if fields:
            fields.append("updated_at = ?")
            values.append(_now())
            values.extend([parent_id, actor["organization_id"]])

            conn.execute(
                f"""
                UPDATE education_parents
                SET {", ".join(fields)}
                WHERE id = ? AND organization_id = ?
                """,
                values,
            )
            conn.commit()

        updated = conn.execute(
            """
            SELECT *
            FROM education_parents
            WHERE id = ? AND organization_id = ?
            """,
            (parent_id, actor["organization_id"]),
        ).fetchone()

        return dict(updated)
    finally:
        conn.close()


@router.delete("/parents/{parent_id}")
def archive_parent(parent_id: int, request: Request):
    actor = _actor(request)
    conn = _conn(request)
    try:
        _init_schema(conn)

        row = conn.execute(
            """
            SELECT *
            FROM education_parents
            WHERE id = ? AND organization_id = ?
            """,
            (parent_id, actor["organization_id"]),
        ).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Parent not found")

        metadata = json.loads(row["metadata"] or "{}")
        metadata["archived"] = True
        metadata["archived_at"] = _now()

        conn.execute(
            """
            UPDATE education_parents
            SET metadata = ?, updated_at = ?
            WHERE id = ? AND organization_id = ?
            """,
            (
                json.dumps(metadata),
                _now(),
                parent_id,
                actor["organization_id"],
            ),
        )
        conn.commit()

        return {
            "status": "archived",
            "id": parent_id,
            "organization_id": actor["organization_id"],
        }
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



@router.post("/admissions", status_code=201)
def create_admission(payload: dict, request: Request):
    actor = _actor(request)
    conn = _conn(request)
    try:
        _init_schema(conn)
        applicant_name = str(payload.get("applicant_name", "")).strip()
        if not applicant_name:
            raise HTTPException(status_code=400, detail="applicant_name is required")
        now = _now()
        cur = conn.execute(
            """INSERT INTO education_admissions
               (organization_id, student_id, applicant_name, status,
                application_date, metadata, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (actor["organization_id"], payload.get("student_id"),
             applicant_name, payload.get("status","pending"),
             payload.get("application_date"),
             json.dumps(payload.get("metadata",{})), now, now))
        conn.commit()
        row=conn.execute(
            "SELECT * FROM education_admissions WHERE id=? AND organization_id=?",
            (cur.lastrowid,actor["organization_id"])).fetchone()
        return dict(row)
    finally:
        conn.close()


@router.patch("/admissions/{admission_id}")
def update_admission(admission_id:int,payload:dict,request:Request):
    actor=_actor(request); conn=_conn(request)
    try:
        _init_schema(conn)
        row=conn.execute(
            "SELECT * FROM education_admissions WHERE id=? AND organization_id=?",
            (admission_id,actor["organization_id"])).fetchone()
        if not row:
            raise HTTPException(status_code=404,detail="Admission not found")
        allowed={"student_id","applicant_name","status","application_date","metadata"}
        fields=[]; values=[]
        for k in allowed:
            if k in payload:
                v=payload[k]
                if k=="applicant_name":
                    v=str(v).strip()
                    if not v: raise HTTPException(status_code=400,detail="applicant_name cannot be empty")
                if k=="metadata": v=json.dumps(v)
                fields.append(f"{k}=?"); values.append(v)
        if fields:
            fields.append("updated_at=?"); values.append(_now())
            values += [admission_id,actor["organization_id"]]
            conn.execute(
                f"UPDATE education_admissions SET {','.join(fields)} WHERE id=? AND organization_id=?",
                values)
            conn.commit()
        return dict(conn.execute(
            "SELECT * FROM education_admissions WHERE id=? AND organization_id=?",
            (admission_id,actor["organization_id"])).fetchone())
    finally:
        conn.close()


@router.delete("/admissions/{admission_id}")
def archive_admission(admission_id:int,request:Request):
    actor=_actor(request); conn=_conn(request)
    try:
        _init_schema(conn)
        row=conn.execute(
            "SELECT * FROM education_admissions WHERE id=? AND organization_id=?",
            (admission_id,actor["organization_id"])).fetchone()
        if not row: raise HTTPException(status_code=404,detail="Admission not found")
        metadata=json.loads(row["metadata"] or "{}")
        metadata["archived"]=True
        metadata["archived_at"]=_now()
        conn.execute(
            "UPDATE education_admissions SET metadata=?,status='archived',updated_at=? WHERE id=? AND organization_id=?",
            (json.dumps(metadata),_now(),admission_id,actor["organization_id"]))
        conn.commit()
        return {"status":"archived","id":admission_id,"organization_id":actor["organization_id"]}
    finally:
        conn.close()


@router.post("/attendance", status_code=201)
def create_attendance(payload:dict,request:Request):
    actor=_actor(request); conn=_conn(request)
    try:
        _init_schema(conn)
        if payload.get("student_id") is None:
            raise HTTPException(status_code=400,detail="student_id is required")
        if not payload.get("attendance_date"):
            raise HTTPException(status_code=400,detail="attendance_date is required")
        if not payload.get("status"):
            raise HTTPException(status_code=400,detail="status is required")
        student=conn.execute(
            "SELECT id FROM education_students WHERE id=? AND organization_id=?",
            (payload["student_id"],actor["organization_id"])).fetchone()
        if not student:
            raise HTTPException(status_code=404,detail="Student not found")
        cur=conn.execute(
            """INSERT INTO education_attendance
               (organization_id,student_id,attendance_date,status,notes,created_at)
               VALUES (?,?,?,?,?,?)""",
            (actor["organization_id"],payload["student_id"],
             payload["attendance_date"],payload["status"],
             payload.get("notes"),_now()))
        conn.commit()
        return dict(conn.execute(
            "SELECT * FROM education_attendance WHERE id=? AND organization_id=?",
            (cur.lastrowid,actor["organization_id"])).fetchone())
    finally:
        conn.close()


@router.patch("/attendance/{attendance_id}")
def update_attendance(attendance_id:int,payload:dict,request:Request):
    actor=_actor(request); conn=_conn(request)
    try:
        _init_schema(conn)
        row=conn.execute(
            "SELECT * FROM education_attendance WHERE id=? AND organization_id=?",
            (attendance_id,actor["organization_id"])).fetchone()
        if not row: raise HTTPException(status_code=404,detail="Attendance not found")
        allowed={"student_id","attendance_date","status","notes"}
        fields=[]; values=[]
        for k in allowed:
            if k in payload:
                if k=="student_id":
                    st=conn.execute(
                        "SELECT id FROM education_students WHERE id=? AND organization_id=?",
                        (payload[k],actor["organization_id"])).fetchone()
                    if not st: raise HTTPException(status_code=404,detail="Student not found")
                fields.append(f"{k}=?"); values.append(payload[k])
        if fields:
            values += [attendance_id,actor["organization_id"]]
            conn.execute(
                f"UPDATE education_attendance SET {','.join(fields)} WHERE id=? AND organization_id=?",
                values)
            conn.commit()
        return dict(conn.execute(
            "SELECT * FROM education_attendance WHERE id=? AND organization_id=?",
            (attendance_id,actor["organization_id"])).fetchone())
    finally:
        conn.close()


@router.delete("/attendance/{attendance_id}")
def delete_attendance(attendance_id:int,request:Request):
    actor=_actor(request); conn=_conn(request)
    try:
        row=conn.execute(
            "SELECT id FROM education_attendance WHERE id=? AND organization_id=?",
            (attendance_id,actor["organization_id"])).fetchone()
        if not row: raise HTTPException(status_code=404,detail="Attendance not found")
        conn.execute(
            "DELETE FROM education_attendance WHERE id=? AND organization_id=?",
            (attendance_id,actor["organization_id"]))
        conn.commit()
        return {"status":"deleted","id":attendance_id,"organization_id":actor["organization_id"]}
    finally:
        conn.close()


@router.post("/fees", status_code=201)
def create_fee(payload:dict,request:Request):
    actor=_actor(request); conn=_conn(request)
    try:
        _init_schema(conn)
        description=str(payload.get("description","")).strip()
        if not description: raise HTTPException(status_code=400,detail="description is required")
        if payload.get("student_id") is not None:
            st=conn.execute(
                "SELECT id FROM education_students WHERE id=? AND organization_id=?",
                (payload["student_id"],actor["organization_id"])).fetchone()
            if not st: raise HTTPException(status_code=404,detail="Student not found")
        now=_now()
        cur=conn.execute(
            """INSERT INTO education_fees
               (organization_id,student_id,description,amount,status,due_date,created_at,updated_at)
               VALUES (?,?,?,?,?,?,?,?)""",
            (actor["organization_id"],payload.get("student_id"),description,
             float(payload.get("amount",0)),payload.get("status","pending"),
             payload.get("due_date"),now,now))
        conn.commit()
        return dict(conn.execute(
            "SELECT * FROM education_fees WHERE id=? AND organization_id=?",
            (cur.lastrowid,actor["organization_id"])).fetchone())
    finally:
        conn.close()


@router.patch("/fees/{fee_id}")
def update_fee(fee_id:int,payload:dict,request:Request):
    actor=_actor(request); conn=_conn(request)
    try:
        row=conn.execute(
            "SELECT * FROM education_fees WHERE id=? AND organization_id=?",
            (fee_id,actor["organization_id"])).fetchone()
        if not row: raise HTTPException(status_code=404,detail="Fee not found")
        allowed={"student_id","description","amount","status","due_date"}
        fields=[]; values=[]
        for k in allowed:
            if k in payload:
                if k=="student_id" and payload[k] is not None:
                    st=conn.execute(
                        "SELECT id FROM education_students WHERE id=? AND organization_id=?",
                        (payload[k],actor["organization_id"])).fetchone()
                    if not st: raise HTTPException(status_code=404,detail="Student not found")
                if k=="description":
                    payload[k]=str(payload[k]).strip()
                fields.append(f"{k}=?"); values.append(payload[k])
        if fields:
            fields.append("updated_at=?"); values.append(_now())
            values += [fee_id,actor["organization_id"]]
            conn.execute(
                f"UPDATE education_fees SET {','.join(fields)} WHERE id=? AND organization_id=?",
                values)
            conn.commit()
        return dict(conn.execute(
            "SELECT * FROM education_fees WHERE id=? AND organization_id=?",
            (fee_id,actor["organization_id"])).fetchone())
    finally:
        conn.close()


@router.delete("/fees/{fee_id}")
def archive_fee(fee_id:int,request:Request):
    actor=_actor(request); conn=_conn(request)
    try:
        row=conn.execute(
            "SELECT * FROM education_fees WHERE id=? AND organization_id=?",
            (fee_id,actor["organization_id"])).fetchone()
        if not row: raise HTTPException(status_code=404,detail="Fee not found")
        conn.execute(
            "UPDATE education_fees SET status='archived',updated_at=? WHERE id=? AND organization_id=?",
            (_now(),fee_id,actor["organization_id"]))
        conn.commit()
        return {"status":"archived","id":fee_id,"organization_id":actor["organization_id"]}
    finally:
        conn.close()


@router.post("/site-content", status_code=201)
def create_site_content(payload:dict,request:Request):
    actor=_actor(request); conn=_conn(request)
    try:
        _init_schema(conn)
        key=str(payload.get("content_key","")).strip()
        if not key: raise HTTPException(status_code=400,detail="content_key is required")
        now=_now()
        try:
            cur=conn.execute(
                """INSERT INTO education_site_content
                   (organization_id,content_key,content,updated_at)
                   VALUES (?,?,?,?)""",
                (actor["organization_id"],key,str(payload.get("content","")),now))
            conn.commit()
        except Exception:
            raise HTTPException(status_code=409,detail="content_key already exists")
        return dict(conn.execute(
            "SELECT * FROM education_site_content WHERE id=? AND organization_id=?",
            (cur.lastrowid,actor["organization_id"])).fetchone())
    finally:
        conn.close()


@router.patch("/site-content/{content_id}")
def update_site_content(content_id:int,payload:dict,request:Request):
    actor=_actor(request); conn=_conn(request)
    try:
        row=conn.execute(
            "SELECT * FROM education_site_content WHERE id=? AND organization_id=?",
            (content_id,actor["organization_id"])).fetchone()
        if not row: raise HTTPException(status_code=404,detail="Site content not found")
        fields=[]; values=[]
        for k in ("content_key","content"):
            if k in payload:
                v=str(payload[k]).strip() if k=="content_key" else str(payload[k])
                fields.append(f"{k}=?"); values.append(v)
        if fields:
            fields.append("updated_at=?"); values.append(_now())
            values += [content_id,actor["organization_id"]]
            conn.execute(
                f"UPDATE education_site_content SET {','.join(fields)} WHERE id=? AND organization_id=?",
                values)
            conn.commit()
        return dict(conn.execute(
            "SELECT * FROM education_site_content WHERE id=? AND organization_id=?",
            (content_id,actor["organization_id"])).fetchone())
    finally:
        conn.close()


@router.delete("/site-content/{content_id}")
def delete_site_content(content_id:int,request:Request):
    actor=_actor(request); conn=_conn(request)
    try:
        row=conn.execute(
            "SELECT id FROM education_site_content WHERE id=? AND organization_id=?",
            (content_id,actor["organization_id"])).fetchone()
        if not row: raise HTTPException(status_code=404,detail="Site content not found")
        conn.execute(
            "DELETE FROM education_site_content WHERE id=? AND organization_id=?",
            (content_id,actor["organization_id"]))
        conn.commit()
        return {"status":"deleted","id":content_id,"organization_id":actor["organization_id"]}
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
