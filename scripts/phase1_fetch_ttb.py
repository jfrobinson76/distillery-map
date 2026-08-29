"""
Phase 1 — Step 2: Download TTB Spirits Producers and Bottlers permit list.

Source: https://www.ttb.gov/public-information/foia/list-of-permittees
File:   FRL_Spirits_Producers_and_Bottlers_List.csv (updated weekly by TTB)

State and permit_type are derived from the permit_number prefix (e.g. AK-S-15000).
permit_type is the FAA Act basic-permit code ("S" on every DSP row). It is NOT a
distiller / warehouseman / processor split; TTB does not publish operations. A
permit proves permission, not a working still. See
docs/data-quality/ttb-permit-type-research-2026-08-29.md before treating rows as
distilleries.

Output: data/enriched/ttb_dsp_raw.csv with columns:
  permit_number, business_name, dba_name, street, city, state, zip, permit_type
"""

import re
import sys
import time
import io
from pathlib import Path

import requests
import pandas as pd

TTB_INDEX_URL = 'https://www.ttb.gov/public-information/foia/list-of-permittees'
OUTPUT_PATH = Path(__file__).parent.parent / 'data' / 'enriched' / 'ttb_dsp_raw.csv'

HEADERS = {'User-Agent': 'Stillbound-Research/1.0 (data@stillbound.ai)'}

# Permit number format: STATE-TYPE-SERIAL, e.g. AK-S-15000, CA-D-12345
PERMIT_RE = re.compile(r'^([A-Z]{2})-([A-Z])-\d+')


def find_spirits_csv_url(index_url: str) -> str:
    resp = requests.get(index_url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    time.sleep(1)

    # Look for the Spirits Producers and Bottlers CSV link
    matches = re.findall(r'href="(/system/files/[^"]*(?:Spirits[^"]*|spirit[^"]*)\.csv)"', resp.text, re.I)
    if matches:
        return 'https://www.ttb.gov' + matches[0]

    # Fallback: any CSV in /system/files/
    matches = re.findall(r'href="(/system/files/[^"]*\.csv)"', resp.text)
    if matches:
        return 'https://www.ttb.gov' + matches[0]

    raise RuntimeError(
        f'Could not find Spirits Producers CSV on {index_url}. '
        'TTB may have changed their page — check manually at that URL.'
    )


def derive_state(permit_number: str) -> str:
    m = PERMIT_RE.match(str(permit_number))
    return m.group(1) if m else ''


def derive_permit_type(permit_number: str) -> str:
    m = PERMIT_RE.match(str(permit_number))
    return m.group(2) if m else ''


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f'Fetching TTB permittees index: {TTB_INDEX_URL}')
    csv_url = find_spirits_csv_url(TTB_INDEX_URL)
    print(f'Downloading: {csv_url}')

    resp = requests.get(csv_url, headers=HEADERS, timeout=120)
    resp.raise_for_status()
    time.sleep(1)

    df = pd.read_csv(io.BytesIO(resp.content), dtype=str, encoding='cp1252').fillna('')

    print(f'Raw rows: {len(df)}  Columns: {list(df.columns)}')

    # Normalise to our schema
    df = df.rename(columns={
        'Permit_Number': 'permit_number',
        'Owner_Name': 'business_name',
        'Operating_Name': 'dba_name',
        'Street': 'street',
        'City': 'city',
        'Prem_Zip': 'zip',
    })

    df['state'] = df['permit_number'].apply(derive_state)
    df['permit_type'] = df['permit_number'].apply(derive_permit_type)

    out_cols = [
        'permit_number', 'business_name', 'dba_name',
        'street', 'city', 'state', 'zip',
        'permit_type',
    ]
    for col in out_cols:
        if col not in df.columns:
            df[col] = ''

    df[out_cols].to_csv(OUTPUT_PATH, index=False, encoding='utf-8')

    state_dist = df['state'].value_counts().head(10).to_dict()
    print(f'Output rows: {len(df)}')
    print(f'Top states: {state_dist}')
    print(f'Output: {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
