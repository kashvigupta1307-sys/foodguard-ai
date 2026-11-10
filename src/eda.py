"""Exploratory analysis for the FSSAI state-year aggregate dataset.

Run from the project root with:
    .venv/bin/python -m src.eda

The charts show reported counts, not risk rates. The source covers one fiscal
year and does not contain monthly, district, or product-level observations.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "fssai_state_summary_2021-22_clean.csv"
REPORTS_DIR = PROJECT_ROOT / "reports"
CHARTS_DIR = REPORTS_DIR / "eda_charts"

CATEGORY_COLUMNS = {
    "Unsafe": "unsafe_samples",
    "Substandard": "substandard_samples",
    "Labelling / misleading / other": "labelling_misleading_misc_samples",
}

PALETTE = {
    "Unsafe": "#C7473A",
    "Substandard": "#E3A33B",
    "Labelling / misleading / other": "#4C78A8",
}


def load_data(path: Path = INPUT_FILE) -> pd.DataFrame:
    """Load the processed aggregate table and check its basic structure."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Processed dataset not found at {path}. Run src/preprocessing.py first."
        )

    frame = pd.read_csv(path)
    required = {
        "state_ut",
        "fiscal_year",
        "total_nonconforming_samples",
        "total_state_inspections",
        *CATEGORY_COLUMNS.values(),
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Processed dataset is missing columns: {sorted(missing)}")
    if frame["state_ut"].isna().any():
        raise ValueError("State/UT labels must not be blank for EDA.")
    return frame


def _save_category_mix(frame: pd.DataFrame) -> dict[str, int]:
    """Plot national category totals and return the totals for the report."""
    totals = {
        label: int(frame[column].sum())
        for label, column in CATEGORY_COLUMNS.items()
    }
    plot_data = pd.Series(totals, name="Reported count").sort_values()

    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.barh(
        plot_data.index,
        plot_data.values,
        color=[PALETTE[label] for label in plot_data.index],
    )
    ax.bar_label(bars, labels=[f"{int(v):,}" for v in plot_data.values], padding=5)
    ax.set_title("Reported non-conforming outcomes by category\nFSSAI FY 2021-22")
    ax.set_xlabel("Count in annual report")
    ax.set_ylabel("")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(False, axis="y")
    ax.grid(True, axis="x", alpha=0.2)
    ax.set_axisbelow(True)
    fig.text(
        0.01,
        0.01,
        "Counts include results from prior-year samples reported this year.",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(CHARTS_DIR / "national_nonconforming_categories.png", dpi=180)
    plt.close(fig)
    return totals


def _save_state_category_counts(frame: pd.DataFrame, top_n: int = 15) -> list[str]:
    """Plot the states with the largest reported non-conforming counts."""
    top = frame.nlargest(top_n, "total_nonconforming_samples").sort_values(
        "total_nonconforming_samples", ascending=True
    )
    fig, ax = plt.subplots(figsize=(11, 8))
    left = pd.Series(0, index=top.index, dtype="int64")
    for label, column in CATEGORY_COLUMNS.items():
        values = top[column]
        ax.barh(
            top["state_ut"],
            values,
            left=left,
            label=label,
            color=PALETTE[label],
            height=0.72,
        )
        left = left + values

    ax.set_title(
        f"Top {len(top)} State/UTs by reported non-conforming outcomes\nFY 2021-22"
    )
    ax.set_xlabel("Reported count (including prior-year sample results)")
    ax.set_ylabel("")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(False, axis="y")
    ax.grid(True, axis="x", alpha=0.2)
    ax.set_axisbelow(True)
    ax.legend(
        title="Reported category",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.09),
        ncol=3,
        frameon=False,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(CHARTS_DIR / "state_nonconforming_category_counts.png", dpi=180)
    plt.close(fig)
    return top.sort_values("total_nonconforming_samples", ascending=False)[
        "state_ut"
    ].tolist()


def _save_inspection_counts(frame: pd.DataFrame, top_n: int = 15) -> list[str]:
    """Plot reported FoSCoRIS inspection counts; this is activity volume."""
    top = frame.nlargest(top_n, "total_state_inspections").sort_values(
        "total_state_inspections", ascending=True
    )
    fig, ax = plt.subplots(figsize=(10, 7.5))
    bars = ax.barh(
        top["state_ut"],
        top["total_state_inspections"],
        color="#4C78A8",
        height=0.72,
    )
    ax.bar_label(
        bars,
        labels=[f"{int(v):,}" for v in top["total_state_inspections"]],
        padding=4,
        fontsize=8,
    )
    ax.set_title("Top State/UTs by reported FoSCoRIS inspections\nFY 2021-22")
    ax.set_xlabel("Inspections reported")
    ax.set_ylabel("")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(False, axis="y")
    ax.grid(True, axis="x", alpha=0.2)
    ax.set_axisbelow(True)
    fig.text(
        0.01,
        0.01,
        "Inspection counts measure activity; they are not normalized by FBO population.",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(CHARTS_DIR / "state_inspection_counts.png", dpi=180)
    plt.close(fig)
    return top.sort_values("total_state_inspections", ascending=False)[
        "state_ut"
    ].tolist()


def _format_ranked(frame: pd.DataFrame, metric: str, limit: int = 5) -> list[str]:
    """Format the largest state values for the beginner-friendly summary."""
    selected = frame.nlargest(limit, metric)[["state_ut", metric]]
    return [f"{row.state_ut}: {int(getattr(row, metric)):,}" for row in selected.itertuples()]


def _write_summary(
    frame: pd.DataFrame,
    category_totals: dict[str, int],
    top_nonconforming: list[str],
    top_inspections: list[str],
) -> None:
    """Write factual observations and data-scope limitations to Markdown."""
    category_sum = sum(category_totals.values())
    category_lines = []
    for label, value in category_totals.items():
        share = value / category_sum * 100 if category_sum else 0
        category_lines.append(f"- {label}: {value:,} ({share:.1f}% of category total)")

    sample_total = int(frame["samples_analysed"].sum())
    lifted_total = int(frame["samples_lifted"].sum())
    inspection_total = int(frame["total_state_inspections"].sum())
    nonconforming_total = int(frame["total_nonconforming_samples"].sum())

    lines = [
        "# Exploratory data analysis: FSSAI FY 2021-22",
        "",
        "## Dataset scope",
        "",
        f"- {len(frame)} State/UT aggregate rows for fiscal year {frame['fiscal_year'].dropna().iloc[0]}.",
        f"- The source reports {lifted_total:,} samples lifted and {sample_total:,} samples analysed across these state rows.",
        f"- Table 14 reports {nonconforming_total:,} non-conforming outcomes in total (previous-year sample results plus current-year sample results).",
        f"- Table 15 reports {inspection_total:,} state/UT FoSCoRIS inspections; the additional all-India railway/airport inspections are not allocated to the state rows.",
        "",
        "## Reported non-conforming outcome categories",
        "",
        *category_lines,
        "",
        "These are counts reported by the regulator, not estimates of the share of all food in circulation that is unsafe.",
        "",
        "## State/UT comparisons",
        "",
        "Largest reported non-conforming outcome counts (not rates):",
        *[f"- {value}" for value in _format_ranked(frame, "total_nonconforming_samples")],
        "",
        "Largest reported inspection counts:",
        *[f"- {value}" for value in _format_ranked(frame, "total_state_inspections")],
        "",
        f"The stacked count chart includes these top State/UTs: {', '.join(top_nonconforming)}.",
        f"The inspection chart includes these top State/UTs: {', '.join(top_inspections)}.",
        "",
        "## Interpretation limits",
        "",
        "- Counts depend on testing and inspection volume, reporting practices, and results declared for samples collected in earlier years. A larger count does not by itself mean a higher underlying food-safety rate.",
        "- Inspection counts are not divided by the number of food businesses, population, or samples tested.",
        "- The current dataset has one fiscal year and no monthly date, district, or product fields. Monthly trends, year-over-year trends, district comparisons, and product rankings cannot be calculated from it.",
        "- Do not interpret an unsafe category count or any future analytical score as evidence that a particular food or business is adulterated.",
        "",
        "## Generated charts",
        "",
        "- `reports/eda_charts/national_nonconforming_categories.png`",
        "- `reports/eda_charts/state_nonconforming_category_counts.png`",
        "- `reports/eda_charts/state_inspection_counts.png`",
        "",
    ]
    (REPORTS_DIR / "eda_summary.md").write_text("\n".join(lines), encoding="utf-8")


def run_eda() -> pd.DataFrame:
    """Generate charts, descriptive statistics, and a Markdown summary."""
    sns.set_theme(style="whitegrid", context="notebook")
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    frame = load_data()
    category_totals = _save_category_mix(frame)
    top_nonconforming = _save_state_category_counts(frame)
    top_inspections = _save_inspection_counts(frame)
    _write_summary(frame, category_totals, top_nonconforming, top_inspections)

    numeric_columns = [
        "samples_lifted",
        "samples_analysed",
        "analysis_reports_awaited",
        "total_nonconforming_samples",
        *CATEGORY_COLUMNS.values(),
        "total_state_inspections",
    ]
    frame[numeric_columns].describe().T.to_csv(
        REPORTS_DIR / "eda_descriptive_statistics.csv", index=True
    )
    return frame


if __name__ == "__main__":
    analyzed = run_eda()
    print(f"EDA complete for {len(analyzed)} State/UT rows.")
    print(f"Charts saved in {CHARTS_DIR}")
    print(f"Summary saved in {REPORTS_DIR / 'eda_summary.md'}")
