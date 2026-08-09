CREATE TABLE IF NOT EXISTS auth_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_hash TEXT NOT NULL UNIQUE,
    subject TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    expires_at INTEGER NOT NULL,
    revoked INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_auth_sessions_token
ON auth_sessions(token_hash);

CREATE INDEX IF NOT EXISTS idx_auth_sessions_expiry
ON auth_sessions(expires_at);

CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    value REAL NOT NULL,
    labels TEXT DEFAULT '',
    created_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_metrics_name_time
ON metrics(name, created_at);

CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    actor TEXT,
    payload TEXT,
    created_at INTEGER NOT NULL
);
