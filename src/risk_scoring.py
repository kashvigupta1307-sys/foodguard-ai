"""Assess risk-score feasibility and calculate cautious reporting indicators.

Run from the project root with:
    .venv/bin/python -m src.risk_scoring

This one-year, state-level dataset cannot support the requested Low/Medium/High
food-safety risk labels. The module therefore reports descriptive indicators
and sets risk_score/status explicitly to unavailable/not_scored.
"""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "fssai_state_summary_2021-22_clean.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "state_reporting_indicators_2021-22.csv"
REPORT_FILE = PROJECT_ROOT / "reports" / "risk_scoring_feasibility.md"

REQUIRED_COLUMNS = {
    "fiscal_year",
    "state_ut",
    "samples_analysed",
    "nonconforming_current_year_samples",
    "nonconforming_previous_year_samples",
    "unsafe_samples",
    "substandard_samples",
    "labelling_misleading_misc_samples",
    "total_state_inspections",
}


def load_data(path: Path = INPUT_FILE) -> pd.DataFrame:
    """Load and validate the state-year aggregate dataset."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Processed dataset not found at {path}. Run src.preprocessing first."
        )
    frame = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing columns: {sorted(missing)}")
    if frame["state_ut"].isna().any():
        raise ValueError("State/UT labels must not be blank.")
    return frame


def assess_scoring_readiness(frame: pd.DataFrame) -> dict[str, object]:
    """Return explicit reasons why severity-weighted risk scoring is unavailable."""
    years = frame["fiscal_year"].dropna().astype(str).unique().tolist()
    return {
        "risk_score_available": False,
        "risk_category_available": False,
        "risk_score": pd.NA,
        "risk_category": "Not scored",
        "reason": (
            "The data is aggregated by State/UT and contains "
            f"{len(years)} fiscal year(s) ({', '.join(years)}). It has no inspection "
            "dates or recent inspection outcomes, no entity-level history, and no "
            "validated severity weights. Required recency and repeated-violation "
            "signals are unavailable."
        ),
    }


def build_reporting_indicators(frame: pd.DataFrame) -> pd.DataFrame:
    """Calculate descriptive counts/shares and mark risk score as unavailable.

    The current-year non-conformance ratio is an indicative reporting yield,
    not an official rate: state reporting has count inconsistencies and
    denominator differences. A zero denominator yields a missing ratio.
    """
    output_columns = [
        "fiscal_year",
        "state_ut",
        "samples_analysed",
        "nonconforming_current_year_samples",
        "nonconforming_previous_year_samples",
        "unsafe_samples",
        "substandard_samples",
        "labelling_misleading_misc_samples",
        "total_state_inspections",
    ]
    output = frame[output_columns].copy()

    denominator = output["samples_analysed"].where(output["samples_analysed"] > 0)
    output["indicative_current_year_nonconforming_yield_percent"] = (
        output["nonconforming_current_year_samples"].div(denominator).mul(100)
    )

    issue_total = (
        output["unsafe_samples"]
        + output["substandard_samples"]
        + output["labelling_misleading_misc_samples"]
    )
    output["unsafe_share_of_reported_issue_categories_percent"] = (
        output["unsafe_samples"].div(issue_total.where(issue_total > 0)).mul(100)
    )
    output["has_zero_samples_analysed"] = output["samples_analysed"] == 0
    output["risk_score"] = pd.NA
    output["risk_category"] = "Not scored"
    output["risk_score_limitation"] = (
        "Insufficient temporal and entity-level detail; indicator is not evidence of adulteration"
    )
    return output


def _format_extreme(frame: pd.DataFrame, column: str, descending: bool) -> str:
    """Format the non-missing state with an extreme indicative ratio."""
    available = frame.dropna(subset=[column])
    if available.empty:
        return "No State/UT has a non-zero analysis denominator."
    row = available.sort_values(column, ascending=not descending).iloc[0]
    return f"{row['state_ut']}: {row[column]:.1f}%"


def build_report(frame: pd.DataFrame, indicators: pd.DataFrame) -> str:
    """Write an accessible explanation of what can and cannot be scored."""
    readiness = assess_scoring_readiness(frame)
    nonconforming_sum = int(indicators["nonconforming_current_year_samples"].sum())
    inspected_sum = int(indicators["total_state_inspections"].sum())
    lines = [
        "# Food safety risk scoring: feasibility assessment",
        "",
        "## Decision: no Low/Medium/High risk labels",
        "",
        readiness["reason"],
        "",
        "A score from these data could create a false impression of precision. State-year totals do not identify businesses, products, districts, inspection dates, or repeat outcomes. Therefore this project does not assign a food-safety risk score or Low/Medium/High category to any State/UT.",
        "",
        "## Descriptive reporting indicators",
        "",
        f"- Reported current-year non-conforming samples: {nonconforming_sum:,} across the state rows.",
        f"- Reported state/UT FoSCoRIS inspections: {inspected_sum:,}.",
        f"- Highest indicative current-year non-conformance yield: {_format_extreme(indicators, 'indicative_current_year_nonconforming_yield_percent', descending=True)}.",
        f"- Lowest indicative current-year non-conformance yield among states with samples analysed: {_format_extreme(indicators, 'indicative_current_year_nonconforming_yield_percent', descending=False)}.",
        "",
        "### Indicator definitions and caveats",
        "",
        "- `indicative_current_year_nonconforming_yield_percent` = reported non-conforming samples lifted and analysed in FY 2021-22 divided by samples analysed, multiplied by 100. This is a rough reporting yield only, not an official compliance rate; counts reflect testing/reporting activity and the report has denominator inconsistencies for some State/UTs.",
        "- `unsafe_share_of_reported_issue_categories_percent` = unsafe count divided by unsafe + substandard + labelling/misleading/miscellaneous counts. This describes the composition of reported issue categories, not the chance that a food item is unsafe.",
        "- Zero denominators result in blank percentages, never zero risk.",
        "- `risk_score` is intentionally blank and `risk_category` is `Not scored` for every row.",
        "",
        "## What a future risk-scoring dataset needs",
        "",
        "To produce an explainable and useful prioritization score, obtain authentic repeated records with a stable food-business or sampling-site identifier, inspection dates, outcomes, count of prior violations, severity defined by the regulator, and enough history to define a recent window. Validate sampling and reporting consistency, then document thresholds with domain experts. Any resulting score would be a prioritization aid, not confirmed evidence of adulteration.",
        "",
        "## Output",
        "",
        "- `data/processed/state_reporting_indicators_2021-22.csv`",
        "",
    ]
    return "\n".join(lines)


def run_risk_analysis() -> pd.DataFrame:
    """Create indicative metrics and the explicit score feasibility report."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    frame = load_data()
    indicators = build_reporting_indicators(frame)
    indicators.to_csv(OUTPUT_FILE, index=False)
    REPORT_FILE.write_text(build_report(frame, indicators), encoding="utf-8")
    return indicators


if __name__ == "__main__":
    result = run_risk_analysis()
    print(f"Risk scoring readiness assessed for {len(result)} State/UT rows.")
    print("No risk score or Low/Medium/High category was assigned.")
    print(f"Indicators: {OUTPUT_FILE}")
