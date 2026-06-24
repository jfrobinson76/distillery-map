"""
Phase 1 — Step 4: Generate enrichment validation report.

Reads all Phase 1 output CSVs and writes data/enriched/enrichment_report.txt.
"""

from datetime import datetime, timezone
from pathlib import Path
from collections import Counter

import pandas as pd

BASE = Path(__file__).parent.parent / 'data' / 'enriched'

HIGH_CONF_PATH = BASE / 'matched_high_confidence.csv'
REVIEW_PATH = BASE / 'matched_review.csv'
UNMATCHED_PATH = BASE / 'unmatched.csv'
TTB_PATH = BASE / 'ttb_dsp_raw.csv'
REPORT_PATH = BASE / 'enrichment_report.txt'
SEED_PATH = BASE / 'us_distilleries_seed.csv'


def load(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str).fillna('')


def main():
    seed = load(SEED_PATH)
    high = load(HIGH_CONF_PATH)
    review = load(REVIEW_PATH)
    unmatched = load(UNMATCHED_PATH)
    ttb = load(TTB_PATH)

    total_us = len(seed)
    total_ttb = len(ttb)
    n_high = len(high)
    n_review = len(review)
    n_unmatched = len(unmatched)

    pct = lambda n: f'{n/total_us*100:.1f}%' if total_us else 'N/A'

    unmatched_states = Counter(unmatched['state'].tolist()) if 'state' in unmatched.columns else Counter()
    top_unmatched = unmatched_states.most_common(10)

    inactive = []
    if not high.empty and 'ttb_status' in high.columns:
        inactive = high[high['ttb_status'].str.upper() != 'ACTIVE'][
            ['ttb_permit_number', 'name', 'state', 'ttb_status']
        ].values.tolist()

    state_parse_fail = seed[seed['state'] == ''].shape[0] if 'state' in seed.columns else 'N/A'
    ttb_no_dba = ttb[ttb['dba_name'] == ''].shape[0] if 'dba_name' in ttb.columns else 'N/A'

    lines = [
        'STILLBOUND ENRICHMENT REPORT — Phase 1',
        f'Generated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}',
        '',
        'INPUT STATS',
        f'  GeoJSON US entities:         {total_us}',
        f'  TTB DSP records:             {total_ttb}',
        '',
        'MATCH RESULTS',
        f'  High confidence (>=85):      {n_high} ({pct(n_high)})',
        f'  Review (70-84):              {n_review} ({pct(n_review)})',
        f'  Unmatched (<70):             {n_unmatched} ({pct(n_unmatched)})',
        '',
        'TOP UNMATCHED STATES',
    ]

    if top_unmatched:
        for state, count in top_unmatched:
            label = state if state else '(no state parsed)'
            lines.append(f'  {label:<6} {count}')
    else:
        lines.append('  (no unmatched records)')

    lines += [
        '',
        'TTB STATUS FLAGS (matched entities where status != ACTIVE)',
    ]

    if inactive:
        for permit, name, state, status in inactive:
            lines.append(f'  {permit:<20} {name[:40]:<40} {state:<4} {status}')
    else:
        lines.append('  (none — all matched entities are ACTIVE)')

    lines += [
        '',
        'NOTES',
        f'  Rows where state parse failed:   {state_parse_fail}',
        f'  TTB records with blank dba_name: {ttb_no_dba}',
        '',
        'NEXT STEP',
        '  Review matched_review.csv for borderline matches.',
        '  If high-confidence match rate < 30%, investigate TTB column mapping',
        '  or state parse failures before proceeding to Phase 2.',
    ]

    report_text = '\n'.join(lines)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report_text, encoding='utf-8')

    print(report_text)
    print(f'\nReport saved: {REPORT_PATH}')


if __name__ == '__main__':
    main()
