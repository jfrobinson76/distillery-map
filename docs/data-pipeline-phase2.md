# Stillbound Data Pipeline — Phase 2 Scope

Phase 2 is gated on John validating Phase 1 match quality.

## Gate check

Before starting Phase 2, review:
- `data/enriched/matched_high_confidence.csv` — 1,122 matches at ≥85 score
- `data/enriched/matched_review.csv` — 123 borderline matches (70–84)

Regenerate Phase 1 outputs from scratch:

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements_data.txt
.venv/bin/python scripts/phase1_parse_geojson.py
.venv/bin/python scripts/phase1_fetch_ttb.py
.venv/bin/python scripts/phase1_match.py
.venv/bin/python scripts/phase1_report.py
```

## Phase 2 deliverables

- `scripts/phase2_schema.sql` — Postgres 15 schema
  Tables: entities, locations, regulatory, products, contacts, enrichment_log
- `scripts/phase2_loaders/` — one loader per source
  - `load_phase1_matched.py` — matched_high_confidence.csv → entities + locations + regulatory
  - `load_ttb_cola.py` — COLA approvals → products
- `scripts/phase2_state_scrapers/` — one scraper per state
  - CA, NY, TX, KY, CO (priority states for craft spirits licensing)
- `api/main.py` — FastAPI read-only API (single API key, internal only)
- `docker-compose.yml` — Postgres 15 + FastAPI
- `README_DATA.md` — setup instructions and data source index

## Stack additions (append to requirements_data.txt)

```
fastapi>=0.115
sqlalchemy>=2.0
asyncpg>=0.30
uvicorn>=0.30
httpx>=0.27
```

## Plan file

Full build brief: `~/.claude/plans/stillbound-data-layer-synchronous-honey.md`
