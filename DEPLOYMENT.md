# Deploy FoodGuard AI with Streamlit Community Cloud

This project can be hosted as a Streamlit app without a separate backend. The app reads its default FSSAI dataset and analysis files from the project folder. Community Cloud needs those files in the GitHub repository because it runs the app in a fresh environment.

## Before publishing

1. Decide whether your GitHub repository should be public or private. Anyone can view a public repository and a public Streamlit app. Community Cloud can deploy private repositories too, but requires additional GitHub authorization.
2. Review the files that will be committed. The `.gitignore` file excludes `.venv/`, `.env`, raw source files, and most processed data. It allows the FSSAI source notes and only these small State/UT aggregate files needed by the app:
   - `data/raw/FSSAI_SOURCE_NOTES.md`
   - `data/processed/fssai_state_summary_2021-22_clean.csv`
   - `data/processed/state_reporting_indicators_2021-22.csv`
   - `data/processed/state_volume_clusters_2021-22.csv`
   - `data/processed/data_validation_report.md`
3. Keep the raw PDF and raw source tables out of the repository unless you have checked their redistribution terms. Do not commit passwords, API keys, `.env` files, or `.venv/`.
4. The local `.venv` currently uses Python 3.9. For a new cloud deployment, select a supported Python version in the Community Cloud advanced settings and make sure the dependency installation succeeds. If you update the Python version, reproduce it locally before relying on it.

## Create a GitHub repository

The project folder is not currently a Git repository. From a terminal opened in the project root, initialize and review the files before publishing:

```bash
git init
git status --short
```

Review the status carefully. Confirm that `.venv/`, `.env`, the source PDF, and raw source CSVs are absent. `data/raw/FSSAI_SOURCE_NOTES.md` and the required processed aggregate files listed above should appear. Then stage the project files, review the staged list, and commit:

```bash
git add .
git status --short
git commit -m "Prepare FoodGuard AI Streamlit app"
```

Create an empty repository on GitHub, connect it as `origin`, and push the branch shown by `git branch --show-current` to GitHub. Do not paste a GitHub token into the terminal or into project files.

## Deploy the app

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub and authorize access to the repository you chose.
2. Select **Create app** and choose your repository, branch, and `app.py` as the entrypoint.
3. In **Advanced settings**, select a supported Python version. There are no app secrets to configure for the current version.
4. Choose **Deploy** and wait for the build. If it fails, open the app logs and read the first dependency or missing-file error.
5. Once it launches, open every page and verify the dashboard totals, filters, CSV/Excel preview, report downloads, and charts. The app's URL can then be shared with the intended audience.

Community Cloud builds from the GitHub repository and expects dependencies in `requirements.txt`. Changes pushed to the selected branch can update the deployed app, so review future commits before pushing.

## Files used by the deployed app

- `app.py` — Streamlit entrypoint.
- `requirements.txt` — Python packages.
- `data/processed/` — allowlisted public aggregate inputs and validation report.
- `reports/` — generated markdown summaries, tables, and plots shown in the app.
- `src/` — preprocessing and analysis modules.

The app is educational and descriptive. Its State/UT counts are not rates, predictions, or proof of adulteration. The app's file upload feature reads data into the active session and does not persist uploads to disk.
