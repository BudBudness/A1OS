CREATE TABLE IF NOT EXISTS a1os_tasks (
  task_id TEXT PRIMARY KEY NOT NULL,
  target TEXT NOT NULL,
  role TEXT NOT NULL,
  action TEXT NOT NULL,
  payload TEXT NOT NULL CHECK (json_valid(payload)),
  status TEXT NOT NULL DEFAULT 'queued',
  attempts INTEGER NOT NULL DEFAULT 0,
  max_attempts INTEGER NOT NULL DEFAULT 3 CHECK (max_attempts > 0),
  error TEXT,
  next_attempt_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  completed_at TEXT,
  lease_token TEXT,
  lease_expires_at TEXT
);
CREATE INDEX IF NOT EXISTS a1os_tasks_status_idx
ON a1os_tasks (status, created_at, task_id);
CREATE INDEX IF NOT EXISTS a1os_tasks_lease_idx
ON a1os_tasks (status, lease_expires_at);
