PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS tasks (
  task_id TEXT PRIMARY KEY,
  target TEXT NOT NULL CHECK(length(target) BETWEEN 1 AND 120),
  role TEXT NOT NULL CHECK(length(role) BETWEEN 1 AND 80),
  action TEXT NOT NULL CHECK(length(action) BETWEEN 1 AND 120),
  payload_json TEXT NOT NULL CHECK(json_valid(payload_json)),
  status TEXT NOT NULL DEFAULT 'queued'
    CHECK(status IN ('queued','running','retry','completed','failed')),
  attempts INTEGER NOT NULL DEFAULT 0 CHECK(attempts >= 0),
  max_attempts INTEGER NOT NULL DEFAULT 3 CHECK(max_attempts BETWEEN 1 AND 20),
  error TEXT,
  next_attempt_at TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  completed_at TEXT
);

CREATE INDEX IF NOT EXISTS tasks_ready_idx
  ON tasks(status, next_attempt_at, created_at);
CREATE INDEX IF NOT EXISTS tasks_stale_idx
  ON tasks(status, updated_at);
