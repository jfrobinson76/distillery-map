-- Phase 2B schema migration — adds columns needed for website verification,
-- global entity loading, new entrant signals, and contact enrichment.
-- Safe to run multiple times (uses IF NOT EXISTS / IGNORE patterns where possible).
-- SQLite does not support IF NOT EXISTS on ALTER TABLE — each ADD COLUMN will
-- silently fail if the column already exists; that is fine for idempotency.

-- Website verification columns on entities
ALTER TABLE entities ADD COLUMN website_status TEXT;         -- LIVE / REDIRECT / DEAD / NO_WEBSITE
ALTER TABLE entities ADD COLUMN website_checked_date TEXT;
ALTER TABLE entities ADD COLUMN region TEXT;                 -- 'ireland', 'scotland', 'uk', 'usa', etc.

-- New entrant flag on regulatory
ALTER TABLE regulatory ADD COLUMN is_new_entrant INTEGER DEFAULT 0;

-- Signals table — matches between entities and RSS/news stories
CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_source_id TEXT REFERENCES entities(source_id),
    signal_type TEXT NOT NULL,    -- 'new_entrant', 'rss_mention', 'expansion', 'exec_hire'
    source TEXT,                  -- feed id or 'ttb_new_permit' etc.
    headline TEXT,
    url TEXT,
    published_date TEXT,
    matched_name TEXT,            -- which entity name matched
    detected_date TEXT,
    actioned INTEGER DEFAULT 0    -- 1 = John has seen / acted on this
);

CREATE INDEX IF NOT EXISTS idx_signals_entity ON signals(entity_source_id);
CREATE INDEX IF NOT EXISTS idx_signals_type ON signals(signal_type);
CREATE INDEX IF NOT EXISTS idx_signals_actioned ON signals(actioned);
