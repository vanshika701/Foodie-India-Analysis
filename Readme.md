# Foodie India — Restaurant Tipping Analysis (MP1)

Course project (DOM207/DOM3007/DOM6401, MP1): acting as a DSA consulting
team hired by a restaurant chain, "Foodie India," to recommend viable
business-expansion propositions based solely on `Restaurant.xlsx`, a
365-row dataset of party-level bills, tips, and demographics. Full brief
in [MP1Specs.pdf](MP1Specs.pdf).

## Project structure

```
.
├── Restaurant.xlsx              # Raw client data (proprietary — do not add new data to it)
├── log.md                       # Running decision log — why each cleaning/analysis choice was made
├── requirements.txt             # Pinned Python dependencies
│
├── notebooks/                   # Cleaning + EDA pipeline, notebook form (for interactive exploration)
│   ├── 01_clean_data.ipynb
│   └── 02_eda.ipynb
│
├── data/
│   ├── restaurant_clean_with_na.csv    # Byproduct of notebooks/01 — typos fixed, invalid values NaN
│   └── Restaurant_cleaned_final.csv    # TEAM'S ACTUAL FINAL DATASET — provided by a teammate, used by all EDA
│
└── figures/                     # Chart outputs from scripts/02_eda_partial.py
```

Not tracked in git (see `.gitignore`): `venv/`, `MP1Specs.pdf`, `scripts/`, `data/restaurant_clean_final.csv`.

## Data fields

| Column      | Meaning                                              |
|-------------|-------------------------------------------------------|
| `Amount`    | Total bill for a party at a single meal               |
| `Tip`       | Tip given by the party to the waiter                   |
| `Gender`    | Gender of the waiter who served the party              |
| `Smoker`    | Whether any individual in the party smoked             |
| `Day`       | Day of the meal (Thur / Fri / Sat / Sun)                |
| `Time`      | Meal time (Lunch / Dinner)                              |
| `Partysize` | Number of people in the party                           |
| `TipPct`    | Derived: `Tip / Amount * 100` (added during cleaning)   |

## Pipeline

> **As of 2026-09-24, EDA reads `data/Restaurant_cleaned_final.csv`** — a
> file a teammate cleaned and provided directly, adopted as the team's
> agreed-final dataset (349 rows). `scripts/01_clean_data.py` /
> `notebooks/01_clean_data.ipynb` (step 1 below) still run as an
> independent, documented cross-check, but their own output
> (`restaurant_clean_final.csv`, 352 rows, gitignored) is no longer what
> downstream analysis uses. See [log.md](log.md) for why, and note the
> Data Processing section of the report still needs the cleaning
> rationale for `Restaurant_cleaned_final.csv` from that teammate, since
> it wasn't produced by a checked-in script.

1. **Clean (cross-check only)** — `source venv/bin/activate && python scripts/01_clean_data.py`
   Fixes typo/formatting errors (e.g. `28,87` → `28.87`), flags
   domain-invalid values (negative bills, implausible tips, out-of-range
   party sizes) as missing, then imputes them group-wise by `Day`+`Time`
   rather than with a single global value. Rows where `Day` can't be
   recovered at all (blank or an unresolvable typo like `San`) are dropped
   rather than imputed. Full rationale for every decision is in
   [log.md](log.md).

2. **Explore** — `python scripts/02_eda_partial.py`
   Reads `data/Restaurant_cleaned_final.csv`, prints summary statistics,
   and writes 7 charts to `figures/`: bill/tip distributions, tip % by
   day/time, tip % by smoker status, party volume by day/time, tip % by
   waiter gender, tip % by party size, and average bill amount by
   day/time. Findings (incl. which patterns are backed by too few rows to
   trust) are in [log.md](log.md).

3. **Next (not yet done):** full Phase 3 hypothesis testing (Phase 4) and
   the final write-up (Introduction, Data
   Processing, Data Visualization, Analysis, Discussion/Recommendations,
   References — per the report structure required in
   [MP1Specs.pdf](MP1Specs.pdf)).

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
