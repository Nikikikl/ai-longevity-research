# Phase 8A release readiness

## Decision

**Fail the v2.1.0 stable release gate.** Keep Local AI labeled experimental. The application and provenance checks passed, but the model made critical scientific errors on independently phrased questions. The prompt trial introduced new errors and was discarded. The evaluated application code remains at `9edd99e6b9bf38e670a4b6afb23413353fe3e2c5`. This audit does not create or recommend a release tag.

| Run | Cases | Pass | Minor | Critical | Median for model-backed cases |
| --- | --- | --- | --- | --- | --- |
| Baseline | 20 | 5 | 9 | 6 | 2.87 s |
| Prompt trial | 20 | 4 | 4 | 12 | 2.99 s |

All six baseline critical failures were in Series B.

### Prioritized blockers

1. Require the selected evidence to support every central claim. B01 and B03–B05 selected an excerpt that could not substantiate part or all of the requested conclusion even when the supporting excerpt was retrieved. This affects prior publication, human genotype evidence and comparisons of culture with animal survival.
2. Preserve missingness, denominators and endpoints. B06 read an unmeasured TERT value as zero. B09 substituted the sign-agreement count for eligibility and confused the matching variables with the donor-age endpoint.
3. Preserve study boundaries under changes in wording and prompting. The prompt trial reversed the direction of the FOXO3 association, called the SIRT6 subtype established and made additional claims about human evidence. A new candidate must be evaluated on unchanged questions with zero critical errors.

## Protocol

The baseline used commit `9edd99e6b9bf38e670a4b6afb23413353fe3e2c5`. Series A contains all 10 scenarios from the existing evaluation in their original order. Series B contains 10 new Russian and English phrasings authored for this audit and fixed before inference. The new questions were authored and scored by the same reviewer. A05 follows A04, and B04 follows B03. Each other question started with an empty conversation. [Existing evaluation](phase8a_local_ai_evaluation.md)

All model calls in both runs used local **qwen3:1.7b**, model digest `8f68893c685c3ddff2aa3fffce2aa60a30bb2da65ca488b61fff134a4d1730e7`, and **Ollama 0.40.15**. The host was Apple M2 with 8 GB of RAM and macOS 26.6.2. Python was 3.11.7 and Streamlit was 1.67.0. The Streamlit AppTest adapter submitted the questions through the real application handler and local API. A transport observer recorded the returned content and did not substitute responses. The 18 model-backed cases in each run used one chat request each. The two out-of-scope cases were handled before inference. Response times are elapsed wall-clock times from submission through the Streamlit adapter and include retrieval and rendering. They exclude clearing the previous conversation.

Critical means a central unsupported claim or citation, a materially false scientific result or one of the specified causal, lifespan, novelty, universal-negative or measurement errors. Minor includes omissions, wording, or a peripheral claim without adequate support when the central result and citation are sound. A scientifically appropriate refusal to infer an effect can use either app status. A source ID matching the request is necessary for a source card but does not establish support. The answers below are verbatim test outputs and include errors. The review is based on the frozen report passages.

The prompt trial appended the following to the existing system instruction in memory. Retrieval, model, decoding settings, source validation and questions stayed fixed. It fixed no baseline critical case and introduced six new critical cases (A03, A05, A06, A09, B02 and B07). The application prompt was left at the baseline.

```text
Support each central claim with a selected excerpt, including both sides of a comparison. Match each number and denominator to the exact outcome asked about. A blank or ineligible measurement is unmeasured, not zero. If a claim is unsupported, leave it out and state what information is missing.
```

## Release audit

| Check | Result |
| --- | --- |
| Automated suite | Pass. 73 tests from `tests` and 8 from `tests/phase7`. The Streamlit tests checked both deterministic modes without contacting Ollama. |
| Streamlit startup and detection | Pass. The loopback server returned HTTP 200 for the main page and `ok` for its health endpoint. AppTest confirmed model availability, the presence of the retrieved-evidence expander when passages were returned, and the source-card links for every model-selected ID. |
| Research Q&A and Evidence records | Pass. Independent CLI and adapter regression tests passed. The Phase 7B ledger check and Phase 7D record check passed. Frozen exact-answer scores reproduced at 18/24 for Phase 7C and 10/10 for Phase 7D. |
| Published source links | Pass. Fetched all five GitHub file pages in plain code view at `ba0365a234d4b0b4bf16bc8aa5ce5049dbf7819a`. Compared GitHub's published line data with the tagged and local files and verified all 87 passage ranges and their GitHub line markup. |
| Local runtime and cost | Pass. Ollama started with `OLLAMA_NO_CLOUD=1` and logged that cloud was disabled. Streamlit and inference used loopback. With packages and weights installed, the local code requires no account, API key or paid endpoint. Opening GitHub links requires internet access. |
| Tracked content | Pass. The working tree outside dependency environments and tracked filenames had no model-weight or local-log matches. Reachable Git history had no matching model or log paths or blob larger than 10 MB. A common credential-pattern scan of tracked text found no matches. Evaluation transcripts contain only the synthetic prompts and model responses. |
| README | Pass. Records the tested hardware, macOS requirement, setup, offline boundary and the test and evaluation results. |
| Frozen release | Pass. Local and remote `v2.0.0` point to annotated tag object `e59616868d09e84f49d0ceb472d369d172d61b75`, which peels to `ba0365a234d4b0b4bf16bc8aa5ce5049dbf7819a`. Reports, benchmarks and pinned data are identical to the tagged release. No application or tag changes were made. |

Run the automated checks from the repository root.

```sh
.venv/ui/bin/python -B -m unittest discover -s tests -v
.venv/phase7/bin/python -B -m unittest discover -s tests/phase7 -v
```

## Series A · Existing scientific evaluation

### A01 · TP53 restoration

**Exact question.** What happened when researchers restored p53 in EJ carcinoma cells?

**Expected evidence.** Restoration of wild-type p53 in human EJ bladder carcinoma cells caused durable arrest and senescence markers. The three CellAge labels do not establish three separately tested triggers. [GENES-L31-L31](../reports/gene_case_studies.md?plain=1#L31)

**Retrieved in both runs.** `GENES-L31-L31`, `P7B-L9-L16`, `V2-L29-L29`, `V2-L31-L31`

| Run | App status | Selected citation IDs | Response time |
| --- | --- | --- | --- |
| Baseline | `answered` | `GENES-L31-L31` | 6.95 s |
| Prompt trial | `answered` | `GENES-L31-L31` | 4.08 s |

**Baseline. Model output**

> When researchers restored p53 in EJ carcinoma cells, they observed durable G1 and G2/M arrest, DNA synthesis and cell-cycle distribution were measured using BrdU incorporation and DNA-content flow cytometry, and recovery was assessed by colony formation after switching the transgene off. The cells enlarged, stained positive for SA-β-gal, and accumulated lipofuscin-like inclusions, demonstrating that p53 restoration was sufficient for rapid senescence in this tumor model.

**Prompt trial. Model output**

> When researchers restored p53 in EJ carcinoma cells, they observed durable G1 and G2/M arrest, measured DNA synthesis and cell-cycle distribution using BrdU incorporation and flow cytometry, and assessed recovery by colony formation after switching the transgene off. The cells enlarged, stained positive for SA-β-gal, and accumulated lipofuscin-like inclusions. The experiment demonstrated that p53 restoration was sufficient for rapid senescence in this tumor model.

| Review | Baseline | Prompt trial |
| --- | --- | --- |
| Severity | Minor | Minor |
| Factual correctness | Correct model, arrest and markers. | Correct model, arrest and markers. |
| Citation support | Supports the central and supporting claims. | Supports the central and supporting claims. |
| Missing essential context | The three CellAge labels do not establish independent triggers. | Same CellAge label boundary omitted. |
| Overstatement or unsupported claim | None identified. | None identified. |
| Abstention appropriateness | An answer was appropriate. | An answer was appropriate. |

### A02 · TERT in culture

**Exact question.** Did hTERT expression delay replicative senescence or reverse established arrest?

**Expected evidence.** hTERT delayed replicative senescence in human cultures, with at least 20 extra population doublings reported. Reversal of established arrest was not tested. [GENES-L51-L51](../reports/gene_case_studies.md?plain=1#L51)

**Retrieved in both runs.** `GENES-L51-L51`, `GENES-L61-L61`, `P7B-L9-L16`, `P7B-L20-L20`

| Run | App status | Selected citation IDs | Response time |
| --- | --- | --- | --- |
| Baseline | `answered` | `GENES-L51-L51` | 3.03 s |
| Prompt trial | `answered` | `GENES-L51-L51` | 2.99 s |

**Both runs. Model output**

> hTERT expression delayed replicative senescence in these cultures, as the gain-of-function experiment supports this outcome. The study followed growing cells and did not test reversal of established arrest.

| Review | Baseline | Prompt trial |
| --- | --- | --- |
| Severity | Minor | Minor |
| Factual correctness | Correctly distinguishes delay from reversal. | Same correct distinction. |
| Citation support | Supports both central statements. | Supports both central statements. |
| Missing essential context | The at-least-20 additional doublings and specific human cell types were omitted. | Same quantitative and model details omitted. |
| Overstatement or unsupported claim | None identified. | None identified. |
| Abstention appropriateness | An answer was appropriate. | An answer was appropriate. |

### A03 · Missing TERT estimates

**Exact question.** Why are the Phase 7A partial correlations for TERT missing?

**Expected evidence.** TERT failed the expression filter in both cohorts. The analysis did not estimate either partial correlation. [P7A-L17-L17](../reports/phase7_baseline_results.md?plain=1#L17)

**Retrieved in both runs.** `P7A-L17-L17`, `P7B-L22-L22`, `GENES-L51-L51`, `GENES-L53-L53`

| Run | App status | Selected citation IDs | Response time |
| --- | --- | --- | --- |
| Baseline | `answered` | `P7A-L17-L17` | 2.41 s |
| Prompt trial | `answered` | `P7A-L17-L17` | 2.99 s |

**Baseline. Model output**

> The Phase 7A partial correlations for TERT are missing because TERT failed the expression filter in both cohorts, as stated in the primary excerpt.

**Prompt trial. Model output**

> The Phase 7A partial correlations for TERT are missing because TERT failed the expression filter in both cohorts, as stated in the primary excerpt. The study did not report these correlations as they did not meet the threshold for significance in both cohorts with the same direction.

| Review | Baseline | Prompt trial |
| --- | --- | --- |
| Severity | Pass | Critical |
| Factual correctness | Correct reason and cohort scope. | Starts with the correct filter reason, then wrongly attributes the missing TERT values to a significance threshold. |
| Citation support | Directly supports the reason. | Supports filtering and describes the threshold for eligible genes. It does not support a significance result for TERT. |
| Missing essential context | None essential to the question. | The TERT estimates were never made. |
| Overstatement or unsupported claim | None identified. | Confuses missing estimates with measured correlations that failed a test. |
| Abstention appropriateness | An answer was appropriate. | An answer was appropriate, but this explanation is internally inconsistent. |

### A04 · FOXO3 knockdown

**Exact question.** What happened when FOXO3 was knocked down in human dermal fibroblasts?

**Expected evidence.** Stable siRNA knockdown in primary human dermal fibroblasts prolonged doubling time and increased markers including SA-β-gal. The reviewed abstract does not resolve stable arrest or activation effects. [P7D-L16-L16](../reports/phase7d_case_studies.md?plain=1#L16)

**Retrieved in both runs.** `P7D-L16-L16`, `P7D-L41-L41`, `V2-L52-L52`, `V2-L55-L55`

| Run | App status | Selected citation IDs | Response time |
| --- | --- | --- | --- |
| Baseline | `answered` | `P7D-L16-L16` | 2.86 s |
| Prompt trial | `answered` | `P7D-L16-L16` | 2.86 s |

**Baseline. Model output**

> When FOXO3 was knocked down in human dermal fibroblasts, it led to longer population doubling times, altered morphology, more SA-β-gal staining, increased reactive oxygen species, and higher levels of p53 and p21 protein. These changes suggest an inhibitory role for endogenous FOXO3 in this culture model.

**Prompt trial. Model output**

> When FOXO3 was knocked down in human dermal fibroblasts, it led to increased senescence markers, altered morphology, more SA-β-gal staining, reactive oxygen species, and increased p53 and p21 protein expression. These changes support an inhibitory role for endogenous FOXO3 in this culture model.

| Review | Baseline | Prompt trial |
| --- | --- | --- |
| Severity | Minor | Minor |
| Factual correctness | Correct cellular outcomes and model-specific inference. | Correct markers and scoped interpretation. |
| Citation support | Directly supports the claims. | Directly supports the claims. |
| Missing essential context | Stable arrest and the effect of FOXO3 activation remain unresolved. | Omits longer doubling time as well as the arrest and activation boundaries. |
| Overstatement or unsupported claim | None identified. | None identified. |
| Abstention appropriateness | An answer was appropriate. | An answer was appropriate. |

### A05 · FOXO3 follow-up on human longevity

**Exact question.** And what did they find about human longevity?

**Conversation context.** Follows A04 in the same conversation.

**Expected evidence.** In Japanese American men, rs2802292 GG versus TT was associated with greater odds of long-lived case status (OR 2.75, 95% CI 1.51–5.02). The case-control study did not manipulate expression. [P7D-L18-L18](../reports/phase7d_case_studies.md?plain=1#L18)

**Retrieved in both runs.** `P7D-L18-L18`, `P7D-L16-L16`, `V2-L52-L52`, `P7D-L41-L41`

| Run | App status | Selected citation IDs | Response time |
| --- | --- | --- | --- |
| Baseline | `answered` | `P7D-L18-L18` | 3.24 s |
| Prompt trial | `answered` | `P7D-L18-L18` | 3.16 s |

**Baseline. Model output**

> The study found that individuals with the GG genotype of rs2802292 had a significantly higher odds ratio (2.75) of being long-lived compared to those with TT genotype in a nested case-control study of Japanese American men. The findings support a genetic association between FOXO3 and longevity in this population. The study did not test the effects of altering FOXO3 expression directly.

**Prompt trial. Model output**

> The study found that FOXO3 genotype was associated with lower odds of being long-lived in Japanese American men, with an odds ratio of 2.75 for the GG genotype compared to TT. The study did not measure the effect of altering FOXO3 expression, and the outcome was human longevity. The findings are supported by the human link in the GenAge entry and the study's reported odds ratio.

| Review | Baseline | Prompt trial |
| --- | --- | --- |
| Severity | Minor | Critical |
| Factual correctness | Correct direction, odds ratio, population and observational design. | Says lower odds, reversing the reported direction despite quoting OR 2.75. |
| Citation support | Directly supports the answer. | The selected passage contradicts the central direction. |
| Missing essential context | The 95% confidence interval was omitted. | Omits the confidence interval. |
| Overstatement or unsupported claim | None identified. | Inverts the association for GG versus TT. |
| Abstention appropriateness | An answer was appropriate. | An answer was appropriate, but the central result is wrong. |

### A06 · SIRT6 and replicative senescence

**Exact question.** Доказывает ли нокдаун SIRT6 в хондроцитах репликативное старение?

**Expected evidence.** Depletion in cultured human knee chondrocytes increased SA-β-gal positivity and reduced proliferation. The reviewed design did not establish serial-passage exhaustion or persistent arrest after the perturbation. [P7D-L22-L22](../reports/phase7d_case_studies.md?plain=1#L22)

**Retrieved in both runs.** `P7D-L22-L22`, `V2-L53-L53`, `P7D-L24-L24`, `P7D-L41-L41`

| Run | App status | Selected citation IDs | Response time |
| --- | --- | --- | --- |
| Baseline | `answered` | `P7D-L22-L22` | 3.78 s |
| Prompt trial | `answered` | `P7D-L22-L22` | 3.86 s |

**Baseline. Model output**

> Доказывает ли нокдаун SIRT6 в хондроцитах репликативное старение? Нет, так как исследование не подтверждает репликативное старение, а указывает на предварительные изменения, связанные с старением. Измеренный результат - повреждение ДНК, предел вывода - сенесценция.

**Prompt trial. Model output**

> Доказывает ли нокдаун SIRT6 в хондроцитах репликативное старение? Нокдаун SIRT6 в хондроцитах подтверждает репликативное старение по измеренному результату 'повреждение ДНК' и 'сенесценция', но не установляет сохранение теломер длины. Результаты подтверждают наличие репликативного старения, но не подтверждают сохранение теломер длины.

| Review | Baseline | Prompt trial |
| --- | --- | --- |
| Severity | Minor | Critical |
| Factual correctness | Correctly rejects proof of replicative senescence. The reported result was increased DNA damage markers. | Claims that SIRT6 depletion confirmed replicative senescence. |
| Citation support | Supports the central distinction. | The cited passage explicitly limits the findings to premature senescence-associated changes and explains why the replicative subtype is unestablished. |
| Missing essential context | Omits SA-β-gal positivity, reduced proliferation and the specific serial-passage or durable-arrest limitation. | Omits the serial-passage and persistent-arrest limitation. |
| Overstatement or unsupported claim | Imprecise wording treats a marker as the measured damage itself. | Turns short-term markers into proof of a specific subtype. Telomere length is tangential and not established by the cited paragraph. |
| Abstention appropriateness | A qualified answer was appropriate. | A qualified answer was appropriate. The answer should have rejected the inference. |

### A07 · SIRT6 mouse lifespan

**Exact question.** Did overexpressing SIRT6 extend lifespan in mice?

**Expected evidence.** Kanfi et al. reported longer survival for male Sirt6-overexpressing transgenic mice compared with wild type, with no significant extension in females in that experiment. [P7D-L28-L28](../reports/phase7d_case_studies.md?plain=1#L28)

**Retrieved in both runs.** `P7D-L28-L28`, `GENES-L37-L37`, `P7B-L22-L22`, `V2-L53-L53`

| Run | App status | Selected citation IDs | Response time |
| --- | --- | --- | --- |
| Baseline | `answered` | `P7D-L28-L28` | 2.73 s |
| Prompt trial | `answered` | `P7D-L28-L28` | 2.63 s |

**Baseline. Model output**

> Yes, overexpressing SIRT6 extended lifespan in mice, as reported by Kanfi et al. (2012) in transgenic mice, with no significant difference in female mice. This supports the scoped mammalian rationale for the entry.

**Prompt trial. Model output**

> Yes, overexpressing SIRT6 extended lifespan in mice. The study by Kanfi et al. (2012) showed that transgenic mice overexpressing Sirt6 lived longer than wild-type controls in males, with no significant extension in females. This result supports the scoped mammalian rationale for the entry.

| Review | Baseline | Prompt trial |
| --- | --- | --- |
| Severity | Minor | Pass |
| Factual correctness | Correctly reports the mouse finding and no significant female extension. | Correct male result, wild-type comparator and nonsignificant female result. |
| Citation support | Supports the central result. | Directly supports all central claims. |
| Missing essential context | Positive effect in males and the wild-type comparator were not stated explicitly. | None essential. |
| Overstatement or unsupported claim | The opening sentence is broader than the sex-specific result; the next clause qualifies it. | None identified. |
| Abstention appropriateness | An answer was appropriate. | An answer was appropriate. |

### A08 · SIRT6 and GAF 591445

**Exact question.** Does GAF 591445 show that intervening on SIRT6 increases human lifespan?

**Expected evidence.** The cited human study compared natural rs107251 genotypes and age at death. It did not perturb SIRT6 or demonstrate a causal effect on lifespan. [P7D-L26-L26](../reports/phase7d_case_studies.md?plain=1#L26)

**Retrieved in both runs.** `P7D-L26-L26`, `P7B-L22-L22`, `P7D-L30-L30`, `GENES-L37-L37`

| Run | App status | Selected citation IDs | Response time |
| --- | --- | --- | --- |
| Baseline | `answered` | `P7D-L26-L26` | 3.01 s |
| Prompt trial | `answered` | `P7D-L26-L26` | 2.96 s |

**Baseline. Model output**

> No, GAF 591445 does not show that intervening on SIRT6 increases human lifespan. The study reports a variant association with lower age at death but does not establish a functional effect of the variant, perturb SIRT6, or show that SIRT6 determines lifespan.

**Prompt trial. Model output**

> No, GAF 591445 does not show that intervening on SIRT6 increases human lifespan. The study reports a variant association with lower age at death in TT genotype individuals, but the design did not establish a functional effect of the variant, perturb SIRT6, or show that the gene determines lifespan. The outcome is not a proven outcome, and the evidence is limited to a correlation without causal intervention.

| Review | Baseline | Prompt trial |
| --- | --- | --- |
| Severity | Pass | Pass |
| Factual correctness | Correctly distinguishes the genotype association from a human intervention. | Correctly distinguishes the genotype association from a human intervention. |
| Citation support | Directly supports the central distinction. | Directly supports the central distinction. |
| Missing essential context | None essential. | None essential. |
| Overstatement or unsupported claim | None identified. | None identified. |
| Abstention appropriateness | Appropriately rejects the causal inference while answering the question about the record. | Appropriately rejects the causal inference. |

### A09 · TERT human lifespan boundary

**Exact question.** Does TERT help people live longer?

**Expected evidence.** The reports describe culture outcomes and observational markers. They do not establish human lifespan extension from a TERT intervention. [GENES-L51-L51](../reports/gene_case_studies.md?plain=1#L51) · [GENES-L57-L57](../reports/gene_case_studies.md?plain=1#L57)

**Retrieved in both runs.** `GENES-L57-L57`, `GENES-L51-L51`, `GENES-L55-L55`, `GENES-L53-L53`

| Run | App status | Selected citation IDs | Response time |
| --- | --- | --- | --- |
| Baseline | `answered` | `GENES-L57-L57` | 2.68 s |
| Prompt trial | `answered` | `GENES-L57-L57` | 2.84 s |

**Baseline. Model output**

> TERT does not directly prove that people live longer. The study suggests TERT may delay replicative senescence in cultured cells, but it does not establish sustained tissue benefit, cancer safety, or effects on survival in people.

**Prompt trial. Model output**

> TERT does not directly help people live longer, as the study does not establish sustained tissue benefit, cancer safety, or effects on survival in people. The study suggests TERT may delay replicative senescence in cultured cells, but this is not proven to translate to longer lifespan in humans.

| Review | Baseline | Prompt trial |
| --- | --- | --- |
| Severity | Minor | Critical |
| Factual correctness | Correctly declines to infer a human survival effect. | Its first sentence asserts that TERT does not help people live longer. The later qualification describes a lack of evidence. |
| Citation support | Supports the human boundary. The claim specifically about delayed replicative senescence is more directly documented in the uncited Bodnar passage. | The selected passage supports uncertainty about human survival, not a negative effect conclusion. |
| Missing essential context | No essential omission for the human question. | The human effect remains unestablished. |
| Overstatement or unsupported claim | The secondary culture characterization is more specific than the selected passage. | Turns absence of evidence into a negative conclusion in the lead answer. |
| Abstention appropriateness | Appropriate substantive abstention despite the status being answered. | The final clause qualifies the claim, but the lead fails to abstain from an unsupported effect conclusion. |

### A10 · Out of scope in English

**Exact question.** How do I bake sourdough bread?

**Expected evidence.** No relevant passages. The app should decline without calling the model.

**Retrieved in both runs.** None

| Run | App status | Selected citation IDs | Response time |
| --- | --- | --- | --- |
| Baseline | `insufficient_evidence` | None | 0.07 s |
| Prompt trial | `insufficient_evidence` | None | 0.03 s |

**Both runs. Application message, no model call**

> No matching passages in the project reports. Try naming the gene, study or outcome.

| Review | Baseline | Prompt trial |
| --- | --- | --- |
| Severity | Pass | Pass |
| Factual correctness | No scientific claim. | No scientific claim. |
| Citation support | No sources expected. | No sources expected. |
| Missing essential context | None. | None. |
| Overstatement or unsupported claim | None. | None. |
| Abstention appropriateness | Appropriate retrieval abstention. No inference ran. | Appropriate retrieval abstention. No inference ran. |

## Series B · Independent phrasings


### B01 · Overlap and prior publication

**Exact question.** Можно ли считать 113 совпавших генов новым результатом по сравнению с работой Bonnefous?

**Expected evidence.** 113 is the reproduced intersection count, previously reported by Bonnefous et al. Membership equivalence is unverified because eligibility differs and comparable lists were unavailable. [V2-L11-L11](../reports/research_report_v2.md?plain=1#L11) · [V2-L15-L15](../reports/research_report_v2.md?plain=1#L15)

**Retrieved in both runs.** `V2-L17-L17`, `V2-L7-L7`, `V2-L15-L15`, `P7A-L7-L7`

| Run | App status | Selected citation IDs | Response time |
| --- | --- | --- | --- |
| Baseline | `answered` | `V2-L17-L17` | 2.88 s |
| Prompt trial | `answered` | `V2-L17-L17` | 2.99 s |

**Baseline. Model output**

> Нет, 113 совпавших генов не является новым результатом по сравнению с работой Bonnefous. Это результат наблюдения, который был подтверждён в рамках исследования GenAge–CellAge, и не является новым выводом из отдельной работы Bonnefous.

**Prompt trial. Model output**

> Невозможно считать 113 совпавших генов новым результатом по сравнению с работой Bonnefous. Эти гены были уже определены в предыдущих исследованиях, и их совпадение подтверждается данными из отрывка. Результаты из этого отрывка не приводят к новым выводам по сравнению с работой Bonnefous.

| Review | Baseline | Prompt trial |
| --- | --- | --- |
| Severity | Critical | Critical |
| Factual correctness | Correctly rejects novelty of the count, although the phrasing about Bonnefous is unclear. | Correctly rejects novelty of the count but implies that the same individual genes were previously determined. |
| Citation support | The selected GO annotation paragraph contains 113 but does not discuss Bonnefous or novelty. Retrieved V2-L15-L15 or V2-L7-L7 supports the central claim. | The selected GO paragraph still does not support prior publication or membership equivalence. |
| Missing essential context | Independent reproduction of the count and unverified membership equivalence. | Same count does not verify identical membership. |
| Overstatement or unsupported claim | The central statement lacks support from its selected citation. | Implies membership equivalence beyond the report. |
| Abstention appropriateness | An answer was appropriate with the prior-publication evidence. | An answer was appropriate with the prior-publication evidence. |

### B02 · Panel against matched controls

**Exact question.** How did the fixed RNA-seq panel's age-association score compare with the expression-matched panels in the validation analysis?

**Expected evidence.** The cross-cohort score was 0.00464 versus a matched-panel median of 0.00685. The panel did not exceed the prespecified threshold for superiority on this comparison. [V2-L23-L23](../reports/research_report_v2.md?plain=1#L23)

**Retrieved in both runs.** `V2-L21-L21`, `V2-L7-L7`, `V2-L23-L23`, `V2-L25-L25`

| Run | App status | Selected citation IDs | Response time |
| --- | --- | --- | --- |
| Baseline | `answered` | `V2-L23-L23` | 2.13 s |
| Prompt trial | `answered` | `V2-L21-L21` | 2.38 s |

**Baseline. Model output**

> The fixed RNA-seq panel's age-association score did not outperform expression-matched controls in the validation analysis.

**Prompt trial. Model output**

> The fixed RNA-seq panel's age-association score did not outperform expression-matched controls in the validation analysis. The analysis found that the panel did not achieve a stronger reproducible donor-age expression signal than matched genes outside the panel.

| Review | Baseline | Prompt trial |
| --- | --- | --- |
| Severity | Minor | Critical |
| Factual correctness | Correct direction and comparison. Its wording follows the question's validation phrasing. | The direction of the result is correct. |
| Citation support | Supports the cross-cohort comparison and decision. | The selected methods passage states the hypothesis and cohort design. It does not report the score or the result. The outcomes passage was retrieved. |
| Missing essential context | Does not specify that the score combines discovery and validation, or report the numeric comparison. | Cross-cohort score and comparator median omitted. |
| Overstatement or unsupported claim | None identified beyond imprecise scope. | Attributes a central result to a design-only passage. |
| Abstention appropriateness | An answer was appropriate. | An answer was appropriate with an outcomes citation. |

### B03 · FOXO3 experiment versus human genotypes

**Exact question.** Какой вывод о FOXO3 позволяет сделать опыт с фибробластами, а какой — данные по генотипам людей?

**Expected evidence.** Knockdown in cultured dermal fibroblasts increased senescence-associated markers. A separate observational case-control study linked rs2802292 to exceptional longevity in Japanese American men and did not manipulate expression. [P7D-L16-L16](../reports/phase7d_case_studies.md?plain=1#L16) · [P7D-L18-L18](../reports/phase7d_case_studies.md?plain=1#L18)

**Retrieved in both runs.** `P7D-L41-L41`, `P7D-L18-L18`, `V2-L55-L55`, `P7D-L16-L16`

| Run | App status | Selected citation IDs | Response time |
| --- | --- | --- | --- |
| Baseline | `answered` | `P7D-L16-L16` | 4.08 s |
| Prompt trial | `answered` | `P7D-L16-L16` | 4.56 s |

**Baseline. Model output**

> Опыт с фибробластами позволяет сделать вывод о том, что endogenous FOXO3 играет ингибирующее роль в культурном моделировании старения, так как наблюдалось уменьшение экспрессии FOXO3a и изменения в клеточной активности. Данные по генотипам людей не подтверждают или опровергают эффекты изменения уровня FOXO3, так как не тестировали те же гипотезы.

**Prompt trial. Model output**

> Опыт с фибробластами показывает, что FOXO3 играет ингибирующее роль в культурном моделировании, где наблюдается уменьшение экспрессии и увеличение п53 и п21. Данные по генотипам людей не подтверждают или опровергают эффекты, связанные с изменением экспрессии FOXO3, так как они оценивают исходы, связанные с долголетием, но не тестируют саму генетическую модификацию.

| Review | Baseline | Prompt trial |
| --- | --- | --- |
| Severity | Critical | Critical |
| Factual correctness | Gives the broad cell-culture conclusion and notes the design boundary, but fails to report the human association. | Adds p53 and p21 and distinguishes longevity from an expression intervention. Still does not state the genotype association. |
| Citation support | The cited fibroblast excerpt cannot support the central account of human genotype evidence. The relevant human passage was retrieved. | The only citation is again the fibroblast excerpt. |
| Missing essential context | Specific culture readouts and the human association and population. | The human genotype result and population. |
| Overstatement or unsupported claim | Presents a two-part comparison with support for only the cell part. | The human side of the central comparison remains uncited. |
| Abstention appropriateness | An answer covering both parts was possible. | An answer covering both parts was possible. |

### B04 · FOXO3 follow-up on changing expression

**Exact question.** А можно ли по этим данным сказать, что изменение экспрессии этого гена продлит жизнь человеку?

**Conversation context.** Follows B03 in the same conversation.

**Expected evidence.** The culture experiment measured cell outcomes. The human genotype result was observational. Neither establishes that altering FOXO3 expression extends human lifespan. [P7D-L16-L16](../reports/phase7d_case_studies.md?plain=1#L16) · [P7D-L18-L18](../reports/phase7d_case_studies.md?plain=1#L18)

**Retrieved in both runs.** `P7D-L41-L41`, `P7D-L18-L18`, `V2-L55-L55`, `P7D-L16-L16`

| Run | App status | Selected citation IDs | Response time |
| --- | --- | --- | --- |
| Baseline | `answered` | `P7D-L16-L16` | 2.68 s |
| Prompt trial | `answered` | `P7D-L41-L41` | 2.87 s |

**Baseline. Model output**

> Нет, изменение экспрессии гена FOXO3 в фибробластах не подтверждается данными, поскольку они описывают эффекты, вызванные введением изменений, а не результаты генотипических исследований. Данные по генотипам людей не подтверждают, что изменение этого гена продлит жизнь человеку.

**Prompt trial. Model output**

> Нет, изменение экспрессии FOXO3 не подтверждается данными исследований. Исследования с фибробластами показывают, что снижение экспрессии FOXO3 приводит к замедлению старения, но это не подтверждает продление жизни человека. Данные по генотипам людей не подтверждают, что изменение гена продлит жизнь.

| Review | Baseline | Prompt trial |
| --- | --- | --- |
| Severity | Critical | Critical |
| Factual correctness | Declines a human lifespan inference, but the first sentence is misleading about the documented fibroblast manipulation. | Declines human lifespan extrapolation but reverses the culture result by saying reduced FOXO3 expression slowed aging. |
| Citation support | The cell passage supports a culture boundary, but does not support the central assertion about human genotype evidence. | The cited cross-cohort discussion does not support the claimed slowing of aging or the central human-genotype explanation. |
| Missing essential context | The genotype study design and its lack of an expression intervention. | The knockdown increased senescence-associated markers. The human study compared genotypes observationally. |
| Overstatement or unsupported claim | May imply that changing expression in the cell experiment was unconfirmed. | Reverses the effect and generalizes a cellular result to aging. |
| Abstention appropriateness | Declines the unsupported lifespan effect, with a flawed explanation. | Declines the lifespan effect, but supplies an unsupported premise. |

### B05 · SIRT6 culture versus survival

**Exact question.** How do the SIRT6 findings in human knee chondrocytes differ from the survival findings in Sirt6-overexpressing mice?

**Expected evidence.** Nagai depleted SIRT6 in human chondrocyte culture and measured cellular markers and proliferation. Kanfi overexpressed Sirt6 in mice and measured survival, with longer lifespan in males and no significant extension in females. [P7D-L22-L22](../reports/phase7d_case_studies.md?plain=1#L22) · [P7D-L28-L28](../reports/phase7d_case_studies.md?plain=1#L28)

**Retrieved in both runs.** `P7D-L22-L22`, `P7D-L41-L41`, `P7D-L28-L28`, `GENES-L37-L37`

| Run | App status | Selected citation IDs | Response time |
| --- | --- | --- | --- |
| Baseline | `answered` | `P7D-L22-L22` | 3.56 s |
| Prompt trial | `answered` | `P7D-L22-L22` | 3.81 s |

**Baseline. Model output**

> The SIRT6 findings in human knee chondrocytes show premature senescence-associated changes after depletion, with increased SA-β-gal positivity, p16, and DNA damage markers, and reduced proliferation. In contrast, the survival findings in Sirt6-overexpressing mice demonstrate extended lifespan in males but not in females. The human studies measure cellular changes after depletion, while the mouse studies measure survival outcomes in a transgenic model.

**Prompt trial. Model output**

> The SIRT6 findings in human knee chondrocytes show premature senescence-associated changes after depletion, as indicated by increased SA-β-gal positivity, p16, and DNA damage markers, with reduced proliferation. In contrast, the survival findings in Sirt6-overexpressing mice demonstrate extended lifespan in males but not in females, as reported by Kanfi et al. The human study focuses on cellular changes after SIRT6 depletion, while the mouse study evaluates survival outcomes in a transgenic model.

| Review | Baseline | Prompt trial |
| --- | --- | --- |
| Severity | Critical | Critical |
| Factual correctness | Correctly separates the interventions, models and outcomes. The female result should be phrased as no significant extension. | Again gives the correct contrast and attributes the mouse result to Kanfi. The female result remains too categorical. |
| Citation support | The selected chondrocyte excerpt does not support the central mouse-survival claim. P7D-L28-L28 was retrieved but not cited. | Still cites only the chondrocyte passage. |
| Missing essential context | Qualification on the female comparison. | Qualification on the female comparison. |
| Overstatement or unsupported claim | The mouse half of the answer is uncited. | Naming Kanfi in the prose does not supply the missing mouse source card. |
| Abstention appropriateness | An answer covering both experiments was possible. | An answer covering both experiments was possible. |

### B06 · Interpretation of empty TERT cells

**Exact question.** В таблице Phase 7A для TERT пустые значения. Их надо читать как нулевую корреляцию?

**Expected evidence.** A blank is not zero. TERT failed expression eligibility in both cohorts and neither partial correlation was estimated. [P7A-L7-L7](../reports/phase7_baseline_results.md?plain=1#L7) · [P7A-L17-L17](../reports/phase7_baseline_results.md?plain=1#L17)

**Retrieved in both runs.** `P7A-L17-L17`, `P7B-L22-L22`, `GENES-L51-L51`, `GENES-L53-L53`

| Run | App status | Selected citation IDs | Response time |
| --- | --- | --- | --- |
| Baseline | `answered` | `P7A-L17-L17` | 2.42 s |
| Prompt trial | `answered` | `P7A-L17-L17` | 2.63 s |

**Baseline. Model output**

> Да, значения пустые в таблице Phase 7A для TERT следует считать нулевой корреляцией.

**Prompt trial. Model output**

> В таблице Phase 7A для TERT пустые значения следует читать как нулевую корреляцию, так как они не измерены.

| Review | Baseline | Prompt trial |
| --- | --- | --- |
| Severity | Critical | Critical |
| Factual correctness | Incorrectly says to read missing values as zero. | Still explicitly equates missing values with zero, even while saying they were unmeasured. |
| Citation support | The cited passage says TERT failed the expression filter. It contains no measured zero. | The selected source still does not support zero. |
| Missing essential context | No estimate in either cohort. | The reason was expression-filter ineligibility in both cohorts. |
| Overstatement or unsupported claim | Presents a zero correlation where no value was measured. | Still fabricates a numerical interpretation for an absent value. |
| Abstention appropriateness | A direct correction of the premise was possible. | A direct correction of the premise was possible. |

### B07 · Unsupported human SIRT6 treatment estimate

**Exact question.** Can a clinician tell a patient how many extra years they would gain from SIRT6 treatment based on these reports?

**Expected evidence.** No human SIRT6 intervention in the reviewed evidence establishes years of life gained. The human genotype study and the mouse intervention cannot supply a patient treatment estimate. [P7D-L26-L26](../reports/phase7d_case_studies.md?plain=1#L26) · [P7D-L28-L28](../reports/phase7d_case_studies.md?plain=1#L28)

**Retrieved in both runs.** `GENES-L37-L37`, `P7D-L26-L26`, `P7D-L22-L22`, `P7D-L24-L24`

| Run | App status | Selected citation IDs | Response time |
| --- | --- | --- | --- |
| Baseline | `insufficient_evidence` | None | 2.12 s |
| Prompt trial | `answered` | `GENES-L37-L37` | 3.02 s |

**Baseline. Model output**

> No, a clinician cannot determine how many extra years a patient would gain from SIRT6 treatment based on the provided reports.

**Prompt trial. Model output**

> No, a clinician cannot tell a patient how many extra years they would gain from SIRT6 treatment based on these reports. The reports do not provide measured outcomes related to lifespan extension or age gain from SIRT6 treatment. The evidence is limited to animal models and does not include human data or measurable outcomes for patients.

| Review | Baseline | Prompt trial |
| --- | --- | --- |
| Severity | Pass | Critical |
| Factual correctness | Correctly declines to estimate years gained. | Correctly declines to estimate years gained, then falsely says the evidence contains no human data. |
| Citation support | No passage is cited and the reply makes no positive scientific claim. | The selected mouse passage cannot support absence of human data. The retrieved SIRT6 genotype and human chondrocyte passages contradict that claim. |
| Missing essential context | None essential to the requested estimate. | Human observational and cell-culture evidence exists; a human treatment survival outcome is missing. |
| Overstatement or unsupported claim | None identified. | Materially misstates the evidence base used to justify the refusal. |
| Abstention appropriateness | Appropriate in-corpus abstention. | Appropriately declines a number, but the scientific explanation is wrong. |

### B08 · Human rs107251 association

**Exact question.** Как интерпретировать связь rs107251 с возрастом смерти, если сравнивались группы людей с разными генотипами?

**Expected evidence.** Natural genotype groups differed in adjusted age at death. The small TT group had lower adjusted mean age at death than CC and CT. The comparison is observational and does not demonstrate a functional or intervention effect. [P7D-L26-L26](../reports/phase7d_case_studies.md?plain=1#L26)

**Retrieved in both runs.** `P7D-L26-L26`, `GENES-L63-L63`, `P7D-L18-L18`, `P7D-L41-L41`

| Run | App status | Selected citation IDs | Response time |
| --- | --- | --- | --- |
| Baseline | `answered` | `P7D-L26-L26` | 4.01 s |
| Prompt trial | `answered` | `P7D-L26-L26` | 3.71 s |

**Baseline. Model output**

> Связь rs107251 с возрастом смерти показана как реальное результат, но дизайн исследования не установил функционального эффекта гена, не изменяющего SIRT6, и не показал, что ген определяет возраст смерти. Сравнение групп людей с разными генотипами не подтверждает или опровергает эффекты, измеренные в Phase 7A.

**Prompt trial. Model output**

> Связь rs107251 с возрастом смерти показана как реальное результат, но дизайн исследования не установил функциональное влияние гена на возраст смерти. В группе с генотипом TT возраст смерти был на 5.5 года ниже, чем в группе CC, но это не подтверждает или опровергает эффекты, связанные с введением в исследование.

| Review | Baseline | Prompt trial |
| --- | --- | --- |
| Severity | Minor | Minor |
| Factual correctness | Conveys the observational boundary but is difficult to read. | Correct direction and 5.5-year difference for TT versus CC. Rejects a functional inference. |
| Citation support | Supports the central association and lack of causal evidence. The added Phase 7A comparison is not stated in this passage. | Supports the central claims. |
| Missing essential context | Which genotype had lower adjusted age at death is omitted. | Does not describe the difference as an adjusted mean or give the TT sample size and CT comparison. |
| Overstatement or unsupported claim | Adds an unnecessary comparison to Phase 7A. | The final clause about an intervention is awkward and vague. |
| Abstention appropriateness | An answer was appropriate. | An answer was appropriate. |

### B09 · RNA-seq eligibility and endpoint

**Exact question.** How many of the original panel genes were eligible in both RNA-seq cohorts, and what did that comparison actually measure?

**Expected evidence.** 109 of 113 genes were eligible in both cohorts. Phase 7A estimated expression associations with donor chronological age. The 63 is the number with matching directions among the 109. [V2-L21-L21](../reports/research_report_v2.md?plain=1#L21) · [V2-L23-L23](../reports/research_report_v2.md?plain=1#L23)

**Retrieved in both runs.** `V2-L7-L7`, `V2-L21-L21`, `V2-L61-L61`, `V2-L23-L23`

| Run | App status | Selected citation IDs | Response time |
| --- | --- | --- | --- |
| Baseline | `answered` | `V2-L23-L23` | 2.50 s |
| Prompt trial | `answered` | `V2-L23-L23` | 3.48 s |

**Baseline. Model output**

> 63 out of 109 original panel genes were eligible in both RNA-seq cohorts, and the comparison measured the partial Pearson correlations of expression abundance and detection across the cohorts.

**Prompt trial. Model output**

> 63 out of 109 original panel genes were eligible in both RNA-seq cohorts. The comparison measured the partial Pearson correlations of expression abundance and detection across the two cohorts, adjusting for sex and sequencing platform. The target value (0.00464 for the panel and 0.00685 at the median) fell below the matched 95th-percentile cutoff of 0.01034.

| Review | Baseline | Prompt trial |
| --- | --- | --- |
| Severity | Critical | Critical |
| Factual correctness | Incorrectly reports 63 eligible genes out of 109 original genes and misidentifies the endpoint. | Repeats the wrong denominator and endpoint. Quotes the cross-cohort score and threshold accurately but adds them to an incorrect answer. |
| Citation support | V2-L23-L23 gives 63/109 for sign agreement. It does not support the asserted count or expression-abundance/detection endpoint. | The source supports the scores and matching description, not the central answer. The eligibility passage was retrieved. |
| Missing essential context | 109 of 113 and donor chronological age. Expression abundance and detection were used for matching. | 109 of 113 and donor chronological age. |
| Overstatement or unsupported claim | Reassigns the count and the measured endpoint to different quantities. | Reassigns the count and endpoint, and attributes the adjustment to the wrong formulation of the measure. |
| Abstention appropriateness | An answer was possible from the retrieved cohort-design and outcome passages. | An answer was possible from the retrieved cohort-design and outcome passages. |

### B10 · Out of scope in Russian

**Exact question.** Как пересадить орхидею после цветения?

**Expected evidence.** No relevant passages. The app should decline without calling the model.

**Retrieved in both runs.** None

| Run | App status | Selected citation IDs | Response time |
| --- | --- | --- | --- |
| Baseline | `insufficient_evidence` | None | 0.04 s |
| Prompt trial | `insufficient_evidence` | None | 0.03 s |

**Both runs. Application message, no model call**

> В отчётах проекта не найдено подходящих фрагментов. Уточните ген, исследование или показатель.

| Review | Baseline | Prompt trial |
| --- | --- | --- |
| Severity | Pass | Pass |
| Factual correctness | No scientific claim. | No scientific claim. |
| Citation support | No sources expected. | No sources expected. |
| Missing essential context | None. | None. |
| Overstatement or unsupported claim | None. | None. |
| Abstention appropriateness | Appropriate retrieval abstention. No inference ran. | Appropriate retrieval abstention. No inference ran. |
