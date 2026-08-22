from pathlib import Path
import csv
import json
import re
from collections import Counter

ROOT = Path(__file__).parent.parent
ENRICHED = ROOT / 'data' / 'enriched'
GEOJSON = ROOT / 'public' / 'data' / 'distilleries.geojson'


def norm(value: str) -> str:
    value = (value or '').lower().strip()
    return re.sub(r'\s+', ' ', value)


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def main():
    geo = json.loads(GEOJSON.read_text(encoding='utf-8'))
    map_us = [feature for feature in geo['features'] if feature.get('properties', {}).get('region') == 'usa']
    map_us_country = [feature for feature in map_us if feature.get('properties', {}).get('country') == 'United States']
    ttb = read_csv(ENRICHED / 'ttb_dsp_raw.csv')
    high = read_csv(ENRICHED / 'matched_high_confidence.csv')
    review = read_csv(ENRICHED / 'matched_review.csv')
    unmatched = read_csv(ENRICHED / 'unmatched.csv')

    high_permits = {row['ttb_permit_number'] for row in high if row.get('ttb_permit_number')}
    review_permits = {row['ttb_permit_number'] for row in review if row.get('ttb_permit_number')}
    matched_permits = high_permits | review_permits
    all_permits = {row['permit_number'] for row in ttb if row.get('permit_number')}

    unique_owner = {norm(row.get('business_name', '')) for row in ttb if norm(row.get('business_name', ''))}
    unique_dba = {norm(row.get('dba_name', '')) for row in ttb if norm(row.get('dba_name', ''))}
    source_counts = Counter(feature.get('properties', {}).get('source', '(blank)') for feature in map_us_country)
    region_country_counts = Counter(feature.get('properties', {}).get('country', '(blank)') for feature in map_us)
    map_names = Counter(norm(feature.get('properties', {}).get('name', '')) for feature in map_us)
    duplicate_map_names = sum(1 for count in map_names.values() if count > 1)
    ttb_by_state = Counter(row.get('state', '') for row in ttb)

    print('TTB_COMPARISON_AUDIT')
    print(f'TTB_ACTIVE_PERMIT_RECORDS\t{len(ttb)}')
    print(f'TTB_UNIQUE_PERMIT_NUMBERS\t{len(all_permits)}')
    print(f'TTB_UNIQUE_OWNER_NAMES\t{len(unique_owner)}')
    print(f'TTB_UNIQUE_NONBLANK_DBA_NAMES\t{len(unique_dba)}')
    print(f'TTB_ROWS_WITH_BLANK_DBA\t{sum(1 for row in ttb if not norm(row.get("dba_name", "")))}')
    print(f'MAP_US_REGION_RECORDS\t{len(map_us)}')
    print(f'MAP_UNITED_STATES_COUNTRY_RECORDS\t{len(map_us_country)}')
    print(f'MAP_DUPLICATE_NORMALIZED_NAMES_IN_US_REGION\t{duplicate_map_names}')
    print(f'HIGH_CONFIDENCE_MAP_ROWS\t{len(high)}')
    print(f'REVIEW_MAP_ROWS\t{len(review)}')
    print(f'UNMATCHED_MAP_ROWS\t{len(unmatched)}')
    print(f'UNIQUE_TTB_PERMITS_MATCHED_BY_MAP\t{len(matched_permits)}')
    print(f'TTB_PERMITS_NOT_MATCHED_TO_MAP\t{len(all_permits - matched_permits)}')
    print(f'MAP_ROWS_WITH_UNPARSED_STATE\t{sum(1 for row in unmatched if not row.get("state", "").strip())}')

    print('\nMAP_US_COUNTRY_BREAKDOWN')
    for country, count in region_country_counts.most_common():
        print(f'{count}\t{country}')
    print('\nMAP_UNITED_STATES_SOURCE_BREAKDOWN')
    for source, count in source_counts.most_common():
        print(f'{count}\t{source}')
    print('\nTOP_TTB_STATES')
    for state, count in ttb_by_state.most_common(15):
        print(f'{count}\t{state}')


if __name__ == '__main__':
    main()
