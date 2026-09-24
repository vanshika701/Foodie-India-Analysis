# Project Log — Foodie India MP1

Running log of what was done, when, why, and how. Newest entries at the bottom.
Read this before touching `scripts/` if you're picking this up mid-project —
every cleaning decision has a reason recorded here, not just in code comments.

---

## 2026-09-17 — Project setup

**What:** Created project structure: `venv/` (Python virtual environment),
`data/` (cleaned datasets), `figures/` (chart outputs), `scripts/` (analysis
code), `.gitignore` (excludes `venv/`, caches, `.DS_Store`).

**Why:** macOS blocks global `pip install` (PEP 668, externally-managed
environment), so a venv is required to install pandas/numpy/matplotlib/
seaborn/scipy/openpyxl without touching system Python. Keeping `venv/` out
of git means anyone cloning the repo rebuilds the exact same environment
from `requirements.txt` instead of depending on whatever's on their machine.


## 2026-09-17 — Raw data structural investigation (before writing any cleaning code)

**What:** Profiled `Restaurant.xlsx` before deciding a cleaning strategy —
checked row lengths, per-column value counts, and cross-referenced Excel's
internal cell references (e.g. `C15`, `G22`) to see exactly which column
each raw value truly belongs to.

**Why:** An early quick-and-dirty scan (indexing raw XML cells by list
position rather than by their actual column letter) made it look like rows
with a missing field had *shifted* all subsequent columns left — e.g. `Day`
appearing to contain `"Dinner"`. That would have meant every downstream
column needed token-reclassification, a much bigger job. Re-checking with
the real cell reference (column letter from the XML, and confirmed via
`pandas.read_excel`, which reconstructs blanks by position automatically)
showed this was **wrong** — pandas/openpyxl already places each value in
its correct column; a missing field is just `NaN`, nothing shifts. Lesson:
verify structural assumptions against the actual column reference before
designing a fix, not just against list order.

**Findings:**
- 365 data rows, 7 real columns (`Amount, Tip, Gender, Smoker, Day, Time,
  Partysize`) + junk `Unnamed: 7-10` columns from stray artifacts (one row
  has a stray `+` character in a phantom column K — dropped).
- Missing values per column (confirmed via `df.isna().sum()`):
  `Tip`: 2, `Smoker`: 9, `Day`: 4, `Partysize`: 3. No row is missing more
  than one field.
- Every other "dirty" value is a typo/formatting issue within its own
  correct column (not cross-column contamination).

---

## 2026-09-17 — Phase 2: Data cleaning (`scripts/01_clean_data.py`)

> **Superseded:** the imputation step described below (global mode/median)
> was replaced with group-wise imputation later the same day — see the
> entry further down. The typo-correction and invalid-value decisions in
> this entry are still current and unchanged.

**What:** Wrote and ran the cleaning script. Column-by-column decisions:

- **Amount** — `28,87`, `25-89`, `27-23` are decimal-separator typos
  (comma/dash used instead of `.`) → corrected to `28.87`, `25.89`, `27.23`.
  One value was **negative** (`-7.78`) — a bill can't be negative → marked
  invalid → imputed with the column median ($19.11).
- **Tip** — `2.0\`` had a stray trailing backtick → stripped → `2.0`. Three
  values (`288`, `300`, `3487`) appeared on ~$21-22 bills — physically
  implausible (no one tips 15-150x the bill); rather than guess the
  intended decimal placement (e.g. is `288` meant to be `2.88` or `28.8`?),
  they're treated as invalid and imputed with the median ($2.85). **Policy:
  never guess a specific corrected value when more than one correction is
  equally plausible — mark it missing and impute instead.** This same
  policy is applied consistently to Day, Time, and Partysize below.
- **Gender** — explicit typo map: `M/Mal/Mle → Male`, `F/Fe/Fmle/Femle/Fem
  → Female`. All 21 typo'd values resolved unambiguously (no missing
  values in this column).
- **Smoker** — explicit map: `N → No`, `Y → Yes`. The single value `s`
  doesn't unambiguously match either `Yes` or `No` (unlike `N`/`Y`, which
  are literal first letters) → left as missing. Combined with 9 originally
  blank cells → 10 missing → imputed with the mode (`No`).
- **Day** — explicit map for confident prefix/typo matches: `Thur/Thurs/
  Trhurs/Th/T → Thur`, `Fri/Friday → Fri`, `Sat/Saturday → Sat`, `Sun/Sn/
  sun → Sun`. Left as missing: `S`, `SS`, `SSS`, `San`, `Ft` — these are
  equally close to more than one day (e.g. `San` is a 2-of-3-letter match
  to *both* "Sun" and "Sat", a genuine tie) so "correcting" them would be
  guessing, not cleaning. 13 missing total → imputed with the mode (`Sat`).
- **Time** — explicit map: `Dinner/Diner/DD/DDD/Di/Din/D → Dinner`,
  `Lunch/L/Lu/Lan → Lunch`. Left as missing: `LD`, `er`, `Afd`,
  `Din/Lun` (literally contradictory or unrecognizable). 5 missing →
  imputed with the mode (`Dinner`).
- **Partysize** — converted to numeric. Valid observed range is 1-6 guests;
  values `<= 0`, `> 6` (e.g. `200`, `45`, `38`, `29`, `26`, `22`, `12`,
  `10`, `-2`, `0`), or non-integer (`0.2`) are data-entry errors (extra/
  garbled digit), not real party sizes → invalid → imputed with the median
  (rounded to `2`). **Bug caught during review:** the first version of this
  filter only checked `<=0 or >6`, which let `0.2` slip through (it's
  technically in range) — it then got silently truncated to `0` by
  `astype(int)`. Fixed by explicitly rejecting non-integer values too.
  Always spot-check `value_counts()` on a cleaned column before trusting it.

**Outputs:**
- `data/restaurant_clean_with_na.csv` — typos fixed, invalid values are
  `NaN` (no imputation yet). Use this if you want to try a different
  imputation strategy or just inspect what was actually missing/invalid.
- `data/restaurant_clean_final.csv` — the above **plus** imputation, plus a
  derived `TipPct = Tip / Amount * 100` column. This is the file every
  later script (EDA, hypothesis tests) should read from.

**Full cleaning report** (from the last run):
```
Amount: negative (invalid): 1
Tip: implausibly large (invalid): 3
Gender: typo values corrected: 21
Smoker: typo values corrected: 12, missing/unresolved: 10
Day: typo values corrected: 14, missing/unresolved: 13
Time: typo values corrected: 14, missing/unresolved: 5
Partysize: domain-invalid: 14, originally blank: 3
Smoker: imputed with mode 'No' (10 rows)
Day: imputed with mode 'Sat' (13 rows)
Time: imputed with mode 'Dinner' (5 rows)
Amount: imputed with median 19.11 (1 row)
Tip: imputed with median 2.85 (5 rows)
Partysize: imputed with median 2 (17 rows)
```
Final dataset: 365 rows, 0 missing values, 0 known-invalid values.

**Known limitation to state honestly in the report:** mode/median
imputation is a simple default, not a sophisticated method (e.g. no
model-based imputation was used). Missing fractions are all small
(≤ 4.7% for any column), so the effect on downstream statistics should be
minor, but this is worth naming explicitly in the Data Processing section
rather than presenting the cleaned data as if it had no uncertainty.

---

## 2026-09-17 — Phase 3 (partial): First-pass EDA (`scripts/02_eda_partial.py`)

**What:** Ran summary statistics and produced 4 charts against
`restaurant_clean_final.csv`, saved to `figures/`:
1. `01_amount_tippct_distribution.png` — histograms of `Amount` and
   `TipPct`.
2. `02_tippct_by_day_time.png` — average tip % by day and by time
   (bar charts, direct-labeled).
3. `03_tippct_by_smoker.png` — tip % boxplot, smoker vs non-smoker.
4. `04_party_volume_day_time.png` — grouped bar chart of party counts by
   day × time (relevant for staffing-type recommendations later).

**Why these charts specifically:** the spec penalizes "useless" charts, so
each one was picked to answer a business-relevant question (what's a
typical bill/tip, does tipping behavior vary by day/time/smoker status,
when are parties busiest) rather than just plotting every column.
Categorical colors are fixed by entity (blue = primary metric, orange =
secondary) and reused consistently across all 4 charts rather than
re-cycled per chart, per standard chart-design practice.

**Notable pattern surfaced:** `TipPct` is right-skewed with a handful of
genuine (not invalid — checked Amount/Tip individually, both plausible)
extreme ratios, e.g. a $1.01 bill tipped $1.68 (166%). These are kept in
the dataset since neither value is individually wrong; the ratio is just
naturally noisy for very small bills. Worth flagging in the Analysis
section, and worth deciding later (Phase 4) whether any hypothesis test
needs a robustness check excluding these.

**Summary stats (final cleaned data):**
```
Amount:  mean 21.21, median 19.11, std 10.90, range [1.01, 117.81]
Tip:     mean 3.08,  median 2.85,  std 2.04,  range [0.01, 22.23]
TipPct:  mean 16.14, median 14.67, std 13.07, range [0.15, 166.34]
Partysize: mean 2.55, median 2, range [1, 6]

Gender: Male 209, Female 156
Smoker: No 222, Yes 143
Day: Sat 128, Sun 108, Thur 90, Fri 39
Time: Dinner 230, Lunch 135
```

**Not done yet (deliberately deferred to full Phase 3):** more visuals
(e.g. tip % vs party size, gender comparisons), and no hypothesis testing
yet — that's Phase 4 per the project plan.

---

## 2026-09-17 — Upgraded imputation: global mode/median → group-wise

**What:** Replaced the earlier "fill every missing value in a column with
that column's single global mode/median" step in `scripts/01_clean_data.py`
with group-wise imputation: each missing value is now filled from the
mode (categorical) or median (numeric) of *other rows sharing the same
Day+Time* (Day and Time themselves are imputed first, from each other,
since no row is missing both — see below), falling back to the global
mode/median only if a group happens to have no usable data.

**Why:** A single global value ignores real structure in the data — e.g.
Thursday is overwhelmingly a Lunch day (70 Lunch vs 19 Dinner) while
Saturday/Sunday are overwhelmingly Dinner (91 vs 22, 90 vs 17). Filling
every missing `Time` with the single global mode ("Dinner") would
incorrectly force Thursday's missing rows into Dinner too.
Grouping by Day+Time keeps the imputed value consistent with the pattern
actually observed for similar rows, while staying simple enough to explain
in the report as "we filled it in from what's typical for that day/time
slot," not a black-box model.

**Why median, not mean, for the numeric columns (Amount, Tip, Partysize):**
Amount and Tip are both right-skewed — a small number of large parties or
generous tips pull the *mean* upward past what a typical party actually
pays/tips (confirmed in the summary stats: Amount mean $21.21 vs median
$19.10; Tip mean $3.08 vs median $2.87 — mean > median is the standard
signature of right skew). If we imputed with the mean, every missing bill
would be nudged toward the "high roller" end and systematically overstate
what a typical party spends. The median is the middle observation, so it's
unaffected by those few large outliers and represents the row's likely
true value better. `Partysize` is discrete count data (a party has a whole
number of people), so its central tendency should also land on/near an
actual observed value rather than an average that could produce a
fractional person — median handles that naturally; we still round+cast to
int afterward as a safety net.

**Order of operations (matters):** `Day` is imputed first (grouped by
`Time`), then `Time` (grouped by `Day`) — this works because no single row
is missing both at once (checked: only 3 rows have 2+ missing fields
total, and none of them are the Day+Time pair). Only after Day and Time
are both complete do `Smoker`, `Amount`, `Tip`, and `Partysize` get
imputed grouped by the now-complete Day+Time pair.

**Result — every group had enough data, so no case fell back to the
global value:**
```
Day: imputed via mode within Time group: 13
Time: imputed via mode within Day group: 5
Smoker: imputed via mode within Day+Time group: 10
Amount: imputed via median within Day+Time group: 1
Tip: imputed via median within Day+Time group: 5
Partysize: imputed via median within Day+Time group: 17
```
Final dataset: still 365 rows, 0 missing, 0 invalid. Overall summary stats
barely moved (e.g. Amount mean still 21.21, median 19.10; Partysize median
still 2) — group-wise imputation didn't distort the aggregate distribution,
it just made each individual fill more contextually accurate than one
number for everyone.

**How:** Rewrote the imputation section of `scripts/01_clean_data.py` with
two helpers, `impute_categorical_grouped()` and `impute_numeric_grouped()`,
each taking the target column and its grouping column(s). Re-ran
`python scripts/01_clean_data.py` and `python scripts/02_eda_partial.py`
to refresh `data/restaurant_clean_final.csv` and the charts in `figures/`
against the new values. Minor downstream shifts worth noting: `Day` counts
are now Sat 122 / Sun 108 / Thur 96 / Fri 39 (was Sat 128 / Sun 108 /
Thur 90 / Fri 39), and `Time` is Dinner 228 / Lunch 137 (was Dinner 230 /
Lunch 135) — small movements since only the previously-`Sat`-mode and
previously-`Dinner`-mode rows were redistributed to their group's actual
mode instead.

---

## 2026-09-17 — Extended EDA: gender, party size, and revenue-by-slot charts

**What:** Added 3 charts to `scripts/02_eda_partial.py` and
`notebooks/02_eda.ipynb`, closing out the items explicitly deferred in the
first EDA pass:
5. `05_tippct_by_gender.png` — Tip % boxplot, male vs female waiter.
6. `06_tippct_by_partysize.png` — average Tip % by party size, annotated
   with each group's `n`.
7. `07_amount_by_day_time.png` — average bill *Amount* by Day×Time (a
   revenue view, to pair with the existing party-count/volume view).

**Findings:**
- **Gender (n=209 Male / 156 Female):** medians and IQRs are nearly
  identical (median ~14.6-14.7% both); the only difference is a couple of
  high outliers on the female side, including the same $1.01-bill/166%
  outlier already flagged in Chart 1. No evidence waiter gender affects
  tipping — ruled out as a factor, not raised as a lead.
- **Party size:** sizes 2-4 (the bulk, n=92-206) sit in a stable 13.5-16.8%
  band. Sizes 1, 5, 6 show much higher averages (30.8%, 36.1%, 16.1%) but
  rest on **n=11, 7, 3** respectively — too few rows to trust; almost
  certainly a couple of generous individual tippers, not a real party-size
  effect. **Decision: any party-size recommendation should be scoped to
  the 2-4 range only**, and the small-n groups should be nb u tmed as
  data-limited if mentioned at all, per the same "don't guess/overclaim"
  policy used during cleaning.
- **Revenue by Day×Time:** weekday (Thur/Fri) dinners out-earn weekday
  lunches per bill, but the pattern **flips on weekends** — Sat/Sun lunch
  bills average higher than Sat/Sun dinner bills, with Sun lunch highest
  overall (~$28). Cross-checked against slot sizes: Sat lunch n=22, Sun
  lunch n=17 — smaller than the ~90-100 row dinner slots on those same
  days, so this reads as a lead worth investigating (a possibly
  under-served high-value slot) rather than a settled finding, given the
  smaller sample.

**How:** `python scripts/02_eda_partial.py` (regenerates all 7 figures);
notebook updated with matching cells + interpretation and re-executed via
`jupyter nbconvert --to notebook --execute --inplace notebooks/02_eda.ipynb`.

---

## 2026-09-24 — Reworked Day handling: drop unrecoverable rows instead of imputing

> **Supersedes:** the `Day` imputation described in the "Phase 2: Data
> cleaning" and "Upgraded imputation" entries above no longer happens.
> Everything else in those entries (Amount/Tip/Gender/Smoker/Time/Partysize
> handling) is unchanged.

**What:** `Day` previously had 13 rows where no value could be recovered:
4 originally blank, and 9 with a typed-but-ambiguous value (`S` x5, `SS`,
`SSS`, `San`, `Ft`) that doesn't map confidently to a single day (e.g.
`San` is an equally close match to both "Sun" and "Sat" -- a genuine tie,
not a typo with one obvious fix). These were being imputed via the mode of
each row's `Time` group. Changed `scripts/01_clean_data.py` (and mirrored
in `notebooks/01_clean_data.ipynb`) to **drop all 13 of these rows
entirely** instead, right after the `Day` typo-mapping step, before any
imputation runs. `Time`'s own imputation (still grouped by `Day`) and every
downstream step now runs on the reduced dataset.

**Why:** raised as a direct question -- since `Day` truly carries no
recoverable signal for these rows (unlike, say, a decimal-separator typo in
`Amount`, which has exactly one sensible reading), is it better to guess a
value from group context, or to just not have an opinion about that row's
`Day` at all? Two options were discussed:
  - keep imputing via the `Time`-group mode (statistically grounded, but
    means the *same* raw string, e.g. `"S"`, silently becomes a *different*
    final day depending on the row's `Time` -- confusing to explain/defend
    in the report without the reader digging into the code)
  - drop the row (loses the row's other real data -- Amount, Tip, etc. --
    but avoids fabricating a `Day` value with no real basis)
  Decision: **drop**, for both the blank and the ambiguous-typo rows.
  Rationale: with 365 rows total, losing 13 (3.6%) is a small, statable
  cost, and it keeps the reported `Day` column fully observed data rather
  than a mix of real and guessed values -- simpler to defend than
  explaining a same-input-different-output imputation rule.

**Impact:** dataset shrinks from 365 -> **352** rows. Re-ran
`scripts/01_clean_data.py` and `scripts/02_eda_partial.py`; summary stats
barely moved (e.g. Amount mean 21.21 -> 21.15, median unchanged at ~19.1;
TipPct mean 16.16 -> 16.28). Category counts shift slightly (`Day`: Sat 115
/ Sun 108 / Thur 90 / Fri 39, was Sat 122 / Sun 108 / Thur 96 / Fri 39).
All 7 figures in `figures/` regenerated against the 352-row dataset.

**How:** replaced the `Day` block's `report["Day: missing/unresolved"]`
line with an explicit `blank_day` / `ambiguous_day` mask, dropped both via
`df[~(blank_day | ambiguous_day)].reset_index(drop=True)`, and removed the
now-dead `impute_categorical_grouped("Day", ["Time"])` call (nothing left
to impute). Re-executed both notebooks via `jupyter nbconvert --to
notebook --execute --inplace`.

---

## 2026-09-24 — Adopted teammate-provided file as the team's final dataset

**What:** A teammate pushed `data/Restaurant_cleaned_final.csv` directly
(commit `8662d3d`, "Add files via upload" — no script or notebook came
with it). Compared it against this pipeline's own
`data/restaurant_clean_final.csv` (349 rows vs. 352). Team decision: adopt
the teammate's file as-is as the actual final dataset for all downstream
analysis. Repointed `scripts/02_eda_partial.py` and `notebooks/02_eda.ipynb`
to read `data/Restaurant_cleaned_final.csv` instead. Deleted the old
`data/restaurant_clean_final.csv` from the repo and added it to
`.gitignore` (it can still be regenerated locally by
`scripts/01_clean_data.py` / `notebooks/01_clean_data.ipynb`, kept as an
independent cross-check, but that output is no longer tracked or used
downstream).

**Independent validation performed before adopting it** (since its
cleaning process isn't documented in this repo):
- 0 missing values in any column.
- `Gender` ∈ {Male, Female}, `Smoker` ∈ {No, Yes}, `Day` ∈ {Thur, Fri, Sat,
  Sun}, `Time` ∈ {Lunch, Dinner} — no stray categories.
- `Partysize` fully within 1–6.
- No negative `Amount`, no `Tip` > 100.
- `TipPct` column matches `Tip / Amount * 100` exactly for every row.

**Known discrepancy vs. this pipeline's own output (not yet resolved):**
row-level diffing found the teammate's file resolves a few ambiguous raw
values differently than this pipeline does — e.g. raw `Day = "T"` and
`Day = "Sn"` are treated here as confident matches to `Thur`/`Sun`
respectively, but appear dropped as unresolved in the teammate's version;
a row with `Partysize = -2` and blank `Smoker` is imputed here but absent
there. This means the teammate used a different (undocumented) rule set,
not just a different random seed or rounding. **Action item: get the
teammate's cleaning rationale in writing before finalizing the Data
(pre)processing section of the report** — per the assignment brief
([MP1Specs.pdf](MP1Specs.pdf)), every cleansing step needs a documented
justification, and right now this file's don't exist anywhere in the repo.

**Impact:** EDA re-run against the new 349-row file — summary stats
essentially unchanged from this pipeline's own 352-row version (e.g.
Amount mean 21.15 → 21.19, TipPct mean 16.28 → 16.29). All 7 figures in
`figures/` regenerated; `notebooks/02_eda.ipynb` re-executed.

---

## Template for new entries

```
## YYYY-MM-DD — <short title>

**What:** <what you did>
**Why:** <the reasoning / decision, especially anything non-obvious>
**How:** <command(s) run, or file(s) changed>
```
