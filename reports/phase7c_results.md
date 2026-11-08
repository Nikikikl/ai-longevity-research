# Phase 7C generalization and robustness results

Terminology normalization raised exact answer accuracy from **5/24 (20.8%)** to **18/24 (75.0%)** on the held-out prompts. Thirteen prompts moved from incorrect to correct, five remained correct and six remained incorrect. Both methods used the same evidence corpus and scorer. See the [frozen protocol](../docs/phase7c_evaluation_protocol.md) and [32 questions with source-checked references](../benchmarks/phase7c_questions.json).

| Held-out metric | Frozen Phase 7B | Normalized lookup |
| --- | ---: | ---: |
| Correct answers | 5/24 (20.8%) | 18/24 (75.0%) |
| Exact citation ID matches | 5/24 (20.8%) | 18/24 (75.0%) |
| Correct evidence type | 9/24 (37.5%) | 21/24 (87.5%) |
| Correct abstentions | 2/10 (20.0%) | 6/10 (60.0%) |
| False abstentions on answerable prompts | 11/14 (78.6%) | 2/14 (14.3%) |
| Responses with unsupported assertions, manual review | 0/24 | 0/24 |

On the eight development prompts, answers and citations each rose from 1/8 to 7/8, evidence-type matches from 3/8 to 7/8, and correct abstentions from 0/3 to 2/3. False abstentions fell from 4/5 to 0/5. Both development runs had 0/8 responses with unsupported assertions. The untouched baseline also reproduced the original Phase 7B development score of 21/22.

## What changed

The initial development failures clustered around synonyms for genes, database names, publication IDs, statistical terms and the scope of the review. The [normalizer](../scripts/phase7c_qa.py) maps common variants to the existing lookup vocabulary. It resolves p53 as TP53 for the applicable gene lookup and keeps the p16 and p14ARF products distinct. It applies the same citation, evidence and answer logic as Phase 7B. D08 remained a generic abstention because there is no handler for a direct question about unmeasured external prediction performance.

On the held-out split, the new interface recovered cohort sign agreement (H01), alternative gene and source labels (H02–H08), the measured negative for p14ARF (H11), the audit boundary for FOXO3 (H17), the q-value threshold (H21), the repeated p53 trigger premise (H22) and a PMID absent from the audit (H24). For example, H07 now finds CellAge 845 and GAF lines 27897 and 27918 for one Bodnar study. H04 reports missing TERT estimates and cites the association ledger. [Phase 7B evidence ledger](phase7b_evidence_ledger.csv), [Phase 7A association ledger](phase7_gene_associations.csv), [Bodnar et al.](https://doi.org/10.1126/science.279.5349.349)

| Prompt | Remaining failure in both methods | What the reference requires |
| --- | --- | --- |
| H09 | False abstention on a compound comparison | Compare the 63/109 cohort sign matches with TP53's opposite signs. |
| H12 | Generic abstention for an unmeasured culture endpoint | Bodnar tested delayed senescence in growing cultures. Reversal of stable arrest was untested. |
| H14 | Generic abstention for a compound source and longevity question | Cite the Bodnar culture study and explain why its endpoint cannot establish human survival. |
| H18 | False abstention on a comparison across endpoints | TERT has no eligible Phase 7A estimate. CellAge and Bodnar address a different endpoint. |
| H19 | Generic abstention for unmeasured external prediction | Phase 7A measured prediction error within discovery only. |
| H23 | Generic abstention on a compound scope and survival premise | BRCA1 is outside the manual audit, which supplies no human survival result for the proposed intervention. |

Each of these responses used `unsupported_question` and gave scope references. Those references missed the required source IDs on all six prompts. In H14, H18 and H23 the generic scope label coincided with the expected evidence type. The correct-abstention metric requires the specific expected status. Manual review of the emitted claims, facts and source locations found no unsupported assertion in either run.

## Reproduction and decision

The baseline held-out JSON was saved before editing the query interface and opened after the candidate was fixed. Its SHA-256 is `4f3763f65a378b0adee2274fc19d632a74c2dcebe3fa7d1d388047fec96e90da`. The candidate source SHA-256 before the final run was `c43fcb0ffb5cc4944e265b7af15b92dfa8d5ac886b3d41f639e51b269b8cc823`. The final candidate JSON SHA-256 is `36ab96e55acc8239fcd056799aee6327f26ad7de6a9df1c122f2d8d5beec3aa8`. The [evaluator](../scripts/phase7c_score.py) emits the response and all automated flags for each prompt.

```sh
python3 -B -m scripts.phase7c_score baseline heldout
python3 -B -m scripts.phase7c_score candidate heldout
```

The gain covers unfamiliar wording for existing lookup tasks. The 24 final prompts were selected by one author, share evidence and topics with the development prompts, and were not independently reviewed. The evaluation does not establish reliability for arbitrary scientific questions or performance on new evidence.

**Decision C — Expand the manually audited scientific evidence.** The lookup now handles more names and phrasings. Its six remaining misses include synthesis across endpoints and a claim outside the three-gene review. A language interface could help express some questions, but additional reviewed experiments and explicit endpoint links would directly extend the scientific claims the system can support. These results do not justify adding an LLM.
