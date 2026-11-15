CREATE TABLE IF NOT EXISTS enquiry_reviews (
  enquiry_id TEXT PRIMARY KEY NOT NULL REFERENCES enquiries(id),
  decision TEXT NOT NULL CHECK (decision IN ('needs_review', 'follow_up', 'test_or_duplicate', 'closed')),
  assignee TEXT NOT NULL DEFAULT '',
  next_action TEXT NOT NULL DEFAULT '',
  updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
