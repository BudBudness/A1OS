CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    industry TEXT NOT NULL DEFAULT 'general',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'member',
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

CREATE TABLE IF NOT EXISTS auth_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT NOT NULL UNIQUE,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    permissions TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (organization_id, name)
);

CREATE TABLE IF NOT EXISTS parties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    party_type TEXT NOT NULL DEFAULT 'customer',
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    location TEXT,
    external_ref TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    sku TEXT NOT NULL UNIQUE,
    category TEXT,
    unit TEXT NOT NULL DEFAULT 'kg',
    cost_price REAL,
    selling_price REAL,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    account_type TEXT NOT NULL,
    name TEXT NOT NULL,
    party_id INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (party_id) REFERENCES parties(id)
);

CREATE TABLE IF NOT EXISTS ledger_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    entry_date TEXT NOT NULL,
    description TEXT,
    debit_account_id INTEGER NOT NULL,
    credit_account_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK (amount >= 0),
    reference TEXT,
    created_by INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (debit_account_id) REFERENCES accounts(id),
    FOREIGN KEY (credit_account_id) REFERENCES accounts(id)
);

CREATE TABLE IF NOT EXISTS stock_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    warehouse TEXT NOT NULL DEFAULT 'main',
    quantity REAL NOT NULL DEFAULT 0,
    unit_cost REAL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (organization_id, product_id, warehouse),
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    warehouse TEXT NOT NULL DEFAULT 'main',
    movement_type TEXT NOT NULL,
    quantity REAL NOT NULL,
    reference TEXT,
    created_by INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    channel TEXT NOT NULL DEFAULT 'inapp',
    recipient TEXT,
    subject TEXT,
    body TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    actor_user_id INTEGER,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (actor_user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_ledger_org_date ON ledger_entries (organization_id, entry_date);
CREATE INDEX IF NOT EXISTS idx_movements_org_product ON stock_movements (organization_id, product_id);
CREATE INDEX IF NOT EXISTS idx_audit_org ON audit_log (organization_id, created_at);
CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY AUTOINCREMENT, organization_id INTEGER NOT NULL, customer_party_id INTEGER, sale_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, status TEXT NOT NULL DEFAULT 'completed', subtotal REAL NOT NULL DEFAULT 0 CHECK (subtotal >= 0), total REAL NOT NULL DEFAULT 0 CHECK (total >= 0), payment_status TEXT NOT NULL DEFAULT 'unpaid', reference TEXT, created_by INTEGER, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (organization_id) REFERENCES organizations(id), FOREIGN KEY (customer_party_id) REFERENCES parties(id), FOREIGN KEY (created_by) REFERENCES users(id));
CREATE TABLE IF NOT EXISTS sale_items (id INTEGER PRIMARY KEY AUTOINCREMENT, sale_id INTEGER NOT NULL, organization_id INTEGER NOT NULL, product_id INTEGER NOT NULL, quantity REAL NOT NULL CHECK (quantity > 0), unit_price REAL NOT NULL CHECK (unit_price >= 0), line_total REAL NOT NULL CHECK (line_total >= 0), FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE, FOREIGN KEY (organization_id) REFERENCES organizations(id), FOREIGN KEY (product_id) REFERENCES products(id));
CREATE TABLE IF NOT EXISTS sale_payments (id INTEGER PRIMARY KEY AUTOINCREMENT, sale_id INTEGER NOT NULL, organization_id INTEGER NOT NULL, method TEXT NOT NULL, amount REAL NOT NULL CHECK (amount > 0), reference TEXT, created_by INTEGER, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE, FOREIGN KEY (organization_id) REFERENCES organizations(id), FOREIGN KEY (created_by) REFERENCES users(id));
CREATE INDEX IF NOT EXISTS idx_sales_org_date ON sales (organization_id, sale_date);
CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON sale_items (sale_id);
CREATE INDEX IF NOT EXISTS idx_sale_payments_sale ON sale_payments (sale_id);

