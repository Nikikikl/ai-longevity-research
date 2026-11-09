# Phase 8A B09 panel eligibility and endpoint

## Investigation

B09 retrieved `V2-L7-L7`, `V2-L21-L21`, `V2-L61-L61` and `V2-L23-L23`. The method and result were both available, although the summary ranked first. The model selected only `V2-L23-L23`, treated 63 sign agreements as the eligibility numerator, and treated the matching variables as the association endpoint. That passage supports sign agreement and describes matching. It does not support either claim in the answer. The citation validator accepted the supplied ID without assessing those claims. [Original audit](phase8a_release_readiness.md#b09--rna-seq-eligibility-and-endpoint) · [B06 replay](phase8a_b06_missing_estimates.md#unchanged-20-case-evaluation)

The Phase 7B/7C lookup derives the original panel size and paired eligibility from the frozen association ledger. It counts concordant directions from the signs of the paired estimates. There are 109 eligible genes out of 113 and 63 sign-concordant genes out of 109. Partial Pearson correlations between fibroblast expression and donor chronological age were estimated separately by cohort, adjusting for sex in both and sequencing platform in discovery. Expression abundance and detection in both cohorts were used for matching control panels. The fixed panel score was 0.00464 versus a matched median of 0.00685, and the prespecified decision rule was unmet. This is a scoped comparison with approximately matched controls. [Cohort methods](../reports/research_report_v2.md?plain=1#L21) · [Panel results and matching](../reports/research_report_v2.md?plain=1#L23) · [Interpretation](../reports/phase7_baseline_results.md?plain=1#L34)

## Frozen regression cases

The questions and expected outcomes below were fixed before the baseline inference and implementation.

| ID | Exact question | Expected behavior |
| --- | --- | --- |
| A | How many of the original panel genes were eligible in both RNA-seq cohorts, and what did that comparison actually measure? | Report 109 of 113 for eligibility, 63 of 109 for sign agreement, and separate the donor-age endpoint, cohort adjustments and control matching. Cite methods and results. |
| B | How many of the 113 genes passed eligibility in both cohorts? | Report 109 of 113. Keep 63 of 109 labeled sign agreement. |
| C | What does 63 out of 109 mean? | Explain agreement of estimated association directions among jointly eligible genes. |
| D | Did only 63 genes pass the expression filter? | Correct the premise with the 109-of-113 eligibility count and the 63-of-109 sign-agreement count. |
| E | Was chronological age or expression abundance the outcome of the Phase 7A association analysis? | Name donor chronological age. Distinguish the separate partial correlations and covariate adjustments from control matching. |
| F | What variables were used to match the control panels? | Report expression abundance and detection in both cohorts. Keep those variables separate from the donor-age endpoint. |
| G | В фазе 7А чем 109 генов, прошедших отбор, отличаются от 63 генов с совпавшим направлением связи? | In Russian, preserve both denominators and what each count represents. |
| H | What did the Phase 7A matched-panel comparison find, and what are its limitations? | Report the score and matched median, the unmet prespecified rule, and limits of the approximate matching and cohort scope. |
| I | Was the Phase 7A discovery partial correlation for CDKN2A a measured value near zero? | Preserve the B06 route and measured discovery coefficient of −0.001464046161, with the original CSV citation. |
| J | What temperature should I use to bake sourdough bread? | Abstain without inference or a citation. |

## Correction

Local AI handles narrow Phase 7A panel questions before generation and after the B06 single-gene lookup. The route recognizes panel eligibility, the two report ratios, the association endpoint, control matching and the scoped matched-panel comparison. It calls the existing Phase 7B `Evidence.association_answer` methods for eligibility, sign agreement and the frozen replication metrics. Ratio questions without a study name must match a ratio derived from the ledger. An unqualified question about control matching must use a narrow methods form. Other questions retain the existing retrieval and generation path.

Responses cite the passages for the specific facts they present. When a required passage is unavailable, the route reports insufficient evidence. The reports, frozen benchmarks, Phase 7C/7D interfaces, B06 single-gene path, prompt and Streamlit presentation stay as they were. This change selects a deterministic answer for a defined set of questions. It does not change Qwen3's scientific performance on the remaining questions.

The implementation is in `scripts/local_ai.py` and the tests are in `tests/test_local_ai.py`.

## Live regression on 2026-11-09

Both runs used Streamlit AppTest with the real loopback Ollama API, cloud features disabled, and a fresh conversation for each question. Ollama 0.40.15 served `qwen3:1.7b` (model ID `8f68893c685c`). A transport observer recorded requests without replacing responses. The baseline made eight inference calls (A–H). The corrected regression made none, since A–H used the panel lookup, I used the existing single-gene lookup, and J abstained before inference. The blocks below contain the exact displayed answers.

### A

**Baseline model output.** Status `answered`. Retrieved `V2-L7-L7`, `V2-L21-L21`, `V2-L61-L61`, `V2-L23-L23`. Selected `V2-L23-L23`.

> 63 out of 109 original panel genes were eligible in both RNA-seq cohorts, and the comparison measured the partial Pearson correlations of expression abundance and detection across the cohorts.

**Deterministic response.** Status `answered`. Retrieved `V2-L21-L21`, `V2-L23-L23`, `P7A-L34-L34`. Selected `V2-L21-L21`, `V2-L23-L23`, `P7A-L34-L34`.

> 109 of 113 panel genes were eligible in both cohorts. For 63 of 109 eligible genes, the estimated associations agreed in direction. Phase 7A estimated associations between fibroblast gene expression and donor chronological age. Partial Pearson correlations were estimated separately in each cohort, adjusting for sex in both and sequencing platform in discovery. Expression abundance and detection in both cohorts were used to match control panels.

The baseline confused the two denominators and assigned the matching variables to the outcome. The corrected answer gives both counts, names the donor-age endpoint and distinguishes the separate cohort fits, their covariates and matching. The cited methods, result and interpretation passages support those claims.

### B

**Baseline model output.** Status `answered`. Retrieved `V2-L23-L23`, `P7A-L34-L34`, `P7A-L7-L7`, `V2-L21-L21`. Selected `V2-L23-L23`.

> 63

**Deterministic response.** Status `answered`. Retrieved `V2-L21-L21`, `V2-L23-L23`. Selected `V2-L21-L21`, `V2-L23-L23`.

> 109 of 113 panel genes were eligible in both cohorts. For 63 of 109 eligible genes, the estimated associations agreed in direction.

The baseline answered 63 with the sign-agreement source. The corrected answer provides 109 of 113 for eligibility and separately identifies 63 of 109 as sign agreement.

### C

**Baseline model output.** Status `answered`. Retrieved `P7A-L21-L21`, `V2-L23-L23`, `P7A-L23-L28`. Selected `P7A-L21-L21`.

> 63 out of 109 means that 63 genes out of 109 genes showed agreement in sign between the two cohorts, indicating a moderate level of correlation in their expression patterns.

**Deterministic response.** Status `answered`. Retrieved `V2-L21-L21`, `V2-L23-L23`. Selected `V2-L21-L21`, `V2-L23-L23`.

> 109 of 113 panel genes were eligible in both cohorts. For 63 of 109 eligible genes, the estimated associations agreed in direction.

The baseline recognized sign agreement but cited the prediction methods and added an unsupported interpretation about expression patterns. The corrected answer identifies the denominator and agreement of estimated association directions, supported by the association result.

### D

**Baseline model output.** Status `answered`. Retrieved `P7D-L41-L41`, `P7A-L17-L17`, `GENES-L67-L67`, `GENES-L31-L31`. Selected `P7A-L17-L17`.

> Yes, 63 genes passed the expression filter.

**Deterministic response.** Status `answered`. Retrieved `V2-L21-L21`, `V2-L23-L23`. Selected `V2-L21-L21`, `V2-L23-L23`.

> 109 of 113 panel genes were eligible in both cohorts. For 63 of 109 eligible genes, the estimated associations agreed in direction.

The baseline affirmed the false premise. The corrected counts and citations show that 63 is the number with concordant directions, while 109 passed joint eligibility.

### E

**Baseline model output.** Status `answered`. Retrieved `P7B-L22-L22`, `V2-L23-L23`, `V2-L7-L7`, `P7A-L3-L3`. Selected `P7A-L3-L3`.

> Chronological age was the outcome of the Phase 7A association analysis.

**Deterministic response.** Status `answered`. Retrieved `V2-L21-L21`, `V2-L23-L23`, `P7A-L34-L34`. Selected `V2-L21-L21`, `V2-L23-L23`, `P7A-L34-L34`.

> Phase 7A estimated associations between fibroblast gene expression and donor chronological age. Partial Pearson correlations were estimated separately in each cohort, adjusting for sex in both and sequencing platform in discovery. Expression abundance and detection in both cohorts were used to match control panels.

The baseline named the correct endpoint without explaining its relation to matching. The corrected answer retains donor chronological age and identifies the design and separate matching variables. The cited interpretation explicitly names the chronological-age outcome.

### F

**Baseline model output.** Status `answered`. Retrieved `P7A-L30-L30`, `P7A-L34-L34`, `V2-L7-L7`. Selected `P7A-L30-L30`.

> The variables used to match the control panels include donor chronological age, as the primary result concerns the relative evidence for the panel within these assays and eligibility rules, and the outcome is donor chronological age.

**Deterministic response.** Status `answered`. Retrieved `V2-L21-L21`, `V2-L23-L23`, `P7A-L34-L34`. Selected `V2-L21-L21`, `V2-L23-L23`, `P7A-L34-L34`.

> Phase 7A estimated associations between fibroblast gene expression and donor chronological age. Partial Pearson correlations were estimated separately in each cohort, adjusting for sex in both and sequencing platform in discovery. Expression abundance and detection in both cohorts were used to match control panels.

The baseline gave donor age as a matching variable and cited a prediction result. The corrected answer identifies expression abundance and detection in both cohorts as matching variables. The result passage states both.

### G

**Baseline model output.** Status `answered`. Retrieved `P7A-L17-L17`, `P7A-L7-L7`, `V2-L21-L21`, `V2-L23-L23`. Selected `P7A-L17-L17`.

> В фазе 7А 109 генов, прошедших отбор, отличаются от 63 генов с совпавшим направлением связи тем, что у 48 из них в отборе прошли но в валидации не прошли. Это указывает на различия в эффекте между кохортами.

**Deterministic response.** Status `answered`. Retrieved `V2-L21-L21`, `V2-L23-L23`. Selected `V2-L21-L21`, `V2-L23-L23`.

> В обеих когортах критериям отбора соответствовали 109 из 113 генов панели. У 63 из 109 прошедших отбор генов направления связи совпали между когортами.

The baseline confused eligibility with the significance counts. The corrected Russian response distinguishes 109 of 113 from 63 of 109 and cites the corresponding cohort and result passages.

### H

**Baseline model output.** Status `answered`. Retrieved `V2-L23-L23`, `P7A-L3-L3`, `V2-L21-L21`, `V2-L25-L25`. Selected `V2-L23-L23`.

> The Phase 7A matched-panel comparison found that the fixed panel did not show a stronger reproducible age association than expression-matched gene sets. The mean product of partial correlations was 0.00464 for the panel and 0.00685 at the median for matched panels. The target fell below the matched 95th-percentile cutoff of 0.01034. Limitations include prediction error in an external cohort, differences in quantification, sample composition, culture, and incomplete technical metadata.

**Deterministic response.** Status `answered`. Retrieved `V2-L23-L23`, `P7A-L34-L34`. Selected `V2-L23-L23`, `P7A-L34-L34`.

> The cross-cohort panel score was 0.00464, versus a matched-panel median of 0.00685. The prespecified decision rule for superiority was not met. The comparison is limited to these two cohorts and approximate matching on expression abundance and detection, with no guarantee of comparable co-expression.

The baseline got the main comparison and scores right but included a prediction-specific limitation without citation support. The corrected response preserves the scores, reports the unmet rule and limits the claim to the two cohorts and approximately matched controls. The two citations support the comparison and its scope.

### I

**Both runs.** Status `answered`. Retrieved `P7A-CSV-L15-L15`, `P7A-L17-L17`. Selected `P7A-CSV-L15-L15`, `P7A-L17-L17`.

> CDKN2A, Phase 7A. Fibroblast expression and donor chronological age. Discovery cohort. r = -0.001464046161. Validation cohort. r = -0.1722628565.

The same B06 single-gene route returned both recorded values before and after. The discovery coefficient remained a measured near-zero value at stored precision, supported by the exact CSV row.

### J

**Both runs.** Status `insufficient_evidence`. Retrieved None. Selected None.

> No matching passages in the project reports. Try naming the gene, study or outcome.

Both runs appropriately abstained before inference with no retrieved or selected source.

## Frozen 20-case replay

The same questions, order and follow-up context were used. The comparator is the documented post-B06 replay. The 19 other cases reproduced their displayed text, retrieved passages, status and selected citations exactly. Their verbatim responses and detailed scientific reviews are in the earlier audits. B09 matches regression A above. The new replay made 15 real inference calls, three deterministic replies (A03, B06 and B09), and two pre-inference abstentions. [Post-B06 review](phase8a_b06_missing_estimates.md#unchanged-20-case-evaluation) · [Historical release audit](phase8a_release_readiness.md)

| Case | Review | Selected source IDs | Scientific assessment |
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
| B09 | Pass | `V2-L21-L21`, `V2-L23-L23`, `P7A-L34-L34` | The baseline confused the two denominators and assigned the matching variables to the outcome. The corrected answer gives both counts, names the donor-age endpoint and distinguishes the separate cohort fits, their covariates and matching. The cited methods, result and interpretation passages support those claims. |
| B10 | Pass | None | Appropriate out-of-scope abstention before inference. |

The replay had **7 Pass, 9 Minor and 4 Critical**, compared with **6 Pass, 9 Minor and 5 Critical** after B06. A03 and B06 retain the exact TERT ledger row and expression-filter explanation. CDKN2A retains the exact measured near-zero coefficient in regression I.

The stable release remains **NOT READY**. B01 still lacks citation support for the prior publication. B03 and B04 still lack adequate support for the human-genotype side of the FOXO3 evidence. B05 still cites only the cell experiment for a comparison that includes mouse survival. Questions outside the scoped routes remain subject to model errors.

## Automated checks

`python3 -B -m unittest discover -s tests -v` discovered 80 tests and skipped three Streamlit tests in the base interpreter. All 80 passed in the UI environment, and all eight separate Phase 7 tests passed in the Phase 7 environment. `git diff --check` passed. The frozen reports, data and benchmarks match the scientific release.
