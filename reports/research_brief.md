# Research brief · AI for Science and computational biology

*Experimental v2.0 · For prospective research internship supervisors*

## Research question

Can evidence curated for cellular senescence and organismal aging identify a gene panel with reproducible age-associated expression in human fibroblasts? A second question is whether a small research assistant can trace each answer to the source record and distinguish an unmeasured outcome from a measured negative.

## Methods and contribution

The project connects checksum-pinned GenAge, CellAge, HGNC, NCBI Gene and Gene Ontology inputs with two public GEO fibroblast RNA-seq cohorts. The workflow resolves gene identifiers, records exclusions, compares a fixed panel with expression-matched controls, and traces selected literature claims to their interventions and endpoints. A deterministic lookup returns exact citations and evidence types. These are examples of provenance tracking, statistical evaluation and benchmark design on a scientific problem. [Consolidated report and inputs](research_report_v2.md)

## Selected results

| Question | Result |
| --- | --- |
| Where do the curated sets overlap? | **113 shared genes** among 307 confirmed GenAge genes and 865 confirmed CellAge genes. Bonnefous et al. reported the same count under different eligibility rules. Gene-level equivalence remains unverified. |
| Does the panel show a stronger reproducible RNA-seq age signal? | **109 genes** could be tested in both cohorts. The panel replication score was **0.00464**, below the **0.00685** matched-panel median. Within discovery, Ridge reached **15.34 years MAE**, compared with **20.38** for median age and **15.03** for the median matched Ridge comparator. |
| What do the curated labels establish? | An audit of five genes found cases where several records cite one experiment and where an annotation is more specific than the measured endpoint. For SIRT6, acute depletion increased senescence markers in cultured chondrocytes. Replicative exhaustion was unestablished in the reviewed methods. |
| Does the evidence lookup handle new wording? | Terminology normalization improved exact answers from **5/24 to 18/24** on held-out prompts. The remaining misses were generic abstentions, including questions combining evidence across sources. |

## Limits and research interests

The RNA-seq analysis concerns donor chronological age in cultured fibroblasts. It leaves external prediction performance and intervention effects on human lifespan unresolved. The held-out benchmark is small, uses a common evidence corpus and has no external reviewer.

A follow-up research question is whether a comparable independent cohort with recorded culture passage and technical covariates would reproduce the association result. The accompanying report gives source locators, commands and limitations for assessing the work. [Full scientific report](research_report_v2.md) · [Evidence audit and lookup](phase7b_evidence_audit.md#phase-7d-extension)
