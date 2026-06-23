import os, requests, pandas as pd
from io import StringIO

# Eviction Lab bulk data download — Texas tracts
# Source: evictionlab.org/data-download/
# Select: Tracts > Texas > Download CSV
EVICTION_URL = (
    'https://eviction-lab-data-downloads.s3.amazonaws.com/'
    'ets/tracts/texas.csv'
)

BEXAR_GEOID_PREFIX = '48029'

def pull_eviction():
    print('Downloading Eviction Lab data for Texas tracts...')
    resp = requests.get(EVICTION_URL, timeout=120)
    resp.raise_for_status()

    os.makedirs('data/raw', exist_ok=True)
    with open('data/raw/eviction_texas_tracts.csv', 'w') as f:
        f.write(resp.text)

    df = pd.read_csv(StringIO(resp.text), dtype={'GEOID': str})

    # Standardise GEOID — Eviction Lab uses 11-digit tract FIPS
    df['GEOID'] = df['GEOID'].str.zfill(11)

    # Filter to Bexar County
    bexar = df[df['GEOID'].str[:5] == BEXAR_GEOID_PREFIX].copy()

    # Keep the most recent year available
    if 'year' in bexar.columns:
        latest_year = bexar['year'].max()
        bexar = bexar[bexar['year'] == latest_year]
        print(f'  Using eviction data for year: {latest_year}')

    # Key columns: eviction rate, filing rate, eviction count
    keep = ['GEOID', 'name', 'year',
            'eviction-filings', 'evictions',
            'eviction-filing-rate', 'eviction-rate',
            'renter-occupied-households', 'population']
    bexar = bexar[[c for c in keep if c in bexar.columns]]

    os.makedirs('data/processed', exist_ok=True)
    bexar.to_csv('data/processed/eviction_bexar_tracts.csv', index=False)
    print(f'Eviction pull complete: {len(bexar)} Bexar County tracts saved.')

if __name__ == '__main__':
    pull_eviction()