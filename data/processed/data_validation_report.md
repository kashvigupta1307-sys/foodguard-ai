# FSSAI 2021-22 data cleaning and validation

## Cleaning performed

- Joined Table 14 and Table 15 at state/UT and fiscal-year level; 36 rows retained.
- Trimmed whitespace and harmonized two state/UT spelling variants for joining. Original labels are preserved in source-name columns.
- Converted counts to integer values and rejected missing required columns, negative counts, or duplicate state-year keys.
- No rows were imputed or expanded into individual samples. No source counts were changed.

## Reconciliation checks

- Table 14 summed state counts: samples_lifted=165,381, samples_analysed=144,345, analysis_reports_awaited=36,920, nonconforming_previous_year_samples=8,423, nonconforming_current_year_samples=24,511, unsafe_samples=4,890, substandard_samples=16,582, labelling_misleading_misc_samples=11,462.
- Table 15 state inspection total: 214,712.
- Table 14 non-conforming totals reconcile to the three reported issue categories for 36/36 state/UT rows.
- Table 15 inspection subtotals reconcile to the reported state total for 36/36 state/UT rows.
- Samples analysed exceed samples lifted in these rows: Madhya Pradesh, Uttarakhand.
- Reports-awaited counts differ from max(samples lifted - samples analysed, 0) in these rows: Andhra Pradesh, Assam, Dadra & Nagar Haveli & Daman and Diu, Himachal Pradesh, Jammu & Kashmir, Ladakh, Madhya Pradesh, Tamil Nadu, Uttar Pradesh, Uttarakhand.
- The last two checks are review flags, not automatic errors: counts can reflect reporting periods and samples carried over from a prior year. Interpret them using FSSAI's table definitions.

## Scope and limitations

- Data grain: one aggregate row per State/UT for FY 2021-22.
- These counts do not identify individual samples, districts, products, or businesses and cannot support sample-level prediction.
- Non-conforming results are not synonymous with confirmed adulteration.
- Source PDF: `data/raw/Annual.pdf`; see `data/raw/FSSAI_SOURCE_NOTES.md`.
