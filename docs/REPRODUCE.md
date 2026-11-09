# Reproduce the research

Choose the check that matches your goal. To run the app, install Streamlit and use the results already in Git. To check the evidence ledger or rerun the lookup benchmarks, use the tracked files and Python 3.11 or newer. To rebuild the scientific analyses, obtain the exact source files listed below. The scientific release is tagged `v2.0.0`. [App setup](TRY_ASSISTANT.md) · [Scientific report and release verification](../reports/research_report_v2.md#reproducibility-and-sources)

Run the commands from the repository root.

## Verify the evidence audit and benchmarks

These lookups and checks use the Python standard library.

```sh
python3 -B -m scripts.phase7c_qa 'Give the partial r for p53 in each dataset.'
python3 -B -m scripts.phase7d_evidence 'cellage SIRT6'

python3 -B -m scripts.phase7b_ledger --check
python3 -B -m scripts.phase7b_score
python3 -B -m scripts.phase7c_score baseline heldout
python3 -B -m scripts.phase7c_score candidate heldout
python3 -B -m scripts.phase7d_evidence --score
```

The Phase 7B ledger records exact source rows and notes where several records cite one paper. The 22-question Phase 7B benchmark checks facts, references, evidence types and when the lookup declines to answer. It is a development set for focused English questions. The Phase 7C results describe performance on unfamiliar wording within the same evidence collection. [Ledger](../reports/phase7b_evidence_ledger.csv) · [Phase 7B benchmark](../benchmarks/phase7b_questions.json) · [Phase 7C results](../reports/phase7c_results.md) · [Phase 7D checks](../reports/phase7b_evidence_audit.md#phase-7d-extension)

For Python callers, use `scripts.research_assistant.answer_question(question, mode="research")` for Phase 7C or `mode="records"` for Phase 7D. Each call is independent. The returned dictionary contains `status`, `abstains`, `answer`, `facts`, `evidence_type`, `references`, `limitations` and optional `details`. Status is one of `answered`, `not_measured`, `insufficient_evidence` or `unsupported_question`. [Python interface](../scripts/research_assistant.py)

## Official inputs

A SHA-256 fingerprint identifies the bytes used in a run. The manifests record the exact fingerprints, file sizes and provenance. Keep the original files outside Git. The HAGR download URLs can serve newer builds, and the NCBI Gene URL changes in place. A manifest can identify a mismatch. An exact rebuild needs a retained copy of any original file that the publisher has replaced.

| Source and version | Exact files and provenance |
| --- | --- |
| GenAge Human Build 21 (2023-08-28) | [Download human_genes.zip](https://genomics.senescence.info/genes/human_genes.zip) · [Release notes](https://genomics.senescence.info/genes/release.html) · [Pinned archive](../data/raw/human_genes.zip.json) |
| CellAge gene manipulations, Build 3 (2023-04-23) | [Download cellAge.zip](https://genomics.senescence.info/cells/cellAge.zip) · [Release notes](https://genomics.senescence.info/cells/release.html) · [Pinned archive](../data/raw/cellAge.zip.json) |
| HGNC quarterly complete set, 2026-10-06, and NCBI Gene daily export with HTTP Last-Modified 2026-11-07T08:31:40Z | [Filenames, download URLs and hashes](../data/reference_provenance.json) |
| GO archive release 2026-08-05, ontology data version 2026-07-26, with the UniProt human GAF 2.2 annotation file | [Filenames, download URLs and hashes](../data/go_provenance.json) |
| Four submitted, processed GEO files for GSE113957 and GSE226189, retrieved 2026-11-08 | [Filenames, download URLs and hashes](../data/phase7_sources.json) |

The pinned GenAge archive contains comma-delimited `genage_human.csv` and `release.html`. The CellAge archive contains tab-delimited `cellage3.tsv` and `release.html`. The archive contents determine the formats. The HAGR download index describes different delimiters and offers a separate CellAge expression-signature export, which this project did not use. [HAGR download index](https://genomics.senescence.info/download.html)

## Rebuild the inventory, overlap and GO summaries

Use Python 3.11 or newer. These stages use the standard library.

### 1. Inventory the source archives

```sh
python3 -B -m scripts.download_data
python3 -B -m scripts.inspect_data
```

The downloader saves both ZIPs and their provenance records under `data/raw/`. It checks ZIP integrity and verifies existing archives without overwriting them. If only a provenance record remains, it restores the ZIP only when the download matches the recorded fingerprint. Keep the provenance records. The inspector verifies the fingerprints, reads the tables from the ZIPs and regenerates the inventory. [Inventory report](../reports/data_inventory.md)

If HTTPS fails in a portable Python installation, point `SSL_CERT_FILE` to a trusted local CA bundle. On the tested macOS setup, `SSL_CERT_FILE=/etc/ssl/cert.pem` worked. If you download the ZIPs in a browser, save them as `data/raw/human_genes.zip` and `data/raw/cellAge.zip` with that exact spelling, then run:

```sh
python3 -B -m scripts.download_data --register-local
python3 -B -m scripts.inspect_data
```

Manual registration records when you registered a local archive. If a provenance record exists, it verifies the ZIP against it. If you cannot obtain matching files, keep the records and document the mismatch before proceeding.

### 2. Check the gene identifiers

Save the exact HGNC and NCBI Gene files under `data/raw/references/` with the filenames in the manifest. The script checks file sizes and SHA-256 before using them. [Reference manifest](../data/reference_provenance.json)

```sh
python3 -B -m scripts.harmonize_genes
python3 -B -m scripts.harmonize_genes --check
```

This generates the identifier audit and the local `data/processed/gene_mapping.csv`. The mapping keeps original symbols, identifiers and source row numbers. It fills in approved identifiers only for confirmed matches. Git ignores the downloaded reference files and the local mapping. [Identifier audit](../reports/gene_identifier_audit.md)

### 3. Rebuild the gene overlap

Use `data/processed/gene_mapping.csv` from step 2. The overlap script checks its fingerprint against the identifier audit.

```sh
python3 -B -m scripts.analyze_overlap
python3 -B -m scripts.analyze_overlap --check
```

The shared-gene table links each gene to its GenAge and CellAge records. The report keeps the unresolved FNTB / CHURC1-FNTB mapping separate. Neither possible assignment changes the overlap count. [Overlap report](../reports/gene_overlap.md) · [Shared-gene table](../reports/gene_overlap_genes.csv)

### 4. Rebuild the Gene Ontology (GO) annotations

Keep the pinned HGNC file and the mapping from step 2. Save the two official GO files under `data/raw/references/` using the exact filenames in the GO manifest. The script verifies the GO and HGNC inputs and reconstructs the shared-gene table for a byte-for-byte input check. [GO manifest](../data/go_provenance.json)

```sh
python3 -B -m scripts.annotate_go
python3 -B -m scripts.annotate_go --check
```

The GO counts describe the available annotations under two evidence filters. They do not test whether a process occurs more often than expected. [GO report](../reports/go_biological_processes.md) · [Annotation table](../reports/go_gene_annotations.csv) · [Process counts](../reports/go_process_summary.csv) · [Figure](../reports/go_biological_processes.svg)

## Rebuild the RNA-seq analysis

Use Python 3.11 with the pinned Phase 7 packages in a separate environment. Keep the pinned HGNC file and the shared-gene table from the overlap analysis. Save the four files in the GEO manifest under `data/raw/phase7/` using their exact basenames. The commands and download loop are in the data audit. Skip the download loop if you already have matching copies. [Phase 7 setup, downloads and commands](../reports/phase7_data_feasibility.md#provenance-reuse-and-reproduction) · [GEO manifest](../data/phase7_sources.json) · [Dependency pins](../requirements-phase7.txt)

Once the files and environment are in place, run:

```sh
.venv/phase7/bin/python -B -m scripts.phase7_data
.venv/phase7/bin/python -B -m scripts.phase7_baseline
```

The baseline verifies the frozen protocol fingerprint and writes aggregate metrics and gene-level estimates under `data/processed/phase7/`. The study measured donor-age associations in cultured fibroblasts and tested age prediction within the discovery dataset. External prediction performance and the effect of an intervention on human lifespan remain unknown. [Frozen protocol](phase7_research_protocol.md) · [RNA-seq results](../reports/phase7_baseline_results.md)

## Run the automated tests

Use the Streamlit environment for the full application suite, including the UI tests. Use the separate Phase 7 environment for the RNA-seq tests. The standard-library command `python3 -B -m unittest discover -s tests -v` also runs the main suite but skips the Streamlit tests when Streamlit is unavailable. [UI environment setup](TRY_ASSISTANT.md#1-start-the-assistant)

```sh
.venv/ui/bin/python -B -m unittest discover -s tests -v
.venv/phase7/bin/python -B -m unittest discover -s tests/phase7 -v
```

## Source attribution and reuse

HAGR gives attribution terms under CC BY 3.0 Unported and asks users to contact its maintainers before making many queries or retrieving large volumes. Cite de Magalhães et al. (2024) for HAGR, Tacutu et al. (2018) for GenAge and Avelar et al. (2020) for CellAge. [HAGR terms](https://genomics.senescence.info/legal.html) · [References](../reports/research_report_v1.md#references)

GO archive data from release 2026-08-05 are © Gene Ontology Consortium and available under CC BY 4.0. This project filtered, joined and summarized those data in its derived tables and figure. [GO attribution](../reports/go_biological_processes.md#provenance-and-outputs) · [GO citation policy](https://geneontology.org/docs/go-citation-policy/)

For RNA-seq, cite the GEO series and the originating studies. GEO notes that submitters may assert rights in their data. The repository has no explicit reuse license for its original code and prose. The source-data terms apply to their respective materials. [GEO disclaimer](https://www.ncbi.nlm.nih.gov/geo/info/disclaimer.html) · [Data sources and papers](../reports/phase7_data_feasibility.md)
