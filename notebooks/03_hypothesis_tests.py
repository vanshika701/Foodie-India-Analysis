import pandas as pd
import numpy as np
from scipy import stats

df = pd.read_csv('Restaurant_cleaned_final.csv')

df['DayType'] = df['Day'].map({
    'Thur': 'Weekday', 'Fri': 'Weekday',
    'Sat': 'Weekend', 'Sun': 'Weekend'
})


# HT 1: Bill Amount — Weekday vs Weekend
weekday = df[df['DayType'] == 'Weekday']['Amount']
weekend = df[df['DayType'] == 'Weekend']['Amount']

print("HT 1: Bill Amount, Weekday vs Weekend")
print(f"Weekday: n={len(weekday)}, mean={weekday.mean():.2f}")
print(f"Weekend: n={len(weekend)}, mean={weekend.mean():.2f}")

u_stat, p_value = stats.mannwhitneyu(weekday, weekend, alternative='two-sided')
r_effect = 1 - (2 * u_stat) / (len(weekday) * len(weekend))

print(f"U statistic = {u_stat:.1f}")
print(f"p-value     = {p_value:.5f}")
print(f"Effect size (r) = {r_effect:.3f}")
print("Reject H0" if p_value < 0.05 else "Fail to reject H0")
print()


# HT 2: Party Size vs Bill Amount
r_stat, p_value = stats.pearsonr(df['Partysize'], df['Amount'])

print("HT 2: Party Size vs Bill Amount (Correlation)")
print(f"Pearson r = {r_stat:.3f}")
print(f"p-value   = {p_value:.2e}")
print(f"r-squared = {r_stat**2:.3f}  (variance in Amount explained by Partysize)")
print("Reject H0" if p_value < 0.05 else "Fail to reject H0")
print()


# HT 3: Day vs Time (Chi-square test of independence)
contingency_table = pd.crosstab(df['Day'], df['Time'])
print("Contingency table (Day x Time):")
print(contingency_table)

chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

n = contingency_table.sum().sum()
cramers_v = np.sqrt(chi2 / (n * (min(contingency_table.shape) - 1)))

print("\nHT 3: Day vs Time (Chi-square Test of Independence)")
print(f"Chi-square = {chi2:.3f}")
print(f"df         = {dof}")
print(f"p-value    = {p_value:.2e}")
print(f"Cramer's V = {cramers_v:.3f}")
print("Reject H0" if p_value < 0.05 else "Fail to reject H0")