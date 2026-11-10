"""Assess ML readiness and explore state reporting-volume profiles.

Run from the project root with:
    MPLCONFIGDIR=reports/.mplconfig .venv/bin/python -m src.model_training

No supervised classifier is trained: this source has no individual inspection
records or reliable per-record compliance labels. K-Means is used only to
explore reporting-volume profiles, not to predict safety or adulteration.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "fssai_state_summary_2021-22_clean.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "ml_figures"
CLUSTER_FILE = OUTPUT_DIR / "state_volume_clusters_2021-22.csv"
SILHOUETTE_FILE = REPORTS_DIR / "kmeans_silhouette_scores.csv"
REPORT_FILE = REPORTS_DIR / "ml_feasibility.md"
FIGURE_FILE = FIGURES_DIR / "state_activity_clusters_pca.png"

# These features are administrative/reporting counts. They are intentionally
# called volume profiles so clusters cannot be mistaken for safety risk levels.
CLUSTER_FEATURES = [
    "samples_lifted",
    "samples_analysed",
    "total_state_inspections",
    "unsafe_samples",
    "substandard_samples",
    "labelling_misleading_misc_samples",
]


def load_data(path: Path = INPUT_FILE) -> pd.DataFrame:
    """Load the processed state-year dataset and verify cluster inputs."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Processed dataset not found at {path}. Run src.preprocessing first."
        )
    frame = pd.read_csv(path)
    required = {"state_ut", "fiscal_year", *CLUSTER_FEATURES}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing columns: {sorted(missing)}")
    if frame[CLUSTER_FEATURES].isna().any().any():
        raise ValueError("Cluster features contain missing values; resolve them explicitly first.")
    if (frame[CLUSTER_FEATURES] < 0).any().any():
        raise ValueError("Count features cannot be negative.")
    return frame


def supervised_readiness(frame: pd.DataFrame) -> dict[str, str]:
    """Return the supervised-learning decision and its data-based reason."""
    return {
        "decision": "not_supported",
        "reason": (
            f"The source contains {len(frame)} state/UT aggregates for one fiscal year, "
            "not individual inspection or sample records. It has no reliable per-record "
            "compliance target and no record-level predictor fields. Counts cannot be "
            "expanded into synthetic labels."
        ),
        "consequence": (
            "Logistic Regression, Decision Tree, Random Forest, and XGBoost classification "
            "metrics (accuracy, precision, recall, F1, confusion matrix, ROC-AUC) are not "
            "defined for this dataset."
        ),
    }


def _prepare_features(frame: pd.DataFrame) -> tuple[np.ndarray, StandardScaler]:
    """Log-transform skewed counts, then standardize each feature."""
    counts = frame[CLUSTER_FEATURES].to_numpy(dtype=float)
    log_counts = np.log1p(counts)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(log_counts)
    return scaled, scaler


def _choose_k(features: np.ndarray) -> tuple[int, pd.DataFrame]:
    """Compare a small set of cluster counts using silhouette score."""
    n_rows = len(features)
    candidate_ks = range(2, min(6, n_rows))
    results = []
    for k in candidate_ks:
        model = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels = model.fit_predict(features)
        score = silhouette_score(features, labels)
        results.append({"k": k, "silhouette_score": float(score)})
    scores = pd.DataFrame(results)
    best_k = int(scores.sort_values("silhouette_score", ascending=False).iloc[0]["k"])
    return best_k, scores


def _save_cluster_figure(
    frame: pd.DataFrame,
    projection: np.ndarray,
    labels: np.ndarray,
    explained_variance: np.ndarray,
) -> None:
    """Plot cluster assignments in a two-component PCA view."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 8))
    palette = plt.get_cmap("tab10")
    for cluster_id in sorted(np.unique(labels)):
        mask = labels == cluster_id
        ax.scatter(
            projection[mask, 0],
            projection[mask, 1],
            s=70,
            alpha=0.85,
            color=palette(int(cluster_id) % 10),
            label=f"Cluster {cluster_id}",
            edgecolor="white",
            linewidth=0.7,
        )
        for index in np.flatnonzero(mask):
            distances = np.linalg.norm(projection - projection[index], axis=1)
            nearby = np.flatnonzero(distances < 0.22)
            if len(nearby) > 1:
                rank = int(np.flatnonzero(nearby == index)[0])
                vertical_offset = int((rank - (len(nearby) - 1) / 2) * 28)
            else:
                vertical_offset = 3
            ax.annotate(
                frame.iloc[index]["state_ut"],
                (projection[index, 0], projection[index, 1]),
                xytext=(4, vertical_offset),
                textcoords="offset points",
                fontsize=7,
                alpha=0.85,
            )
    ax.set_title("Exploratory K-Means reporting-volume profiles\nFY 2021-22")
    ax.set_xlabel(f"PCA component 1 ({explained_variance[0] * 100:.1f}% variance)")
    ax.set_ylabel(f"PCA component 2 ({explained_variance[1] * 100:.1f}% variance)")
    ax.legend(title="Arbitrary cluster ID", frameon=False)
    ax.grid(alpha=0.2)
    fig.text(
        0.01,
        0.01,
        "Clusters summarize transformed reporting counts; they are not safety or adulteration risk classes.",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(FIGURE_FILE, dpi=180)
    plt.close(fig)


def _build_report(
    readiness: dict[str, str],
    frame: pd.DataFrame,
    best_k: int,
    scores: pd.DataFrame,
    profiles: pd.DataFrame,
    explained_variance: np.ndarray,
) -> str:
    """Write model feasibility, cluster method, findings, and caveats."""
    score_lines = [
        f"- k={int(row.k)}: silhouette={row.silhouette_score:.3f}"
        for row in scores.itertuples(index=False)
    ]
    profile_lines = []
    for row in profiles.itertuples(index=False):
        profile_lines.append(
            f"- Cluster {int(row.cluster_id)}: {int(row.state_ut_count)} State/UTs; "
            f"median samples analysed={int(row.median_samples_analysed):,}; "
            f"median inspections={int(row.median_total_state_inspections):,}; "
            f"median reported non-conforming outcomes={int(row.median_total_nonconforming_samples):,}."
        )

    lines = [
        "# Machine-learning feasibility and exploratory clustering",
        "",
        "## Supervised prediction decision",
        "",
        f"- Decision: `{readiness['decision']}`.",
        f"- Reason: {readiness['reason']}",
        f"- {readiness['consequence']}",
        "- No labels or individual samples were fabricated, and no classifier was trained.",
        "",
        "A future supervised model would need authentic individual sample/inspection records, a clearly defined outcome label, predictors available before the outcome, sufficient examples per class, and time-aware validation that avoids leakage.",
        "",
        "## Exploratory K-Means analysis",
        "",
        f"- Observations: {len(frame)} State/UT aggregates from FY {frame['fiscal_year'].dropna().iloc[0]}.",
        f"- Features: {', '.join(CLUSTER_FEATURES)}.",
        "- Counts were transformed with `log1p` to reduce skew, then standardized before fitting K-Means.",
        "- Candidate k values and silhouette scores:",
        *score_lines,
        f"- The selected exploratory solution used k={best_k}, the highest silhouette score among the tested values.",
        f"- The first two PCA components explain {explained_variance.sum() * 100:.1f}% of variance in the standardized features; the scatter plot is only a 2-D projection.",
        "",
        "### Cluster profiles",
        "",
        *profile_lines,
        "",
        "Cluster IDs are arbitrary and can change if data or settings change. Because the input features are administrative counts, clusters primarily group reporting and activity volume. They are not Low/Medium/High risk labels, predictions, or evidence of adulteration. Silhouette score measures geometric separation only; it does not establish that the groups are meaningful for food safety.",
        "",
        "## Output files",
        "",
        "- `data/processed/state_volume_clusters_2021-22.csv`",
        "- `reports/kmeans_silhouette_scores.csv`",
        "- `reports/ml_figures/state_activity_clusters_pca.png`",
        "- `reports/ml_feasibility.md`",
        "",
    ]
    return "\n".join(lines)


def run_ml_analysis() -> pd.DataFrame:
    """Write the supervised-readiness note and exploratory cluster outputs."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    frame = load_data()
    readiness = supervised_readiness(frame)
    scaled_features, _ = _prepare_features(frame)
    best_k, scores = _choose_k(scaled_features)
    scores.to_csv(SILHOUETTE_FILE, index=False)

    model = KMeans(n_clusters=best_k, random_state=42, n_init=20)
    labels = model.fit_predict(scaled_features)
    pca = PCA(n_components=2, random_state=42)
    projection = pca.fit_transform(scaled_features)

    clusters = frame[
        [
            "fiscal_year",
            "state_ut",
            "samples_lifted",
            "samples_analysed",
            "total_state_inspections",
            "unsafe_samples",
            "substandard_samples",
            "labelling_misleading_misc_samples",
            "total_nonconforming_samples",
        ]
    ].copy()
    clusters["cluster_id"] = labels
    clusters["pca_component_1"] = projection[:, 0]
    clusters["pca_component_2"] = projection[:, 1]
    clusters.to_csv(CLUSTER_FILE, index=False)

    profiles = (
        clusters.groupby("cluster_id")
        .agg(
            state_ut_count=("state_ut", "count"),
            median_samples_analysed=("samples_analysed", "median"),
            median_total_state_inspections=("total_state_inspections", "median"),
            median_total_nonconforming_samples=("total_nonconforming_samples", "median"),
        )
        .reset_index()
    )
    profiles.to_csv(REPORTS_DIR / "kmeans_cluster_profiles.csv", index=False)

    _save_cluster_figure(frame, projection, labels, pca.explained_variance_ratio_)
    report = _build_report(
        readiness,
        frame,
        best_k,
        scores,
        profiles,
        pca.explained_variance_ratio_,
    )
    REPORT_FILE.write_text(report, encoding="utf-8")
    return profiles


if __name__ == "__main__":
    cluster_profiles = run_ml_analysis()
    print(f"ML feasibility analysis complete; {len(cluster_profiles)} exploratory clusters.")
    print(cluster_profiles.to_string(index=False))
