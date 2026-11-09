# Start here

The project began with a practical question. If two public databases connect a gene to aging, what evidence lies behind the entries? We wanted to check which genes the databases shared, whether those genes showed a stronger age-related signal in human cell data, and how far the underlying experiments let us go.

## 1. Find genes that the databases share

GenAge Human lists genes linked to aging, sometimes on the basis of experiments in other species. CellAge records experiments in which researchers changed a gene's activity and looked for changes in **cellular senescence**, a state in which a cell stops dividing but stays alive. A **gene** is a stretch of DNA that carries instructions a cell can use.

One gene can have several names. We used official identifiers from NCBI Gene and the HUGO Gene Nomenclature Committee (HGNC) to match the same human gene across sources. We counted **113 shared genes** among **307** confirmed GenAge Human genes and **865** confirmed CellAge genes. Bonnefous et al. (2024) had already reported 113 under different eligibility rules. The published materials let us compare counts. We cannot tell whether the studies identified the same 113 genes. [Identifier audit](../reports/gene_identifier_audit.md) · [Overlap report](../reports/gene_overlap.md) · [Prior work](related_work.md#bonnefous-et-al-2024)

## 2. See which biological processes are documented

Gene Ontology (GO) gives researchers a shared vocabulary for describing what genes and their products do. We counted the biological processes that source records connect to the 113 genes. Each gene still had at least one direct link to a process after we excluded links inferred by software alone. These counts describe the available records. We did not test whether particular processes were more common than expected. [GO methods and results](../reports/go_biological_processes.md) · [Figure](../reports/go_biological_processes.svg)

## 3. Test the age signal in two groups of donors

We used two public datasets from the Gene Expression Omnibus, GSE113957 and GSE226189. They contain measurements from lab-grown human fibroblasts, a type of connective tissue cell. Cells make RNA copies of instructions in DNA. **RNA sequencing (RNA-seq)** measures the RNA in a sample, which researchers can use to estimate how active genes are.

We asked whether the selected set of genes, also called a **panel**, showed a stronger relationship with donor age across the two groups than comparable gene sets. A **correlation** measures the direction and strength of a relationship between two quantities. Here we used partial correlations, which estimate the relationship after accounting for variables included in the analysis. A relationship can exist without either quantity causing the other.

**109** of the 113 genes passed the filters in both groups. For **63 of those 109**, the estimated relationship with age pointed in the same direction in both groups. Under the rule we set before analysis, the panel did not outperform sets of other genes chosen to have similar measured activity and rates of detection. That result applies to this comparison and these cells. [Data and donors](../reports/phase7_data_feasibility.md) · [Analysis protocol](phase7_research_protocol.md) · [Results](../reports/phase7_baseline_results.md)

## 4. Check what the original studies measured

We examined records for TP53, CDKN2A and TERT, then extended the review to FOXO3 and SIRT6. A **citation** points to a source for a claim. Two database records can cite the same study. To judge a claim, check who or what was studied, what researchers changed and what they measured.

For example, an experiment that reduced FOXO3 activity in lab-grown human skin cells measured changes in the cells. A separate study found an association between **genotype**, the versions of DNA a person carries at a given location, and exceptional longevity in Japanese American men. The second study did not change FOXO3 activity. The two studies cannot tell us whether changing FOXO3 would extend a person's life. [TP53, CDKN2A and TERT](../reports/gene_case_studies.md) · [FOXO3 and SIRT6](../reports/phase7d_case_studies.md) · [Evidence audit](../reports/phase7b_evidence_audit.md)

## 5. Make the evidence easier to find

Research Q&A and Evidence records use fixed rules to return information from the project's saved results. Research Q&A handles focused English questions. Evidence records accepts commands that look up a record, paper or selected gene evidence. The evaluation tested whether the lookup could handle unfamiliar wording and point to the right source. [Lookup evaluation](../reports/phase7c_results.md) · [Evidence records checks](../reports/phase7b_evidence_audit.md#phase-7d-extension)

## 6. Test an optional local model

Local AI searches excerpts from five project reports. It can use a model on your computer to summarize passages in English or Russian. We evaluated real answers, including whether the cited passages supported them. A separate set of questions exposed a critical error about FOXO3 activation and human lifespan. The mode remains experimental. [Latest evaluation](phase8a_multistudy_reliability.md) · [Phase 8A handoff](phase8a_final_status.md)

To follow the evidence yourself, open the scientific report or try the app and inspect the sources below an answer. [Full scientific report](../reports/research_report_v2.md) · [Try the assistant](TRY_ASSISTANT.md) · [Reproduce the research](REPRODUCE.md)
