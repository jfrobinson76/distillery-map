"""
Phase 1 — Step 3: Fuzzy match GeoJSON US entities against TTB DSP registry.

Inputs:
  data/enriched/us_distilleries_seed.csv
  data/enriched/ttb_dsp_raw.csv

Outputs:
  data/enriched/matched_high_confidence.csv  (score >= 85)
  data/enriched/matched_review.csv           (score 70-84, needs human review)
  data/enriched/unmatched.csv                (score < 70 or no TTB record in state)

Idempotent — overwrites outputs on each run.
"""

import re
import csv
from pathlib import Path

import pandas as pd
from rapidfuzz import fuzz, process

SEED_PATH = Path(__file__).parent.parent / 'data' / 'enriched' / 'us_distilleries_seed.csv'
TTB_PATH = Path(__file__).parent.parent / 'data' / 'enriched' / 'ttb_dsp_raw.csv'

HIGH_CONF_PATH = Path(__file__).parent.parent / 'data' / 'enriched' / 'matched_high_confidence.csv'
REVIEW_PATH = Path(__file__).parent.parent / 'data' / 'enriched' / 'matched_review.csv'
UNMATCHED_PATH = Path(__file__).parent.parent / 'data' / 'enriched' / 'unmatched.csv'

HIGH_THRESH = 85
REVIEW_THRESH = 70

ADDR_ABBREV = {
    r'\bSt\b': 'Street',
    r'\bAve\b': 'Avenue',
    r'\bBlvd\b': 'Boulevard',
    r'\bDr\b': 'Drive',
    r'\bRd\b': 'Road',
    r'\bLn\b': 'Lane',
    r'\bCt\b': 'Court',
    r'\bPl\b': 'Place',
    r'\bHwy\b': 'Highway',
    r'\bPkwy\b': 'Parkway',
}


def normalise_name(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r'\b(distillery|distilleries|brewing|winery|spirits?|co\.|company|llc|inc\.?|ltd\.?)\b', '', name)
    name = re.sub(r'[^a-z0-9 ]', ' ', name)
    return re.sub(r'\s+', ' ', name).strip()


def normalise_address(addr: str) -> str:
    addr = addr.lower()
    for pattern, replacement in ADDR_ABBREV.items():
        addr = re.sub(pattern, replacement.lower(), addr, flags=re.I)
    addr = re.sub(r'[^a-z0-9 ]', ' ', addr)
    return re.sub(r'\s+', ' ', addr).strip()


def address_token_overlap(addr1: str, addr2: str) -> float:
    if not addr1 or not addr2:
        return 0.0
    t1 = set(normalise_address(addr1).split())
    t2 = set(normalise_address(addr2).split())
    stop = {'usa', 'us', 'suite', 'ste', 'unit', 'po', 'box', ''}
    t1 -= stop
    t2 -= stop
    if not t1 or not t2:
        return 0.0
    return len(t1 & t2) / max(len(t1), len(t2))


def match_entity(row, ttb_by_state: dict) -> dict:
    state = (row.get('state') or '').strip().upper()
    name = row.get('name', '')
    address = row.get('address', '')

    candidates = ttb_by_state.get(state, [])

    best_score = 0
    best_ttb = None
    norm_name = normalise_name(name)

    for ttb in candidates:
        for field in ('business_name', 'dba_name'):
            ttb_name = normalise_name(ttb.get(field, ''))
            if not ttb_name:
                continue
            score = fuzz.token_sort_ratio(norm_name, ttb_name)
            if score > best_score:
                best_score = score
                best_ttb = ttb

    match_method = 'name'

    if REVIEW_THRESH <= best_score < HIGH_THRESH and best_ttb:
        overlap = address_token_overlap(address, best_ttb.get('street', ''))
        if overlap >= 0.5:
            best_score = HIGH_THRESH
            match_method = 'name+address'

    if best_ttb and best_score >= REVIEW_THRESH:
        return {
            **row,
            'ttb_permit_number': best_ttb.get('permit_number', ''),
            'ttb_business_name': best_ttb.get('business_name', ''),
            'ttb_dba_name': best_ttb.get('dba_name', ''),
            'ttb_status': best_ttb.get('status', ''),
            'ttb_issue_date': best_ttb.get('issue_date', ''),
            'ttb_permit_type': best_ttb.get('permit_type', ''),
            'match_score': best_score,
            'match_method': match_method,
        }

    return {
        **row,
        'ttb_permit_number': '',
        'ttb_business_name': '',
        'ttb_dba_name': '',
        'ttb_status': '',
        'ttb_issue_date': '',
        'ttb_permit_type': '',
        'match_score': best_score,
        'match_method': 'none',
    }


def main():
    seed = pd.read_csv(SEED_PATH, dtype=str).fillna('')
    ttb = pd.read_csv(TTB_PATH, dtype=str).fillna('')

    ttb_by_state: dict[str, list] = {}
    for _, row in ttb.iterrows():
        state = (row.get('state') or '').strip().upper()
        ttb_by_state.setdefault(state, []).append(row.to_dict())

    high_conf = []
    review = []
    unmatched = []

    for _, row in seed.iterrows():
        result = match_entity(row.to_dict(), ttb_by_state)
        score = result['match_score']

        if score >= HIGH_THRESH:
            high_conf.append(result)
        elif score >= REVIEW_THRESH:
            review.append(result)
        else:
            unmatched.append(result)

    out_cols = list(seed.columns) + [
        'ttb_permit_number', 'ttb_business_name', 'ttb_dba_name',
        'ttb_status', 'ttb_issue_date', 'ttb_permit_type',
        'match_score', 'match_method',
    ]

    def write(path, rows):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=out_cols, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(rows)

    write(HIGH_CONF_PATH, high_conf)
    write(REVIEW_PATH, review)
    write(UNMATCHED_PATH, unmatched)

    total = len(seed)
    print(f'Total US seed entities:       {total}')
    print(f'High confidence (>={HIGH_THRESH}):     {len(high_conf)} ({len(high_conf)/total*100:.1f}%)')
    print(f'Review ({REVIEW_THRESH}-{HIGH_THRESH-1}):                {len(review)} ({len(review)/total*100:.1f}%)')
    print(f'Unmatched (<{REVIEW_THRESH}):           {len(unmatched)} ({len(unmatched)/total*100:.1f}%)')
    print(f'Outputs written to data/enriched/')


if __name__ == '__main__':
    main()
