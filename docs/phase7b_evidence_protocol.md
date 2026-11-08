# Phase 7B | Evidence integrity and research Q&A protocol

**Research question:** Can an evidence-grounded system distinguish independent experimental support from repeated database references, while correctly answering biological questions and abstaining when data are insufficient?

This is a small development benchmark for a deterministic lookup, based on the project state at commit `c421ddb06545b1fb7de84507c6a661c72533e825`. The literature audit covers TP53 (7157), CDKN2A (1029) and TERT (7015) only. The other 110 shared genes remain eligible for Phase 7A numerical lookups; they have no comparable manual literature review here.

## Sources and units of evidence

- **CellAge Build 3 (2023-04-23):** original one-based data ordinal in `cellage3.tsv` from the pinned [archive](../data/raw/cellAge.zip.json). Type, cancer-cell flag and effect are curated fields. They are distinct from what an investigator manipulated or measured.
- **GO Biological Process (archive 2026-08-05; ontology version 2026-07-26):** direct, positive rows selected by Phase 5A from the [Phase 4 table](../reports/go_gene_annotations.csv). The [manifest](../data/go_provenance.json) identifies the pinned GAF; line numbers include headers. Keep accession, product form, GO term, relation, evidence code and reference. A GO evidence code describes the basis of an annotation. It does not classify a human intervention or replicate an assay.
- **Review of primary studies:** carry forward the [Phase 5A matrix](../reports/gene_evidence_matrix.csv) and its review depths. Bibliographic verification establishes citation identity. Abstracts support only details visible there. Full text and publisher methods/results support the documented methods or measurements in their specific models. The focused checks use the original papers cited in the [audit](../reports/phase7b_evidence_audit.md).
- **Phase 7A:** use the [association ledger](../reports/phase7_gene_associations.csv), [results](../reports/phase7_baseline_results.md) and a [small projection of the generated metrics](../data/phase7b_metrics.json). Counts, signs and threshold passes come from the CSV; donor sizes, permutation results and prediction errors come from the aggregate projection. Neither is an intervention dataset.

The ledger has one row per original record or GAF line, with the curated claim and reviewed result in separate columns. Group identical PMIDs across those rows and report source and gene coverage. Exclude GO method references from PMID counts. Keep separate claims even when they share a paper. Mark a common reported assay, common study or distinct perturbation only when the reviewed study descriptions establish it; leave other relationships `not_assessed`. Two PMIDs can share data, and one PMID can describe multiple experiments. There is no automatic evidence-strength score or statistical independence claim.

## Query and answer contract

Run from the repository root with Python 3.11 or newer; Phase 7B needs only the standard library and tracked files.

```sh
python3 -B -m scripts.phase7b_qa 'Where is PMID 9454332 cited across CellAge and GO in the audit?'
python3 -B -m scripts.phase7b_qa 'Which CellAge records list CDKN2A?'
python3 -B -m scripts.phase7b_qa 'experiment 7157'
python3 -B -m scripts.phase7b_qa 'What were the Phase 7A partial correlations for TERT?'
```

The interface handles one narrow English lookup at a time. Recognized forms include `cited PMID <number>`, a CellAge record question with a gene symbol or Entrez ID, `experiment <gene>`, Phase 7A partial correlation questions with a panel gene, and short prompts with terms such as “sign agreement”, “replication score” or “Ridge MAE”. A small set of source checks covers specified claims such as the Egan and Collins recombination attribution. It does not interpret arbitrary wording, resolve compound requests, or retrieve new papers.

JSON includes `answer`, machine-checkable `facts`, `evidence_type`, `references`, `limitations`, `status` and `abstains`. An answer can report a negative measurement (`answered`). Use `not_measured` for an untested endpoint or a missing estimate, `insufficient_evidence` for a scoped claim the sources cannot establish, and `unsupported_question` for a lookup the interface could not route. All three non-answer statuses explicitly abstain. In the last case the references describe scope, not the requested claim.

## Reference answers and scoring

The [22 questions and reference answers](../benchmarks/phase7b_questions.json) were written and checked against the original pinned rows, earlier numerical results and the cited papers or abstracts before writing the lookup. Each item records a prose reference answer, exact expected source IDs, structured facts, evidence type and status. Reference answers were manually source-checked separately from the CLI implementation; no outside reviewer adjudicated them. The CLI does not read the benchmark. Cases and lookup share the same small source corpus, and fixes were made after an initial run. Treat the resulting score as development evidence, not as a held-out generalization estimate.

Reference IDs resolve as follows:

| Prefix | Location |
| --- | --- |
| `CellAge:` | Original CellAge Build 3 data ordinal; see the ledger for the archive and member |
| `GAF:` | Original decompressed GAF line; see the ledger and Phase 4 annotation CSV |
| `PMID:` | Publication entry and reviewed text link in the ledger |
| `P7A:association`, `P7A:prediction` | Named sections of the [Phase 7A results](../reports/phase7_baseline_results.md) |
| `P7A:gene:`, `P3:gene:` | Entrez ID in the [association CSV](../reports/phase7_gene_associations.csv) or [shared gene CSV](../reports/gene_overlap_genes.csv) |
| `P5A:scope`, `P5A:comparison` | Named sections of the [case studies](../reports/gene_case_studies.md) |

The [scorer](../scripts/phase7b_score.py) compares status, abstention flag and exact structured facts for answer correctness, and checks that the answer and limitations are present. It compares the complete set of expected source IDs per question; missing, extra or duplicate IDs fail the citation check. Evidence type is scored separately. Correct abstention uses only questions whose reference requires `insufficient_evidence` or `not_measured` and requires the specific status plus an explicit abstention flag. False abstentions use only answerable questions. The automated check does not establish textual entailment. Read the output alongside the reference answers and source rows to check prose and actual citation locators.

## Related work

[Gao et al. (2023), ALCE](https://doi.org/10.18653/v1/2023.emnlp-main.398) evaluate answer correctness and citation quality separately in text generation. [Asai et al. (2026), OpenScholar](https://doi.org/10.1038/s41586-025-10072-4) evaluate retrieval and citation in scientific synthesis. [Zhavoronkov et al. (2026), LongevityBench](https://pubmed.ncbi.nlm.nih.gov/42753698/) evaluate models on a broader suite of tasks in aging biology. Phase 7B uses a fixed local corpus and exact provenance instead of generated synthesis. It does not claim a new scientific finding or compare its scores directly with those benchmarks.
