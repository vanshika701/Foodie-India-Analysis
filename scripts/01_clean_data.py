"""
Phase 2 - Data Cleaning for Foodie India MP1.

Reads the raw Restaurant.xlsx, fixes typos/formatting errors, flags
domain-invalid values as missing, imputes them, and writes two outputs:
  data/restaurant_clean_with_na.csv   -> typos fixed, invalid values set to NaN
  data/restaurant_clean_final.csv     -> above + missing values imputed

NOTE (2026-09-24): the team has since adopted a teammate-provided file,
data/Restaurant_cleaned_final.csv, as the actual final dataset used
downstream (scripts/02_eda_partial.py reads that one, not this script's
output) -- see log.md. This script still runs and its output is kept as an
independent, fully-documented cross-check, but re-running it will
regenerate restaurant_clean_final.csv locally; that file is gitignored so
it won't get re-tracked.

Every cleaning decision here is documented with its rationale in log.md.
Run: source venv/bin/activate && python scripts/01_clean_data.py
"""
import pandas as pd
import numpy as np

RAW_PATH = "Restaurant.xlsx"
OUT_WITH_NA = "data/restaurant_clean_with_na.csv"
OUT_FINAL = "data/restaurant_clean_final.csv"


def fix_numeric_typo(v):
    """Amount/Tip were entered with stray punctuation instead of a decimal
    point (e.g. '28,87', '25-89') or trailing junk characters (e.g. '2.0`').
    A single comma/dash in a currency-like string is almost certainly a
    decimal separator typo, not subtraction or a thousands separator, since
    it appears exactly once and in the expected decimal position."""
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if "," in s:
        s = s.replace(",", ".", 1)
    elif s.count("-") == 1 and not s.startswith("-"):
        s = s.replace("-", ".", 1)
    s = "".join(ch for ch in s if ch.isdigit() or ch == "." or ch == "-")
    try:
        return float(s)
    except ValueError:
        return np.nan


GENDER_MAP = {
    "male": "Male", "m": "Male", "mal": "Male", "mle": "Male",
    "female": "Female", "f": "Female", "fe": "Female", "fmle": "Female",
    "femle": "Female", "fem": "Female",
}

SMOKER_MAP = {"no": "No", "n": "No", "yes": "Yes", "y": "Yes"}
# 's' alone doesn't unambiguously match "Yes" or "No" -> left unmapped (becomes NaN)

DAY_MAP = {
    "thur": "Thur", "thurs": "Thur", "trhurs": "Thur", "th": "Thur", "t": "Thur",
    "fri": "Fri", "friday": "Fri",
    "sat": "Sat", "saturday": "Sat",
    "sun": "Sun", "sn": "Sun",
}
# 'S', 'SS', 'SSS', 'San', 'Ft' are equally consistent with more than one day
# (e.g. 'San' is a 2/3-letter match to both "Sun" and "Sat") -> left unmapped

TIME_MAP = {
    "dinner": "Dinner", "diner": "Dinner", "dd": "Dinner", "ddd": "Dinner",
    "di": "Dinner", "din": "Dinner", "d": "Dinner",
    "lunch": "Lunch", "l": "Lunch", "lu": "Lunch", "lan": "Lunch",
}
# 'LD', 'er', 'Afd', 'Din/Lun' don't map confidently to a single value -> NaN


def map_category(series, mapping):
    return series.astype(str).str.strip().str.lower().map(mapping)


def clean():
    df = pd.read_excel(RAW_PATH)
    df = df[["Amount", "Tip", "Gender", "Smoker", "Day", "Time", "Partysize"]].copy()
    n_raw = len(df)

    report = {}

    # --- Amount ---
    df["Amount"] = df["Amount"].apply(fix_numeric_typo)
    invalid_amount = df["Amount"] < 0  # a negative bill is physically impossible
    report["Amount: negative (invalid)"] = int(invalid_amount.sum())
    df.loc[invalid_amount, "Amount"] = np.nan

    # --- Tip ---
    df["Tip"] = df["Tip"].apply(fix_numeric_typo)
    # Tips of 288 / 300 / 3487 on ~$21-22 bills are not plausible generosity,
    # they're decimal-placement errors; we don't guess the intended value,
    # we mark them invalid like any other unrecoverable entry.
    invalid_tip = df["Tip"] > 100
    report["Tip: implausibly large (invalid)"] = int(invalid_tip.sum())
    df.loc[invalid_tip, "Tip"] = np.nan

    # --- Gender ---
    mapped = map_category(df["Gender"], GENDER_MAP)
    report["Gender: typo values corrected"] = int((mapped != df["Gender"]).sum())
    df["Gender"] = mapped
    report["Gender: unresolved -> missing"] = int(df["Gender"].isna().sum())

    # --- Smoker ---
    mapped = map_category(df["Smoker"], SMOKER_MAP)
    report["Smoker: typo values corrected"] = int(
        ((mapped != df["Smoker"]) & mapped.notna()).sum()
    )
    df["Smoker"] = mapped
    report["Smoker: missing/unresolved"] = int(df["Smoker"].isna().sum())

    # --- Day ---
    raw_day = df["Day"]
    mapped = map_category(df["Day"], DAY_MAP)
    report["Day: typo values corrected"] = int(
        ((mapped != raw_day) & mapped.notna()).sum()
    )
    # Day can't be recovered for two kinds of rows: it was left blank, or a
    # value was entered that doesn't map to any single day unambiguously
    # (e.g. 'S', 'SSS', 'San', 'Ft' -- 'San' is an equally close match to
    # both "Sun" and "Sat"). Rather than guess/impute a specific day for
    # either case, both are dropped entirely.
    blank_day = raw_day.isna()
    ambiguous_day = mapped.isna() & raw_day.notna()
    report["Day: blank (dropped)"] = int(blank_day.sum())
    report["Day: ambiguous typo (dropped)"] = int(ambiguous_day.sum())
    df["Day"] = mapped
    df = df[~(blank_day | ambiguous_day)].reset_index(drop=True)

    # --- Time ---
    mapped = map_category(df["Time"], TIME_MAP)
    report["Time: typo values corrected"] = int(
        ((mapped != df["Time"]) & mapped.notna()).sum()
    )
    df["Time"] = mapped
    report["Time: missing/unresolved"] = int(df["Time"].isna().sum())

    # --- Partysize ---
    df["Partysize"] = pd.to_numeric(df["Partysize"], errors="coerce")
    # Observed valid range is 1-6 guests; anything <=0, >6 (200, 45, 22, ...),
    # or non-integer (0.2 -- a party has a whole number of people) is a
    # data-entry error rather than a real party size. We do not guess the
    # intended digit -> treat as invalid/missing.
    non_integer = (df["Partysize"] % 1 != 0) & df["Partysize"].notna()
    invalid_party = (df["Partysize"] <= 0) | (df["Partysize"] > 6) | non_integer
    report["Partysize: domain-invalid (<=0 or >6)"] = int(invalid_party.sum())
    df.loc[invalid_party, "Partysize"] = np.nan
    report["Partysize: originally blank"] = int(
        pd.read_excel(RAW_PATH)["Partysize"].isna().sum()
    )

    df.to_csv(OUT_WITH_NA, index=False)

    # --- Imputation: group-wise, not a single global constant ---
    # A single global mode/median (e.g. "every missing Smoker becomes No")
    # ignores that these fields correlate with each other in real dining
    # patterns (Thur is overwhelmingly Lunch, Sat/Sun overwhelmingly Dinner
    # -- see log.md for the crosstab). Filling from the value typical of a
    # similar subgroup (same Day+Time) is a small step up in realism while
    # staying simple enough to justify in the report, with a global
    # fallback for the rare case a group has no usable data.
    imputed = df.copy()

    def impute_categorical_grouped(col, group_cols):
        if not imputed[col].isna().any():
            return
        missing_idx = imputed[imputed[col].isna()].index
        global_mode = imputed[col].mode(dropna=True)[0]
        filled_from_group, filled_from_fallback = 0, 0
        for idx in missing_idx:
            key = imputed.loc[idx, group_cols]
            if key.isna().any():
                imputed.loc[idx, col] = global_mode
                filled_from_fallback += 1
                continue
            mask = (imputed[group_cols] == key).all(axis=1) & imputed[col].notna()
            group_vals = imputed.loc[mask, col]
            if len(group_vals) == 0:
                imputed.loc[idx, col] = global_mode
                filled_from_fallback += 1
            else:
                imputed.loc[idx, col] = group_vals.mode().iloc[0]
                filled_from_group += 1
        report[f"{col}: imputed via mode within {'+'.join(group_cols)} group"] = filled_from_group
        if filled_from_fallback:
            report[f"{col}: imputed via global mode (group had no data)"] = filled_from_fallback

    def impute_numeric_grouped(col, group_cols):
        if not imputed[col].isna().any():
            return
        missing_idx = imputed[imputed[col].isna()].index
        global_median = imputed[col].median()
        filled_from_group, filled_from_fallback = 0, 0
        for idx in missing_idx:
            key = imputed.loc[idx, group_cols]
            if key.isna().any():
                imputed.loc[idx, col] = global_median
                filled_from_fallback += 1
                continue
            mask = (imputed[group_cols] == key).all(axis=1) & imputed[col].notna()
            group_vals = imputed.loc[mask, col]
            if len(group_vals) == 0:
                imputed.loc[idx, col] = global_median
                filled_from_fallback += 1
            else:
                imputed.loc[idx, col] = group_vals.median()
                filled_from_group += 1
        report[f"{col}: imputed via median within {'+'.join(group_cols)} group"] = filled_from_group
        if filled_from_fallback:
            report[f"{col}: imputed via global median (group had no data)"] = filled_from_fallback

    # Day has no missing/unresolved values left at this point -- rows where
    # it couldn't be recovered (blank or an ambiguous typo) were dropped
    # above rather than imputed. Time is imputed grouped by the now-complete
    # Day column, then Smoker/Amount/Tip/Partysize group on the complete
    # Day+Time pair.
    impute_categorical_grouped("Time", ["Day"])
    impute_categorical_grouped("Smoker", ["Day", "Time"])

    # Amount, Tip and Partysize are all right-skewed (mean > median in the
    # summary stats -- e.g. Amount mean 21.21 vs median 19.11, Tip mean
    # 3.08 vs median 2.85) because a handful of large parties/bills pull
    # the mean upward. The MEDIAN is used instead of the mean for every
    # numeric imputation here because it represents the "typical" party in
    # that Day+Time slot without being dragged by those few outliers --
    # using the mean would systematically overstate the imputed values.
    impute_numeric_grouped("Amount", ["Day", "Time"])
    impute_numeric_grouped("Tip", ["Day", "Time"])
    impute_numeric_grouped("Partysize", ["Day", "Time"])
    imputed["Partysize"] = imputed["Partysize"].round().astype(int)

    # Derived metric used throughout Phase 3/4
    imputed["TipPct"] = (imputed["Tip"] / imputed["Amount"]) * 100

    imputed.to_csv(OUT_FINAL, index=False)

    print(f"Raw rows: {n_raw} | Final rows: {len(imputed)}")
    print("\n--- Cleaning report ---")
    for k, v in report.items():
        print(f"{k}: {v}")
    print(f"\nSaved: {OUT_WITH_NA}")
    print(f"Saved: {OUT_FINAL}")
    return imputed, report


if __name__ == "__main__":
    clean()
