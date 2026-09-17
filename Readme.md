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
└── data/                        # Generated outputs (not raw — reproducible from notebooks/01)
    ├── restaurant_clean_with_na.csv   # Typos fixed; invalid values left as NaN (no imputation)
    └── restaurant_clean_final.csv     # Above + imputed + derived TipPct column — used by all EDA
```

Not tracked in git (see `.gitignore`): `venv/`, `MP1Specs.pdf`, `scripts/`, `figures/`.

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

1. **Clean** — `source venv/bin/activate && python scripts/01_clean_data.py`
   Fixes typo/formatting errors (e.g. `28,87` → `28.87`), flags
   domain-invalid values (negative bills, implausible tips, out-of-range
   party sizes) as missing, then imputes them group-wise by `Day`+`Time`
   rather than with a single global value. Full rationale for every
   decision is in [log.md](log.md).

2. **Explore** — `python scripts/02_eda_partial.py`
   Reads `data/restaurant_clean_final.csv`, prints summary statistics, and
   writes the four charts in `figures/`.

3. **Next (not yet done):** full Phase 3 visualization pass, Phase 4
   hypothesis testing, and the final write-up (Introduction, Data
   Processing, Data Visualization, Analysis, Discussion/Recommendations,
   References — per the report structure required in
   [MP1Specs.pdf](MP1Specs.pdf)).

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
