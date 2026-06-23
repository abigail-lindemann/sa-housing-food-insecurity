import os, requests, pandas as pd

# 211 San Antonio / Alamo Area open data endpoint (HSDS standard)
# If this URL returns 401, request a free API key at call211.org
API_BASE = 'https://api.211.org/search'

# Service taxonomy codes for food assistance
FOOD_TAXONOMY = [
    'BD-1800',          # Food Pantries
    'BD-1800.1400',     # Community Food Pantries
    'BD-1800.2000',     # Emergency Food Assistance
    'BD-1800.5500',     # Mobile Food Pantries
    'BD-1800.6500',     # Senior Food Programs
]

def pull_food_banks():
    all_locations = []

    for taxonomy in FOOD_TAXONOMY:
        params = {
            'keyword': 'food',
            'location': 'San Antonio, TX',
            'radius': 40,   # miles — covers all of Bexar County
            'taxonomy_term': taxonomy,
            'page': 1,
            'per_page': 100,
        }
        try:
            resp = requests.get(API_BASE, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            locations = data.get('results', data.get('data', []))
            all_locations.extend(locations)
        except Exception as e:
            print(f'  Warning: taxonomy {taxonomy} failed: {e}')

    if not all_locations:
        print('No results from 211 API — falling back to static file if available.')
        return

    df = pd.json_normalize(all_locations)

    # Standardise key columns — 211 APIs vary in their field names
    rename = {
        'agency_name': 'name', 'organization.name': 'name',
        'physical_address.address_1': 'address',
        'physical_address.city': 'city',
        'location.latitude': 'latitude', 'geometry.coordinates[1]': 'latitude',
        'location.longitude': 'longitude', 'geometry.coordinates[0]': 'longitude',
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    # Keep rows with coordinates
    df = df.dropna(subset=['latitude', 'longitude'])
    df = df[df['latitude'].between(27.5, 30.0) & df['longitude'].between(-99.5, -97.5)]

    os.makedirs('data/processed', exist_ok=True)
    df[['name','address','city','latitude','longitude']].drop_duplicates().to_csv(
        'data/processed/food_banks_bexar.csv', index=False
    )
    print(f'Food bank pull complete: {len(df.drop_duplicates())} locations saved.')

if __name__ == '__main__':
    pull_food_banks()