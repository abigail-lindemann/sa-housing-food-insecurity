# Housing & Food Insecurity in San Antonio

A CivicData SA analysis mapping housing and food insecurity across Bexar County at the neighborhood level.

**Live site:** https://abigail-lindemann.github.io/sa-housing-food-insecurity  
**Contact:** abigail.c.lindemann@gmail.com  
**GitHub:** github.com/abigail-lindemann/sa-housing-food-insecurity

---

## About

This project combines spatial analysis with plain-language narrative to make data on housing and food insecurity accessible and actionable. The goal is not just to describe the problem but to reveal the shape of it: where insecurity clusters, how it overlaps with income and demographics, and what the gaps in existing support look like on a map.

The project produces two linked analysis pages:

- **Page 1 — Housing insecurity:** cost burden, overcrowding, housing quality
- **Page 2 — Food insecurity:** distance to grocery stores, food desert designation, SNAP/WIC participation
- **Combined overlap view:** where housing and food insecurity co-occur

---

## Data Sources

| Dataset | Source | Update frequency | Script |
|---|---|---|---|
| ACS housing & demographic variables | Census API (api.census.gov) | Annual (January 1) | `pull_acs.py` |
| USDA Food Access Research Atlas | USDA ERS | Every few years (manual URL update required) | `pull_usda.py` |
| SNAP-authorized grocery stores | USDA FNS ArcGIS (opendata.arcgis.com) | Monthly (1st of month) | `pull_snap_retailers.py` |
| Food bank & pantry locations | Static CSV — manually maintained | Update 1–2x per year | See below |
| WIC clinic locations | Static CSV — manually maintained | Update 1–2x per year | See below |

### Static Files (Manually Maintained)

Two data sources do not have reliable public APIs and are maintained as static CSVs:

| File | Columns | How to update |
|---|---|---|
| `data/processed/food_banks_bexar.csv` | name, address, city, latitude, longitude | Check safoodbank.org and call211.org annually |
| `data/processed/wic_clinics_bexar.csv` | name, address, city, latitude, longitude | Check texaswic.org annually |

When a location changes, update the CSV and commit. The site will reflect the change on next deploy.

### Data Sources Evaluated and Removed

| Source | Reason removed |
|---|---|
| Eviction Lab (Princeton) | Bulk download no longer public; data request required; replaced with methodology note |
| 211 San Antonio API | Endpoint returns 404; no public replacement found |
| Texas DSHS WIC API (texaswic.org) | API not publicly accessible |

---

## Automated Workflows

Three GitHub Actions workflows keep data current and the site rebuilt automatically.

| Workflow | Trigger | What it does |
|---|---|---|
| `annual.yml` | January 1 each year | Pulls ACS and USDA data, reruns analysis, exports GeoJSON |
| `monthly.yml` | 1st of each month | Re-pulls grocery store locations, reruns food access distance analysis |
| `deploy.yml` | Every push to main | Rebuilds and publishes the site to GitHub Pages |

All workflows also include a manual trigger — go to Actions → select workflow → Run workflow.

### Required Secrets

Add these in your repo Settings → Secrets and variables → Actions:

| Secret | Description |
|---|---|
| `CENSUS_API_KEY` | Free key from api.census.gov/data/key_signup.html |

`GITHUB_TOKEN` is provided automatically by GitHub — no setup needed.

---

## Keeping Data Current

Most of the project is automated, but a few things need human attention once or twice a year. This section is written for future-you: someone coming back after months away who just needs a clear checklist.

### Annual checklist (run each January)

Work through these in order. The whole process should take under an hour if nothing is broken.

**1. Let the annual workflow run**

The `annual.yml` workflow triggers automatically on January 1. Give it 10–15 minutes, then go to Actions → Annual data refresh and confirm the run shows a green checkmark. If it failed, see "If a workflow fails" below.

**2. Verify the ACS data pulled correctly**

The workflow pulls the most recent Census ACS 5-year estimates. Census typically releases the new year's data in December, so the January 1 trigger is intentionally timed to catch the latest release. After the workflow runs, check `data/processed/acs_bexar_block_groups.csv` and confirm the row count looks right (should be ~1,139 block groups).

**3. Check the USDA Food Atlas URL**

The USDA occasionally moves or replaces the Food Access Research Atlas file without redirecting the old URL. If `pull_usda.py` failed in the annual workflow, go to [ers.usda.gov/data-products/food-access-research-atlas](https://ers.usda.gov/data-products/food-access-research-atlas/), find the current download link, and update `USDA_URL` in `scripts/pull_usda.py`. Commit and re-run the workflow manually.

**4. Update food bank locations**

The automated workflows don't cover food banks — this one is manual. Go to [safoodbank.org](https://safoodbank.org) and check whether any locations have opened, closed, or moved since your last update. Edit `data/processed/food_banks_bexar.csv` and commit.

**5. Update WIC clinic locations**

Same process. Go to [texaswic.org](https://texaswic.org), search San Antonio, and compare against `data/processed/wic_clinics_bexar.csv`. Edit and commit any changes.

**6. Spot-check the live site**

Visit the live site and click through all four pages. Confirm the maps load, popups work, and the data looks reasonable. Pay attention to the "Data last updated" badge — it should reflect the current year.

**7. Update the "last verified" date below**

Once everything looks good, update the date at the bottom of this section.

---

### If a workflow fails

Go to Actions → click the failed run → click the failed step to read the log. The most likely causes:

| Symptom | Likely cause | Fix |
|---|---|---|
| `pull_usda.py` fails with 404 | USDA moved the Food Atlas file | Update `USDA_URL` in `scripts/pull_usda.py` |
| `pull_snap_retailers.py` fails on column name | USDA ArcGIS renamed a column | Run `df.columns.tolist()` locally to inspect, update column references in the script |
| `pull_acs.py` fails with 429 | Census API rate limit hit | Add `time.sleep(1)` between requests, or re-run manually — it usually clears on retry |
| `deploy.yml` fails with permission error | GITHUB_TOKEN permissions issue | Check the `permissions:` block in `deploy.yml` includes `contents: write` |
| Any workflow: `ModuleNotFoundError` | A Python package is missing | Add it to the `pip install` step in the relevant workflow file |

If a workflow fails and you're not sure why, re-running it manually often resolves transient network errors: Actions → select workflow → Run workflow.

---

### Monthly checks (optional)

The `monthly.yml` workflow re-pulls SNAP grocery store locations automatically on the 1st of each month. You don't need to do anything — but if you notice a known grocery store missing from the food access map, check the Actions log for that month's run to see if the pull succeeded.

---

**Last verified:** June 2026

---

## Project Structure

```
sa-housing-food-insecurity/
├── .github/
│   └── workflows/
│       ├── annual.yml
│       ├── monthly.yml
│       └── deploy.yml
├── scripts/
│   ├── pull_acs.py             # Census ACS data
│   ├── pull_usda.py            # USDA Food Desert Atlas
│   └── pull_snap_retailers.py  # Grocery store locations
├── notebooks/
│   ├── 01_housing_insecurity.ipynb
│   ├── 02_food_access.ipynb
│   ├── 03_overlap_analysis.ipynb
│   └── 04_export_geojson.ipynb
├── data/
│   ├── raw/                    # Original downloads (gitignored)
│   └── processed/              # Cleaned outputs used in analysis
└── site/                       # Static website files
    ├── index.html
    ├── housing.html
    ├── food.html
    ├── overlap.html
    ├── css/
    ├── js/
    └── data/                   # GeoJSON files served to the map
```

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

Each script prints a summary line on success. If a script fails, the error message will tell you what went wrong.

---

## Methods

### Housing Insecurity Score
Each block group receives a housing insecurity score (0–1), computed as a normalized average of:
- Renter cost burden rate (% of renters paying >30% income on housing)
- Severe cost burden rate (% paying >50%)
- Overcrowding rate (% of units with >1 person per room)

### Food Access Scoring
Distance analysis from block group centroids to nearest full-service grocery store using a KD-tree spatial index. Two thresholds are shown simultaneously on the map:
- **Strict (0.5 mile)** — consistent with CivicData SA park equity methodology
- **USDA standard (1 mile)** — consistent with USDA Food Desert Atlas definition

### Combined Insecurity View
Block groups are classified into four quadrants by crossing housing insecurity (high/low) with food access (high/low). This quadrant map is the signature cross-page finding.

### A Note on Eviction Data
Eviction data at the census tract level was evaluated as a fourth housing insecurity indicator. The Eviction Lab (Princeton) no longer provides public bulk downloads; tract-level data for Bexar County requires a formal data request. This indicator has been excluded from the current version of the analysis. A future update will incorporate eviction data from Texas Housers (texashousers.org), which tracks Bexar County eviction filings annually via the Texas Public Information Act.

---

## Tech Stack

| Component | Tool |
|---|---|
| Hosting | GitHub Pages (via `peaceiris/actions-gh-pages`) |
| Mapping | Leaflet.js with CartoDB tile layers |
| Data processing | Python (pandas, geopandas, scipy) + JupyterLab |
| Spatial analysis | `scipy.spatial.cKDTree` (nearest-neighbor distance) |
| Data format | GeoJSON (map layers), CSV (tabular) |
| Front-end | HTML / CSS / JS |

---

*Built with open data · San Antonio, TX*
