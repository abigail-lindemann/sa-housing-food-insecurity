import os, requests, pandas as pd

# Texas DSHS WIC clinic API endpoint
# This endpoint returns all WIC clinics in Texas as JSON
WIC_API = 'https://www.texaswic.org/api/clinics'

BEXAR_COUNTY = 'Bexar'

def pull_wic():
    print('Pulling WIC clinic locations from Texas DSHS...')
    try:
        resp = requests.get(WIC_API, timeout=30)
        resp.raise_for_status()
        clinics = resp.json()
    except Exception as e:
        print(f'WIC API failed: {e}')
        print('Falling back to manual download — see note in this script.')
        return

    df = pd.json_normalize(clinics)

    # Filter to Bexar County
    if 'county' in df.columns:
        df = df[df['county'].str.title().eq(BEXAR_COUNTY)]
    elif 'County' in df.columns:
        df = df[df['County'].str.title().eq(BEXAR_COUNTY)]

    # Standardise columns
    rename = {
        'clinicName': 'name', 'clinic_name': 'name',
        'streetAddress': 'address', 'street_address': 'address',
        'cityName': 'city', 'city_name': 'city',
        'lat': 'latitude', 'lng': 'longitude',
        'long': 'longitude',
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    df = df.dropna(subset=['latitude', 'longitude'])

    os.makedirs('data/processed', exist_ok=True)
    df[['name','address','city','latitude','longitude']].to_csv(
        'data/processed/wic_clinics_bexar.csv', index=False
    )
    print(f'WIC pull complete: {len(df)} clinics in Bexar County saved.')

if __name__ == '__main__':
    pull_wic()