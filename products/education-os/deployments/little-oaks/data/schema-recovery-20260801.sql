PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE organization (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    organization_type TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO organization VALUES(1,'Little Oaks Montessori Nursery & Kindergarten','school','2026-08-01 06:01:35');
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, password_hash TEXT,
    FOREIGN KEY (organization_id) REFERENCES organization(id)
);
INSERT INTO users VALUES(1,1,'Leticia Byamugisha','director_ceo_teacher','leticia@littleoaks.ug',NULL,1,'2026-07-24 16:51:31','pbkdf2_sha256$310000$34043bb02094ee7736859c8f3e3d5b53$5486aa15f96d3861948998f3e61c7b30cb654a460dab211bf012e7ae14b2b8ec');
INSERT INTO users VALUES(2,1,'Head Mistress','head_mistress','headmistress@littleoaks.ug',NULL,1,'2026-07-24 16:51:40',NULL);
INSERT INTO users VALUES(3,1,'Little Oaks Staff','staff','staff@littleoaks.ug',NULL,1,'2026-07-24 16:51:51',NULL);
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    admission_number TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT,
    gender TEXT,
    class_level TEXT,
    enrollment_status TEXT NOT NULL DEFAULT 'active',
    guardian_name TEXT,
    guardian_phone TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organization(id)
);
INSERT INTO students VALUES(1,1,'LO-000001','Verification','Student','2020-01-01','female',NULL,'active',NULL,NULL,'2026-07-23 16:46:16','2026-07-23 16:46:16');
INSERT INTO students VALUES(2,1,'LO-000002','Verification','Student','2020-01-01','female',NULL,'active',NULL,NULL,'2026-07-23 16:48:27','2026-07-23 16:48:27');
INSERT INTO students VALUES(3,1,'LO-000003','Verification','Student','2020-01-01','female',NULL,'active',NULL,NULL,'2026-07-23 16:49:39','2026-07-23 16:49:39');
INSERT INTO students VALUES(4,1,'LO-000004','Verification','Student','2020-01-01','female',NULL,'active',NULL,NULL,'2026-07-23 17:17:31','2026-07-23 17:17:31');
INSERT INTO students VALUES(5,1,'LO-000005','Verification','Student','2020-01-01','female',NULL,'active',NULL,NULL,'2026-07-23 17:18:23','2026-07-23 17:18:23');
INSERT INTO students VALUES(6,1,'LO-000006','Verification','Student','2020-01-01','female',NULL,'active',NULL,NULL,'2026-07-23 17:34:37','2026-07-23 17:34:37');
INSERT INTO students VALUES(7,1,'LO-000007','Verification','Student','2020-01-01','female',NULL,'active',NULL,NULL,'2026-07-23 17:36:35','2026-07-23 17:36:35');
INSERT INTO students VALUES(8,1,'LO-000008','Verification','Student','2020-01-01','female',NULL,'active',NULL,NULL,'2026-07-23 17:39:45','2026-07-23 17:39:45');
INSERT INTO students VALUES(9,1,'LO-000009','Verification','Student','2020-01-01','female',NULL,'active',NULL,NULL,'2026-07-23 17:47:02','2026-07-23 17:47:02');
INSERT INTO students VALUES(10,1,'LO-000010','Frontend','Integration-c8f7507e','2020-01-01','female',NULL,'active',NULL,NULL,'2026-07-23 22:48:36','2026-07-23 22:48:36');
CREATE TABLE admissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    application_reference TEXT NOT NULL UNIQUE,
    applicant_name TEXT NOT NULL,
    requested_class TEXT,
    guardian_name TEXT,
    guardian_phone TEXT,
    status TEXT NOT NULL DEFAULT 'submitted',
    decision_notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organization(id)
);
INSERT INTO admissions VALUES(1,1,'LO-000010','Frontend Integration-c8f7507e','Nursery',NULL,NULL,'pending',NULL,'2026-07-23 22:48:36','2026-07-23 22:48:36');
INSERT INTO admissions VALUES(2,1,'LO-000010-91AEBC6D','Frontend Integration-c8f7507e','Production Acceptance Verification',NULL,NULL,'pending',NULL,'2026-07-24 19:26:15','2026-07-24 19:26:15');
INSERT INTO admissions VALUES(3,1,'LO-000010-EA0563B6','Frontend Integration-c8f7507e','Production Acceptance Verification',NULL,NULL,'pending',NULL,'2026-07-24 19:27:00','2026-07-24 19:27:00');
INSERT INTO admissions VALUES(4,1,'LO-000010-65987369','Frontend Integration-c8f7507e','Production Acceptance Verification',NULL,NULL,'pending',NULL,'2026-07-24 19:28:49','2026-07-24 19:28:49');
INSERT INTO admissions VALUES(5,1,'LO-000010-89C0577A','Frontend Integration-c8f7507e','Final Acceptance 223202',NULL,NULL,'pending',NULL,'2026-07-24 19:32:02','2026-07-24 19:32:02');
INSERT INTO admissions VALUES(6,1,'LO-000010-8202D5E0','Frontend Integration-c8f7507e','Final Acceptance 1784921662',NULL,NULL,'pending',NULL,'2026-07-24 19:34:22','2026-07-24 19:34:22');
CREATE TABLE fee_obligations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    academic_period TEXT NOT NULL,
    fee_type TEXT NOT NULL,
    amount REAL NOT NULL CHECK (amount >= 0),
    amount_paid REAL NOT NULL DEFAULT 0 CHECK (amount_paid >= 0),
    due_date TEXT,
    status TEXT NOT NULL DEFAULT 'outstanding',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organization(id),
    FOREIGN KEY (student_id) REFERENCES students(id)
);
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    fee_obligation_id INTEGER,
    payment_reference TEXT NOT NULL UNIQUE,
    amount REAL NOT NULL CHECK (amount > 0),
    payment_method TEXT NOT NULL,
    transaction_reference TEXT,
    verification_status TEXT NOT NULL DEFAULT 'pending',
    paid_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organization(id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (fee_obligation_id) REFERENCES fee_obligations(id)
);
INSERT INTO payments VALUES(1,1,10,1,'E2E-20260724-001',250000.0,'mobile_money','E2E-20260724-001','verified','2026-07-24 17:23:53');
INSERT INTO payments VALUES(2,1,10,NULL,'RBAC-director_ceo_teacher',1.0,'test',NULL,'verified','2026-07-24 17:24:38');
CREATE TABLE attendance_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    session_date TEXT NOT NULL,
    class_level TEXT NOT NULL,
    recorded_by INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (organization_id, session_date, class_level),
    FOREIGN KEY (organization_id) REFERENCES organization(id),
    FOREIGN KEY (recorded_by) REFERENCES users(id)
);
CREATE TABLE attendance_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('present', 'absent', 'late', 'excused')),
    notes TEXT,
    recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (session_id, student_id),
    FOREIGN KEY (session_id) REFERENCES attendance_sessions(id),
    FOREIGN KEY (student_id) REFERENCES students(id)
);
CREATE TABLE school_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    operation_type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'open',
    assigned_to INTEGER,
    due_date TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organization(id),
    FOREIGN KEY (assigned_to) REFERENCES users(id)
);
INSERT INTO school_operations VALUES(1,1,'production_acceptance_verification','Final Live Operations Acceptance','Final production workflow verification','open',NULL,NULL,'2026-07-24 19:34:23','2026-07-24 19:34:23');
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    actor_user_id INTEGER,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organization(id),
    FOREIGN KEY (actor_user_id) REFERENCES users(id)
);
INSERT INTO audit_log VALUES(158,1,1,'auth',1,'login','{"email": "leticia@littleoaks.ug", "role": "director_ceo_teacher"}','2026-08-01 06:02:14');
INSERT INTO audit_log VALUES(159,1,1,'auth',1,'login','{"email": "leticia@littleoaks.ug", "role": "director_ceo_teacher"}','2026-08-01 06:03:51');
CREATE TABLE auth_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT NOT NULL UNIQUE,
    expires_at TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP, session_token TEXT, last_used_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
INSERT INTO auth_sessions VALUES(153,1,'H9FJ3GPLlkOoArj4ZTIQ5X0Rg1_rAwXIgJhNDdI6j-UuOTcGbxHCXcLuuv0QyxC8','2026-08-31T05:59:04.072092+00:00','2026-08-01 05:59:04',NULL,'2026-08-01 06:03:37');
INSERT INTO auth_sessions VALUES(154,1,'w_ir-_fl7h7Ay5RO5c9DeODycaxSlE7efgSSSS3HCufObJe-JPDnWuEQbpe4JOLx','2026-08-31T06:02:14.477082+00:00','2026-08-01 06:02:14',NULL,'2026-08-01 06:03:37');
INSERT INTO auth_sessions VALUES(155,1,'WlWqvNqvczVfUQMq9CNtMsdH7DKAuCDmANX37kj9g0v8aelu1fP8norUGPP9PUm1','2026-08-31T06:03:51.542264+00:00','2026-08-01 06:03:51',NULL,'2026-08-01 06:03:52');
PRAGMA writable_schema=ON;
CREATE TABLE IF NOT EXISTS sqlite_sequence(name,seq);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('organization',1);
INSERT INTO sqlite_sequence VALUES('students',14);
INSERT INTO sqlite_sequence VALUES('admissions',6);
INSERT INTO sqlite_sequence VALUES('users',3);
INSERT INTO sqlite_sequence VALUES('auth_sessions',155);
INSERT INTO sqlite_sequence VALUES('audit_log',159);
INSERT INTO sqlite_sequence VALUES('fee_obligations',2);
INSERT INTO sqlite_sequence VALUES('payments',2);
INSERT INTO sqlite_sequence VALUES('attendance_sessions',4);
INSERT INTO sqlite_sequence VALUES('school_operations',5);
INSERT INTO sqlite_sequence VALUES('academic_years',3);
INSERT INTO sqlite_sequence VALUES('academic_periods',4);
INSERT INTO sqlite_sequence VALUES('class_levels',4);
PRAGMA writable_schema=OFF;
COMMIT;
