# Human Aging and Cellular Senescence Genes

*Research brief for prospective master's research internship supervisors*

## Motivation

Cellular senescence is relevant to aging, but a change in cell proliferation in culture answers a different question from a change in organismal survival. This project examines where two curated gene sets overlap and how much of the shared evidence can be traced to a defined experiment.

## Data and workflow

We used HAGR GenAge Human Build 21 (2023-08-28), CellAge gene manipulations Build 3 (2023-04-23) and GO archive release 2026-08-05. We validated human Gene IDs and symbols against pinned HGNC and NCBI Gene snapshots, computed the intersection, and summarized direct GO Biological Process annotations with and without electronically inferred annotations (IEA). We then traced CellAge and selected GO citations for TP53, CDKN2A and TERT. [Full report and input versions](research_report_v1.md)

## Main results

- **113 shared genes** among 307 confirmed GenAge Human and 865 confirmed CellAge genes. The union contained 1,059 genes (Jaccard similarity 0.106704).
- **125 CellAge records** map to the shared genes. A record can reuse a publication. One unresolved CellAge mapping, FNTB / CHURC1-FNTB, was excluded. Neither candidate assignment changes the shared count.
- **113 of 113 shared genes** have direct GO Biological Process coverage under both evidence policies. Distinct terms decrease from 1,805 to 1,532 after removing IEA.
- **Three case studies show distinct experimental outcomes.** Restoring p53 in EJ carcinoma cells and delivering p16 to normal TIG-3 fibroblasts induced senescence phenotypes. Expressing hTERT in two initially telomerase-negative human cell types delayed replicative senescence. The same TERT study appears in both CellAge and GO. [Evidence matrix](gene_evidence_matrix.csv)

## Scientific limitations

The counts depend on database inclusion rules, curation and annotation coverage. They describe overlap and annotation frequency. The study did not test enrichment or train a machine-learning model. Culture results and model-specific animal survival results do not establish effects on human lifespan.

## Future research directions

A follow-up could audit more of the 125 CellAge records by unique publication, cell type, perturbation and endpoint. Comparing those strata would help identify which conclusions have independent support across cell models. [Methods, figures and references](research_report_v1.md)
