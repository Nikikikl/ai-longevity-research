# Phase 7C generalization and robustness protocol

How reliably does the Phase 7B lookup answer unfamiliar English questions about its existing evidence? The unit of analysis is a prompt. Phase 7B's 21/22 score describes its development set. The Phase 7C comparison uses the same evidence corpus and two query interfaces.

## Freeze and split

- Baseline commit `ea6a10d759f5ba773cf51550fc802c3d5e3800b6`. The SHA-256 of `scripts/phase7b_qa.py` is `6f099b4df3fe3a9e782cb7f5912e5a6c0020b776555cc3411b518979987f7a19`. The evaluator checks this digest before running the baseline.
- [New benchmark](../benchmarks/phase7c_questions.json) SHA-256 `956bbd50e3ba95ef0eda6597f14f9a0e7a57732cf9f55fb2216f07f9bf87a86e`. The questions, split and references were fixed before evaluating either method. D01–D08 are development prompts. H01–H24 are the final held-out prompts.
- Author the references from the pinned CellAge Build 3 TSV, GO GAF, Phase 7A association rows and report, and cited papers. Record exact reference IDs using the [Phase 7B convention](phase7b_evidence_protocol.md#reference-answers-and-scoring). Scope assessments also use the Phase 5A review boundary and shared-gene table. One author set the questions and reviewed the answers. No external reviewer participated.
- Run the untouched baseline on both splits. Examine only the development output before coding. Save the held-out output and record its digest without opening it. Select a small change based on the development failures and debug with the development split and separate regression fixtures. Fix the candidate code before scoring its held-out output and opening the baseline held-out output. Treat any further tuning as work for a new evaluation.

This split holds out prompts from debugging and evaluation feedback. The question author also implemented the candidate, so the wording was not blinded from that person. The split holds neither evidence records nor topics out of the system. The prompts share facts, and the scores characterize this constructed set.

## Scoring

Use the [Phase 7B scorer](../scripts/phase7b_score.py) for both methods. Correct answers require exact structured facts and status, the correct abstention flag, and nonempty prose and limitations. Exact citation match compares the complete set of IDs per prompt, including multiplicity. Evidence-type labels are scored separately. Correct abstentions are divided by questions whose references require `not_measured` or `insufficient_evidence` and must match the specific status. False abstentions are divided by answerable prompts. An `unsupported_question` response does not earn credit for an evidence-based abstention.

Review the prose, facts and cited locations for every output from both methods. Mark a response as containing an unsupported assertion if it states or clearly attributes a result, mechanism, experiment or provenance that the cited material cannot establish as stated. Count responses with at least one such assertion and report them over all prompts. A supported statement about the wrong endpoint is a relevance error and earns no answer credit. A generic abstention with scope links may miss the correct citations and does not assert a biological result. Record the adjudication and any disagreements with the automatic scores in the report. This check is manual and depends on reviewer judgment.

Run from the repository root with Python 3.11 or newer:

```sh
python3 -B -m scripts.phase7c_score baseline development
python3 -B -m scripts.phase7c_score baseline heldout
python3 -B -m scripts.phase7c_score candidate heldout
```
