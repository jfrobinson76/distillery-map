import csv, re
from collections import Counter
from pathlib import Path
from rapidfuzz import fuzz

ROOT = Path(__file__).parent.parent
BASE = ROOT / 'data/audit/us_1752_ttb_reconciliation'


def norm(value):
    value = (value or '').lower()
    value = re.sub(r'\b(distillery|distilleries|brewing|winery|spirits?|co\.|company|llc|inc\.?|ltd\.?)\b', '', value)
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', value)).strip()


def load(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def main():
    unmatched = [r for r in load(BASE / 'map_unmatched.csv') if not r['state']]
    permits = load(ROOT / 'data/enriched/ttb_dsp_raw.csv')
    results = []
    for row in unmatched:
        best_score, best = 0, None
        for permit in permits:
            for key in ('business_name', 'dba_name'):
                candidate = norm(permit.get(key, ''))
                if candidate:
                    score = fuzz.token_sort_ratio(norm(row['name']), candidate)
                    if score > best_score: best_score, best = score, permit
        tier = 'strong_name_candidate_95_plus' if best_score >= 95 else 'high_name_candidate_85_94' if best_score >= 85 else 'review_name_candidate_70_84' if best_score >= 70 else 'no_name_candidate_below_70'
        results.append({**row, 'global_name_score':round(best_score,1), 'candidate_tier':tier, 'candidate_permit':best.get('permit_number','') if best else '', 'candidate_owner':best.get('business_name','') if best else '', 'candidate_dba':best.get('dba_name','') if best else '', 'candidate_state':best.get('state','') if best else '', 'candidate_city':best.get('city','') if best else ''})
    with (BASE / 'map_unparsed_state_global_name_candidates.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(results[0])); w.writeheader(); w.writerows(results)
    counts = Counter(r['candidate_tier'] for r in results)
    lines = ['UNPARSED_US_MAP_STATE_GLOBAL_NAME_CANDIDATES', f'TOTAL_UNPARSED_MAP_ROWS\t{len(results)}']
    lines += [f'{tier}\t{counts[tier]}' for tier in ('strong_name_candidate_95_plus','high_name_candidate_85_94','review_name_candidate_70_84','no_name_candidate_below_70')]
    lines += ['', 'STRONG_CANDIDATES']
    lines += [f"{r['global_name_score']}\t{r['slug']}\t{r['name']}\t{r['candidate_permit']}\t{r['candidate_owner']}\t{r['candidate_state']}" for r in results if r['candidate_tier'] == 'strong_name_candidate_95_plus']
    (BASE / 'unparsed_state_candidate_summary.tsv').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print('\n'.join(lines))

if __name__ == '__main__': main()
