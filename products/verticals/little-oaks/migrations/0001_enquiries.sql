CREATE TABLE IF NOT EXISTS enquiries (
  id TEXT PRIMARY KEY NOT NULL,
  parent_name TEXT NOT NULL,
  child_name TEXT NOT NULL,
  child_age TEXT NOT NULL,
  programme TEXT NOT NULL DEFAULT '',
  phone TEXT NOT NULL,
  message TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
