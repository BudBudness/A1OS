PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS profiles (
  user_id TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  full_name TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('partner','advocate','clerk','finance','administrator','client')),
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS clients (
  id TEXT PRIMARY KEY,
  client_number TEXT NOT NULL UNIQUE,
  client_type TEXT NOT NULL,
  legal_name TEXT NOT NULL,
  phone TEXT,
  email TEXT,
  address TEXT,
  notes TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS matters (
  id TEXT PRIMARY KEY,
  matter_number TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  client_id TEXT NOT NULL REFERENCES clients(id),
  practice_area TEXT NOT NULL,
  matter_type TEXT,
  status TEXT NOT NULL DEFAULT 'intake',
  confidentiality TEXT NOT NULL DEFAULT 'restricted',
  description TEXT,
  opened_at TEXT,
  closed_at TEXT,
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS matter_members (
  matter_id TEXT NOT NULL REFERENCES matters(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
  assignment_role TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (matter_id,user_id)
);
CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  matter_id TEXT REFERENCES matters(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  assigned_to TEXT,
  status TEXT NOT NULL DEFAULT 'open',
  priority TEXT NOT NULL DEFAULT 'normal',
  due_at TEXT,
  completed_at TEXT,
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS deadlines (
  id TEXT PRIMARY KEY,
  matter_id TEXT NOT NULL REFERENCES matters(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  deadline_at TEXT NOT NULL,
  source TEXT,
  status TEXT NOT NULL DEFAULT 'open',
  owner_id TEXT,
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  matter_id TEXT NOT NULL REFERENCES matters(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  document_type TEXT NOT NULL,
  storage_path TEXT NOT NULL,
  mime_type TEXT,
  version INTEGER NOT NULL DEFAULT 1,
  checksum TEXT,
  uploaded_by TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS invoices (
  id TEXT PRIMARY KEY,
  matter_id TEXT NOT NULL REFERENCES matters(id) ON DELETE CASCADE,
  invoice_number TEXT NOT NULL UNIQUE,
  amount REAL NOT NULL CHECK (amount >= 0),
  currency TEXT NOT NULL DEFAULT 'UGX',
  status TEXT NOT NULL DEFAULT 'draft',
  due_date TEXT,
  issued_at TEXT,
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS payments (
  id TEXT PRIMARY KEY,
  invoice_id TEXT NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
  amount REAL NOT NULL CHECK (amount > 0),
  currency TEXT NOT NULL DEFAULT 'UGX',
  method TEXT,
  reference TEXT,
  paid_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  recorded_by TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research (
  id TEXT PRIMARY KEY,
  matter_id TEXT REFERENCES matters(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  source TEXT NOT NULL,
  citation TEXT,
  url TEXT,
  notes TEXT,
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS audit_events (
  id TEXT PRIMARY KEY,
  actor_id TEXT NOT NULL,
  matter_id TEXT,
  action TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  entity_id TEXT,
  metadata TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_matters_client ON matters(client_id);
CREATE INDEX IF NOT EXISTS idx_members_user ON matter_members(user_id,matter_id);
CREATE INDEX IF NOT EXISTS idx_deadlines_due ON deadlines(status,deadline_at);
CREATE INDEX IF NOT EXISTS idx_tasks_due ON tasks(status,due_at);
CREATE INDEX IF NOT EXISTS idx_docs_matter ON documents(matter_id,created_at);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_events(created_at);
