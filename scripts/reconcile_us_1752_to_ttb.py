import csv, json, re
from collections import Counter, defaultdict
from pathlib import Path
from rapidfuzz import fuzz

ROOT = Path(__file__).parent.parent
GEO = ROOT / 'public/data/distilleries.geojson'
TTB = ROOT / 'data/enriched/ttb_dsp_raw.csv'
OUT = ROOT / 'data/audit/us_1752_ttb_reconciliation'
HIGH, REVIEW = 85, 70
STATE_RE = re.compile(r',\s*([A-Z]{2})(?:\s+\d{5}(?:-\d{4})?)?(?:\s*,\s*USA?)?$')


def state(address):
    m = STATE_RE.search(address or '')
    return m.group(1) if m else ''


def norm_name(value):
    value = (value or '').lower().strip()
    value = re.sub(r'\b(distillery|distilleries|brewing|winery|spirits?|co\.|company|llc|inc\.?|ltd\.?)\b', '', value)
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', value)).strip()


def norm_address(value):
    value = (value or '').lower()
    value = re.sub(r'\b(st)\b', 'street', value)
    value = re.sub(r'\b(ave)\b', 'avenue', value)
    value = re.sub(r'\b(rd)\b', 'road', value)
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', value)).strip()


def overlap(left, right):
    a, b = set(norm_address(left).split()), set(norm_address(right).split())
    a -= {'usa','us','suite','ste','unit','po','box',''}
    b -= {'usa','us','suite','ste','unit','po','box',''}
    return len(a & b) / max(len(a), len(b)) if a and b else 0


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    features = json.loads(GEO.read_text(encoding='utf-8'))['features']
    with TTB.open(encoding='utf-8-sig', newline='') as f: permits = list(csv.DictReader(f))
    sites = []
    for f in features:
        p = f.get('properties', {})
        if p.get('country') == 'United States' and p.get('region') == 'usa':
            sites.append({'slug':p.get('slug',''),'name':p.get('name',''),'address':p.get('address','') or '', 'state':'', 'source':p.get('source','') or ''})
    for site in sites: site['state'] = state(site['address'])
    by_state = defaultdict(list)
    for permit in permits: by_state[permit.get('state','')].append(permit)
    rows = []
    for site in sites:
        best_score, best = 0, None
        for permit in by_state[site['state']]:
            for field in ('business_name','dba_name'):
                candidate = norm_name(permit.get(field,''))
                if candidate:
                    score = fuzz.token_sort_ratio(norm_name(site['name']), candidate)
                    if score > best_score: best_score, best = score, permit
        address_overlap = overlap(site['address'], best.get('street','')) if best else 0
        method = 'name'
        if REVIEW <= best_score < HIGH and address_overlap >= .5: best_score, method = HIGH, 'name+address'
        bucket = 'high_confidence' if best_score >= HIGH else 'review' if best_score >= REVIEW else 'unmatched'
        rows.append({**site, 'bucket':bucket, 'score':round(best_score,1), 'method':method if bucket != 'unmatched' else 'none', 'address_overlap':round(address_overlap,3), 'permit_number':best.get('permit_number','') if best and bucket != 'unmatched' else '', 'permit_owner':best.get('business_name','') if best and bucket != 'unmatched' else '', 'permit_dba':best.get('dba_name','') if best and bucket != 'unmatched' else ''})
    fields = list(rows[0])
    for bucket in ('high_confidence','review','unmatched'):
        with (OUT / f'map_{bucket}.csv').open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(r for r in rows if r['bucket'] == bucket)
    matched = {r['permit_number'] for r in rows if r['permit_number']}
    with (OUT / 'ttb_permits_not_matched_to_map.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(permits[0])); w.writeheader(); w.writerows(p for p in permits if p.get('permit_number','') not in matched)
    buckets = Counter(r['bucket'] for r in rows)
    matched_high = {r['permit_number'] for r in rows if r['bucket'] == 'high_confidence' and r['permit_number']}
    matched_review = {r['permit_number'] for r in rows if r['bucket'] == 'review' and r['permit_number']}
    by_unmatched_state = Counter(r['state'] or '(unparsed)' for r in rows if r['bucket'] == 'unmatched')
    by_bucket_source = {b:Counter(r['source'] or '(blank)' for r in rows if r['bucket'] == b) for b in buckets}
    lines = ['US_1752_TTB_STRICT_RECONCILIATION', 'SCOPE\tcountry=United States AND region=usa', f'MAP_US_RECORDS\t{len(rows)}', f'TTB_ACTIVE_PRODUCER_BOTTLER_PERMITS\t{len(permits)}', f'MAP_HIGH_CONFIDENCE_ROWS\t{buckets["high_confidence"]}', f'MAP_REVIEW_ROWS\t{buckets["review"]}', f'MAP_UNMATCHED_ROWS\t{buckets["unmatched"]}', f'MAP_UNPARSED_STATE_ROWS\t{sum(not r["state"] for r in rows)}', f'HIGH_CONFIDENCE_UNIQUE_TTB_PERMITS\t{len(matched_high)}', f'REVIEW_UNIQUE_TTB_PERMITS\t{len(matched_review)}', f'TOTAL_UNIQUE_TTB_PERMITS_WITH_MAP_CANDIDATE\t{len(matched)}', f'TTB_PERMITS_WITHOUT_MAP_CANDIDATE\t{len(permits)-len(matched)}', '\nUNMATCHED_MAP_ROWS_BY_STATE']
    lines += [f'{count}\t{key}' for key,count in by_unmatched_state.most_common()]
    lines += ['\nMAP_SOURCE_BY_BUCKET']
    for bucket in ('high_confidence','review','unmatched'):
        lines += [bucket] + [f'{count}\t{key}' for key,count in by_bucket_source[bucket].most_common()]
    (OUT / 'summary.tsv').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print('\n'.join(lines))

if __name__ == '__main__': main()
