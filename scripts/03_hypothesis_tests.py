import pandas as pd
import numpy as np
from scipy import stats


df = pd.read_csv('data/Restaurant_cleaned_final.csv')

df['DayType'] = df['Day'].map({
    'Thur': 'Weekday', 'Fri': 'Weekday',
    'Sat': 'Weekend', 'Sun': 'Weekend'
})


# ===========================================================
# HT 1: Bill Amount — Weekday vs Weekend

weekday = df[df['DayType'] == 'Weekday']['Amount']
weekend = df[df['DayType'] == 'Weekend']['Amount']

print("HT 1: Bill Amount, Weekday vs Weekend")
print(f"Weekday: n={len(weekday)}, mean={weekday.mean():.2f}")
print(f"Weekend: n={len(weekend)}, mean={weekend.mean():.2f}")

u_stat, p_value = stats.mannwhitneyu(weekday, weekend, alternative='two-sided')

# Effect size: rank-biserial correlation
r_effect = 1 - (2 * u_stat) / (len(weekday) * len(weekend))

print(f"U statistic = {u_stat:.1f}")
print(f"p-value     = {p_value:.5f}")
print(f"Effect size (r) = {r_effect:.3f}")
print("Reject H0" if p_value < 0.05 else "Fail to reject H0")
print()


# ===========================================================
# HT 2: Party Size vs Bill Amount

r_stat, p_value = stats.pearsonr(df['Partysize'], df['Amount'])

print("HT 2: Party Size vs Bill Amount (Correlation)")
print(f"Pearson r = {r_stat:.3f}")
print(f"p-value   = {p_value:.2e}")
print(f"r-squared = {r_stat**2:.3f}  (variance in Amount explained by Partysize)")
print("Reject H0" if p_value < 0.05 else "Fail to reject H0")
print()


# ===========================================================
# HT 3: Day vs Time (Chi-square test of independence)

contingency_table = pd.crosstab(df['Day'], df['Time'])
print("Contingency table (Day x Time):")
print(contingency_table)

chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

# Effect size: Cramer's V
n = contingency_table.sum().sum()
cramers_v = np.sqrt(chi2 / (n * (min(contingency_table.shape) - 1)))

print("\nHT 3: Day vs Time (Chi-square Test of Independence)")
print(f"Chi-square = {chi2:.3f}")
print(f"df         = {dof}")
print(f"p-value    = {p_value:.2e}")
print(f"Cramer's V = {cramers_v:.3f}")
print("Reject H0" if p_value < 0.05 else "Fail to reject H0")
print()


# ===========================================================
# HT 4: Tip % by Smoker status

no_smoke = df.loc[df['Smoker'] == 'No', 'TipPct']
yes_smoke = df.loc[df['Smoker'] == 'Yes', 'TipPct']

print("HT 4: Tip % by Smoker Status")
print(f"No:  n={len(no_smoke)}, mean={no_smoke.mean():.2f}%")
print(f"Yes: n={len(yes_smoke)}, mean={yes_smoke.mean():.2f}%")

u_stat, p_value = stats.mannwhitneyu(no_smoke, yes_smoke, alternative='two-sided')
r_effect = 1 - (2 * u_stat) / (len(no_smoke) * len(yes_smoke))

print(f"U statistic = {u_stat:.1f}")
print(f"p-value     = {p_value:.4f}")
print(f"Effect size (r) = {r_effect:.3f}")
print("Reject H0" if p_value < 0.05 else "Fail to reject H0")
print()


# ===========================================================
# HT 5: Tip % by Waiter Gender

female = df.loc[df['Gender'] == 'Female', 'TipPct']
male = df.loc[df['Gender'] == 'Male', 'TipPct']

print("HT 5: Tip % by Waiter Gender")
print(f"Female: n={len(female)}, mean={female.mean():.2f}%")
print(f"Male:   n={len(male)}, mean={male.mean():.2f}%")

u_stat, p_value = stats.mannwhitneyu(female, male, alternative='two-sided')
r_effect = 1 - (2 * u_stat) / (len(female) * len(male))

print(f"U statistic = {u_stat:.1f}")
print(f"p-value     = {p_value:.4f}")
print(f"Effect size (r) = {r_effect:.3f}")
print("Reject H0" if p_value < 0.05 else "Fail to reject H0")
print()


# ===========================================================
# HT 6: Tip % vs Party Size (sizes 2-4 only)

sub = df[df['Partysize'].between(2, 4)]

print("HT 6: Tip % vs Party Size (sizes 2-4 only)")
print(f"n = {len(sub)}")

rho, p_value = stats.spearmanr(sub['Partysize'], sub['TipPct'])
r_pearson, p_pearson = stats.pearsonr(sub['Partysize'], sub['TipPct'])

print(f"Spearman rho = {rho:.4f}")
print(f"p-value      = {p_value:.4f}")
print(f"(Pearson r for reference = {r_pearson:.4f}, p = {p_pearson:.4f})")
print("Reject H0" if p_value < 0.05 else "Fail to reject H0")
print()


# ===========================================================
# HT 7: Bill Amount — Weekend Lunch vs Weekend Dinner

weekend = df[df['Day'].isin(['Sat', 'Sun'])]
wk_lunch = weekend.loc[weekend['Time'] == 'Lunch', 'Amount']
wk_dinner = weekend.loc[weekend['Time'] == 'Dinner', 'Amount']

print("HT 7: Bill Amount, Weekend Lunch vs Weekend Dinner")
print(f"Lunch:  n={len(wk_lunch)}, mean=${wk_lunch.mean():.2f}")
print(f"Dinner: n={len(wk_dinner)}, mean=${wk_dinner.mean():.2f}")

u_stat, p_value = stats.mannwhitneyu(wk_lunch, wk_dinner, alternative='two-sided')
r_effect = 1 - (2 * u_stat) / (len(wk_lunch) * len(wk_dinner))

print(f"U statistic = {u_stat:.1f}")
print(f"p-value     = {p_value:.4f}")
print(f"Effect size (r) = {r_effect:.3f}")
print("Reject H0" if p_value < 0.05 else "Fail to reject H0")