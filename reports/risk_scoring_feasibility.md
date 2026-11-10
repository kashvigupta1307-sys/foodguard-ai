# Food safety risk scoring: feasibility assessment

## Decision: no Low/Medium/High risk labels

The data is aggregated by State/UT and contains 1 fiscal year(s) (2021-22). It has no inspection dates or recent inspection outcomes, no entity-level history, and no validated severity weights. Required recency and repeated-violation signals are unavailable.

A score from these data could create a false impression of precision. State-year totals do not identify businesses, products, districts, inspection dates, or repeat outcomes. Therefore this project does not assign a food-safety risk score or Low/Medium/High category to any State/UT.

## Descriptive reporting indicators

- Reported current-year non-conforming samples: 24,511 across the state rows.
- Reported state/UT FoSCoRIS inspections: 214,712.
- Highest indicative current-year non-conformance yield: Jharkhand: 48.6%.
- Lowest indicative current-year non-conformance yield among states with samples analysed: Tripura: 0.0%.

### Indicator definitions and caveats

- `indicative_current_year_nonconforming_yield_percent` = reported non-conforming samples lifted and analysed in FY 2021-22 divided by samples analysed, multiplied by 100. This is a rough reporting yield only, not an official compliance rate; counts reflect testing/reporting activity and the report has denominator inconsistencies for some State/UTs.
- `unsafe_share_of_reported_issue_categories_percent` = unsafe count divided by unsafe + substandard + labelling/misleading/miscellaneous counts. This describes the composition of reported issue categories, not the chance that a food item is unsafe.
- Zero denominators result in blank percentages, never zero risk.
- `risk_score` is intentionally blank and `risk_category` is `Not scored` for every row.

## What a future risk-scoring dataset needs

To produce an explainable and useful prioritization score, obtain authentic repeated records with a stable food-business or sampling-site identifier, inspection dates, outcomes, count of prior violations, severity defined by the regulator, and enough history to define a recent window. Validate sampling and reporting consistency, then document thresholds with domain experts. Any resulting score would be a prioritization aid, not confirmed evidence of adulteration.

## Output

- `data/processed/state_reporting_indicators_2021-22.csv`
