# FSSAI source notes

- Publisher: Food Safety and Standards Authority of India (FSSAI), Ministry of Health and Family Welfare, Government of India.
- Source report: Annual Report 2021-22, Tables 14 and 15 (printed pages 52-55).
- Official PDF URL: https://www.fssai.gov.in/upload/uploadfiles/files/Annual.pdf
- Download/check date: 2026-11-08.
- Source PDF: `Annual.pdf` (provided by the user in this folder; verified as a readable, unencrypted 370-page PDF).
- Extracted files: `fssai_sample_testing_2021-22.csv` (selected Table 14 fields) and `fssai_inspections_2021-22.csv` (Table 15).
- The CSV values are aggregate report values, not individual records. The totals in both CSVs match the corresponding state-table totals published in the report. The local PDF is retained for reference.
- Table 14 source categories: samples lifted, analysed, reports awaited, non-conforming results on samples collected in previous year but declared this year, non-conforming results on samples lifted and analysed this year, and unsafe/sub-standard/labelling defects-misleading-miscellaneous counts.
- Table 15 source categories: FoSCoRIS inspections for central-licensed, state-licensed and registered food business operators (FBOs), with state/UT totals. FSSAI reports an additional 5,063 inspections by Railways and Airport authorities, making a grand total of 219,775; those inspections are not assigned to state rows in this CSV.
- Preserve the source values. The non-conforming category counts reconcile to non-conforming totals in all 36 states/UTs, and inspection subtotals reconcile in all 36. In Madhya Pradesh and Uttarakhand, analysed counts exceed lifted counts; reports-awaited counts also differ from the simple lifted-minus-analysed balance in several states. These may reflect reporting-period differences. Do not silently correct them; review them with the table definitions.
- These are state-year aggregates; they cannot support individual sample-level classification or claims about particular businesses/products.
