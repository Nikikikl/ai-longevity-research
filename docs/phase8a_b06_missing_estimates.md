# Phase 8A B06 missing numerical estimates

The original release audit remains the baseline. B06 selected `P7A-L17-L17`, which says TERT failed the expression filter in both cohorts. The model interpreted the blanks as zero anyway. The Local AI validator checked the response schema and citation ID, so it accepted the unsupported interpretation. Phase 7C already returns `not_measured` with two null estimates for the corresponding narrow English question. [Original B06 audit](phase8a_release_readiness.md#b06--interpretation-of-empty-tert-cells) · [Phase 7A evidence](../reports/phase7_baseline_results.md?plain=1#L17) · [Association ledger](../reports/phase7_gene_associations.csv?plain=1#L103)

## Regression cases fixed before implementation

| ID | Exact question | Expected behavior |
| --- | --- | --- |
| B06 | В таблице Phase 7A для TERT пустые значения. Их надо читать как нулевую корреляцию? | Explicitly reject zero and explain that TERT failed the expression filter in both cohorts. Cite the frozen TERT row. |
| A03 | Why are the Phase 7A partial correlations for TERT missing? | Preserve the correct explanation for both cohorts and the existing Phase 7A report reference. |
| R01 | In Phase 7A, do blank correlation estimates for FGF21 mean zero? | Neither cohort has an estimate. FGF21 failed the discovery filter and was eligible in validation. Cite its row and distinguish eligibility from an estimate. |
| R02 | Как в Phase 7A для TERT отличить измеренный ноль от отсутствующей оценки корреляции? | Explain the difference and identify the TERT fields as unestimated. Cite its row. |
| R03 | Was the Phase 7A discovery partial correlation for CDKN2A a measured value near zero? | Report the measured discovery estimate of −0.001464046161 from its row. Treat it as measured. |
| R04 | What were the Phase 7A partial correlations for CFTR? | Report insufficient evidence because the Phase 7A ledger has no CFTR row. Cite the report describing the ledger's scope. |
| B09 | How many of the original panel genes were eligible in both RNA-seq cohorts, and what did that comparison actually measure? | Remain on the existing generative path. The frozen expected result is 109 of 113 genes and expression associations with donor chronological age. Review any remaining error separately. |

## Correction

Local AI answers a single-gene Phase 7A partial-correlation question from the frozen association ledger when the question explicitly identifies Phase 7A and asks for partial correlations or the interpretation of missing or zero correlations. A present coefficient is displayed at its stored precision. A blank is reported as unestimated, with the cohort's eligibility status. A named gene outside the ledger produces an insufficient-evidence response. The source card links to the exact published CSV row, alongside the supporting report passage. A03 and B06 retain `P7A-L17-L17`.

This uses the same source as Phase 7C. Its lookup correctly classifies a blank estimate but takes narrow English input and rounds measured values. The Local AI path reads the existing ledger directly to preserve its recorded precision and render Russian and English responses. It returns before generation for this limited class of questions. The shared prompt, ranking, source validator, scientific reports and other modes remain unchanged. Unrecognized phrasing and questions outside this scope still use the existing path and can exhibit numerical errors.

The change is in `scripts/local_ai.py`, with regression tests in `tests/test_local_ai.py`. The original release-readiness audit and its test questions remain unchanged.

## Live regression on 2026-11-09

Both runs used Streamlit AppTest with the real loopback API and a fresh conversation for each case. Ollama 0.40.15 served `qwen3:1.7b` with model ID `8f68893c685c` and cloud features disabled. The observer forwarded requests unchanged. All seven baseline cases made one inference request each. Six cases used the ledger after the change and made no inference request. B09 continued to use the real model. The blocks below preserve the exact displayed text. Baseline outputs include the errors identified in the review.

### B06

**Baseline model output.** Sources `P7A-L17-L17`.

> Да, значения пустые в таблице Phase 7A для TERT следует считать нулевой корреляцией.

**Ledger response after the change.** Status `answered`. Sources `P7A-CSV-L103-L103`, `P7A-L17-L17`.

> TERT, Phase 7A. Экспрессия в фибробластах и возраст доноров. Поисковая когорта. Частичная корреляция не оценивалась (ген не прошёл фильтр экспрессии). Валидационная когорта. Частичная корреляция не оценивалась (ген не прошёл фильтр экспрессии). Пропуск не означает измеренный ноль.

The baseline reproduced the critical zero substitution with a valid citation ID. The corrected answer reports both blanks, explains the expression filter and distinguishes the blanks from a measured zero. The selected report and CSV line support the explanation.

### A03

**Baseline model output.** Sources `P7A-L17-L17`.

> The Phase 7A partial correlations for TERT are missing because TERT failed the expression filter in both cohorts, as stated in the primary excerpt.

**Ledger response after the change.** Status `answered`. Sources `P7A-CSV-L103-L103`, `P7A-L17-L17`.

> TERT, Phase 7A. Fibroblast expression and donor chronological age. Discovery cohort. Partial correlation not estimated (gene failed the expression filter). Validation cohort. Partial correlation not estimated (gene failed the expression filter). A blank estimate does not represent a measured zero.

The baseline already gave the correct reason. The deterministic answer preserves it, retains the original report citation and adds the TERT ledger row.

### R01

**Baseline model output.** Sources `V2-L23-L23`.

> No, blank correlation estimates for FGF21 do not mean zero. The study reports that for the panel, the mean product of discovery and validation partial correlations was 0.00464, and the median was 0.00685. The estimates do not meet the threshold of q < 0.05 in both cohorts with concordant signs. The results indicate that while some genes had significant associations, FGF21's estimates are not reported as zero.

**Ledger response after the change.** Status `answered`. Sources `P7A-CSV-L29-L29`, `P7A-L7-L7`.

> FGF21, Phase 7A. Fibroblast expression and donor chronological age. Discovery cohort. Partial correlation not estimated (gene failed the expression filter). Validation cohort. Partial correlation not estimated (gene passed eligibility). A blank estimate does not represent a measured zero. The paired analysis required eligibility in both cohorts.

The baseline rejected zero but cited an aggregate result and speculated about a significance threshold. The corrected answer reports both blank estimates and the distinct discovery and validation eligibility statuses, supported by the FGF21 row and the report scope.

### R02

**Baseline model output.** Sources `GENES-L51-L51`.

> В Phase 7A для TERT отличить измеренный ноль от отсутствующей оценки корреляции невозможно, так как эксперимент не тестировал reversal of established arrest. Измеренный ноль указывает на отсутствие корреляции, а отсутствие оценки корреляции означает, что данные не были собраны.

**Ledger response after the change.** Status `answered`. Sources `P7A-CSV-L103-L103`, `P7A-L17-L17`.

> TERT, Phase 7A. Экспрессия в фибробластах и возраст доноров. Поисковая когорта. Частичная корреляция не оценивалась (ген не прошёл фильтр экспрессии). Валидационная когорта. Частичная корреляция не оценивалась (ген не прошёл фильтр экспрессии). Пропуск не означает измеренный ноль.

The baseline shifted to a separate culture experiment and gave an unsupported explanation for the missing estimates. The corrected answer distinguishes the recorded blanks from an estimated zero and gives the actual exclusion reason from the TERT row.

### R03

**Baseline model output.** Sources `P7A-L17-L17`.

> No, the Phase 7A discovery partial correlation for CDKN2A was not a measured value near zero. It was −0.001 and −0.172, indicating a small but significant correlation in the discovery cohort, but not meeting the threshold for statistical significance in validation.

**Ledger response after the change.** Status `answered`. Sources `P7A-CSV-L15-L15`, `P7A-L17-L17`.

> CDKN2A, Phase 7A. Fibroblast expression and donor chronological age. Discovery cohort. r = -0.001464046161. Validation cohort. r = -0.1722628565.

The baseline gave rounded coefficients, wrongly denied that the discovery estimate was near zero and called it significant. The corrected answer gives the two stored coefficients, including the measured discovery value of −0.001464046161. It draws no significance conclusion.

### R04

**Baseline model output.** Sources None.

> The reported reason for insufficient evidence is that the primary excerpt does not provide information about the Phase 7A partial correlations for CFTR.

**Ledger response after the change.** Status `insufficient_evidence`. Sources `P7A-L7-L7`.

> The Phase 7A ledger has no row for CFTR. It provides no partial correlation estimate.

The baseline correctly abstained without verifying whether CFTR was in the ledger. The corrected answer confirms the absent row against the frozen CSV and links to the report that defines the scope of that ledger.

### B09

**Baseline model output.** Sources `V2-L23-L23`.

> 63 out of 109 original panel genes were eligible in both RNA-seq cohorts, and the comparison measured the partial Pearson correlations of expression abundance and detection across the cohorts.

**Model output after the change.** Status `answered`. Sources `V2-L23-L23`.

> 63 out of 109 original panel genes were eligible in both RNA-seq cohorts, and the comparison measured the partial Pearson correlations of expression abundance and detection across the cohorts.

The output and selected citation matched the baseline exactly. The answer still mistakes sign agreement among 109 genes for eligibility and misstates the donor-age outcome. This remains a separate critical blocker.

## Unchanged 20-case evaluation

Replayed all frozen questions with the original follow-up context and compared each status, displayed answer, retrieved passage list and selected citation list with the release-audit baseline. Only A03 and B06 differed. The other 18 cases matched exactly, including B09 and both pre-inference abstentions. The replay made 16 real model calls. The table records the scientific review for each replayed case. The original audit supplies the verbatim outputs for the unchanged rows. [Release audit](phase8a_release_readiness.md)

| Case | Review | Selected source IDs | Scientific outcome |
| --- | --- | --- | --- |
| A01 | Minor | `GENES-L31-L31` | Supported p53 restoration and arrest in EJ cells. Separate CellAge trigger boundary omitted. |
| A02 | Minor | `GENES-L51-L51` | Correctly distinguishes delay from reversal in culture. Quantitative doubling detail omitted. |
| A03 | Pass | `P7A-CSV-L103-L103`, `P7A-L17-L17` | Both cohorts failed the expression filter. CSV line and original report paragraph support the explanation. |
| A04 | Minor | `P7D-L16-L16` | Supported FOXO3 knockdown effects in fibroblasts. Stable arrest and activation limits omitted. |
| A05 | Minor | `P7D-L18-L18` | Correct association direction and odds ratio in Japanese American men. Confidence interval omitted. |
| A06 | Minor | `P7D-L22-L22` | Correctly rejects proof of replicative senescence. Specific marker and serial-passage details omitted. |
| A07 | Minor | `P7D-L28-L28` | Reports mouse survival and qualifies the female result. Male group and wild-type comparator not explicit. |
| A08 | Pass | `P7D-L26-L26` | Correctly separates the SIRT6 genotype association from a human intervention. |
| A09 | Minor | `GENES-L57-L57` | Declines a human survival inference. The culture characterization is more specific than the selected source. |
| A10 | Pass | None | Appropriate out-of-scope abstention before inference. |
| B01 | Critical | `V2-L17-L17` | The cited GO paragraph does not support prior publication of the overlap count. |
| B02 | Minor | `V2-L23-L23` | Correct comparison direction. Cross-cohort scope and numeric results omitted. |
| B03 | Critical | `P7D-L16-L16` | The cited fibroblast passage does not support the human side of the FOXO3 comparison. |
| B04 | Critical | `P7D-L16-L16` | Declines a human lifespan inference but gives a misleading account of the cell intervention and lacks support for the genotype claim. |
| B05 | Critical | `P7D-L22-L22` | The cited chondrocyte paragraph does not support the mouse-survival claim. |
| B06 | Pass | `P7A-CSV-L103-L103`, `P7A-L17-L17` | Rejects zero and reports both unestimated coefficients with the expression-filter reason and supporting citations. |
| B07 | Pass | None | Appropriately abstains from estimating human lifespan gained by treatment. |
| B08 | Minor | `P7D-L26-L26` | Conveys the observational boundary, with an unnecessary Phase 7A claim and no genotype-specific direction. |
| B09 | Critical | `V2-L23-L23` | Reuses the sign-agreement count as the eligibility count and misstates the donor-age endpoint. |
| B10 | Pass | None | Appropriate out-of-scope abstention before inference. |
The replay had 6 passing cases, 9 minor issues and 5 critical cases. B06 was the only case that changed severity. The v2.1.0 gate remains **NOT READY** because B01, B03, B04, B05 and B09 still have critical findings.

## Automated and provenance checks

The requested `python3 -B -m unittest discover -s tests -v` discovered 76 tests, with three Streamlit tests skipped in that interpreter. All 76 passed in the UI environment and all eight Phase 7 tests passed in the Phase 7 environment. `git diff --check` passed. The frozen reports, benchmarks and data matched v2.0.0. GitHub's plain-code view of the frozen association ledger contained the exact published lines 15, 29 and 103 used in the new source cards.
