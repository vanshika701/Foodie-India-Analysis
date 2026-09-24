"""
Phase 3 (partial) - Exploratory Data Analysis for Foodie India MP1.

Uses the cleaned+imputed dataset (data/Restaurant_cleaned_final.csv) to
produce a first pass of summary stats and a handful of business-relevant
charts. This is a PARTIAL pass -- enough to sanity-check the cleaned data
and surface early patterns before the full Phase 3/4 (visualization +
hypothesis testing).

NOTE: as of 2026-09-24 this reads the team's agreed-final dataset
(provided by a teammate), not the output of scripts/01_clean_data.py --
see log.md for why.

Run: source venv/bin/activate && python scripts/02_eda_partial.py
"""
import pandas as pd
import matplotlib.pyplot as plt

IN_PATH = "data/Restaurant_cleaned_final.csv"
FIG_DIR = "figures"

DAY_ORDER = ["Thur", "Fri", "Sat", "Sun"]
TIME_ORDER = ["Lunch", "Dinner"]

# Fixed categorical colors (Okabe-Ito colorblind-safe set), assigned by
# entity identity and reused across every chart -- never re-cycled per chart.
BLUE = "#0072B2"
ORANGE = "#E69F00"
GREEN = "#009E73"
VERMILLION = "#D55E00"
GRAY = "#666666"

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#999999",
    "axes.grid": True,
    "grid.color": "#e6e6e6",
    "grid.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 11,
})


def summary_stats(df):
    print("=== Summary statistics ===")
    print(df[["Amount", "Tip", "TipPct", "Partysize"]].describe().round(2))
    print("\n=== Category counts ===")
    for col in ["Gender", "Smoker", "Day", "Time"]:
        print(f"\n{col}:")
        print(df[col].value_counts())


def chart_amount_tip_distribution(df):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].hist(df["Amount"], bins=20, color=BLUE, edgecolor="white")
    axes[0].set_title("Distribution of Bill Amount")
    axes[0].set_xlabel("Amount ($)")
    axes[0].set_ylabel("Number of parties")

    axes[1].hist(df["TipPct"], bins=20, color=ORANGE, edgecolor="white")
    axes[1].set_title("Distribution of Tip %")
    axes[1].set_xlabel("Tip as % of bill")
    axes[1].set_ylabel("Number of parties")

    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/01_amount_tippct_distribution.png", dpi=150)
    plt.close(fig)


def chart_tippct_by_day_time(df):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    by_day = df.groupby("Day")["TipPct"].mean().reindex(DAY_ORDER)
    axes[0].bar(by_day.index, by_day.values, color=BLUE)
    axes[0].set_title("Average Tip % by Day")
    axes[0].set_ylabel("Average tip %")
    for i, v in enumerate(by_day.values):
        axes[0].text(i, v + 0.15, f"{v:.1f}", ha="center", fontsize=9, color="#333")

    by_time = df.groupby("Time")["TipPct"].mean().reindex(TIME_ORDER)
    axes[1].bar(by_time.index, by_time.values, color=ORANGE)
    axes[1].set_title("Average Tip % by Time")
    axes[1].set_ylabel("Average tip %")
    for i, v in enumerate(by_time.values):
        axes[1].text(i, v + 0.15, f"{v:.1f}", ha="center", fontsize=9, color="#333")

    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/02_tippct_by_day_time.png", dpi=150)
    plt.close(fig)


def chart_tippct_by_smoker(df):
    fig, ax = plt.subplots(figsize=(6, 4))
    groups = [df.loc[df["Smoker"] == cat, "TipPct"].dropna() for cat in ["No", "Yes"]]
    bp = ax.boxplot(groups, tick_labels=["Non-smoking party", "Smoking party"],
                     patch_artist=True, widths=0.5)
    for patch, color in zip(bp["boxes"], [BLUE, VERMILLION]):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    ax.set_title("Tip % by Smoker Status")
    ax.set_ylabel("Tip %")
    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/03_tippct_by_smoker.png", dpi=150)
    plt.close(fig)


def chart_party_volume_day_time(df):
    counts = df.groupby(["Day", "Time"]).size().unstack("Time").reindex(DAY_ORDER)
    counts = counts[TIME_ORDER]

    fig, ax = plt.subplots(figsize=(7, 4))
    x = range(len(counts.index))
    width = 0.35
    ax.bar([i - width / 2 for i in x], counts["Lunch"], width, label="Lunch", color=BLUE)
    ax.bar([i + width / 2 for i in x], counts["Dinner"], width, label="Dinner", color=ORANGE)
    ax.set_xticks(list(x))
    ax.set_xticklabels(counts.index)
    ax.set_ylabel("Number of parties")
    ax.set_title("Party Volume by Day and Time")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/04_party_volume_day_time.png", dpi=150)
    plt.close(fig)


def chart_tippct_by_gender(df):
    fig, ax = plt.subplots(figsize=(6, 4))
    groups = [df.loc[df["Gender"] == cat, "TipPct"].dropna() for cat in ["Male", "Female"]]
    bp = ax.boxplot(groups, tick_labels=["Male waiter", "Female waiter"],
                     patch_artist=True, widths=0.5)
    for patch, color in zip(bp["boxes"], [BLUE, ORANGE]):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    ax.set_title("Tip % by Waiter Gender")
    ax.set_ylabel("Tip %")
    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/05_tippct_by_gender.png", dpi=150)
    plt.close(fig)


def chart_tippct_by_partysize(df):
    by_size = df.groupby("Partysize")["TipPct"].mean().sort_index()
    counts = df.groupby("Partysize").size().sort_index()

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(by_size.index, by_size.values, color=GREEN)
    ax.set_title("Average Tip % by Party Size")
    ax.set_xlabel("Party size (number of guests)")
    ax.set_ylabel("Average tip %")
    ax.set_xticks(list(by_size.index))
    for size, v in by_size.items():
        n = counts.loc[size]
        ax.text(size, v + 0.15, f"{v:.1f}\n(n={n})", ha="center", fontsize=8, color="#333")
    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/06_tippct_by_partysize.png", dpi=150)
    plt.close(fig)


def chart_amount_by_day_time(df):
    avg = df.groupby(["Day", "Time"])["Amount"].mean().unstack("Time").reindex(DAY_ORDER)
    avg = avg[TIME_ORDER]

    fig, ax = plt.subplots(figsize=(7, 4))
    x = range(len(avg.index))
    width = 0.35
    ax.bar([i - width / 2 for i in x], avg["Lunch"], width, label="Lunch", color=BLUE)
    ax.bar([i + width / 2 for i in x], avg["Dinner"], width, label="Dinner", color=ORANGE)
    ax.set_xticks(list(x))
    ax.set_xticklabels(avg.index)
    ax.set_ylabel("Average bill amount ($)")
    ax.set_title("Average Bill Amount by Day and Time")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/07_amount_by_day_time.png", dpi=150)
    plt.close(fig)


def main():
    df = pd.read_csv(IN_PATH)
    summary_stats(df)
    chart_amount_tip_distribution(df)
    chart_tippct_by_day_time(df)
    chart_tippct_by_smoker(df)
    chart_party_volume_day_time(df)
    chart_tippct_by_gender(df)
    chart_tippct_by_partysize(df)
    chart_amount_by_day_time(df)
    print(f"\nSaved 7 charts to {FIG_DIR}/")


if __name__ == "__main__":
    main()
