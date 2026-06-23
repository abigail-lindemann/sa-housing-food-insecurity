import os, requests, pandas as pd, time

API_KEY = os.environ['CENSUS_API_KEY']
BASE    = 'https://api.census.gov/data/2023/acs/acs5'
STATE   = '48'   # Texas FIPS code
COUNTY  = '029'  # Bexar County FIPS code

# Variables to pull — housing insecurity + context
VARS = [
    'B25070_001E', 'B25070_007E', 'B25070_008E',
    'B25070_009E', 'B25070_010E',
    'B25014_005E', 'B25014_006E',
    'B25014_011E', 'B25014_012E',
    'B19013_001E',
    'B03002_001E', 'B03002_003E', 'B03002_012E', 'B03002_004E',
    'B17010_001E', 'B17010_002E',
]

def pull_block_groups():
    url = f'{BASE}?get=NAME,{",".join(VARS)}'
    url += f'&for=block+group:*'
    url += f'&in=state:{STATE}+county:{COUNTY}'
    url += f'&key={API_KEY}'

    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    df = pd.DataFrame(data[1:], columns=data[0])

    # Build a GEOID that matches the Census shapefile
    df['GEOID'] = df['state'] + df['county'] + df['tract'] + df['block group']

    # Convert numeric columns from strings
    for col in VARS:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Derived columns
    df['cost_burden_rate'] = (
        df[['B25070_007E','B25070_008E','B25070_009E','B25070_010E']].sum(axis=1)
        / df['B25070_001E'].replace(0, pd.NA)
    )
    df['severe_cost_burden_rate'] = (
        df['B25070_010E'] / df['B25070_001E'].replace(0, pd.NA)
    )
    df['overcrowding_rate'] = (
        df[['B25014_006E','B25014_012E']].sum(axis=1)
        / df[['B25014_005E','B25014_006E','B25014_011E','B25014_012E']].sum(axis=1).replace(0, pd.NA)
    )
    df['poverty_rate'] = (
        df['B17010_002E'] / df['B17010_001E'].replace(0, pd.NA)
    )
    df['pct_hispanic'] = (
        df['B03002_012E'] / df['B03002_001E'].replace(0, pd.NA)
    )

    os.makedirs('data/processed', exist_ok=True)
    df.to_csv('data/processed/acs_bexar_block_groups.csv', index=False)
    print(f'ACS pull complete: {len(df)} block groups saved.')

if __name__ == '__main__':
    pull_block_groups()