# Research plan

## Question and scope

Which human genes are represented in both the GenAge Human and CellAge databases, and which biological processes are associated with these genes?

The inputs are the GenAge Human export and the CellAge gene-manipulation export documented in the [README](../README.md). The comparison concerns membership in two curated resources. GenAge covers evidence relevant to aging in humans, including candidates supported by model-organism research. CellAge covers perturbation experiments on cellular senescence in human cells.

## Milestones and methodology

1. **Acquire and inspect the source exports.** Preserve the original archives and checksum records. Record the actual schemas, row counts, missing cells, duplicate rows, and identifier consistency. The [data inventory](../reports/data_inventory.md) documents this milestone.
2. **Harmonize identifiers.** Validate current taxon 9606 Gene IDs and cross-references against pinned NCBI Gene and HGNC files. Use approved and previous symbols or aliases to check each mapping. Preserve original identifiers and record references. The [identifier audit](../reports/gene_identifier_audit.md) records confirmed and unresolved mappings. Absent Gene IDs, if encountered in a future run, require targeted history review before they can be classified as retired.
3. **Construct the gene intersection.** Compare confirmed human Entrez Gene IDs and verify that approved HGNC identifiers agree. Preserve links to source records, including multiple CellAge experiments for one gene. The [overlap report](../reports/gene_overlap.md) documents the descriptive counts and the sensitivity analysis for the unresolved CellAge record.
4. **Describe biological processes.** Use a pinned Gene Ontology release and approved HGNC UniProtKB cross-references. Count unique genes per direct positive Biological Process term and report coverage with and without IEA. Preserve excluded annotations for audit. The [GO BP report](../reports/go_biological_processes.md) documents the rules and results. Any later enrichment study would require a separately defined gene universe and a multiple-testing plan.

## Limitations

- Absence from either database reflects the coverage of that snapshot and gives no evidence that a gene is unrelated to aging or senescence.
- Whole-organism aging and cellular senescence are distinct phenomena. A gene manipulation can have different effects depending on the human cell type, perturbation, or senescence trigger.
- The databases differ in their inclusion criteria and evidence. Multiple CellAge records can describe the same gene in different experimental contexts. Gene counts must be computed after identifier resolution and deduplication.
- Curated evidence can reflect publication and selection biases. Database overlap and process annotations support descriptive associations. Causal claims about human aging require separate evidence.
