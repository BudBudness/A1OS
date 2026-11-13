CREATE TABLE IF NOT EXISTS enquiries (
  id TEXT PRIMARY KEY NOT NULL,
  parent_name TEXT,
  child_name TEXT,
  child_age TEXT,
  programme TEXT DEFAULT '',
  phone TEXT,
  message TEXT DEFAULT '',
  status TEXT,
  created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
