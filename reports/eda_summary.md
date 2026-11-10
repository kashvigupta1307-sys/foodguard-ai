# Exploratory data analysis: FSSAI FY 2021-22

## Dataset scope

- 36 State/UT aggregate rows for fiscal year 2021-22.
- The source reports 165,381 samples lifted and 144,345 samples analysed across these state rows.
- Table 14 reports 32,934 non-conforming outcomes in total (previous-year sample results plus current-year sample results).
- Table 15 reports 214,712 state/UT FoSCoRIS inspections; the additional all-India railway/airport inspections are not allocated to the state rows.

## Reported non-conforming outcome categories

- Unsafe: 4,890 (14.8% of category total)
- Substandard: 16,582 (50.3% of category total)
- Labelling / misleading / other: 11,462 (34.8% of category total)

These are counts reported by the regulator, not estimates of the share of all food in circulation that is unsafe.

## State/UT comparisons

Largest reported non-conforming outcome counts (not rates):
- Uttar Pradesh: 13,153
- Tamil Nadu: 3,778
- Madhya Pradesh: 2,900
- Rajasthan: 2,891
- Jammu & Kashmir: 1,735

Largest reported inspection counts:
- Tamil Nadu: 59,069
- Uttar Pradesh: 40,849
- Jammu & Kashmir: 20,050
- Maharashtra: 16,794
- Gujarat: 14,231

The stacked count chart includes these top State/UTs: Uttar Pradesh, Tamil Nadu, Madhya Pradesh, Rajasthan, Jammu & Kashmir, Maharashtra, Haryana, Punjab, Kerala, Gujarat, Uttarakhand, Andhra Pradesh, Telangana, Himachal Pradesh, Odisha.
The inspection chart includes these top State/UTs: Tamil Nadu, Uttar Pradesh, Jammu & Kashmir, Maharashtra, Gujarat, West Bengal, Kerala, Madhya Pradesh, Chhattisgarh, Karnataka, Haryana, Uttarakhand, Assam, Odisha, Andaman & Nicobar Islands.

## Interpretation limits

- Counts depend on testing and inspection volume, reporting practices, and results declared for samples collected in earlier years. A larger count does not by itself mean a higher underlying food-safety rate.
- Inspection counts are not divided by the number of food businesses, population, or samples tested.
- The current dataset has one fiscal year and no monthly date, district, or product fields. Monthly trends, year-over-year trends, district comparisons, and product rankings cannot be calculated from it.
- Do not interpret an unsafe category count or any future analytical score as evidence that a particular food or business is adulterated.

## Generated charts

- `reports/eda_charts/national_nonconforming_categories.png`
- `reports/eda_charts/state_nonconforming_category_counts.png`
- `reports/eda_charts/state_inspection_counts.png`
