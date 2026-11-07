# Research plan

## Question and scope

Which human genes are represented in both the GenAge Human and CellAge databases, and which biological processes are associated with these genes?

The inputs are the GenAge Human export and the CellAge gene-manipulation export documented in the [README](../README.md). The comparison concerns membership in two curated resources. GenAge covers evidence relevant to aging in humans, including candidates supported by model-organism research. CellAge covers perturbation experiments on cellular senescence in human cells.

## Milestones and methodology

1. **Acquire and inspect the source exports.** Preserve the original archives and checksum records. Record the actual schemas, row counts, missing cells, duplicate rows, and identifier consistency. The [data inventory](../reports/data_inventory.md) documents this milestone.
2. **Harmonize identifiers.** Choose and archive a dated human reference from NCBI Gene and use HGNC to verify approved and previous symbols. Check taxon 9606, current and retired identifiers, aliases, and conflicting mappings. Preserve all original identifiers and document each resolution, along with unresolved or ambiguous entries.
3. **Construct the gene intersection.** Reduce each source to unique validated human gene IDs for membership comparisons. Preserve a link to all source rows, including multiple CellAge records for one gene. Report mapping coverage and counts excluded because of unresolved identity. Generate a versioned table with the shared IDs, approved symbols, and source evidence references.
4. **Describe biological processes.** Use a pinned Gene Ontology Biological Process annotation release for human genes. Record evidence codes and annotation coverage and document the policy for inferred annotations and qualifiers such as `NOT`. Start with a descriptive gene-to-process table. Any later enrichment study would require a separately defined gene universe and a multiple-testing plan.

## Limitations

- Absence from either database reflects the coverage of that snapshot and gives no evidence that a gene is unrelated to aging or senescence.
- Whole-organism aging and cellular senescence are distinct phenomena. A gene manipulation can have different effects depending on the human cell type, perturbation, or senescence trigger.
- The databases differ in their inclusion criteria and evidence. Multiple CellAge records can describe the same gene in different experimental contexts. Gene counts must be computed after identifier resolution and deduplication.
- Curated evidence can reflect publication and selection biases. Database overlap and process annotations support descriptive associations. Causal claims about human aging require separate evidence.
