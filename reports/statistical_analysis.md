# Statistical analysis: FSSAI FY 2021-22

## Descriptive statistics

- Analysis unit: State/UT; observations: 36; fiscal year: 2021-22.
- The CSV `reports/statistical_descriptive_statistics.csv` contains count summaries (mean, standard deviation, quartiles, minimum and maximum) across state/UT rows.
- The CSV `reports/state_category_percentages.csv` shows each reported issue category as a percentage of that State/UT's reported non-conforming outcomes. These are composition shares, not the proportion of samples failing tests.

## Category composition across reported outcomes

- Unsafe: 4,890 of 32,934 category counts (14.8%).
- Substandard: 16,582 of 32,934 category counts (50.3%).
- Labelling / misleading / other: 11,462 of 32,934 category counts (34.8%).

## Rank association checks

Spearman's rho compares the rank ordering of state-level counts. A positive coefficient means states with larger values of one count tend also to have larger values of the other count in this one-year table.

- `total_state_inspections` vs `total_nonconforming_samples`: rho=0.718, two-sided p=8.12e-07, n=36.
- `samples_lifted` vs `total_nonconforming_samples`: rho=0.921, two-sided p=1.898e-15, n=36.
- `samples_analysed` vs `total_nonconforming_samples`: rho=0.924, two-sided p=9.348e-16, n=36.

These coefficients are descriptive. States with more testing or inspections have more opportunities to detect and report non-conforming outcomes. The counts also include prior-year samples whose results were declared this year. The table is not a random sample, and p-values here should not be treated as proof of a population-level effect or causal relationship.

## Limitations

- This is a one-year, state/UT aggregate dataset. No month/year trend beyond FY 2021-22, district comparison, or product analysis can be estimated.
- The source does not provide denominators such as food-business population, consumer exposure, or a consistent sample cohort by state. Do not label count comparisons as non-compliance rates.
- Correlation among totals and their component categories is partly structural because the totals are sums of related counts.
- Non-conforming outcomes do not establish confirmed adulteration, and these data do not support sample-level prediction.

## Output files

- `reports/statistical_descriptive_statistics.csv`
- `reports/state_category_percentages.csv`
- `reports/statistical_correlation_results.csv`
- `reports/spearman_correlation_matrix.csv`
- `reports/statistical_figures/spearman_correlation_heatmap.png`
- `reports/statistical_figures/state_category_count_distributions.png`
