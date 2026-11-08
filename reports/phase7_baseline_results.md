# Phase 7A exploratory baseline results

The fixed panel did **not** show a stronger reproducible age association than expression-matched gene sets in these two cohorts. Ridge predicted chronological age better than constant predictions within discovery, but its error was typical of matched random panels. No external age prediction was attempted. These results use the [frozen protocol](../docs/phase7_research_protocol.md) and the [audited GEO inputs](phase7_data_feasibility.md).

## Independent association analysis

The analysis covered 109 of the original 113 genes among 97 healthy discovery donors and 82 healthy validation donors aged 22–89. Each cohort supplied a separate age effect estimated from its own expression units and covariates. The [gene ledger](phase7_gene_associations.csv) contains 113 rows with cohort coverage flags, partial correlations, nominal p-values and within-cohort q-values for jointly eligible genes. The four excluded genes have empty effect fields.

| Association statistic | Fixed panel | Median of 1,000 matched panels | Matched 2.5th–97.5th percentiles |
| --- | ---: | ---: | ---: |
| Mean product of partial correlations across cohorts | 0.00464 | 0.00685 | 0.00258 to 0.01136 |
| Discovery mean squared partial correlation | 0.06202 | 0.05419 | 0.04389 to 0.06462 |
| Validation mean squared partial correlation | 0.01256 | 0.01257 | 0.00982 to 0.01574 |

The panel replication score exceeded 15.2% of matched scores and fell below the frozen 95th-percentile cutoff of 0.01034. Its 95% donor-bootstrap interval was −0.01143 to 0.02270. The sex-stratified validation permutation p-value was 0.2889. The primary decision rule was not met. Restricting discovery to the 84 NextSeq donors gave a similar score of 0.00467. The mean absolute rank differences for discovery abundance, discovery detection, validation abundance and validation detection were 0.0104, 0.0012, 0.0100 and 0.0006. These quantities describe matching on a 0–1 rank scale.

Directions agreed for 63 of 109 genes (57.8%). Within the panel, 48 genes had q < 0.05 in discovery and zero did in validation. No gene met that threshold in both cohorts with the same direction. For example, TP53 had partial correlations of 0.165 and −0.078, and CDKN2A had −0.001 and −0.172. TERT failed the expression filter in both cohorts. These estimates do not supersede the [CellAge perturbation evidence](gene_case_studies.md), which addresses a different endpoint.

## Discovery prediction feasibility

Five-fold cross-validation evaluated held-out donors once each. The five panel Ridge fits each used 109 features and alpha 109. All scaling and feature eligibility used training donors only. The 40 matched-panel comparators per fold used the same split, penalty rule and training-only matching. Five sex-and-platform OLS fits supplied a diagnostic baseline. No hyperparameters were tuned.

| Out-of-fold model | MAE, years | Median absolute error, years | RMSE, years | R² |
| --- | ---: | ---: | ---: | ---: |
| Panel Ridge | 15.34 | 14.32 | 17.65 | 0.373 |
| Training mean age | 20.18 | 23.10 | 22.42 | −0.011 |
| Training median age | 20.38 | 22.00 | 22.80 | −0.047 |
| Sex and platform OLS | 18.48 | 21.44 | 21.42 | 0.076 |

The panel reduced MAE by 5.04 years relative to the median-age baseline. The conditional paired 95% bootstrap interval for panel minus median was −7.11 to −2.95 years. It treats held-out predictions as fixed and omits retraining and cohort-shift uncertainty. Median matched-panel MAE was 15.03 years (2.5th–97.5th percentiles, 14.08 to 16.05). The target outperformed 12 of 40 matched panels (30%). The data show internal age information but no panel advantage over this control benchmark.

## Interpretation and follow-up

The primary result concerns relative evidence for the panel within these assays and eligibility rules. It leaves room for small or context-specific signals. Sample sizes, cohort composition, incomplete batch and passage metadata, and differences between isoform-based FPKM and gene counts limit interpretation. The matched panels control expression and detection approximately, with no guarantee of comparable co-expression or gene architecture. The expression-only Ridge baseline can exploit technical or demographic patterns correlated with age. Its internal error does not establish transfer to another cohort. The outcome is donor chronological age.

A scientific follow-up could use a frozen annotation-matched crosswalk and an independent cohort with comparable gene-level quantification. The next assistant step is to create the manually verified question set in the protocol and score a deterministic lookup against it. Include a question about why TERT has no Phase 7 effect and a question asking whether any gene passed the replication screen, alongside answerable questions that point to exact CellAge records. The analysis provides enough provenance to return those answers and abstain on unmeasured outcomes.

## Execution record

The run used Python 3.11.7 on arm64, NumPy 2.2.6, SciPy 1.15.3, scikit-learn 1.6.1, joblib 1.6.0 and threadpoolctl 3.8.0. BLAS threads were limited to one for analysis. Seed 20261108 and the frozen protocol SHA-256 `b6648a56607a9743a0fba4012826c6316151648d99c79ef2d6bd2d895a8ca702` identify the run. Use the [reproduction commands](phase7_data_feasibility.md#provenance-reuse-and-reproduction) to regenerate aggregate JSON and the gene ledger.
