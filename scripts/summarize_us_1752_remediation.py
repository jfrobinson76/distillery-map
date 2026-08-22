import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
BASE = ROOT / 'data/audit/us_1752_ttb_reconciliation'


def rows(path):
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def main():
    high = rows(BASE / 'map_high_confidence.csv')
    review = rows(BASE / 'map_review.csv')
    unmatched = rows(BASE / 'map_unmatched.csv')
    unmatched_permits = rows(BASE / 'ttb_permits_not_matched_to_map.csv')
    all_ttb_permits = rows(ROOT / 'data/enriched/ttb_dsp_raw.csv')
    unique_ttb_premises = {(r.get('street', '').strip().lower(), r.get('city', '').strip().lower(), r.get('state', '').strip().upper(), r.get('zip', '').strip()) for r in all_ttb_permits}
    unique_ttb_owner_names = {r.get('business_name', '').strip().lower() for r in all_ttb_permits if r.get('business_name', '').strip()}
    unique_ttb_dba_names = {r.get('dba_name', '').strip().lower() for r in all_ttb_permits if r.get('dba_name', '').strip()}
    high_permits = {r['permit_number'] for r in high if r['permit_number']}
    review_permits = {r['permit_number'] for r in review if r['permit_number']}
    all_permits = high_permits | review_permits
    permit_rows = defaultdict(list)
    for row in high + review:
        permit_rows[row['permit_number']].append(row)
    multiple_permit_map_records = {permit: matched for permit, matched in permit_rows.items() if permit and len(matched) > 1}
    unparsed = [r for r in unmatched if not r['state']]
    parsed_low_score = [r for r in unmatched if r['state']]
    output = [
        'US_1752_REMEDIATION_DETAIL',
        f'MAP_HIGH_CONFIDENCE_ROWS\t{len(high)}',
        f'MAP_REVIEW_ROWS\t{len(review)}',
        f'MAP_UNMATCHED_ROWS\t{len(unmatched)}',
        f'UNMATCHED_MAP_ROWS_WITH_UNPARSED_STATE\t{len(unparsed)}',
        f'UNMATCHED_MAP_ROWS_WITH_PARSED_STATE_LOW_SCORE\t{len(parsed_low_score)}',
        f'HIGH_ONLY_UNIQUE_TTB_PERMITS\t{len(high_permits - review_permits)}',
        f'REVIEW_ONLY_UNIQUE_TTB_PERMITS\t{len(review_permits - high_permits)}',
        f'TTB_PERMITS_MATCHED_BY_BOTH_HIGH_AND_REVIEW_MAP_ROWS\t{len(high_permits & review_permits)}',
        f'TOTAL_UNIQUE_TTB_PERMITS_WITH_MAP_CANDIDATE\t{len(all_permits)}',
        f'UNIQUE_TTB_PERMITS_MATCHED_TO_MULTIPLE_MAP_ROWS\t{len(multiple_permit_map_records)}',
        f'EXTRA_MAP_ROWS_BEYOND_ONE_PER_MATCHED_TTB_PERMIT\t{len(high) + len(review) - len(all_permits)}',
        f'TTB_PERMITS_WITHOUT_MAP_CANDIDATE\t{len(unmatched_permits)}',
        f'TTB_ACTIVE_UNIQUE_PREMISES\t{len(unique_ttb_premises)}',
        f'TTB_ACTIVE_UNIQUE_OWNER_NAMES\t{len(unique_ttb_owner_names)}',
        f'TTB_ACTIVE_UNIQUE_NONBLANK_DBA_NAMES\t{len(unique_ttb_dba_names)}',
        f'TTB_UNMATCHED_PERMITS_WITH_NEW_PERMIT_FLAG\t{sum(1 for r in unmatched_permits if r.get("New_Permit_Flag", "").strip())}',
        '',
        'TOP_TTB_PERMITS_WITHOUT_MAP_CANDIDATE_BY_STATE',
    ]
    by_state = Counter(r.get('state', '') or '(blank)' for r in unmatched_permits)
    output.extend(f'{count}\t{state}' for state, count in by_state.most_common(20))
    output.extend(['', 'TOP_UNMATCHED_MAP_ROWS_WITH_PARSED_STATE_BY_STATE'])
    map_states = Counter(r['state'] for r in parsed_low_score)
    output.extend(f'{count}\t{state}' for state, count in map_states.most_common(20))
    output.extend(['', 'HIGH_REVIEW_PERMIT_COLLISION_EXAMPLES'])
    for permit, matched in list(sorted(multiple_permit_map_records.items(), key=lambda item: (-len(item[1]), item[0])))[:25]:
        output.append(f'{permit}\t{len(matched)}\t' + ' | '.join(f"{r['bucket']}:{r['slug']}" for r in matched))
    text = '\n'.join(output) + '\n'
    (BASE / 'remediation_detail.tsv').write_text(text, encoding='utf-8')
    print(text, end='')


if __name__ == '__main__':
    main()
