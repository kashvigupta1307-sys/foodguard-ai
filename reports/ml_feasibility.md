# Machine-learning feasibility and exploratory clustering

## Supervised prediction decision

- Decision: `not_supported`.
- Reason: The source contains 36 state/UT aggregates for one fiscal year, not individual inspection or sample records. It has no reliable per-record compliance target and no record-level predictor fields. Counts cannot be expanded into synthetic labels.
- Logistic Regression, Decision Tree, Random Forest, and XGBoost classification metrics (accuracy, precision, recall, F1, confusion matrix, ROC-AUC) are not defined for this dataset.
- No labels or individual samples were fabricated, and no classifier was trained.

A future supervised model would need authentic individual sample/inspection records, a clearly defined outcome label, predictors available before the outcome, sufficient examples per class, and time-aware validation that avoids leakage.

## Exploratory K-Means analysis

- Observations: 36 State/UT aggregates from FY 2021-22.
- Features: samples_lifted, samples_analysed, total_state_inspections, unsafe_samples, substandard_samples, labelling_misleading_misc_samples.
- Counts were transformed with `log1p` to reduce skew, then standardized before fitting K-Means.
- Candidate k values and silhouette scores:
- k=2: silhouette=0.535
- k=3: silhouette=0.515
- k=4: silhouette=0.429
- k=5: silhouette=0.349
- The selected exploratory solution used k=2, the highest silhouette score among the tested values.
- The first two PCA components explain 94.5% of variance in the standardized features; the scatter plot is only a 2-D projection.

### Cluster profiles

- Cluster 0: 15 State/UTs; median samples analysed=108; median inspections=425; median reported non-conforming outcomes=4.
- Cluster 1: 21 State/UTs; median samples analysed=5,290; median inspections=4,839; median reported non-conforming outcomes=560.

Cluster IDs are arbitrary and can change if data or settings change. Because the input features are administrative counts, clusters primarily group reporting and activity volume. They are not Low/Medium/High risk labels, predictions, or evidence of adulteration. Silhouette score measures geometric separation only; it does not establish that the groups are meaningful for food safety.

## Output files

- `data/processed/state_volume_clusters_2021-22.csv`
- `reports/kmeans_silhouette_scores.csv`
- `reports/ml_figures/state_activity_clusters_pca.png`
- `reports/ml_feasibility.md`
