# FoodGuard AI – Food Safety & Adulteration Analytics

An educational data science project for exploring authentic food safety inspection and laboratory reporting data, prioritizing Indian public sources.

## Current scope

- Streamlit application; no separate backend/API service.
- First dataset: state- and fiscal-year-level FSSAI annual report data.
- Descriptive analysis and transparent analytical indicators. No sample-level violation prediction unless reliable individual labeled records become available.
- Never interpret an analytical risk score as proof of food adulteration.

## Project layout

- `data/raw/`: unchanged source files and source notes.
- `data/processed/`: cleaned, analysis-ready datasets.
- `notebooks/`: learning and analysis notebooks.
- `src/`: reusable Python modules.
- `models/`: saved models only if supported by suitable data.
- `reports/`: generated charts and summaries.
- `powerbi/`: Power BI measures, theme, and report build guide.
- `database/`: optional local data schemas/utilities; no backend service.
- `app.py`: Streamlit application entry point; no separate backend service is used.

## Environment

Python 3.9 or newer is required for this initial dependency set. Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On macOS/Linux, if `python3` points to an older Python, install/select Python 3.9+ first. Do not put source datasets or secrets in Git.

## Run the current analysis pipeline

From the project root, run the modules in this order:

```bash
.venv/bin/python -m src.preprocessing
MPLCONFIGDIR=reports/.mplconfig .venv/bin/python -m src.eda
MPLCONFIGDIR=reports/.mplconfig .venv/bin/python -m src.statistics
MPLCONFIGDIR=reports/.mplconfig .venv/bin/python -m src.model_training
.venv/bin/python -m src.risk_scoring
```

The preprocessing step joins the FSSAI Tables 14 and 15 at state/UT and fiscal-year level. EDA creates charts and a summary under `reports/eda_charts/` and `reports/eda_summary.md`. Statistical analysis creates descriptive tables, category composition percentages, rank-association checks, and figures under `reports/`.

The available data covers FY 2021-22 only and contains state-level aggregates. It cannot support monthly or year-over-year trends, district or product rankings, or sample-level prediction. K-Means output groups reporting-volume profiles only; it does not represent safety risk. The risk-scoring feasibility module deliberately assigns no risk score or Low/Medium/High category because recent inspection outcomes and entity-level histories are unavailable. Rank correlations are descriptive and do not establish causation.

## Launch the Streamlit application

From this project folder, run:

```bash
.venv/bin/python -m streamlit run app.py
```

The application has pages for the dashboard, CSV/Excel upload preview, cleaning review, EDA, statistics, ML feasibility, risk analysis, regional analysis, product-data availability, and reports. Uploaded files are held in memory for the active session and are not saved to disk. Power BI assets and the dashboard build specification are in `powerbi/`; the final `.pbix` must be assembled in Power BI Desktop.

## Deployment

The Streamlit app can be deployed with Streamlit Community Cloud. Before publishing, review which project files will be pushed to GitHub and keep `.venv/`, `.env`, and raw data out of the repository. The exact setup and deployment steps are in [`DEPLOYMENT.md`](DEPLOYMENT.md).
