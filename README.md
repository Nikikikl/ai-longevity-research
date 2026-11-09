# AI & Longevity Research

This project asks what public gene records and experiments can tell us about human aging. We compared two
databases, tested whether genes shared by both had a stronger age-related signal in two studies of human
cells, and traced selected claims back to what researchers measured. You can explore those results with a
small research assistant that runs on your computer.

[Read the research story](docs/START_HERE.md) · [Try the assistant locally](docs/TRY_ASSISTANT.md) · [Read the scientific report](reports/research_report_v2.md)

## The research question

A gene is a stretch of DNA that carries instructions a cell can use. Databases can link the same gene to
aging for different reasons. We wanted to know whether genes listed in both **GenAge Human**, a database
of aging-related genes, and **CellAge**, a database of experiments on cellular senescence, showed a
stronger age-related signal than comparable genes. Cellular senescence is a state in which a cell stops
dividing but remains alive.

## Key findings

- **113 genes appeared in both databases.** Bonnefous et al. (2024) had already published the same count.
  We reproduced the count with documented inputs and eligibility rules. The published materials do
  not let us verify whether the two studies identified exactly the same genes.
  [Prior work and comparison](docs/related_work.md#bonnefous-et-al-2024)
- **109 of the 113 genes qualified for testing in both groups of donors.** Of those 109, **63** showed
  the same direction of association with donor age in both groups. For each of those genes, activity
  tended to rise with age in both groups or fall with age in both groups.
  [Gene-level results](reports/phase7_baseline_results.md#independent-association-analysis)
- **The selected gene set did not outperform matched comparison sets under the rule we set before
  analysis.** We compared it with sets of other genes that had similar levels of measured activity and
  similar rates of detection. [RNA-seq results and interpretation](reports/phase7_baseline_results.md)
- **The project found no evidence that an intervention extends human lifespan.** The evidence review
  found that multiple records sometimes point to a single experiment. To judge a claim, check what the
  study measured. [Evidence audit](reports/phase7b_evidence_audit.md)

![Confirmed genes by database membership: 194 GenAge Human only, 113 in both, 752 CellAge only](reports/gene_overlap.svg)

## How we did the research

1. **Collected versioned public data.** We recorded the exact files used for each analysis.
2. **Checked gene identities and counted the overlap.** We matched database entries using official human
   gene identifiers so that alternate names did not count as separate genes.
3. **Summarized documented gene functions.** We used Gene Ontology, a shared vocabulary for describing
   what genes and their products do, to summarize recorded biological processes.
4. **Tested the shared gene set.** We used RNA sequencing (RNA-seq) measurements as a readout of gene
   activity in lab-grown human fibroblasts, a type of connective tissue cell. The two datasets come from
   the public Gene Expression Omnibus (GEO) archive.
5. **Reviewed original evidence.** We traced selected records for TP53, CDKN2A, TERT, FOXO3 and SIRT6 to
   their studies and recorded what each study actually tested.
6. **Built and evaluated the assistant.** We tested whether it could return findings and source links,
   and whether it could recognize questions outside its scope.

[Research story, vocabulary and stage-by-stage sources](docs/START_HERE.md)

## Research Assistant

| Mode | Use it to |
| --- | --- |
| **Research Q&A** | Look up specific findings in English about the gene activity study or the TP53, CDKN2A and TERT evidence review. |
| **Evidence records** | Find a saved record by ID, a paper by its PubMed ID, or selected FOXO3 and SIRT6 evidence. |
| **Local AI (Experimental)** | Explore excerpts from five project reports in English or Russian. The optional local model, `qwen3:1.7b`, can generate a summary through Ollama. |

The first two modes use fixed lookup rules and stored evidence. This is what **deterministic** means
here. They work without an AI model and answer within the project's scope.

### Launch web chat

The assistant runs on your computer in a browser. There is currently no public online demo. Start with
the two lookup modes and try one of the example buttons. [Install and run Streamlit](docs/TRY_ASSISTANT.md#1-start-the-assistant)

### Local AI — Experimental

Generated answers can make unsupported scientific claims even when the source links are valid. In a
separate bilingual evaluation set, the model cited a study that reduced FOXO3 in cultured cells and used
it to draw an unsupported conclusion about FOXO3 activation and human lifespan. Read the cited passage
before relying on a generated answer. This mode is **not ready for a stable release**.
[Optional Ollama setup](docs/TRY_ASSISTANT.md#3-add-local-ai-optional) · [Phase 8A results and handoff](docs/phase8a_final_status.md)

## Scientific limits

- The overlap depends on the database versions and the rules for matching genes. It counts genes recorded
  in both sources.
- The activity test used two groups of donors and lab-grown fibroblasts. It tested a specific comparison
  with matched genes. The result leaves open the possibility of age-related signals in other tissues or
  settings.
- A relationship between gene activity and donor age can arise for several reasons. Results from cells,
  mice or comparisons between people do not establish the effect of a treatment on human lifespan.

[Full scientific report and open questions](reports/research_report_v2.md#open-questions-and-proposed-experiments)

## Find what you need

| If you want to… | Read |
| --- | --- |
| Understand the project without a biology background | [Start here](docs/START_HERE.md) |
| Run the app and try verified examples | [Try the assistant](docs/TRY_ASSISTANT.md) |
| Inspect the scientific methods, results and sources | [Consolidated report](reports/research_report_v2.md) · [Short research brief](reports/research_brief.md) |
| Check published results or rebuild them from original inputs | [Reproduce the research](docs/REPRODUCE.md) |
| Review where the experimental model succeeded and failed | [Phase 8A handoff](docs/phase8a_final_status.md) · [Live evaluation](docs/phase8a_multistudy_reliability.md) |

## Reproducibility

The `v2.0.0` tag preserves the scientific release. This repository includes code, derived tables and
reports. A full rebuild requires the exact source files listed in the manifests. You can use the
assistant and run its evidence checks with the files already in Git.
[Verification and rebuild commands](docs/REPRODUCE.md)

### Official inputs

The project used GenAge Human Build 21, CellAge Build 3, official gene identifiers from HGNC and NCBI
Gene, a versioned Gene Ontology archive and two GEO studies. The reproduction guide lists each version,
source and fingerprint record. [Inputs and provenance](docs/REPRODUCE.md#official-inputs)

### Run the evidence audit and Q&A

You can score the lookups and verify the evidence ledger using the tracked files.
[Evidence audit and benchmark commands](docs/REPRODUCE.md#verify-the-evidence-audit-and-benchmarks)

### Source attribution and reuse

GenAge and CellAge come from the Human Ageing Genomic Resources (HAGR). The Gene Ontology Consortium
supplies GO data, and the RNA-seq datasets come from their originating studies via GEO. The project
documents the applicable terms and references. [Data credits and reuse terms](docs/REPRODUCE.md#source-attribution-and-reuse)
