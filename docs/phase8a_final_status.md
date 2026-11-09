# Phase 8A final status and handoff

The reproducible scientific analysis is complete and preserved in the immutable `v2.0.0` release. Phase 8A completed the local Ollama integration. Local AI remains **Experimental** and **NOT READY** for a stable release. [Final scientific report](../reports/research_report_v2.md) · [Live evaluation](phase8a_multistudy_reliability.md)

## Completed capabilities

| Mode | Scope and recommended use |
| --- | --- |
| **Research Q&A** | Deterministic Phase 7C lookup for focused English questions about the Phase 7A RNA-seq panel and the TP53, CDKN2A and TERT evidence audit. Use it to check a reported result, including whether a coefficient was estimated. |
| **Evidence records** | Deterministic Phase 7D lookup for exact ledger records and PMIDs. Use `cellage` and `association` with FOXO3 or SIRT6 to inspect the corresponding perturbation and association records. |
| **Local AI — Experimental** | Search project excerpts in Russian or English and use them to guide reading. Some scoped queries return deterministic answers. Other supported queries can generate an answer using `qwen3:1.7b` through local Ollama. |

The deterministic modes evaluate each question independently and work without Ollama. Local AI searches the [consolidated scientific report](../reports/research_report_v2.md), the [TP53, CDKN2A and TERT case studies](../reports/gene_case_studies.md), the [FOXO3 and SIRT6 case studies](../reports/phase7d_case_studies.md), the [Phase 7A RNA-seq results](../reports/phase7_baseline_results.md) and the [Phase 7B evidence audit](../reports/phase7b_evidence_audit.md). Once dependencies and model weights are installed, inference and excerpts are available offline. Published GitHub source links require internet access. [Setup](../README.md#local-ai--experimental)

## Scientific scope

- The pinned GenAge Human and CellAge snapshots reproduce a previously published overlap count of 113 genes. Differences in eligibility and the absence of comparable gene-level lists leave membership equivalence unverified. [Prior work and comparison](related_work.md#bonnefous-et-al-2024)
- The fixed panel did not outperform expression-matched controls on the prespecified cross-cohort test of donor-age associations in cultured human fibroblasts. Of the 113 panel genes, 109 were eligible in both cohorts and 63 of those had concordant association signs. TERT failed the expression filter in both cohorts, so neither partial correlation was estimated. [Phase 7A results](../reports/phase7_baseline_results.md)
- The evidence audit distinguishes gene function, cell-culture perturbations, observational human genotype associations and animal survival interventions. A cell or mouse endpoint or a human genotype association cannot establish the effect of a human lifespan intervention. [Evidence audit](../reports/phase7b_evidence_audit.md) · [FOXO3 and SIRT6 case studies](../reports/phase7d_case_studies.md)

## Evaluation and limitations

The latest live evaluation used the Streamlit adapter with Ollama 0.40.15 serving `qwen3:1.7b` (model ID `8f68893c685c`) with cloud features disabled.

| Evaluation | Pass | Minor | Critical | Execution |
| --- | ---: | ---: | ---: | --- |
| Frozen 20-case replay | 11 | 9 | 0 | 11 Ollama calls, seven deterministic replies and two abstentions before inference |
| Untouched bilingual holdout | 4 | 0 | 1 | Four deterministic replies and one Ollama call |

The frozen cases checked previously identified failure modes. Their minor issues include omitted numerical detail or experimental qualifications. The five holdout questions were kept separate from the corrections and came from the same evaluator. The set is too small to estimate general reliability. [Frozen replay](phase8a_multistudy_reliability.md#frozen-20-case-replay) · [Untouched bilingual holdout](phase8a_multistudy_reliability.md#untouched-bilingual-holdout)

H04 asked how many years FOXO3 activation would add to a human lifespan. The model gave no numerical estimate, but it attributed a cultured-cell effect to activation and categorically denied a human lifespan benefit. Its sole citation, `P7D-L16-L16`, describes FOXO3 knockdown in cultured fibroblasts. It tested neither activation nor a human lifespan intervention. A valid source ID identifies a passage. It does not verify that the passage supports the claim. [H04 answer and review](phase8a_multistudy_reliability.md#h04--critical)

Use the deterministic modes for supported lookups and inspect the cited rows or report lines when recording a finding. Treat generated prose as a reading aid. Open **Retrieved evidence** and check the organism or population, intervention or exposure, endpoint and numerical values against each claim. Leave an estimate or conclusion unresolved when the source cannot support it.

## Verification

All 85 application tests and all eight Phase 7 tests passed in their respective environments. Run from the repository root after installing the dependencies in the [UI environment](../README.md#launch-web-chat) and the [Phase 7 environment](../reports/phase7_data_feasibility.md#provenance-reuse-and-reproduction).

```sh
.venv/ui/bin/python -B -m unittest discover -s tests -v
.venv/phase7/bin/python -B -m unittest discover -s tests/phase7 -v
```

The historical release audit preserves the baseline and rejected prompt trial. The latest live evaluation records the final replay and the holdout, including source IDs and the H04 answer. [Historical release audit](phase8a_release_readiness.md) · [Latest live evaluation](phase8a_multistudy_reliability.md)

## Remaining research opportunities and versioning

- Replicate the fixed-panel association test in an independent cohort with comparable expression quantification and measured culture covariates. Test whether SIRT6 depletion changes serial population doublings and whether arrest persists after the perturbation ends. [Scientific follow-up](../reports/research_report_v2.md#open-questions-and-proposed-experiments)
- If a later phase revisits Local AI release readiness, use a larger, independently authored and reviewed bilingual holdout. Test whether answers distinguish opposite perturbations and whether each source supports the claim it is cited for.

Close Phase 8A as an experimental handoff. Retain `v2.0.0` as the scientific release and defer `v2.1.0` and any release candidate. No implementation work remains for this handoff. A stable Local AI release still requires resolving the H04 failure and passing a new release evaluation.
