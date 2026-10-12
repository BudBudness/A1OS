-- A1OS Charity vertical additive schema.
-- SQLite-compatible. Apply only after the core platform schema.sql.
-- Every record is organization-scoped; application routes MUST derive organization_id
-- from the authenticated actor and must never trust a client-supplied tenant ID.

CREATE TABLE IF NOT EXISTS charity_programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('draft', 'active', 'paused', 'closed')),
    start_date TEXT,
    end_date TEXT,
    created_by INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (organization_id, code),
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS charity_beneficiaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    party_id INTEGER,
    beneficiary_ref TEXT NOT NULL,
    household_ref TEXT,
    vulnerability_category TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'verified', 'active', 'paused', 'exited', 'rejected')),
    consent_status TEXT NOT NULL DEFAULT 'pending'
        CHECK (consent_status IN ('pending', 'granted', 'declined', 'withdrawn')),
    consent_recorded_at TEXT,
    restricted_attributes_json TEXT NOT NULL DEFAULT '{}',
    created_by INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (organization_id, beneficiary_ref),
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (party_id) REFERENCES parties(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS charity_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    case_ref TEXT NOT NULL,
    beneficiary_id INTEGER NOT NULL,
    program_id INTEGER,
    assigned_to INTEGER,
    case_type TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'normal'
        CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    status TEXT NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'assessment', 'approved', 'on_hold', 'closed', 'rejected')),
    summary TEXT NOT NULL,
    restricted_notes TEXT,
    opened_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TEXT,
    created_by INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (organization_id, case_ref),
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (beneficiary_id) REFERENCES charity_beneficiaries(id),
    FOREIGN KEY (program_id) REFERENCES charity_programs(id),
    FOREIGN KEY (assigned_to) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS charity_aid_allocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    allocation_ref TEXT NOT NULL,
    beneficiary_id INTEGER NOT NULL,
    case_id INTEGER,
    program_id INTEGER,
    aid_type TEXT NOT NULL,
    description TEXT NOT NULL,
    quantity REAL NOT NULL DEFAULT 1 CHECK (quantity > 0),
    amount_ugx INTEGER NOT NULL DEFAULT 0 CHECK (amount_ugx >= 0),
    status TEXT NOT NULL DEFAULT 'proposed'
        CHECK (status IN ('proposed', 'approved', 'rejected', 'disbursed', 'cancelled')),
    approved_by INTEGER,
    approved_at TEXT,
    disbursed_by INTEGER,
    disbursed_at TEXT,
    evidence_ref TEXT,
    created_by INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (organization_id, allocation_ref),
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (beneficiary_id) REFERENCES charity_beneficiaries(id),
    FOREIGN KEY (case_id) REFERENCES charity_cases(id),
    FOREIGN KEY (program_id) REFERENCES charity_programs(id),
    FOREIGN KEY (approved_by) REFERENCES users(id),
    FOREIGN KEY (disbursed_by) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS charity_donors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    party_id INTEGER,
    donor_ref TEXT NOT NULL,
    donor_type TEXT NOT NULL DEFAULT 'individual'
        CHECK (donor_type IN ('individual', 'organization', 'anonymous')),
    consent_to_contact INTEGER NOT NULL DEFAULT 0 CHECK (consent_to_contact IN (0, 1)),
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'do_not_contact')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (organization_id, donor_ref),
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (party_id) REFERENCES parties(id)
);

CREATE TABLE IF NOT EXISTS charity_donation_intents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    intent_ref TEXT NOT NULL,
    donor_id INTEGER,
    program_id INTEGER,
    amount_ugx INTEGER NOT NULL CHECK (amount_ugx > 0),
    currency TEXT NOT NULL DEFAULT 'UGX' CHECK (currency = 'UGX'),
    channel TEXT,
    provider_reference TEXT,
    idempotency_key TEXT,
    status TEXT NOT NULL DEFAULT 'intent'
        CHECK (status IN ('intent', 'pending_verification', 'confirmed', 'failed', 'refunded', 'cancelled')),
    provider_verified_at TEXT,
    confirmed_at TEXT,
    created_by INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (organization_id, intent_ref),
    UNIQUE (organization_id, idempotency_key),
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (donor_id) REFERENCES charity_donors(id),
    FOREIGN KEY (program_id) REFERENCES charity_programs(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS charity_volunteers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    party_id INTEGER,
    volunteer_ref TEXT NOT NULL,
    skills_json TEXT NOT NULL DEFAULT '[]',
    availability_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'applicant'
        CHECK (status IN ('applicant', 'active', 'paused', 'inactive', 'rejected')),
    screening_status TEXT NOT NULL DEFAULT 'pending'
        CHECK (screening_status IN ('pending', 'passed', 'failed', 'not_required')),
    created_by INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (organization_id, volunteer_ref),
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (party_id) REFERENCES parties(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS charity_partnerships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    party_id INTEGER,
    partnership_ref TEXT NOT NULL,
    partnership_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'prospect'
        CHECK (status IN ('prospect', 'active', 'paused', 'ended', 'rejected')),
    agreement_ref TEXT,
    start_date TEXT,
    end_date TEXT,
    notes TEXT,
    created_by INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (organization_id, partnership_ref),
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (party_id) REFERENCES parties(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS charity_outreach_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    report_ref TEXT NOT NULL,
    program_id INTEGER,
    event_name TEXT NOT NULL,
    event_date TEXT NOT NULL,
    location TEXT,
    people_reached INTEGER NOT NULL DEFAULT 0 CHECK (people_reached >= 0),
    summary TEXT NOT NULL,
    evidence_refs_json TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'submitted', 'approved', 'rejected')),
    approved_by INTEGER,
    approved_at TEXT,
    created_by INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (organization_id, report_ref),
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (program_id) REFERENCES charity_programs(id),
    FOREIGN KEY (approved_by) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_charity_beneficiaries_org_status
    ON charity_beneficiaries (organization_id, status);
CREATE INDEX IF NOT EXISTS idx_charity_cases_org_status
    ON charity_cases (organization_id, status, priority);
CREATE INDEX IF NOT EXISTS idx_charity_aid_org_status
    ON charity_aid_allocations (organization_id, status);
CREATE INDEX IF NOT EXISTS idx_charity_donations_org_status
    ON charity_donation_intents (organization_id, status, created_at);
CREATE INDEX IF NOT EXISTS idx_charity_reports_org_date
    ON charity_outreach_reports (organization_id, event_date);
