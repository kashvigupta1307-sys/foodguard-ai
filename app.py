"""FoodGuard AI Streamlit dashboard.

Run from the project root:
    .venv/bin/streamlit run app.py

This is a local Streamlit app with no separate backend service. Uploaded files
are read in memory for the current session and are not written to disk.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parent
CLEAN_DATA = ROOT / "data" / "processed" / "fssai_state_summary_2021-22_clean.csv"
INDICATOR_DATA = ROOT / "data" / "processed" / "state_reporting_indicators_2021-22.csv"
EDA_REPORT = ROOT / "reports" / "eda_summary.md"
STAT_REPORT = ROOT / "reports" / "statistical_analysis.md"
ML_REPORT = ROOT / "reports" / "ml_feasibility.md"
RISK_REPORT = ROOT / "reports" / "risk_scoring_feasibility.md"

CATEGORIES = {
    "Unsafe": "unsafe_samples",
    "Substandard": "substandard_samples",
    "Labelling / misleading / other": "labelling_misleading_misc_samples",
}
COLORS = {
    "Unsafe": "#C7473A",
    "Substandard": "#E3A33B",
    "Labelling / misleading / other": "#4C78A8",
}
PAGES = [
    "Home Dashboard",
    "Dataset Upload",
    "Data Cleaning",
    "Exploratory Analysis",
    "Statistical Analysis",
    "Machine Learning",
    "Food Safety Risk Analysis",
    "Regional Analysis",
    "Product Analysis",
    "Reports and Insights",
]


st.set_page_config(
    page_title="FoodGuard AI | Food Safety Analytics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def add_styles() -> None:
    """Apply a restrained dashboard theme."""
    st.markdown(
        """
        <style>
        .stApp { background: #F5F7F6; }
        [data-testid="stSidebar"] { background: #123B35; }
        [data-testid="stSidebar"] * { color: #F2F7F5 !important; }
        [data-testid="stMetric"] {
            background: #FFFFFF; padding: 1rem 1.1rem; border-radius: 14px;
            border: 1px solid #E0E9E5; box-shadow: 0 2px 8px rgba(18,59,53,.04);
        }
        [data-testid="stMetricValue"] { color: #123B35; }
        .hero {
            background: linear-gradient(120deg, #123B35 0%, #246457 100%);
            color: white; padding: 1.6rem 1.8rem; border-radius: 18px;
            margin: .2rem 0 1.3rem 0;
        }
        .hero h1 { color: white; margin: 0 0 .35rem 0; }
        .hero p { color: #D9EAE5; margin: 0; font-size: 1.03rem; }
        .note { background: #E9F1EE; border-left: 4px solid #34796B;
            padding: .8rem 1rem; border-radius: 8px; margin: .5rem 0 1rem 0; }
        .warning { background: #FFF4DD; border-left: 4px solid #D9992F;
            padding: .8rem 1rem; border-radius: 8px; margin: .5rem 0 1rem 0; }
        h1, h2, h3 { color: #173E37; }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def read_csv(path_string: str, modified_at: int) -> pd.DataFrame:
    """Read a project CSV; modification time invalidates stale cached files."""
    del modified_at  # included in Streamlit's cache key
    return pd.read_csv(path_string)


def read_project_csv(path: Path) -> pd.DataFrame:
    """Read a project CSV with its current modification time in the cache key."""
    return read_csv(str(path), path.stat().st_mtime_ns)


def load_dataset() -> pd.DataFrame | None:
    """Load the processed FSSAI aggregate dataset, if available."""
    if not CLEAN_DATA.exists():
        return None
    return read_project_csv(CLEAN_DATA)


def fmt_count(value: int | float) -> str:
    """Format a count for cards and tables."""
    return f"{int(value):,}"


def show_header(title: str, description: str) -> None:
    st.title(title)
    st.caption(description)


def get_filtered_data(frame: pd.DataFrame) -> pd.DataFrame:
    """Offer consistent state and fiscal-year filters in the sidebar."""
    states = sorted(frame["state_ut"].dropna().unique().tolist())
    years = sorted(frame["fiscal_year"].dropna().astype(str).unique().tolist())
    selected_states = st.sidebar.multiselect("State / UT", states, default=states)
    selected_years = st.sidebar.multiselect("Fiscal year", years, default=years)
    return frame[
        frame["state_ut"].isin(selected_states)
        & frame["fiscal_year"].astype(str).isin(selected_years)
    ].copy()


def make_category_chart(frame: pd.DataFrame) -> plt.Figure:
    totals = {label: int(frame[column].sum()) for label, column in CATEGORIES.items()}
    data = pd.Series(totals).sort_values()
    fig, ax = plt.subplots(figsize=(9, 4.4))
    bars = ax.barh(data.index, data.values, color=[COLORS[x] for x in data.index])
    ax.bar_label(bars, labels=[fmt_count(x) for x in data.values], padding=4)
    ax.set_xlabel("Reported count")
    ax.set_ylabel("")
    ax.set_title("Reported non-conforming outcomes by category")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(False, axis="y")
    ax.grid(True, axis="x", alpha=.2)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return fig


def make_state_chart(frame: pd.DataFrame, metric: str, title: str, top_n: int = 12) -> plt.Figure:
    top = frame.nlargest(top_n, metric).sort_values(metric)
    fig, ax = plt.subplots(figsize=(9, 5.3))
    bars = ax.barh(top["state_ut"], top[metric], color="#34796B")
    ax.bar_label(bars, labels=[fmt_count(x) for x in top[metric]], padding=3, fontsize=8)
    ax.set_xlabel("Reported count")
    ax.set_ylabel("")
    ax.set_title(title)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(False, axis="y")
    ax.grid(True, axis="x", alpha=.2)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return fig


def show_home(frame: pd.DataFrame) -> None:
    show_header("Home Dashboard", "A transparent view of published food safety reporting data.")
    st.markdown(
        "<div class='hero'><h1>FoodGuard AI</h1><p>Food safety inspection and laboratory reporting analytics · India</p></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='warning'><b>Interpret with care:</b> the current dataset contains State/UT aggregate counts for FY 2021–22. Counts reflect regulatory sampling and reporting activity; they are not risk rates and do not prove adulteration.</div>",
        unsafe_allow_html=True,
    )
    years = ", ".join(sorted(frame["fiscal_year"].astype(str).unique()))
    lifted = int(frame["samples_lifted"].sum())
    analysed = int(frame["samples_analysed"].sum())
    nonconforming = int(frame["total_nonconforming_samples"].sum())
    state_inspections = int(frame["total_state_inspections"].sum())
    metrics = st.columns(4)
    for col, label, value, help_text in zip(
        metrics,
        ["State / UT rows", "Samples lifted", "Samples analysed", "Non-conforming outcomes"],
        [len(frame), lifted, analysed, nonconforming],
        [f"Fiscal year(s): {years}", "As reported in FSSAI Table 14", "As reported in FSSAI Table 14", "Includes previous-year sample results reported in FY 2021–22"],
    ):
        col.metric(label, fmt_count(value), help=help_text)

    left, right = st.columns([1.2, 1])
    with left:
        st.pyplot(make_category_chart(frame), clear_figure=True, use_container_width=True)
    with right:
        st.pyplot(
            make_state_chart(frame, "total_nonconforming_samples", "Largest reported outcome counts"),
            clear_figure=True,
            use_container_width=True,
        )
    st.metric("State/UT FoSCoRIS inspections", fmt_count(state_inspections))
    st.caption("FSSAI also reports 5,063 inspections by Railways and Airport authorities in Table 15; those are not allocated to State/UT rows here.")


def show_upload() -> None:
    show_header("Dataset Upload", "Preview an additional CSV or Excel dataset for this session.")
    st.info("Uploaded files are read in memory for this app session and are not saved to disk. This upload preview does not replace the FSSAI dashboard data.")
    uploaded = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx", "xls"])
    if uploaded is None:
        st.markdown("Expected columns for record-level analysis may include a sample or inspection ID, product/category, state/district, inspection or testing date, and an authentic result label.")
        return
    try:
        if uploaded.name.lower().endswith(".csv"):
            uploaded_frame = pd.read_csv(uploaded)
        else:
            uploaded_frame = pd.read_excel(uploaded)
        st.session_state["uploaded_frame"] = uploaded_frame
        st.success(f"Loaded {len(uploaded_frame):,} rows and {len(uploaded_frame.columns):,} columns into this session.")
        st.dataframe(uploaded_frame.head(100), use_container_width=True)
        st.download_button(
            "Download this preview as CSV",
            uploaded_frame.to_csv(index=False).encode("utf-8"),
            file_name=f"{Path(uploaded.name).stem}_preview.csv",
            mime="text/csv",
        )
    except Exception as exc:  # show a helpful upload error to the learner
        st.error(f"Could not read that file: {exc}")


def show_cleaning(frame: pd.DataFrame) -> None:
    show_header("Data Cleaning", "Review the cleaned State/UT aggregate table and its validation flags.")
    st.markdown("The raw FSSAI source tables remain unchanged. Cleaning standardized labels, checked numeric counts, joined Tables 14 and 15 by State/UT and fiscal year, and flagged inconsistencies for review.")
    report_path = ROOT / "data" / "processed" / "data_validation_report.md"
    if report_path.exists():
        with st.expander("Read the validation report", expanded=True):
            st.markdown(report_path.read_text(encoding="utf-8"))
    display_cols = [
        "fiscal_year", "state_ut", "samples_lifted", "samples_analysed",
        "analysis_reports_awaited", "total_nonconforming_samples",
        "qc_nonconforming_categories_match", "qc_inspection_subtotals_match",
        "qc_analysed_exceeds_lifted", "qc_awaited_differs_from_lifted_minus_analysed",
    ]
    st.dataframe(frame[display_cols], use_container_width=True, hide_index=True)
    st.download_button("Download cleaned aggregate CSV", frame.to_csv(index=False).encode("utf-8"), "fssai_cleaned_aggregate.csv", "text/csv")


def show_eda(frame: pd.DataFrame) -> None:
    show_header("Exploratory Analysis", "Explore reported outcome categories and State/UT count comparisons.")
    filtered = get_filtered_data(frame)
    if filtered.empty:
        st.warning("Choose at least one State/UT and fiscal year in the sidebar.")
        return
    first, second = st.columns(2)
    with first:
        st.pyplot(make_category_chart(filtered), clear_figure=True, use_container_width=True)
    with second:
        st.pyplot(make_state_chart(filtered, "total_nonconforming_samples", "Reported non-conforming outcome counts"), clear_figure=True, use_container_width=True)
    st.dataframe(
        filtered[["state_ut", "samples_lifted", "samples_analysed", "total_nonconforming_samples", *CATEGORIES.values()]].sort_values("total_nonconforming_samples", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
    st.caption("The source has no month, district, or product fields. Monthly/yearly trends, district comparisons, and product rankings are not available from this dataset.")


def show_statistics(frame: pd.DataFrame) -> None:
    show_header("Statistical Analysis", "Descriptive summaries and rank associations across State/UT reporting totals.")
    summary_cols = ["samples_lifted", "samples_analysed", "analysis_reports_awaited", "total_nonconforming_samples", *CATEGORIES.values(), "total_state_inspections"]
    st.subheader("Descriptive statistics across the selected State/UT rows")
    filtered = get_filtered_data(frame)
    st.dataframe(filtered[summary_cols].describe().T, use_container_width=True)
    st.subheader("Spearman rank associations")
    corr_path = ROOT / "reports" / "statistical_correlation_results.csv"
    if corr_path.exists():
        corr = read_project_csv(corr_path)
        st.dataframe(corr, use_container_width=True, hide_index=True)
    report = ROOT / "reports" / "statistical_analysis.md"
    if report.exists():
        with st.expander("Interpretation and limitations"):
            st.markdown(report.read_text(encoding="utf-8"))
    st.caption("Associations are descriptive, not causal. Counts rise with testing/inspection activity, and this is one reporting year rather than a random sample.")


def show_ml(frame: pd.DataFrame) -> None:
    show_header("Machine Learning", "A data-readiness check and optional exploratory clustering.")
    st.markdown("<div class='warning'><b>Supervised classification is not supported.</b> These are aggregate State/UT counts, not individual samples, and there is no reliable record-level target label. Classifier metrics would be misleading.</div>", unsafe_allow_html=True)
    report_path = ROOT / "reports" / "ml_feasibility.md"
    if report_path.exists():
        with st.expander("Read the feasibility report", expanded=True):
            st.markdown(report_path.read_text(encoding="utf-8"))
    cluster_file = ROOT / "data" / "processed" / "state_volume_clusters_2021-22.csv"
    if cluster_file.exists():
        cluster_data = read_project_csv(cluster_file)
        st.subheader("Exploratory K-Means reporting-volume profiles")
        st.caption("Cluster IDs group count patterns. They are arbitrary and are not food safety risk classes.")
        image_path = ROOT / "reports" / "ml_figures" / "state_activity_clusters_pca.png"
        if image_path.exists():
            st.image(str(image_path), use_container_width=True)
        st.dataframe(cluster_data[["state_ut", "cluster_id", "samples_analysed", "total_state_inspections", "total_nonconforming_samples"]].sort_values("cluster_id"), use_container_width=True, hide_index=True)


def show_risk(frame: pd.DataFrame) -> None:
    show_header("Food Safety Risk Analysis", "Review what the current data can say without overstating risk.")
    st.markdown("<div class='warning'><b>No Low / Medium / High risk labels are assigned.</b> This dataset has one year of State/UT totals, with no entity history, dates, or validated severity weights.</div>", unsafe_allow_html=True)
    if INDICATOR_DATA.exists():
        indicators = read_project_csv(INDICATOR_DATA)
        metric_a, metric_b = st.columns(2)
        with metric_a:
            st.metric("Risk scores available", "No")
        with metric_b:
            st.metric("Rows marked Not scored", fmt_count((indicators["risk_category"] == "Not scored").sum()))
        st.markdown("The indicative current-year non-conformance yield is a rough ratio of reported current-year outcomes to samples analysed. It is not an official compliance rate and may be affected by reporting and denominator inconsistencies.")
        st.dataframe(indicators[["state_ut", "indicative_current_year_nonconforming_yield_percent", "unsafe_share_of_reported_issue_categories_percent", "risk_score", "risk_category"]].sort_values("indicative_current_year_nonconforming_yield_percent", ascending=False), use_container_width=True, hide_index=True)
        st.download_button("Download reporting indicators", indicators.to_csv(index=False).encode("utf-8"), "state_reporting_indicators.csv", "text/csv")
    if RISK_REPORT.exists():
        with st.expander("Scoring feasibility and future data needs"):
            st.markdown(RISK_REPORT.read_text(encoding="utf-8"))
    st.caption("An analytical indicator is not confirmed evidence of food adulteration.")


def show_regional(frame: pd.DataFrame) -> None:
    show_header("Regional Analysis", "Compare State/UT reporting totals with context about their denominators.")
    filtered = get_filtered_data(frame)
    if filtered.empty:
        st.info("Choose at least one State/UT and fiscal year in the sidebar.")
        return
    one, two = st.columns(2)
    with one:
        st.pyplot(make_state_chart(filtered, "total_state_inspections", "FoSCoRIS inspection counts"), clear_figure=True, use_container_width=True)
    with two:
        st.pyplot(make_state_chart(filtered, "total_nonconforming_samples", "Non-conforming outcome counts"), clear_figure=True, use_container_width=True)
    st.dataframe(filtered[["state_ut", "samples_analysed", "total_nonconforming_samples", "total_state_inspections"]].sort_values("state_ut"), use_container_width=True, hide_index=True)
    st.info("These are counts, not normalized rates. The source does not include a consistent food-business or population denominator, so regional rankings should be interpreted as reported activity and outcomes only.")


def show_product(frame: pd.DataFrame) -> None:
    del frame
    show_header("Product Analysis", "Product-level comparisons require product-level records.")
    st.info("The selected FSSAI annual report tables aggregate results by State/UT. They do not provide product names or food categories in the fields currently loaded, so this page cannot rank products or categories.")
    st.markdown("<div class='note'><b>Next data requirement:</b> a published FSSAI product-wise laboratory table with a documented fiscal year, product/category labels, tested counts, and outcome counts. Keep each report's aggregation level and source citation with the data.</div>", unsafe_allow_html=True)
    st.caption("The app does not invent product records to fill the gap.")


def show_reports(frame: pd.DataFrame) -> None:
    show_header("Reports and Insights", "Read and download the analysis outputs generated from the source data.")
    reports = [
        ("Exploratory analysis", EDA_REPORT),
        ("Statistical analysis", STAT_REPORT),
        ("Machine-learning feasibility", ML_REPORT),
        ("Risk-scoring feasibility", RISK_REPORT),
    ]
    for label, path in reports:
        if path.exists():
            with st.expander(label):
                content = path.read_text(encoding="utf-8")
                st.markdown(content)
                st.download_button(
                    f"Download {label.lower()} report",
                    content.encode("utf-8"),
                    file_name=path.name,
                    mime="text/markdown",
                    key=f"download_{path.stem}",
                )
    st.download_button("Download filtered dashboard data", frame.to_csv(index=False).encode("utf-8"), "fssai_dashboard_data.csv", "text/csv")
    st.markdown("### Current highlights")
    st.write(f"- {len(frame)} State/UT rows are available.")
    st.write(f"- Reported unsafe outcomes total {fmt_count(frame['unsafe_samples'].sum())}.")
    st.write(f"- Reported substandard outcomes total {fmt_count(frame['substandard_samples'].sum())}.")
    st.write("- Sample-level prediction and Low/Medium/High risk scoring remain unsupported by the available aggregate data.")


def main() -> None:
    add_styles()
    with st.sidebar:
        st.markdown("## 🛡️ FoodGuard AI")
        st.caption("Food safety analytics · India")
        page = st.radio("Navigate", PAGES, label_visibility="collapsed")
        st.divider()
        st.caption("Source: FSSAI Annual Report 2021–22, Tables 14 and 15")

    frame = load_dataset()
    if frame is None:
        st.error("The processed FSSAI dataset is missing. Run `.venv/bin/python -m src.preprocessing` from the project folder first.")
        st.stop()

    renderers = {
        "Home Dashboard": show_home,
        "Dataset Upload": lambda data: show_upload(),
        "Data Cleaning": show_cleaning,
        "Exploratory Analysis": show_eda,
        "Statistical Analysis": show_statistics,
        "Machine Learning": show_ml,
        "Food Safety Risk Analysis": show_risk,
        "Regional Analysis": show_regional,
        "Product Analysis": show_product,
        "Reports and Insights": show_reports,
    }
    renderers[page](frame)
    st.divider()
    st.caption("Educational analytics application. Reported non-conformance and exploratory indicators are not proof of food adulteration.")


if __name__ == "__main__":
    main()
