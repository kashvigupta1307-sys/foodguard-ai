# FoodGuard AI Power BI dashboard package

This folder contains the model measures, theme, and build specification for a separate Power BI report based on authentic FSSAI annual report data.

## Source

Import this file from the project:

`data/processed/fssai_state_summary_2021-22_clean.csv`

Use **Get data → Text/CSV**, load the file, and rename the table to `FSSAI_State_Summary`. The CSV has 36 State/UT rows for FY 2021-22. It contains report provenance, source labels, counts, and validation flags. Keep the raw files and [FSSAI source notes](../data/raw/FSSAI_SOURCE_NOTES.md) with the project.

## Suggested report pages

### 1. Overview

- Cards: State/UT count, samples lifted, samples analysed, total non-conforming outcomes, unsafe outcomes, and State/UT FoSCoRIS inspections.
- Clustered bar chart: reported outcomes by State/UT. Sort descending by total non-conforming count.
- Donut or bar chart: unsafe, substandard, and labelling/misleading/miscellaneous category counts.
- Slicers: State/UT and fiscal year. The current source contains only FY 2021-22, so the year slicer will have one value until more comparable years are added.
- Add a visible note: “Counts reflect reported regulatory activity and outcomes. They are not rates or proof of adulteration.”

### 2. State comparison

- Horizontal bar chart: samples analysed and total non-conforming outcomes by State/UT.
- Table: State/UT, samples lifted, samples analysed, reports awaited, the three outcome categories, inspections, and validation flags.
- Keep outcome and inspection charts separate; inspections are not the denominator for laboratory outcomes.

### 3. Outcome categories

- Category count visual and category share of reported category counts.
- Explain that category composition describes the breakdown of reported outcomes; it is not the chance that food is unsafe.

Avoid monthly trends, product rankings, district maps, and Low/Medium/High risk cards: these fields are not present in the current source. Keep FSSAI Table 15 inspections separate from Table 14 sample results. Do not infer missing State/UTs, food categories, or dates.

## Measures

Open `measures.dax`, create each measure in Power BI under **Modeling → New measure**, and paste the expression following the measure name. The measures aggregate source-reported counts; their names intentionally say “count” or “share.”

## Theme

In Power BI Desktop, use **View → Themes → Browse for themes** and select `foodguard_theme.json`.

## Validation before sharing

Check that the card totals equal the source report totals: samples lifted 165,381; samples analysed 144,345; previous-year sample outcomes reported this year 8,423; current-year sample outcomes 24,511; unsafe 4,890; substandard 16,582; labelling/misleading/miscellaneous 11,462; and state-row inspections 214,712. Table 15 also reports 5,063 Railways and Airport inspections outside the State/UT row totals, for a grand total of 219,775.

The input has documented count reconciliation flags. Preserve source values; do not silently edit figures to force unrelated counts to balance.

## Power BI file limitation

Power BI Desktop is not installed in this Mac workspace, so a native `.pbix` report cannot be authored or visually checked here. This package provides the source model, measures, visual plan, and theme for building it in Power BI Desktop. The actual canvas layout and final `.pbix` still need to be created and reviewed there.
