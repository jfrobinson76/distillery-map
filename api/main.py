"""
Stillbound Intelligence API — read-only query layer over the distillery DB.

Start: uvicorn api.main:app --reload
Auth:  X-API-Key header (set in .env as STILLBOUND_API_KEY)
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader

DB_PATH = Path(__file__).parent.parent / "data" / "stillbound_intelligence.db"

app = FastAPI(
    title="Stillbound Intelligence API",
    description="Internal read-only API for the distillery intelligence layer.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://distillerymap.org"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(key: Optional[str] = Depends(api_key_header)) -> str:
    expected = os.environ.get("STILLBOUND_API_KEY", "")
    if not expected:
        raise HTTPException(status_code=500, detail="API key not configured")
    if key != expected:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return key


def get_db() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise HTTPException(status_code=503, detail="Database not initialised — run Phase 2 pipeline")
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


@app.get("/stats")
def stats(_key: str = Depends(require_api_key)):
    """Coverage summary by state."""
    con = get_db()
    try:
        total = con.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        with_ttb = con.execute(
            "SELECT COUNT(*) FROM regulatory WHERE ttb_permit_number IS NOT NULL"
        ).fetchone()[0]
        with_state_lic = con.execute(
            "SELECT COUNT(*) FROM regulatory WHERE state_license_number IS NOT NULL"
        ).fetchone()[0]
        products_count = con.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        by_state = con.execute(
            """SELECT l.state, COUNT(*) AS count
               FROM locations l
               WHERE l.state IS NOT NULL AND l.state != ''
               GROUP BY l.state ORDER BY count DESC"""
        ).fetchall()

        return {
            "total_entities": total,
            "ttb_matched": with_ttb,
            "state_licensed": with_state_lic,
            "products_linked": products_count,
            "by_state": [{"state": r["state"], "count": r["count"]} for r in by_state],
        }
    finally:
        con.close()


@app.get("/entities")
def list_entities(
    state: Optional[str] = Query(None, description="2-letter state code, e.g. KY"),
    review_only: bool = Query(False, description="Only return review-flagged matches"),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
    _key: str = Depends(require_api_key),
):
    """List entities with location and regulatory data."""
    con = get_db()
    try:
        conditions = []
        params: list = []

        if state:
            conditions.append("l.state = ?")
            params.append(state.upper())
        if review_only:
            conditions.append("e.review_needed = 1")

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        params += [limit, offset]

        rows = con.execute(
            f"""SELECT e.source_id, e.name, e.lat, e.lng, e.website, e.review_needed,
                       l.address, l.city, l.state, l.zip,
                       r.ttb_permit_number, r.ttb_status, r.match_score,
                       r.state_license_number, r.state_license_source
                FROM entities e
                LEFT JOIN locations l ON l.entity_source_id = e.source_id
                LEFT JOIN regulatory r ON r.entity_source_id = e.source_id
                {where}
                ORDER BY e.name
                LIMIT ? OFFSET ?""",
            params,
        ).fetchall()

        total = con.execute(
            f"""SELECT COUNT(*) FROM entities e
                LEFT JOIN locations l ON l.entity_source_id = e.source_id
                {where.replace('LIMIT ? OFFSET ?', '') if where else ''}""",
            params[:-2],
        ).fetchone()[0]

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": [dict(r) for r in rows],
        }
    finally:
        con.close()


@app.get("/entities/{source_id}")
def get_entity(source_id: str, _key: str = Depends(require_api_key)):
    """Full record including products."""
    con = get_db()
    try:
        entity = con.execute(
            """SELECT e.*, l.address, l.city, l.state, l.zip,
                      r.ttb_permit_number, r.ttb_business_name, r.ttb_dba_name,
                      r.ttb_status, r.ttb_issue_date, r.ttb_permit_type,
                      r.match_score, r.match_method,
                      r.state_license_number, r.state_license_source
               FROM entities e
               LEFT JOIN locations l ON l.entity_source_id = e.source_id
               LEFT JOIN regulatory r ON r.entity_source_id = e.source_id
               WHERE e.source_id = ?""",
            (source_id,),
        ).fetchone()

        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")

        products = con.execute(
            "SELECT * FROM products WHERE entity_source_id = ? ORDER BY approval_date DESC",
            (source_id,),
        ).fetchall()

        return {
            **dict(entity),
            "products": [dict(p) for p in products],
        }
    finally:
        con.close()


@app.get("/health")
def health():
    return {"status": "ok", "db_exists": DB_PATH.exists()}
