# Phase 7B | Research Q&A benchmark results

The deterministic lookup returned the expected facts, source IDs and evidence type on **21 of 22 questions**. It abstained correctly on all six questions that called for insufficient evidence or an unmeasured endpoint. It also abstained on one answerable question whose wording it could not route.

| Metric | Correct / total | Rate |
| --- | ---: | ---: |
| Correct answer, including status and structured facts | 21 / 22 | 95.5% |
| Exact citation ID match per question | 21 / 22 | 95.5% |
| Evidence-type classification | 21 / 22 | 95.5% |
| Correct abstention on evidence-limited questions | 6 / 6 | 100% |
| False abstention on answerable questions | 1 / 16 | 6.25% |

The six expected abstentions comprise four `insufficient_evidence` and two `not_measured` cases. This counts the TERT correlation as unestimated, rather than a zero effect. In contrast, the p14ARF case is answerable: the paper reported growth arrest and did not detect increased SA-β-gal in the specified cells. Its endpoint was measured.

## Failure review

- **Q21, paraphrase.** “How often did the direction of the signal stay the same across the two cohorts?” The reference is 63/109 (57.8%) in the [Phase 7A association section](phase7_baseline_results.md#independent-association-analysis). The lookup recognizes the short term “sign agreement” but did not route this paraphrase. It returned `unsupported_question`, cited scope sources instead of the required association reference alone, and classified the response as a scope assessment. This missed the answer, citation and evidence type without making up a result.
- **Q17, Q18 and Q20, corrected during development.** The first run used the default `answered` status even though the prose correctly said evidence was insufficient. Explicit status checks identified these inconsistencies; all three now return `insufficient_evidence` with `abstains: true`. The reference answers were unchanged. Before the fixes the score was 18/22 for answers and 3/6 for abstentions; citation and evidence-type scores were unchanged.

The [reference set](../benchmarks/phase7b_questions.json) was checked against the source material separately from writing the lookup. The CLI does not load it. The [protocol](../docs/phase7b_evidence_protocol.md#reference-answers-and-scoring) defines the denominators and exact-match rules. The published rates are for the development set after corrections. One author performed the source check and compared the emitted prose and locators with the reference notes; there was no independent human adjudication, held-out sample, or statistical comparison. Several questions share data and Q21 checks the same fact as Q03. These rates cannot be extrapolated to unseen genes, publications or question wording.

```sh
python3 -B -m scripts.phase7b_score
```

The JSON contains each actual output and its pass/fail flags. Review full responses as well as the scores: exact source IDs can be tested automatically, but an ID match alone does not establish that every sentence is supported.

## What the prototype adds

The lookup makes it easier to trace claims to their original rows, find PMID reuse without collapsing distinct annotations, and distinguish missing endpoints from measured negatives. The [audit](phase7b_evidence_audit.md) shows why seven CellAge rows cannot be treated as seven independent publications. A source-checked ledger also lets reviewers identify a citation that does not support a particular GO claim without discarding the original annotation.

Training a model or adding a local LLM is not justified by this benchmark. The observed remaining failure is query phrasing, while evidence scope and citation fidelity are the central constraints. A useful next comparison would use new paraphrases and mixed-evidence questions written by a second reviewer, alongside a structured lookup or small synonym map. Evaluate any later language interface against that held-out set with the same evidence and abstention requirements.
