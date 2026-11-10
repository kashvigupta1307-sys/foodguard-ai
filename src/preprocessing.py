"""Clean and validate the FSSAI state-year aggregate tables.

Run from the project root with:
    .venv/bin/python -m src.preprocessing

This module preserves the published counts. It standardizes state names for
joining the two report tables and adds quality-control flags instead of
silently changing values that do not reconcile.
"""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

SAMPLE_FILE = RAW_DIR / "fssai_sample_testing_2021-22.csv"
INSPECTION_FILE = RAW_DIR / "fssai_inspections_2021-22.csv"
OUTPUT_FILE = PROCESSED_DIR / "fssai_state_summary_2021-22_clean.csv"
REPORT_FILE = PROCESSED_DIR / "data_validation_report.md"

SAMPLE_NUMERIC_COLUMNS = [
    "samples_lifted",
    "samples_analysed",
    "analysis_reports_awaited",
    "nonconforming_previous_year_samples",
    "nonconforming_current_year_samples",
    "unsafe_samples",
    "substandard_samples",
    "labelling_misleading_misc_samples",
]

INSPECTION_NUMERIC_COLUMNS = [
    "central_licensed_fbos",
    "state_licensed_fbos",
    "registered_fbos",
    "total_state_inspections",
]


def _canonical_state_name(value: str) -> str:
    """Trim state labels and harmonize the two known source spelling variants."""
    cleaned = " ".join(str(value).split())
    aliases = {
        "andaman and nicobar islands": "Andaman & Nicobar Islands",
        "andaman & nicobar islands": "Andaman & Nicobar Islands",
        "dadra and nagar haveli & daman and diu": (
            "Dadra & Nagar Haveli & Daman and Diu"
        ),
        "dadra & nagar haveli & daman and diu": (
            "Dadra & Nagar Haveli & Daman and Diu"
        ),
    }
    return aliases.get(cleaned.casefold(), cleaned)


def _load_and_validate_source(
    path: Path, required_columns: list[str], numeric_columns: list[str]
) -> pd.DataFrame:
    """Load a CSV, validate its schema and preserve all reported rows."""
    if not path.is_file():
        raise FileNotFoundError(f"Expected source file was not found: {path}")

    frame = pd.read_csv(path)
    missing_columns = sorted(set(required_columns) - set(frame.columns))
    if missing_columns:
        raise ValueError(f"{path.name} is missing columns: {missing_columns}")

    frame["state_ut_source"] = frame["state_ut"].astype("string").str.strip()
    frame["state_ut"] = frame["state_ut_source"].map(_canonical_state_name)
    frame["fiscal_year"] = frame["fiscal_year"].astype("string").str.strip()

    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="raise").astype("int64")
        if (frame[column] < 0).any():
            raise ValueError(f"Negative count found in {path.name}: {column}")

    key = ["fiscal_year", "state_ut"]
    duplicates = frame.duplicated(key, keep=False)
    if duplicates.any():
        rows = frame.loc[duplicates, key].to_dict(orient="records")
        raise ValueError(f"Duplicate state-year records in {path.name}: {rows}")
    return frame


def _make_validation_report(frame: pd.DataFrame) -> str:
    """Create a short report that distinguishes source values from QC flags."""
    category_ok = int(frame["qc_nonconforming_categories_match"].sum())
    inspection_ok = int(frame["qc_inspection_subtotals_match"].sum())
    analysed_exceeds = frame.loc[
        frame["qc_analysed_exceeds_lifted"], "state_ut"
    ].tolist()
    awaited_differs = frame.loc[
        frame["qc_awaited_differs_from_lifted_minus_analysed"], "state_ut"
    ].tolist()
    table14_totals = {
        column: int(frame[column].sum())
        for column in [
            "samples_lifted",
            "samples_analysed",
            "analysis_reports_awaited",
            "nonconforming_previous_year_samples",
            "nonconforming_current_year_samples",
            "unsafe_samples",
            "substandard_samples",
            "labelling_misleading_misc_samples",
        ]
    }
    state_inspections = int(frame["total_state_inspections"].sum())

    lines = [
        "# FSSAI 2021-22 data cleaning and validation",
        "",
        "## Cleaning performed",
        "",
        f"- Joined Table 14 and Table 15 at state/UT and fiscal-year level; {len(frame)} rows retained.",
        "- Trimmed whitespace and harmonized two state/UT spelling variants for joining. Original labels are preserved in source-name columns.",
        "- Converted counts to integer values and rejected missing required columns, negative counts, or duplicate state-year keys.",
        "- No rows were imputed or expanded into individual samples. No source counts were changed.",
        "",
        "## Reconciliation checks",
        "",
        "- Table 14 summed state counts: "
        + ", ".join(f"{name}={value:,}" for name, value in table14_totals.items())
        + ".",
        f"- Table 15 state inspection total: {state_inspections:,}.",
        f"- Table 14 non-conforming totals reconcile to the three reported issue categories for {category_ok}/{len(frame)} state/UT rows.",
        f"- Table 15 inspection subtotals reconcile to the reported state total for {inspection_ok}/{len(frame)} state/UT rows.",
        f"- Samples analysed exceed samples lifted in these rows: {', '.join(analysed_exceeds) if analysed_exceeds else 'none'}.",
        f"- Reports-awaited counts differ from max(samples lifted - samples analysed, 0) in these rows: {', '.join(awaited_differs) if awaited_differs else 'none'}.",
        "- The last two checks are review flags, not automatic errors: counts can reflect reporting periods and samples carried over from a prior year. Interpret them using FSSAI's table definitions.",
        "",
        "## Scope and limitations",
        "",
        "- Data grain: one aggregate row per State/UT for FY 2021-22.",
        "- These counts do not identify individual samples, districts, products, or businesses and cannot support sample-level prediction.",
        "- Non-conforming results are not synonymous with confirmed adulteration.",
        "- Source PDF: `data/raw/Annual.pdf`; see `data/raw/FSSAI_SOURCE_NOTES.md`.",
        "",
    ]
    return "\n".join(lines)


def build_clean_dataset() -> tuple[pd.DataFrame, str]:
    """Join sample and inspection summaries and attach non-destructive QC flags."""
    sample_required = ["fiscal_year", "state_ut", *SAMPLE_NUMERIC_COLUMNS]
    inspection_required = ["fiscal_year", "state_ut", *INSPECTION_NUMERIC_COLUMNS]

    samples = _load_and_validate_source(
        SAMPLE_FILE, sample_required, SAMPLE_NUMERIC_COLUMNS
    )
    inspections = _load_and_validate_source(
        INSPECTION_FILE, inspection_required, INSPECTION_NUMERIC_COLUMNS
    )

    sample_names = samples[["fiscal_year", "state_ut", "state_ut_source"]].rename(
        columns={"state_ut_source": "state_ut_source_sample_table"}
    )
    inspection_names = inspections[
        ["fiscal_year", "state_ut", "state_ut_source"]
    ].rename(columns={"state_ut_source": "state_ut_source_inspection_table"})
    samples = samples.drop(columns="state_ut_source")
    inspections = inspections.drop(columns="state_ut_source")

    merged = samples.merge(
        inspections,
        on=["fiscal_year", "state_ut"],
        how="outer",
        validate="one_to_one",
        indicator=True,
    )
    unmatched = merged.loc[merged["_merge"] != "both", ["fiscal_year", "state_ut"]]
    if not unmatched.empty:
        raise ValueError(
            "Sample and inspection tables do not cover the same state-year rows: "
            f"{unmatched.to_dict(orient='records')}"
        )
    merged = merged.drop(columns="_merge")

    names = sample_names.merge(
        inspection_names,
        on=["fiscal_year", "state_ut"],
        how="inner",
        validate="one_to_one",
    )
    merged = merged.merge(
        names,
        on=["fiscal_year", "state_ut"],
        how="left",
        validate="one_to_one",
    )

    merged["total_nonconforming_samples"] = (
        merged["nonconforming_previous_year_samples"]
        + merged["nonconforming_current_year_samples"]
    )
    merged["nonconforming_category_count_sum"] = (
        merged["unsafe_samples"]
        + merged["substandard_samples"]
        + merged["labelling_misleading_misc_samples"]
    )
    merged["qc_nonconforming_categories_match"] = (
        merged["total_nonconforming_samples"]
        == merged["nonconforming_category_count_sum"]
    )
    inspection_subtotal = (
        merged["central_licensed_fbos"]
        + merged["state_licensed_fbos"]
        + merged["registered_fbos"]
    )
    merged["qc_inspection_subtotals_match"] = (
        inspection_subtotal == merged["total_state_inspections"]
    )

    # These flags prompt review; they do not alter the FSSAI values.
    merged["qc_analysed_exceeds_lifted"] = (
        merged["samples_analysed"] > merged["samples_lifted"]
    )
    merged["qc_awaited_differs_from_lifted_minus_analysed"] = (
        merged["analysis_reports_awaited"]
        != (merged["samples_lifted"] - merged["samples_analysed"]).clip(lower=0)
    )

    merged = merged.sort_values("state_ut").reset_index(drop=True)
    merged.insert(2, "source_report", "FSSAI Annual Report 2021-22")
    merged.insert(3, "source_sample_table", "Table 14")
    merged.insert(4, "source_inspection_table", "Table 15")
    return merged, _make_validation_report(merged)


def main() -> None:
    """Build and save the analysis-ready aggregate dataset and QC report."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    dataset, report = build_clean_dataset()
    dataset.to_csv(OUTPUT_FILE, index=False)
    REPORT_FILE.write_text(report, encoding="utf-8")
    print(f"Saved {len(dataset)} rows to {OUTPUT_FILE}")
    print(f"Saved validation notes to {REPORT_FILE}")


if __name__ == "__main__":
    main()
