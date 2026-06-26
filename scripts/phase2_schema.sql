-- Stillbound Intelligence Layer — Phase 2 Schema
-- SQLite-compatible. Postgres-ready (swap INTEGER PRIMARY KEY AUTOINCREMENT → SERIAL,
-- TEXT → VARCHAR, add explicit sequence naming for migration to Supabase Phase 3).

CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    lat REAL,
    lng REAL,
    website TEXT,
    geojson_source TEXT,
    review_needed INTEGER DEFAULT 0,   -- 1 = from matched_review.csv
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_source_id TEXT NOT NULL REFERENCES entities(source_id),
    address TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    UNIQUE(entity_source_id)
);

CREATE TABLE IF NOT EXISTS regulatory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_source_id TEXT NOT NULL REFERENCES entities(source_id),
    ttb_permit_number TEXT,
    ttb_business_name TEXT,
    ttb_dba_name TEXT,
    ttb_status TEXT,
    ttb_issue_date TEXT,
    ttb_permit_type TEXT,
    match_score REAL,
    match_method TEXT,
    state_license_number TEXT,
    state_license_source TEXT,
    UNIQUE(entity_source_id)
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_source_id TEXT REFERENCES entities(source_id),
    ttb_permit_number TEXT,
    cola_id TEXT UNIQUE,
    brand_name TEXT,
    product_name TEXT,
    class_type TEXT,
    approval_date TEXT,
    fanciful_name TEXT
);

CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_source_id TEXT REFERENCES entities(source_id),
    contact_name TEXT,
    contact_email TEXT,
    contact_role TEXT,
    source TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS enrichment_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    run_date TEXT DEFAULT (datetime('now')),
    rows_added INTEGER DEFAULT 0,
    rows_updated INTEGER DEFAULT 0,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_locations_state ON locations(state);
CREATE INDEX IF NOT EXISTS idx_regulatory_ttb_permit ON regulatory(ttb_permit_number);
CREATE INDEX IF NOT EXISTS idx_products_permit ON products(ttb_permit_number);
CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
