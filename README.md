# Housing & Food Insecurity in San Antonio

A CivicData SA analysis mapping housing and food insecurity across Bexar County at the neighborhood level.

**Live site:** https://abigail-lindemann.github.io/sa-housing-food-insecurity  
**Contact:** civicdatasa@gmail.com  
**GitHub:** github.com/abigail-lindemann

---

## About

This project combines spatial analysis with plain-language narrative to make data on housing and food insecurity accessible and actionable. The goal is not just to describe the problem but to reveal the shape of it: where insecurity clusters, how it overlaps with income and demographics, and what the gaps in existing support look like on a map.

The project produces four pages published on GitHub Pages:

- **Home** — key findings and links to all analyses
- **Housing insecurity** — cost burden, overcrowding, and rent stress by block group
- **Food access** — distance to grocery stores, USDA food desert designations, food bank coverage
- **Combined overlap view** — where housing and food insecurity co-occur, and where services are missing

---

## Key Findings

- **277** of 1,139 Bexar County block groups have high housing insecurity (top 25% composite score)
- **544** block groups have no full-service grocery store within 1 mile
- **155** block groups show high insecurity on both housing and food dimensions simultaneously (13.6%)
- **72** dual-insecurity block groups are also more than 3 miles from both a food bank and a WIC clinic
- Average distance to nearest food bank in dual-insecurity areas: **4.7 miles**

---

## Data Sources

| Dataset | Source | Update frequency |
|---|---|---|
| ACS housing & demographic variables | Census API (api.census.gov) | Annual — `pull_acs.py` |
| USDA Food Access Research Atlas | USDA ERS (ers.usda.gov) | Every few years — `pull_usda.py` |
| SNAP-authorized grocery stores | USDA FNS ArcGIS (opendata.arcgis.com) | Monthly — `pull_snap_retailers.py` |
| Food bank & pantry locations | Static CSV — manually maintained | Update as needed |
| WIC clinic locations | Static CSV — manually maintained | Update as needed |

### Manually Maintained Static Files

Two data sources do not have stable public APIs and are maintained as static CSVs:

| File | Columns | How to update |
|---|---|---|
| `data/processed/food_banks_bexar.csv` | name, address, city, latitude, longitude | Check safoodbank.org and call211.org annually |
| `data/processed/wic_clinics_bexar.csv` | name, address, city, latitude, longitude | Check texaswic.org annually |

### Data Sources Evaluated and Removed

| Source | Reason removed |
|---|---|
| Eviction Lab (Princeton) | Bulk download no longer public; data request required |
| 211 San Antonio API | Endpoint returns 404; no public replacement found |
| Texas DSHS WIC API | Not publicly accessible |

---

## Project Structure
cat > ~/projects/sa-housing-food-insecurity/README.md << 'EOF'
cat > ~/projects/sa-housing-food-insecurity/README.md << 'EOF'
cat > ~/projects/sa-housing-food-insecurity/README.md << 'EOF' sa-housing-food-insecurity/

├── .github/

│   └── workflows/

│       ├── annual.yml          # Pulls ACS + USDA data every January 1

│       ├── monthly.yml         # Re-pulls grocery locations 1st of each month

│       └── deploy.yml          # Deploys site/ to GitHub Pages on every push

├── scripts/

│   ├── pull_acs.py             # Census ACS block group data

│   ├── pull_usda.py            # USDA Food Desert Atlas

│   └── pull_snap_retailers.py  # SNAP-authorized grocery store locations

├── notebooks/

│   ├── 01_housing_insecurity.ipynb   # Housing insecurity composite score

│   ├── 02_food_access.ipynb          # Food access distance analysis

│   ├── 03_overlap_analysis.ipynb     # Quadrant classification + service gaps

│   └── 04_export_geojson.ipynb       # GeoJSON export for the map

├── data/

│   ├── raw/                    # Original downloads (gitignored)

│   └── processed/              # Cleaned outputs used in analysis

└── site/                       # Static website files

├── index.html

├── housing.html

├── food.html

├── overlap.html

├── css/style.css

└── data/                   # GeoJSON files served to the map

cat > ~/projects/sa-housing-food-insecurity/README.md << 'EOF' ---

## Methods

### Housing Insecurity Score
Each block group receives a composite score (0–1) averaged across normalized components:
- Renter cost burden rate (% of renters paying >30% income on housing)
- Severe cost burden rate (% paying >50%)
- Overcrowding rate (% of units with >1 person per room)

Block groups in the top 25% (score ≥ 0.464) are classified as high housing insecurity.

### Food Access Scoring
Distance from each block group centroid to the nearest full-service SNAP-authorized grocery store,
computed using a KD-tree (scipy.spatial.cKDTree). Two thresholds applied:
- **0.5 mile** — walkable access (strict threshold)
- **1.0 mile** — USDA Food Desert Atlas standard for urban areas

Block groups beyond 1 mile OR in a USDA-designated food desert are classified as high food insecurity.

### Combined Insecurity View
Block groups are classified into four quadrants by crossing housing insecurity (high/low)
with food insecurity (high/low). Service gap flags block groups with dual insecurity
that are also more than 3 miles from both a food bank and a WIC clinic.

### A Note on Eviction Data
Eviction filing rates were evaluated as a fourth housing insecurity indicator.
The Eviction Lab (Princeton) no longer provides public bulk downloads for Texas census tracts.
A future update will incorporate eviction data from Texas Housers (texashousers.org),
which tracks Bexar County filings annually via the Texas Public Information Act.

---

## Automated Workflows

| Workflow | Trigger | What it does |
|---|---|---|
| `annual.yml` | January 1 each year | Pulls ACS and USDA data, reruns analysis, exports GeoJSON |
| `monthly.yml` | 1st of each month | Re-pulls grocery store locations, reruns food access analysis |
| `deploy.yml` | Every push to main | Deploys site/ to GitHub Pages via gh-pages branch |

All workflows include a manual trigger — go to Actions → select workflow → Run workflow.

### Required Secrets

| Secret | Description |
|---|---|
| `CENSUS_API_KEY` | Free key from api.census.gov/data/key_signup.html |

`GITHUB_TOKEN` is provided automatically by GitHub.

### Manual Maintenance Tasks

| Task | Frequency | What to do |
|---|---|---|
| USDA Food Atlas URL | Every few years | Check ers.usda.gov/data-products/food-access-research-atlas/ and update `USDA_URL` in `pull_usda.py` |
| Food bank locations | 1–2x per year | Update `data/processed/food_banks_bexar.csv` |
| WIC clinic locations | 1–2x per year | Update `data/processed/wic_clinics_bexar.csv` |

---

## Running Scripts Locally

```bash
cd ~/projects/sa-housing-food-insecurity
export CENSUS_API_KEY=your_key_here

python scripts/pull_acs.py
python scripts/pull_usda.py
python scripts/pull_snap_retailers.py

ls -lh data/processed/
```

---

## Tech Stack

| Component | Tool |
|---|---|
| Hosting | GitHub Pages (gh-pages branch via GitHub Actions) |
| Mapping | Leaflet.js with CartoDB tiles |
| Data processing | Python (pandas, geopandas, scipy) + Jupyter |
| Data format | GeoJSON (map layers), CSV (tabular) |
| Front-end | HTML / CSS / JS — no framework |
| Census data | Census API (requests) |

---

*Built with open data · San Antonio, TX*
