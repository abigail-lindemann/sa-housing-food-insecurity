import os, requests, pandas as pd
from io import BytesIO, StringIO

# USDA SNAP retailer bulk download
SNAP_URL = 'https://opendata.arcgis.com/datasets/8b260f9a10b0459aa441ad8588c2251c_0.csv'

# Store types considered 'full-service grocery'
GROCERY_TYPES = {
    'Supermarket',
    'Large Grocery Store',
    'Medium Grocery Store',
    'Small Grocery Store',
}

BEXAR_COUNTY = 'Bexar'

def pull_snap_retailers():
    print('Downloading SNAP retailer list for Texas...')
    resp = requests.get(SNAP_URL, timeout=120)
    resp.raise_for_status()

    os.makedirs('data/raw', exist_ok=True)
    with open('data/raw/snap_retailers_tx.xlsx', 'wb') as f:
        f.write(resp.content)

    df = pd.read_csv(BytesIO(resp.content))

    # Normalise column names (USDA occasionally changes capitalisation)
    df.columns = df.columns.str.strip().str.title()

    # Filter to Bexar County and grocery store types
    mask = (
    df['County'].str.strip().str.title().eq(BEXAR_COUNTY) &
    df['Store_Type'].isin(GROCERY_TYPES)
    )
    bexar = df[mask].copy()

    # Keep location + identifier columns
    keep = ['Store_Name', 'Store_Type', 'Store_Street_Address', 'City',
        'State', 'Zip_Code', 'County', 'Latitude', 'Longitude']
    bexar = bexar[[c for c in keep if c in bexar.columns]]

    # Drop rows with missing coordinates
    bexar = bexar.dropna(subset=['Latitude', 'Longitude'])

    os.makedirs('data/processed', exist_ok=True)
    bexar.to_csv('data/processed/grocery_stores_bexar.csv', index=False)
    print(f'SNAP retailer pull complete: {len(bexar)} grocery stores in Bexar County.')
    by_type = bexar['Store_Type'].value_counts().to_dict()
    for k, v in by_type.items():
        print(f'  {k}: {v}')

if __name__ == '__main__':
    pull_snap_retailers()