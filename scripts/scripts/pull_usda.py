import os, requests, pandas as pd
from io import BytesIO

# USDA Food Access Research Atlas — update this URL if USDA changes it
# Check: ers.usda.gov/data-products/food-access-research-atlas/
USDA_URL = (
    'https://ers.usda.gov/webdocs/DataFiles/80591/'
    'FoodAccessResearchAtlasData2019.xlsx'
)

BEXAR_FIPS = '48029'  # State + county FIPS for Bexar County

def pull_usda():
    print('Downloading USDA Food Access Research Atlas...')
    resp = requests.get(USDA_URL, timeout=120)
    resp.raise_for_status()

    # Save raw file
    os.makedirs('data/raw', exist_ok=True)
    with open('data/raw/usda_food_atlas.xlsx', 'wb') as f:
        f.write(resp.content)

    # Read the 'Food Access Research Atlas' sheet
    df = pd.read_excel(BytesIO(resp.content), sheet_name='Food Access Research Atlas')

    # CensusTract is a float in the USDA file — convert to zero-padded string
    df['CensusTract'] = df['CensusTract'].astype(str).str.split('.').str[0].str.zfill(11)

    # Filter to Bexar County (first 5 digits of tract FIPS = state + county)
    bexar = df[df['CensusTract'].str[:5] == BEXAR_FIPS].copy()

    # Keep only columns we use
    keep_cols = [
        'CensusTract', 'State', 'County',
        'LILATracts_1And10', 'LILATracts_halfAnd10',
        'LowIncomeTracts', 'LA1and10', 'LAhalfand10',
        'PovertyRate', 'MedianFamilyIncome',
        'lapop1share', 'lapop05share',  # share of pop with low access
    ]
    bexar = bexar[[c for c in keep_cols if c in bexar.columns]]

    os.makedirs('data/processed', exist_ok=True)
    bexar.to_csv('data/processed/usda_food_desert_bexar.csv', index=False)
    print(f'USDA pull complete: {len(bexar)} Bexar County tracts saved.')
    print(f"  Food deserts (1-mile): {bexar['LILATracts_1And10'].sum()} tracts")
    print(f"  Food deserts (0.5-mile): {bexar['LILATracts_halfAnd10'].sum()} tracts")

if __name__ == '__main__':
    pull_usda()