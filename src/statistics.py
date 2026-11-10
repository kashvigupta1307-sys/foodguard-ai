"""Descriptive statistical analysis for the FSSAI FY 2021-22 aggregates.

Run from the project root with:
    .venv/bin/python -m src.statistics

The statistical outputs describe the 36 reported State/UT aggregates. They do
not establish causal effects or estimate food-safety rates in the population.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import spearmanr


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "fssai_state_summary_2021-22_clean.csv"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "statistical_figures"

CATEGORY_COLUMNS = {
    "Unsafe": "unsafe_samples",
    "Substandard": "substandard_samples",
    "Labelling / misleading / other": "labelling_misleading_misc_samples",
}

COUNT_COLUMNS = [
    "samples_lifted",
    "samples_analysed",
    "analysis_reports_awaited",
    "total_nonconforming_samples",
    "unsafe_samples",
    "substandard_samples",
    "labelling_misleading_misc_samples",
    "total_state_inspections",
]


def load_data(path: Path = INPUT_FILE) -> pd.DataFrame:
    """Read the clean dataset and validate the fields needed for analysis."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Processed dataset not found at {path}. Run src/preprocessing.py first."
        )
    frame = pd.read_csv(path)
    required = {"state_ut", "fiscal_year", *COUNT_COLUMNS}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Processed dataset is missing columns: {sorted(missing)}")
    if frame["state_ut"].isna().any():
        raise ValueError("State/UT labels must not be blank.")
    return frame


def build_state_category_percentages(frame: pd.DataFrame) -> pd.DataFrame:
    """Calculate each category's share of reported non-conforming outcomes."""
    output = frame[["fiscal_year", "state_ut", "total_nonconforming_samples"]].copy()
    for label, column in CATEGORY_COLUMNS.items():
        output[f"{column}_share_percent"] = (
            frame[column]
            .div(frame["total_nonconforming_samples"].where(
                frame["total_nonconforming_samples"] != 0
            ))
            .mul(100)
        )
    return output.sort_values("state_ut").reset_index(drop=True)


def _spearman_result(frame: pd.DataFrame, x: str, y: str) -> dict[str, object]:
    """Compute a rank association and retain its limited interpretation."""
    valid = frame[[x, y]].dropna()
    result = spearmanr(valid[x], valid[y], alternative="two-sided")
    return {
        "variable_x": x,
        "variable_y": y,
        "spearman_rho": float(result.statistic),
        "two_sided_p_value": float(result.pvalue),
        "n_state_ut_rows": int(len(valid)),
        "interpretation": (
            "Descriptive association only; counts may reflect activity volume, "
            "reporting practices, and prior-year results. Not causal or a risk rate."
        ),
    }


def calculate_correlations(frame: pd.DataFrame) -> pd.DataFrame:
    """Compare reported outcome counts with sample and inspection activity."""
    comparisons = [
        ("total_state_inspections", "total_nonconforming_samples"),
        ("samples_lifted", "total_nonconforming_samples"),
        ("samples_analysed", "total_nonconforming_samples"),
    ]
    return pd.DataFrame(
        [_spearman_result(frame, x, y) for x, y in comparisons]
    )


def _save_correlation_heatmap(frame: pd.DataFrame) -> None:
    """Save a Spearman correlation heatmap for the aggregate count columns."""
    columns = [
        "samples_lifted",
        "samples_analysed",
        "total_nonconforming_samples",
        "unsafe_samples",
        "substandard_samples",
        "labelling_misleading_misc_samples",
        "total_state_inspections",
    ]
    correlation = frame[columns].corr(method="spearman")
    correlation.to_csv(REPORTS_DIR / "spearman_correlation_matrix.csv")

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        correlation,
        vmin=-1,
        vmax=1,
        center=0,
        cmap="vlag",
        annot=True,
        fmt=".2f",
        square=True,
        linewidths=0.5,
        cbar_kws={"label": "Spearman rank correlation"},
        ax=ax,
    )
    ax.set_title("Rank associations among reported state-level counts\nFY 2021-22")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=35, ha="right")
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "spearman_correlation_heatmap.png", dpi=180)
    plt.close(fig)


def _save_category_distributions(frame: pd.DataFrame) -> None:
    """Plot across-State/UT category count distributions on a log1p scale."""
    long = frame[["state_ut", *CATEGORY_COLUMNS.values()]].melt(
        id_vars="state_ut", var_name="category_column", value_name="reported_count"
    )
    labels = {column: label for label, column in CATEGORY_COLUMNS.items()}
    long["category"] = long["category_column"].map(labels)
    long["log1p_reported_count"] = np.log1p(long["reported_count"])

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(
        data=long,
        x="category",
        y="log1p_reported_count",
        hue="category",
        legend=False,
        palette={
            "Unsafe": "#C7473A",
            "Substandard": "#E3A33B",
            "Labelling / misleading / other": "#4C78A8",
        },
        ax=ax,
    )
    count_ticks = [0, 10, 100, 1_000, 10_000]
    ax.set_yticks(np.log1p(count_ticks))
    ax.set_yticklabels([f"{value:,}" for value in count_ticks])
    ax.set_title("State/UT distribution of reported outcome counts\nFY 2021-22")
    ax.set_xlabel("")
    ax.set_ylabel("Reported count per State/UT (log1p display)")
    ax.tick_params(axis="x", rotation=15)
    ax.grid(False, axis="x")
    ax.grid(True, axis="y", alpha=0.2)
    sns.despine(ax=ax, top=True, right=True)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "state_category_count_distributions.png", dpi=180)
    plt.close(fig)


def _build_summary(frame: pd.DataFrame, correlations: pd.DataFrame) -> str:
    """Create a readable summary with interpretation limits."""
    lines = [
        "# Statistical analysis: FSSAI FY 2021-22",
        "",
        "## Descriptive statistics",
        "",
        f"- Analysis unit: State/UT; observations: {len(frame)}; fiscal year: {frame['fiscal_year'].dropna().iloc[0]}.",
        "- The CSV `reports/statistical_descriptive_statistics.csv` contains count summaries (mean, standard deviation, quartiles, minimum and maximum) across state/UT rows.",
        "- The CSV `reports/state_category_percentages.csv` shows each reported issue category as a percentage of that State/UT's reported non-conforming outcomes. These are composition shares, not the proportion of samples failing tests.",
        "",
        "## Category composition across reported outcomes",
        "",
    ]
    category_total = sum(int(frame[column].sum()) for column in CATEGORY_COLUMNS.values())
    for label, column in CATEGORY_COLUMNS.items():
        value = int(frame[column].sum())
        share = value / category_total * 100 if category_total else 0
        lines.append(f"- {label}: {value:,} of {category_total:,} category counts ({share:.1f}%).")

    lines.extend(
        [
            "",
            "## Rank association checks",
            "",
            "Spearman's rho compares the rank ordering of state-level counts. A positive coefficient means states with larger values of one count tend also to have larger values of the other count in this one-year table.",
            "",
        ]
    )
    for row in correlations.itertuples(index=False):
        lines.append(
            f"- `{row.variable_x}` vs `{row.variable_y}`: rho={row.spearman_rho:.3f}, "
            f"two-sided p={row.two_sided_p_value:.4g}, n={row.n_state_ut_rows}."
        )

    lines.extend(
        [
            "",
            "These coefficients are descriptive. States with more testing or inspections have more opportunities to detect and report non-conforming outcomes. The counts also include prior-year samples whose results were declared this year. The table is not a random sample, and p-values here should not be treated as proof of a population-level effect or causal relationship.",
            "",
            "## Limitations",
            "",
            "- This is a one-year, state/UT aggregate dataset. No month/year trend beyond FY 2021-22, district comparison, or product analysis can be estimated.",
            "- The source does not provide denominators such as food-business population, consumer exposure, or a consistent sample cohort by state. Do not label count comparisons as non-compliance rates.",
            "- Correlation among totals and their component categories is partly structural because the totals are sums of related counts.",
            "- Non-conforming outcomes do not establish confirmed adulteration, and these data do not support sample-level prediction.",
            "",
            "## Output files",
            "",
            "- `reports/statistical_descriptive_statistics.csv`",
            "- `reports/state_category_percentages.csv`",
            "- `reports/statistical_correlation_results.csv`",
            "- `reports/spearman_correlation_matrix.csv`",
            "- `reports/statistical_figures/spearman_correlation_heatmap.png`",
            "- `reports/statistical_figures/state_category_count_distributions.png`",
            "",
        ]
    )
    return "\n".join(lines)


def run_statistical_analysis() -> pd.DataFrame:
    """Generate descriptive tables, rank-association checks, and figures."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="notebook")

    frame = load_data()
    descriptive = frame[COUNT_COLUMNS].describe().T
    descriptive.to_csv(REPORTS_DIR / "statistical_descriptive_statistics.csv")

    category_percentages = build_state_category_percentages(frame)
    category_percentages.to_csv(
        REPORTS_DIR / "state_category_percentages.csv", index=False
    )

    correlations = calculate_correlations(frame)
    correlations.to_csv(
        REPORTS_DIR / "statistical_correlation_results.csv", index=False
    )
    _save_correlation_heatmap(frame)
    _save_category_distributions(frame)
    (REPORTS_DIR / "statistical_analysis.md").write_text(
        _build_summary(frame, correlations), encoding="utf-8"
    )
    return correlations


if __name__ == "__main__":
    results = run_statistical_analysis()
    print(f"Statistical analysis complete for {len(load_data())} State/UT rows.")
    print(results[["variable_x", "variable_y", "spearman_rho", "n_state_ut_rows"]].to_string(index=False))
